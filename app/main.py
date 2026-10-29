import logging
import time
import uuid
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.config import get_settings
from app.logging_config import configure_logging
from app.rag.service import RAGService

settings = get_settings()
configure_logging(settings.log_level)
settings.validate_for_runtime()
logger = logging.getLogger(__name__)
app = FastAPI(title="Enterprise RAG Knowledge Assistant", version="1.0.0", description="Synthetic, grounded enterprise knowledge assistant")
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origin_list, allow_methods=["GET", "POST"], allow_headers=["Authorization", "Content-Type"])
app.state.rag_service = RAGService(settings, Path(__file__).resolve().parent.parent / "synthetic_confluence" / "documents.json")
app.include_router(router)


@app.middleware("http")
async def access_log(request: Request, call_next):
    request_id = request.headers.get("x-request-id") or uuid.uuid4().hex
    start = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        logger.exception("request_id=%s method=%s path=%s unhandled error", request_id, request.method, request.url.path)
        raise
    response.headers["X-Request-ID"] = request_id
    logger.info("request_id=%s method=%s path=%s status=%s duration_ms=%.1f", request_id, request.method, request.url.path, response.status_code, (time.perf_counter() - start) * 1000)
    return response


@app.get("/health")
def root_health():
    service = app.state.rag_service
    return {"status": "ok", "documents": len(service.repository.documents), "chunks": len(service.repository.chunks)}
