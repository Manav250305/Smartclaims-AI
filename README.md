# SmartClaims AI

SmartClaims AI is a system that leverages Large Language Models (LLMs) to analyze insurance documents and answer natural language claim queries. It provides structured decisions with clause-level justifications extracted from unstructured documents like PDFs, Word files, and emails.

---

## Features

- Upload any insurance policy document (PDF format)
- Enter claim queries in natural language (e.g., "46-year-old male, knee surgery in Mumbai, 2-month-old policy")
- The system returns a structured JSON response including:
  - Claim decision (Approved or Rejected)
  - Claim amount (if applicable)
  - Justification mapped to specific policy clauses
- Semantic search using FAISS and OpenAI embeddings
- Clause-based reasoning using GPT (3.5-turbo or GPT-4)
- Interactive Streamlit-based frontend for ease of use

---

## Example Output

```json
{
  "decision": "Rejected",
  "amount": "0",
  "justification": [
    {
      "clause": "Specified disease/procedure waiting period (Code-Excl02)",
      "explanation": "The policy specifies a waiting period of 24 months for ACL knee surgery. Since the policy duration is only 2 months, the claim is not eligible."
    }
  ]
}
