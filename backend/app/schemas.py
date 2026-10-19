from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field, HttpUrl, ConfigDict

class IngestRequest(BaseModel):
    type: Literal["note", "url"]
    content: str | None = Field(default=None, max_length=100000)
    url: HttpUrl | None = None

    def validate_payload(self):
        if self.type == "note" and not (self.content and self.content.strip()):
            raise ValueError("content is required for note ingestion")
        if self.type == "url" and self.url is None:
            raise ValueError("url is required for URL ingestion")

class IngestResponse(BaseModel):
    item_id: str
    status: str
    message: str

class ItemResponse(BaseModel):
    id: str
    source_type: str
    title: str
    source_url: str | None
    status: str
    error_message: str | None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ItemsResponse(BaseModel):
    items: list[ItemResponse]

class QueryRequest(BaseModel):
    question: str = Field(min_length=3, max_length=2000)
    top_k: int | None = Field(default=None, ge=1, le=10)

class SourceResponse(BaseModel):
    item_id: str
    title: str
    source_type: str
    source_url: str | None
    chunk_id: str
    snippet: str
    score: float

class QueryResponse(BaseModel):
    answer: str
    sources: list[SourceResponse]
    retrieval_count: int
