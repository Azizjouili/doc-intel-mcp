from doc_intel_mcp import recorder
from doc_intel_mcp.tools.documents import get_store


def search_documents(query: str, n_results: int = 5) -> str:
    """Search all documents for passages relevant to a question, by meaning.

    Returns the most relevant chunks with their source and chunk number, so you
    can cite them or read more with `read_chunk`.

    Args:
        query: what to search for, in natural language.
        n_results: how many passages to return.
    """
    hits = get_store().search(query, n_results=n_results)
    if not hits:
        return "No relevant passages found."

    blocks = []
    for h in hits:
        meta = h["metadata"]
        recorder.record(f"[{meta['source']} #{meta['chunk']}] {h['text']}")
        blocks.append(
            f"[{meta['source']} #{meta['chunk']}] (distance {h['distance']:.3f})\n"
            f"{h['text']}"
        )
    return "\n\n---\n\n".join(blocks)