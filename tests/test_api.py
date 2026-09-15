from fastapi.testclient import TestClient
from app.main import app


def test_health_endpoint():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["documents"] == 11


def test_query_endpoint():
    client = TestClient(app)
    response = client.post("/api/v1/query", json={"question": "What is the rollback process?"})
    assert response.status_code == 200
    body = response.json()
    assert body["citations"]
    assert body["request_id"]


def test_missing_document_returns_404():
    client = TestClient(app)
    assert client.get("/api/v1/documents/nope").status_code == 404
