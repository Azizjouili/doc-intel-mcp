from doc_intel_mcp import recorder
from doc_intel_mcp.tools.documents import get_store


def answer_with_citations(question: str, n_results: int = 5) -> str:
    """Gather the most relevant passages for a question, formatted for a grounded,
    cited answer.

    Returns the question plus the supporting passages (each tagged with its source).
    Base the answer ONLY on these passages, and cite each claim as [source #chunk].
    If the passages don't contain the answer, say so instead of guessing.

    Args:
        question: the user's question.
        n_results: how many passages to ground the answer in.
    """
    hits = get_store().search(question, n_results=n_results)
    if not hits:
        return "No relevant passages found — cannot answer from the documents."

    context = "\n\n".join(
        f"[{h['metadata']['source']} #{h['metadata']['chunk']}] {h['text']}"
        for h in hits
    )
    recorder.record(context)
    return (
        f"QUESTION: {question}\n\n"
        f"SOURCES (answer only from these, cite as [source #chunk]):\n\n{context}"
    )