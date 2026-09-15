import logging
import time
import uuid
from pathlib import Path
from app.config import Settings
from app.database.repository import InMemoryRepository
from app.ingestion.pipeline import IngestionPipeline
from app.models import QueryResponse, SearchResult
from app.retrieval.hybrid import HybridRetriever
from app.rag.llm import GroundedAnswerGenerator

logger = logging.getLogger(__name__)


class RAGService:
    def __init__(self, settings: Settings, corpus_path: str | Path) -> None:
        self.settings = settings
        self.repository = InMemoryRepository()
        self.pipeline = IngestionPipeline()
        documents, chunks = self.pipeline.run(corpus_path)
        self.repository.replace(documents, chunks)
        self.retriever = HybridRetriever(chunks)
        self.generator = GroundedAnswerGenerator(mock=settings.mock_llm, client=self._build_client())

    def _build_client(self) -> object | None:
        if self.settings.mock_llm or not self.settings.openai_api_key:
            return None
        from openai import OpenAI
        return OpenAI(api_key=self.settings.openai_api_key, base_url=self.settings.openai_base_url)

    def query(self, question: str, roles: list[str], top_k: int) -> QueryResponse:
        started = time.perf_counter()
        request_id = str(uuid.uuid4())
        retrieval_started = time.perf_counter()
        results = self.retriever.search(question, top_k=top_k, roles=roles)
        retrieval_ms = (time.perf_counter() - retrieval_started) * 1000
        llm_started = time.perf_counter()
        answer, evidence, citations, confidence, grounded = self.generator.generate(question, results)
        llm_ms = (time.perf_counter() - llm_started) * 1000
        latency_ms = (time.perf_counter() - started) * 1000
        logger.info("request_id=%s query=%s retrieved=%s retrieval_ms=%.2f llm_ms=%.2f confidence=%.2f", request_id, question[:200], [item.chunk.page_id for item in results], retrieval_ms, llm_ms, confidence)
        return QueryResponse(request_id=request_id, answer=answer, supporting_evidence=evidence, citations=citations, confidence=confidence, retrieved_chunks=results, latency_ms=round(latency_ms, 2), grounded=grounded)

    def search_documents(self, query: str, roles: list[str] | None = None, top_k: int = 8) -> list[SearchResult]:
        return self.retriever.search(query, top_k=top_k, roles=roles or ["employee"])

    def search_by_metadata(self, space: str | None = None, tag: str | None = None, roles: list[str] | None = None) -> list[SearchResult]:
        return self.retriever.search(tag or space or "", top_k=20, roles=roles or ["employee"], space=space, tag=tag)

    def retrieve_page(self, page_id: str) -> object | None:
        return self.repository.get_document(page_id)

    def summarize_page(self, page_id: str) -> str:
        document = self.repository.get_document(page_id)
        if not document:
            return "I could not find sufficient information in the knowledge base."
        results = [SearchResult(chunk=chunk, rerank_score=1.0) for chunk in self.repository.chunks if chunk.page_id == page_id]
        answer, _, _, _, _ = self.generator.generate(f"Summarize {document.title}", results)
        return answer

    def compare_documents(self, first_id: str, second_id: str) -> str:
        first, second = self.retrieve_page(first_id), self.retrieve_page(second_id)
        if not first or not second:
            return "I could not find sufficient information in the knowledge base."
        return f"{first.title} focuses on {first.tags}; {second.title} focuses on {second.tags}. Both are synthetic knowledge-base documents."
