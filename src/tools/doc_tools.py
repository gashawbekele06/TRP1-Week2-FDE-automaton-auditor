from typing import Dict, Any, List
from pypdf import PdfReader
from langchain_core.tools import tool


@tool
def ingest_pdf(pdf_path: str, chunk_size: int = 1000, overlap: int = 200) -> Dict[str, Any]:
    """Extracts text from a PDF and splits it into chunks."""
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or "" + "\n"
    
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        start = end - overlap
    return {"chunks": chunks, "total_length": len(text)}


@tool
def query_pdf_chunks(chunks: List[str], query: str) -> List[str]:
    """Filters chunks based on a query string."""
    relevant = [chunk for chunk in chunks if query.lower() in chunk.lower()]
    return relevant if relevant else ["No relevant content found."]