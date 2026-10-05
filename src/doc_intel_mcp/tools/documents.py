from doc_intel_mcp.store import DocumentStore

_store: DocumentStore | None = None


def get_store() -> DocumentStore:
    """Create the store once and reuse it (loading the model is expensive)."""
    global _store
    if _store is None:
        _store = DocumentStore()
    return _store


def list_documents() -> str:
    """List the source documents currently available to search.

    Call this first to see which documents exist before searching or answering.
    """
    sources = get_store().list_sources()
    if not sources:
        return "No documents ingested yet."
    return "Available documents:\n" + "\n".join(f"- {s}" for s in sources)



def read_chunk(source: str, chunk: int) -> str:
    """<keep your existing docstring>"""
    from doc_intel_mcp import recorder
    text = get_store().get_chunk(source, chunk)
    if text is None:
        return f"No chunk {chunk} found in {source}."
    recorder.record(f"[{source} #{chunk}] {text}")
    return text