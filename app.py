from pdf_loader import load_pdf, chunk_text
from vector_store import VectorStore
from query_parser import parse_query
from rag_reasoner import reason_with_clauses

if __name__ == "__main__":
    pdf_text = load_pdf("/Users/manav/Documents/SmartClaimsAI/sample docs/BAJHLIP23020V012223.pdf")
    chunks = chunk_text(pdf_text)

    store = VectorStore(chunks)

    raw_query = "46M, knee surgery, Pune, 3-month policy"
    parsed_query = parse_query(raw_query)

    top_chunks = store.search(raw_query)

    decision = reason_with_clauses(parsed_query, "\n\n".join(top_chunks))

    print("\n--- CLAIM DECISION ---")
    print(decision)