from doc_intel_mcp.store import DocumentStore


def test_search_returns_relevant_chunk():
    store = DocumentStore()
    hits = store.search("retrieval augmented generation", n_results=3)
    assert len(hits) > 0
    # every hit carries the metadata the tools rely on
    for h in hits:
        assert "source" in h["metadata"]
        assert "chunk" in h["metadata"]


def test_store_has_documents():
    store = DocumentStore()
    assert store.count() > 0
    assert len(store.list_sources()) > 0