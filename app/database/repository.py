from app.models import Chunk, Document


class InMemoryRepository:
    def __init__(self) -> None:
        self.documents: dict[str, Document] = {}
        self.chunks: list[Chunk] = []

    def replace(self, documents: list[Document], chunks: list[Chunk]) -> None:
        self.documents = {document.page_id: document for document in documents}
        self.chunks = chunks

    def add_document(self, document: Document, chunks: list[Chunk]) -> None:
        self.documents[document.page_id] = document
        self.chunks = [chunk for chunk in self.chunks if chunk.page_id != document.page_id]
        self.chunks.extend(chunks)

    def get_document(self, page_id: str) -> Document | None:
        return self.documents.get(page_id)

    def list_documents(self) -> list[Document]:
        return list(self.documents.values())
