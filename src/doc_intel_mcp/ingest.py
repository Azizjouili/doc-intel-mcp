import sys

from pypdf import PdfReader

from doc_intel_mcp.config import CHUNK_OVERLAP, CHUNK_SIZE, DATA_DIR
from doc_intel_mcp.store import DocumentStore


def read_pdf(path) -> str:
    """Extract plain text from a PDF, one blank line between pages."""
    reader = PdfReader(str(path))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n\n".join(pages)


def chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Split text into overlapping windows of `size` characters."""
    text = " ".join(text.split())  # collapse whitespace/newlines into single spaces
    if not text:
        return []
    chunks: list[str] = []
    start = 0
    step = size - overlap  # advance less than a full window, so windows overlap
    while start < len(text):
        chunks.append(text[start:start + size])
        start += step
    return chunks


def ingest() -> None:
    """Read every PDF in DATA_DIR, chunk it, and load it into the store."""
    store = DocumentStore()
    pdfs = sorted(DATA_DIR.glob("*.pdf"))
    if not pdfs:
        print(f"No PDFs found in {DATA_DIR}")
        return

    total_chunks = 0
    for pdf in pdfs:
        text = read_pdf(pdf)
        chunks = chunk_text(text)
        if not chunks:
            print(f"  ! {pdf.name}: no extractable text (scanned image?) — skipped")
            continue

        ids = [f"{pdf.stem}-{i}" for i in range(len(chunks))]
        metadatas = [{"source": pdf.name, "chunk": i} for i in range(len(chunks))]
        store.add(ids=ids, texts=chunks, metadatas=metadatas)

        total_chunks += len(chunks)
        print(f"  + {pdf.name}: {len(chunks)} chunks")

    print(f"Done. {len(pdfs)} files, {total_chunks} chunks, {store.count()} total in store.")


if __name__ == "__main__":
    try:
        ingest()
    except KeyboardInterrupt:
        sys.exit(1)