from app.ingestion.pipeline import IngestionPipeline


def test_ingestion_loads_synthetic_documents():
    pipeline = IngestionPipeline()
    documents, chunks = pipeline.run("synthetic_confluence/documents.json")
    assert len(documents) == 11
    assert len(chunks) >= len(documents)
    assert all(chunk.page_id and chunk.title and chunk.text for chunk in chunks)


def test_chunk_metadata_is_preserved():
    pipeline = IngestionPipeline()
    documents, chunks = pipeline.run("synthetic_confluence/documents.json")
    assert {chunk.page_id for chunk in chunks} == {document.page_id for document in documents}
