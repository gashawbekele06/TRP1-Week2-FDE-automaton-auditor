import os
from typing import List, Dict, Tuple
from docling.document_converter import DocumentConverter

def ingest_pdf(pdf_path: str) -> List[Dict[str, str]]:
    """Ingests a PDF using docling and chunks it for RAG-lite querying."""
    if not os.path.exists(pdf_path):
        return [{"error": f"PDF file not found at {pdf_path}"}]

    try:
        converter = DocumentConverter()
        result = converter.convert(pdf_path)
        
        chunks = []
        for item, level in result.document.iterate_items():
             if hasattr(item, 'text'):
                 chunks.append({
                     "type": type(item).__name__,
                     "text": item.text,
                     "level": level
                 })
        return chunks
    except Exception as e:
        return [{"error": f"Failed to ingest PDF: {str(e)}"}]

def query_pdf(chunks: List[Dict[str, str]], keywords: List[str]) -> List[Dict[str, str]]:
    """Explicitly searches chunks for specified keywords to determine theoretical depth."""
    found_evidence = []
    
    if len(chunks) == 1 and "error" in chunks[0]:
         return found_evidence
         
    for chunk in chunks:
        text = chunk.get("text", "").lower()
        if not text:
             continue
             
        for keyword in keywords:
            if keyword.lower() in text:
                found_evidence.append({
                    "keyword": keyword,
                    "context": chunk["text"],
                    "confidence": 0.9 if len(chunk["text"]) > 50 else 0.4 # Longer context usually implies explanation vs buzzword
                })
                
    return found_evidence

def extract_cited_filepaths(chunks: List[Dict[str, str]]) -> List[str]:
    """A naive extraction of file paths formatted implicitly as code locations."""
    # Real implementation could use a better NLP model, but this handles basic forms.
    # We look for patterns like 'src/', '.py', '.ts' etc.
    filepaths = set()
    
    if len(chunks) == 1 and "error" in chunks[0]:
         return list(filepaths)
         
    for chunk in chunks:
        text = chunk.get("text", "")
        words = text.split()
        for word in words:
            # Strip common punctuation that might wrap a filename
            clean_word = word.strip(".,;:\"'()`")
            if "src/" in clean_word or clean_word.endswith(".py"):
                filepaths.add(clean_word)
                
    return list(filepaths)
