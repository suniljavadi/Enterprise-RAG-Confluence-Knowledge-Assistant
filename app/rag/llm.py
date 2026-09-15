import re
from app.models import Citation, SearchResult
from app.security.guards import sanitize_document


class GroundedAnswerGenerator:
    def __init__(self, mock: bool = True, client: object | None = None) -> None:
        self.mock = mock
        self.client = client

    def generate(self, question: str, results: list[SearchResult]) -> tuple[str, list[str], list[Citation], float, bool]:
        usable = [result for result in results if result.rerank_score >= 0.18]
        if not usable:
            return "I could not find sufficient information in the knowledge base.", [], [], 0.05, False
        evidence = [sanitize_document(result.chunk.text) for result in usable[:4]]
        citations = [Citation(document=result.chunk.title, section=result.chunk.section, page_chunk=result.chunk.chunk_id, page_id=result.chunk.page_id) for result in usable[:4]]
        if self.mock or self.client is None:
            answer = "Based on the knowledge base: " + " ".join(evidence[:3])
        else:
            answer = self._call_llm(question, evidence)
        confidence = min(0.98, max(0.45, sum(result.rerank_score for result in usable[:3]) / max(1, len(usable[:3])) + 0.35))
        return answer, evidence, citations, round(confidence, 2), True

    def _call_llm(self, question: str, evidence: list[str]) -> str:
        prompt = "Answer only from these sources. If unsupported, say insufficient information.\nQuestion: " + question + "\nSources:\n" + "\n".join(evidence)
        response = self.client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "system", "content": "You are a grounded enterprise knowledge assistant."}, {"role": "user", "content": prompt}])
        return response.choices[0].message.content
