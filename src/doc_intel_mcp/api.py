from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from doc_intel_mcp.agent import ask

app = FastAPI(
    title="doc-intel",
    description="Ask grounded, cited questions about a document collection.",
    version="0.1.0",
)

_INDEX = (Path(__file__).parent / "static" / "index.html").read_text(encoding="utf-8")


@app.get("/", response_class=HTMLResponse)
def home() -> HTMLResponse:
    """Serve the chat UI."""
    return HTMLResponse(_INDEX)

class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    question: str
    answer: str


@app.get("/health")
def health() -> dict:
    """Liveness probe — used by load balancers and Kubernetes."""
    return {"status": "ok"}


@app.post("/ask", response_model=AskResponse)
def ask_endpoint(req: AskRequest) -> AskResponse:
    """Answer a question using the document-intelligence agent."""
    answer = ask(req.question)
    return AskResponse(question=req.question, answer=answer)

import gradio as gr


def _chat(message, history):
    """Gradio chat handler — routes each message through the agent."""
    return ask(message)


demo = gr.ChatInterface(
    _chat,
    title="doc-intel · ask the papers",
    description=(
        "An agentic RAG system over a set of AI/ML papers. Ask a question and the "
        "agent searches, reads, and answers with citations — or says when the "
        "documents don't cover it. Built with LangGraph + MCP + FastAPI."
    ),
    examples=[
        "How does Self-RAG differ from standard RAG?",
        "What metrics does RAGAS use to evaluate RAG systems?",
        "What problem does retrieval-augmented generation solve?",
    ],
)

# Mount the chat UI at "/" ; the API stays at /ask, docs at /docs.
app = gr.mount_gradio_app(app, demo, path="/")