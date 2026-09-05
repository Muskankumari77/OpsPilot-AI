"""
RAG service.

    DOCUMENT -> TEXT EXTRACTION -> CHUNKING -> EMBEDDINGS -> VECTOR STORE
    -> SEMANTIC SEARCH -> (used by the Copilot's search_knowledge_base tool)
    -> LLM -> ANSWER + CITATIONS

Text extraction supports .txt and .md directly (read as plain text). PDF
support would need an extra parsing dependency (pypdf) — deferred as a
future improvement, consistent with the lean-build philosophy of adding a
dependency only when a real request needs it.
"""
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError, ValidationError
from app.models.document import Document, DocumentChunk
from app.rag.chunker import chunk_text
from app.rag.vector_store import cosine_similarity, embed_text
from app.schemas.knowledge_base import DocumentOut, RetrievedChunk

SUPPORTED_EXTENSIONS = {".txt", ".md"}


def ingest_document(db: Session, organization_id: int, user_id: int, filename: str, raw_bytes: bytes) -> Document:
    extension = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if extension not in SUPPORTED_EXTENSIONS:
        raise ValidationError("Only .txt and .md files are supported for the knowledge base right now.")

    text = raw_bytes.decode("utf-8", errors="ignore")
    chunks = chunk_text(text)
    if not chunks:
        raise ValidationError("That file appears to be empty.")

    document = Document(organization_id=organization_id, uploaded_by_user_id=user_id, filename=filename)
    db.add(document)
    db.flush()

    for i, chunk in enumerate(chunks):
        db.add(
            DocumentChunk(
                organization_id=organization_id,
                document_id=document.id,
                chunk_index=i,
                content=chunk,
                embedding=embed_text(chunk),
            )
        )

    db.commit()
    db.refresh(document)
    return document


def list_documents(db: Session, organization_id: int) -> list[DocumentOut]:
    documents = db.query(Document).filter(Document.organization_id == organization_id).all()
    return [
        DocumentOut(id=d.id, filename=d.filename, created_at=d.created_at, chunk_count=len(d.chunks))
        for d in documents
    ]


def delete_document(db: Session, organization_id: int, document_id: int) -> None:
    document = (
        db.query(Document)
        .filter(Document.id == document_id, Document.organization_id == organization_id)
        .first()
    )
    if not document:
        raise NotFoundError("Document not found.")
    db.delete(document)
    db.commit()


def search_knowledge_base(db: Session, organization_id: int, query: str, top_k: int = 3) -> list[RetrievedChunk]:
    chunks = db.query(DocumentChunk).filter(DocumentChunk.organization_id == organization_id).all()
    if not chunks:
        return []

    query_vector = embed_text(query)
    scored = [(c, cosine_similarity(query_vector, c.embedding)) for c in chunks]
    scored.sort(key=lambda x: x[1], reverse=True)

    results = []
    for chunk, score in scored[:top_k]:
        if score <= 0:
            continue  # no meaningful lexical overlap — don't force a citation
        results.append(
            RetrievedChunk(
                document_filename=chunk.document.filename,
                chunk_index=chunk.chunk_index,
                content=chunk.content,
                relevance_score=round(score, 3),
            )
        )
    return results
