import pytest

from doc_intel_mcp.store import DocumentStore


@pytest.fixture
def store():
    s = DocumentStore()
    if s.count() == 0:
        pytest.skip("No ingested documents (run `uv run python -m doc_intel_mcp.ingest`)")
    return s


def test_search_returns_relevant_chunk(store):
    hits = store.search("retrieval augmented generation", n_results=3)
    assert len(hits) > 0
    # every hit carries the metadata the tools rely on
    for h in hits:
        assert "source" in h["metadata"]
        assert "chunk" in h["metadata"]


def test_store_lists_sources(store):
    assert len(store.list_sources()) > 0