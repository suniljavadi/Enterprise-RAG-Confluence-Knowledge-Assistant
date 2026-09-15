def test_hybrid_retrieval_finds_rollback(service):
    results = service.search_documents("What is the rollback process?")
    assert results
    assert results[0].chunk.page_id == "KB-002"


def test_metadata_filtering(service):
    results = service.search_by_metadata(space="Data")
    assert results
    assert all(result.chunk.space == "Data" for result in results)


def test_authorization_filters_security_document(service):
    results = service.search_documents("secret manager", roles=["guest"])
    assert all(result.chunk.page_id != "KB-007" for result in results)
    security_results = service.search_documents("secret manager", roles=["security"])
    assert any(result.chunk.page_id == "KB-007" for result in security_results)
