# doc-intel-mcp

An agentic document-intelligence system: ask natural-language questions about a
collection of PDFs and get **grounded, cited answers**. An LLM agent reasons over
the documents using retrieval tools — it searches, reads, and answers only from
what the documents actually say, citing each claim as `[source #chunk]`.

Built as two front-ends over one set of tools: an **MCP server** (usable from
Claude Desktop or any MCP client) and a **FastAPI service** (`/ask`).

## Why this exists

LLMs hallucinate about documents they weren't trained on, and a long PDF won't
fit in a prompt. This system solves that with **Retrieval-Augmented Generation (RAG)**:
documents are chunked, embedded, and stored in a vector database; at query time the
most relevant passages are retrieved and the model is instructed to answer *only*
from them — and to say so when the answer isn't there.

## Architecture

```
PDFs ──► ingest ──► chunks ──► embeddings ──► vector store (ChromaDB)
                                                      │
                     question ──► LangGraph agent ◄────┘
                                   │  (search · read · answer)
                                   ▼
                        grounded answer with citations
```

- **Ingestion** (`ingest.py`): read PDFs → split into overlapping chunks → embed → store.
- **Retrieval** (`store.py`): local embeddings (`sentence-transformers`) + ChromaDB similarity search.
- **Tools** (`tools/`): `list_documents`, `search_documents`, `read_chunk`, `answer_with_citations`.
- **Agent** (`agent.py`): a LangGraph ReAct agent that decides which tools to call, in sequence, until it can answer.
- **Interfaces**: the same tools are exposed as an MCP server (`server.py`) and a FastAPI service (`api.py`).

## Design notes

- **Grounding guard.** The system prompt instructs the agent to answer only from
  retrieved passages and to admit when they don't cover the question — it refuses
  to answer "What is the capital of France?" from a set of ML papers.
- **One source of truth.** Tool logic lives in plain functions; the MCP server and
  the FastAPI app are thin front-ends over them. A framework change (the project
  survived an `mcp` 1.x→2.x and a LangGraph API break) touches one file.
- **Local, free embeddings.** Retrieval runs offline with no API cost; only the
  agent's reasoning calls a hosted LLM.
- **Rate-limit resilience.** The agent retries transient rate-limit errors with backoff.
- **Testing strategy.** Unit tests cover the deterministic retrieval layer, not the
  non-deterministic LLM output — agent quality belongs in a separate evaluation harness (see Roadmap).

## Setup

```bash
uv sync
# add some PDFs to data/, then build the index:
uv run python -m doc_intel_mcp.ingest
```

Set an LLM key for the agent (Google Gemini free tier):

```bash
export GOOGLE_API_KEY=your-key       # PowerShell: $env:GOOGLE_API_KEY="your-key"
```

## Usage

**Command line:**

```bash
uv run python -m doc_intel_mcp.agent "How does Self-RAG differ from standard RAG?"
```

**As a web service:**

```bash
uv run uvicorn doc_intel_mcp.api:app --port 8000
# then open http://127.0.0.1:8000/docs  (interactive API)
```

**As an MCP server** (e.g. in Claude Desktop): point it at this project and set `DATA_DIR`.

## Development

```bash
uv run pytest        # tests
uv run ruff check .  # lint
```

## Tech

Python · MCP · LangGraph · FastAPI · ChromaDB · sentence-transformers · Google Gemini · pytest · ruff

## Roadmap

- Evaluation harness (RAGAS: faithfulness, answer/context relevance) on a labeled set
- Containerize (Docker) and deploy (Kubernetes / Azure)
- CI pipeline (lint, test, build) via GitHub Actions
- Observability / tracing (Langfuse)
- Smarter chunking (sentence/section-aware); swap ChromaDB for pgvector/Qdrant
- Agent-as-MCP-client wiring (currently tools are imported directly)

---

Built by Ahmed Aziz Jouili.