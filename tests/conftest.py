from pathlib import Path
import pytest
from app.config import Settings
from app.rag.service import RAGService


@pytest.fixture
def service() -> RAGService:
    return RAGService(Settings(mock_llm=True, api_auth_token=None), Path(__file__).parents[1] / "synthetic_confluence" / "documents.json")
