from datetime import date, datetime
from typing import Any
from pydantic import BaseModel, Field


class Document(BaseModel):
    page_id: str
    title: str
    space: str
    author: str
    created_date: date
    updated_date: date
    url: str
    content: str
    tags: list[str] = Field(default_factory=list)
    allowed_roles: list[str] = Field(default_factory=lambda: ["employee", "admin"])


class Chunk(BaseModel):
    chunk_id: str
    page_id: str
    title: str
    space: str
    section: str
    text: str
    tags: list[str] = Field(default_factory=list)
    allowed_roles: list[str] = Field(default_factory=lambda: ["employee", "admin"])
    chunk_index: int = 0


class SearchResult(BaseModel):
    chunk: Chunk
    semantic_score: float = 0.0
    keyword_score: float = 0.0
    hybrid_score: float = 0.0
    rerank_score: float = 0.0


class Citation(BaseModel):
    document: str
    section: str
    page_chunk: str
    page_id: str


class QueryRequest(BaseModel):
    question: str = Field(min_length=3, max_length=2000)
    roles: list[str] = Field(default_factory=lambda: ["employee"])
    top_k: int = Field(default=8, ge=1, le=20)


class QueryResponse(BaseModel):
    request_id: str
    answer: str
    supporting_evidence: list[str]
    citations: list[Citation]
    confidence: float
    retrieved_chunks: list[SearchResult]
    latency_ms: float
    grounded: bool


class DocumentCreate(BaseModel):
    document: Document


class HealthResponse(BaseModel):
    status: str
    documents: int
    chunks: int
    timestamp: datetime


class EvaluationItem(BaseModel):
    question: str
    expected_sources: list[str]
    category: str
    answerable: bool = True
    expected_terms: list[str] = Field(default_factory=list)


class EvaluationReport(BaseModel):
    retrieval_precision: float
    retrieval_recall: float
    answer_correctness: float
    citation_correctness: float
    groundedness: float
    hallucination_rate: float
    average_latency_ms: float
    cases: list[dict[str, Any]]
