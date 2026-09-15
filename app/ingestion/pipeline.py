import json
import re
from pathlib import Path
from app.models import Chunk, Document
from app.security.guards import sanitize_document


class IngestionPipeline:
    def __init__(self, chunk_size: int = 900, overlap: int = 120) -> None:
        self.chunk_size = chunk_size
        self.overlap = overlap

    def load_documents(self, path: str | Path) -> list[Document]:
        records = json.loads(Path(path).read_text(encoding="utf-8"))
        return [Document.model_validate(record) for record in records]

    def chunk_document(self, document: Document) -> list[Chunk]:
        cleaned = sanitize_document(document.content.replace("\r\n", "\n").strip())
        sections = re.split(r"(?m)(?=^# )", cleaned)
        chunks: list[Chunk] = []
        index = 0
        for section_text in sections:
            section_text = section_text.strip()
            if not section_text:
                continue
            heading, _, body = section_text.partition("\n")
            section = heading.removeprefix("# ").strip() or "General"
            words = body.split()
            if not words:
                continue
            for start in range(0, len(words), max(1, self.chunk_size // 5)):
                text = " ".join(words[start:start + self.chunk_size // 5])
                if not text:
                    continue
                chunks.append(Chunk(chunk_id=f"{document.page_id}-C{index:03d}", page_id=document.page_id, title=document.title, space=document.space, section=section, text=text, tags=document.tags, allowed_roles=document.allowed_roles, chunk_index=index))
                index += 1
                if start + self.chunk_size // 5 >= len(words):
                    break
        return chunks

    def run(self, path: str | Path) -> tuple[list[Document], list[Chunk]]:
        documents = self.load_documents(path)
        chunks = [chunk for document in documents for chunk in self.chunk_document(document)]
        return documents, chunks
