from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    filename: str
    created_at: datetime
    chunk_count: int = 0


class RetrievedChunk(BaseModel):
    document_filename: str
    chunk_index: int
    content: str
    relevance_score: float
