from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.config import get_settings
from app.logging_config import configure_logging
from app.rag.service import RAGService

settings = get_settings()
configure_logging(settings.log_level)
app = FastAPI(title="Enterprise RAG Knowledge Assistant", version="1.0.0", description="Synthetic, grounded enterprise knowledge assistant")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.state.rag_service = RAGService(settings, Path(__file__).resolve().parent.parent / "synthetic_confluence" / "documents.json")
app.include_router(router)


@app.get("/health")
def root_health():
    service = app.state.rag_service
    return {"status": "ok", "documents": len(service.repository.documents), "chunks": len(service.repository.chunks)}
