from fastapi import FastAPI
from pydantic import BaseModel

from doc_intel_mcp.agent import ask

app = FastAPI(
    title="doc-intel",
    description="Ask grounded, cited questions about a document collection.",
    version="0.1.0",
)


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