"""
Fixed-size character chunking with overlap — simple and predictable, no
sentence-boundary NLP dependency needed for the document types this
targets (policies, SOPs, short internal docs).
"""


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 100) -> list[str]:
    text = text.strip()
    if not text:
        return []

    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end].strip())
        start = end - overlap  # step forward, re-covering the overlap window
    return [c for c in chunks if c]
