# core.py
from pdf_loader import load_pdf, chunk_text
from vector_store import VectorStore
from query_parser import parse_query
from rag_reasoner import reason_with_clauses

def run_pipeline(query, pdf_path):
    text = load_pdf(pdf_path)
    chunks = chunk_text(text)
    store = VectorStore(chunks)
    parsed = parse_query(query)
    top_chunks = store.search(query)
    decision = reason_with_clauses(parsed, "\n\n".join(top_chunks))
    return parsed, decision