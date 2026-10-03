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
    """Read one specific chunk of a document by its source file and chunk number.

    Use after `search_documents` to read more context around a relevant hit.

    Args:
        source: the document filename (e.g. 'rag.pdf').
        chunk: the chunk number within that document.
    """
    text = get_store().get_chunk(source, chunk)
    return text if text is not None else f"No chunk {chunk} found in {source}."