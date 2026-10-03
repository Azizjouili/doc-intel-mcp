import os
from pathlib import Path

# Where your PDFs live, and where the vector DB persists between runs.
DATA_DIR = Path(os.environ.get("DATA_DIR", "data")).resolve()
CHROMA_DIR = Path(os.environ.get("CHROMA_DIR", "chroma_db")).resolve()

# The embedding model. Small, fast, runs locally, no API key.
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Chunking: how we split documents before embedding.
CHUNK_SIZE = 800       # characters per chunk (~150-200 words)
CHUNK_OVERLAP = 150    # characters shared between neighbours, so we don't cut mid-thought

COLLECTION_NAME = "documents"