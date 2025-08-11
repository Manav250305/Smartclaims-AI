from flask import Flask, request, jsonify
import json
import logging
from datetime import datetime
import traceback
import os
import tempfile

# Import your existing modules
from pdf_loader import load_pdf, chunk_text
from vector_store import VectorStore
from query_parser import parse_query
from rag_reasoner import reason_with_clauses

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Global variable to store the vector store (you might want to use a proper cache/database)
vector_stores = {}


def initialize_vector_store(pdf_path, store_id):
    """Initialize and cache a vector store for a given PDF"""
    try:
        if store_id not in vector_stores:
            logger.info(f"Loading PDF and creating vector store for {store_id}")
            pdf_text = load_pdf(pdf_path)
            chunks = chunk_text(pdf_text)
            vector_stores[store_id] = VectorStore(chunks)
            logger.info(f"Vector store created successfully for {store_id}")
        return vector_stores[store_id]
    except Exception as e:
        logger.error(f"Error initializing vector store: {str(e)}")
        raise


@app.route("/api/v1/hackrx/run", methods=["GET", "POST"])
def hackrx_run():
    """
    Main HackRX endpoint to process insurance claims

    Expected payload:
    {
        "claim_id": "unique_claim_identifier",
        "query": "46M, knee surgery, Pune, 3-month policy",
        "pdf_path": "/path/to/policy/document.pdf",
        "policy_id": "BAJHLIP23020V012223",
        "timestamp": "2024-01-01T10:00:00Z"
    }
    """
    try:
        # Handle GET requests (for testing/health check)
        if request.method == "GET":
            return (
                jsonify(
                    {
                        "status": "ready",
                        "message": "SmartClaimsAI HackRX endpoint is running",
                        "endpoint": "/api/v1/hackrx/run",
                        "method": "POST",
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                ),
                200,
            )

        # Validate request
        if not request.is_json:
            return jsonify({"error": "Request must be JSON", "status": "failed"}), 400

        data = request.get_json()
        # Validate required fields (pdf_path is now optional)
        required_fields = ["claim_id", "query"]
        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            return (
                jsonify(
                    {
                        "error": f"Missing required fields: {', '.join(missing_fields)}",
                        "status": "failed",
                    }
                ),
                400,
            )

        claim_id = data["claim_id"]
        raw_query = data["query"]
        pdf_path = data.get("pdf_path")  # Optional now
        policy_id = data.get("policy_id", "default")

        # If no PDF provided, use default
        if not pdf_path:
            pdf_path = "/Users/manav/Documents/SmartClaimsAI/sample docs/Arogya Sanjeevani Policy - CIN - U10200WB1906GOI001713 1.pdf"
            logger.info("No PDF provided, using default Arogya Sanjeevani policy")

        logger.info(f"Processing claim {claim_id}: {raw_query}")

        # Initialize vector store
        store = initialize_vector_store(pdf_path, policy_id)

        # Parse the query
        parsed_query_str = parse_query(raw_query)

        # Search for relevant chunks
        top_chunks = store.search(raw_query)

        # Make decision using RAG reasoner
        decision_str = reason_with_clauses(parsed_query_str, "\n\n".join(top_chunks))

        # Parse JSON strings into actual objects
        try:
            if parsed_query_str is not None:
                parsed_query = json.loads(parsed_query_str)
            else:
                parsed_query = {
                    "error": "Query string is None",
                    "raw": parsed_query_str,
                }
        except:
            parsed_query = {"error": "Failed to parse query", "raw": parsed_query_str}

        try:
            if decision_str is not None:
                decision = json.loads(decision_str)
            else:
                decision = {"error": "Decision string is None", "raw": decision_str}
        except:
            decision = {"error": "Failed to parse decision", "raw": decision_str}

        # Prepare response
        response = {
            "status": "success",
            "claim_id": claim_id,
            "query": raw_query,
            "parsed_query": parsed_query,
            "decision": decision,
            "processed_at": datetime.utcnow().isoformat(),
            "policy_id": policy_id,
            "pdf_source": (
                "uploaded"
                if pdf_path
                != "/Users/manav/Documents/SmartClaimsAI/sample docs/Arogya Sanjeevani Policy - CIN - U10200WB1906GOI001713 1.pdf"
                else "default"
            ),
        }

        logger.info(f"Claim {claim_id} processed successfully")

        # Clean up temporary file if it was uploaded
        if pdf_path and pdf_path.startswith(tempfile.gettempdir()):
            try:
                os.remove(pdf_path)
                logger.info(f"Temporary file {pdf_path} cleaned up")
            except:
                pass

        return jsonify(response), 200

    except FileNotFoundError:
        error_msg = f"PDF file not found: {data.get('pdf_path', 'unknown')}"
        logger.error(error_msg)
        return (
            jsonify(
                {
                    "error": error_msg,
                    "status": "failed",
                    "claim_id": data.get("claim_id", "unknown"),
                }
            ),
            404,
        )

    except Exception as e:
        error_msg = f"Error processing claim: {str(e)}"
        logger.error(f"{error_msg}\n{traceback.format_exc()}")
        return (
            jsonify(
                {
                    "error": error_msg,
                    "status": "failed",
                    "claim_id": data.get("claim_id", "unknown"),
                }
            ),
            500,
        )


@app.route("/api/v1/hackrx/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return (
        jsonify(
            {
                "status": "healthy",
                "service": "SmartClaimsAI HackRX API",
                "timestamp": datetime.utcnow().isoformat(),
            }
        ),
        200,
    )


@app.route("/api/v1/hackrx/status/<claim_id>", methods=["GET"])
def get_claim_status(claim_id):
    """Get status of a processed claim (you might want to implement proper storage)"""
    # This is a placeholder - you'd typically store claim results in a database
    return (
        jsonify(
            {
                "claim_id": claim_id,
                "message": "Status endpoint - implement database storage for claim tracking",
            }
        ),
        200,
    )


@app.route("/api/v1/hackrx/reload-policy/<policy_id>", methods=["POST"])
def reload_policy(policy_id):
    """Reload a specific policy's vector store"""
    try:
        data = request.get_json() or {}
        pdf_path = data.get("pdf_path")

        if not pdf_path:
            return jsonify({"error": "pdf_path is required", "status": "failed"}), 400

        # Remove existing vector store
        if policy_id in vector_stores:
            del vector_stores[policy_id]

        # Reinitialize
        initialize_vector_store(pdf_path, policy_id)

        return (
            jsonify(
                {
                    "status": "success",
                    "message": f"Policy {policy_id} reloaded successfully",
                    "timestamp": datetime.utcnow().isoformat(),
                }
            ),
            200,
        )

    except Exception as e:
        error_msg = f"Error reloading policy: {str(e)}"
        logger.error(error_msg)
        return jsonify({"error": error_msg, "status": "failed"}), 500


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found", "status": "failed"}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error", "status": "failed"}), 500


if __name__ == "__main__":
    # Initialize with default policy if needed
    default_pdf = "sample docs/Arogya Sanjeevani Policy - CIN - U10200WB1906GOI001713 1.pdf"
    
    try:
        initialize_vector_store(default_pdf, "AROGYA_SANJEEVANI")
        logger.info("Default Arogya Sanjeevani policy loaded successfully")
    except Exception as e:
        logger.warning(f"Could not load default policy: {str(e)}")
    
    # Use Railway's PORT environment variable (or default to 5001)
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port, debug=False)

