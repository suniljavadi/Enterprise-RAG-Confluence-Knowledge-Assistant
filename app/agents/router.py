from app.rag.service import RAGService


class KnowledgeAgent:
    def __init__(self, service: RAGService) -> None:
        self.service = service

    def run(self, request: str, roles: list[str] | None = None) -> object:
        normalized = request.lower()
        roles = roles or ["employee"]
        if normalized.startswith("summarize "):
            for document in self.service.repository.list_documents():
                if document.title.lower() in normalized:
                    return self.service.summarize_page(document.page_id)
        if normalized.startswith("compare "):
            return self.service.search_documents(request, roles=roles)
        return self.service.query(request, roles=roles, top_k=8)
