import chromadb
from chromadb.utils import embedding_functions

from doc_intel_mcp.config import CHROMA_DIR, COLLECTION_NAME, EMBED_MODEL


class DocumentStore:
    """Wraps the vector database: embed + store chunks, and search them."""

    def __init__(self) -> None:
        # Persistent client: the DB is written to disk, so ingestion survives restarts.
        self._client = chromadb.PersistentClient(path=str(CHROMA_DIR))

        # Chroma embeds text for us, using the same local model for docs and queries.
        self._embed = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=EMBED_MODEL
        )
        self._collection = self._client.get_or_create_collection(
            name=COLLECTION_NAME,
            embedding_function=self._embed,
        )

    def add(self, ids: list[str], texts: list[str], metadatas: list[dict]) -> None:
        """Add chunks. Chroma embeds each text and stores vector + text + metadata."""
        self._collection.add(ids=ids, documents=texts, metadatas=metadatas)

    def search(self, query: str, n_results: int = 5) -> list[dict]:
        """Return the n chunks most similar in meaning to the query."""
        res = self._collection.query(query_texts=[query], n_results=n_results)
        hits: list[dict] = []
        # Chroma returns parallel lists wrapped in an outer list (one per query).
        for text, meta, dist in zip(
            res["documents"][0], res["metadatas"][0], res["distances"][0]
        ):
            hits.append({"text": text, "metadata": meta, "distance": dist})
        return hits

    def count(self) -> int:
        return self._collection.count()

    def list_sources(self) -> list[str]:
        """Distinct source filenames currently stored."""
        got = self._collection.get(include=["metadatas"])
        return sorted({m["source"] for m in got["metadatas"]})