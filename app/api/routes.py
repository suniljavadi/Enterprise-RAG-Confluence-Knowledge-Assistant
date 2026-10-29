from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from app.config import get_settings
from app.models import DocumentCreate, HealthResponse, QueryRequest, QueryResponse
from app.rag.service import RAGService
from app.security.auth import token_matches

router = APIRouter(prefix="/api/v1")


def get_service(request: Request) -> RAGService:
    return request.app.state.rag_service


def authorize(authorization: str | None = Header(default=None)) -> None:
    token = get_settings().api_auth_token
    if token and not token_matches(authorization, token):
        raise HTTPException(status_code=401, detail={"code": "unauthorized", "message": "Valid bearer token required"})


@router.post("/query", response_model=QueryResponse, dependencies=[Depends(authorize)])
def query(payload: QueryRequest, service: RAGService = Depends(get_service)) -> QueryResponse:
    return service.query(payload.question, payload.roles, payload.top_k)


@router.post("/documents", dependencies=[Depends(authorize)])
def create_document(payload: DocumentCreate, service: RAGService = Depends(get_service)) -> dict[str, str]:
    chunks = service.pipeline.chunk_document(payload.document)
    service.repository.add_document(payload.document, chunks)
    service.retriever = service.retriever.__class__(service.repository.chunks)
    return {"page_id": payload.document.page_id, "status": "indexed", "chunks": str(len(chunks))}


@router.get("/documents", dependencies=[Depends(authorize)])
def list_documents(service: RAGService = Depends(get_service)):
    return service.repository.list_documents()


@router.get("/documents/{page_id}", dependencies=[Depends(authorize)])
def get_document(page_id: str, service: RAGService = Depends(get_service)):
    document = service.retrieve_page(page_id)
    if not document:
        raise HTTPException(status_code=404, detail={"code": "not_found", "message": "Document not found"})
    return document


@router.get("/health", response_model=HealthResponse)
def health(request: Request, service: RAGService = Depends(get_service)) -> HealthResponse:
    return HealthResponse(status="ok", documents=len(service.repository.documents), chunks=len(service.repository.chunks), timestamp=datetime.now(timezone.utc))
