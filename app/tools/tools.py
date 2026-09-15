from app.rag.service import RAGService


def search_documents(service: RAGService, query: str, roles: list[str] | None = None):
    return service.search_documents(query, roles)


def search_confluence(service: RAGService, query: str, roles: list[str] | None = None):
    return service.search_documents(query, roles)


def retrieve_page(service: RAGService, page_id: str):
    return service.retrieve_page(page_id)


def search_by_metadata(service: RAGService, space: str | None = None, tag: str | None = None, roles: list[str] | None = None):
    return service.search_by_metadata(space, tag, roles)


def summarize_page(service: RAGService, page_id: str) -> str:
    return service.summarize_page(page_id)


def compare_documents(service: RAGService, first_id: str, second_id: str) -> str:
    return service.compare_documents(first_id, second_id)