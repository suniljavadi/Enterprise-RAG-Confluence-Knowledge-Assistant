import re
from app.embeddings.hash_embeddings import HashEmbeddingModel
from app.models import Chunk, SearchResult
from app.security.guards import authorized

STOPWORDS = {"a", "an", "and", "are", "for", "how", "is", "of", "the", "to", "what", "which", "who"}


class HybridRetriever:
    def __init__(self, chunks: list[Chunk], embedding_model: HashEmbeddingModel | None = None) -> None:
        self.chunks = chunks
        self.embedding_model = embedding_model or HashEmbeddingModel()
        self.vectors = [self.embedding_model.embed(chunk.text) for chunk in chunks]

    def search(self, query: str, top_k: int = 8, roles: list[str] | None = None, space: str | None = None, tag: str | None = None) -> list[SearchResult]:
        roles = roles or ["employee"]
        query_tokens = set(re.findall(r"[a-z0-9]+", query.lower())) - STOPWORDS
        query_vector = self.embedding_model.embed(query)
        results: list[SearchResult] = []
        for chunk, vector in zip(self.chunks, self.vectors):
            if not authorized(chunk, roles) or (space and chunk.space != space) or (tag and tag not in chunk.tags):
                continue
            tokens = set(re.findall(r"[a-z0-9]+", chunk.text.lower())) - STOPWORDS
            keyword = len(query_tokens & tokens) / max(1, len(query_tokens))
            semantic = self.embedding_model.similarity(query_vector, vector)
            if keyword == 0.0 and semantic < 0.82:
                continue
            hybrid = 0.35 * semantic + 0.65 * keyword
            results.append(SearchResult(chunk=chunk, semantic_score=semantic, keyword_score=keyword, hybrid_score=hybrid, rerank_score=hybrid))
        results.sort(key=lambda item: item.hybrid_score, reverse=True)
        for result in results[:top_k * 2]:
            title_bonus = 0.08 if any(token in result.chunk.title.lower() for token in query_tokens) else 0.0
            section_bonus = 0.06 if any(token in result.chunk.section.lower() for token in query_tokens) else 0.0
            tag_bonus = 0.25 if any(token in " ".join(result.chunk.tags).lower() for token in query_tokens) else 0.0
            result.rerank_score = result.hybrid_score + title_bonus + section_bonus + tag_bonus
        return sorted(results, key=lambda item: item.rerank_score, reverse=True)[:top_k]
