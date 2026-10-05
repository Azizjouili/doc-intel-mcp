import json
import time
from pathlib import Path

from langchain_google_genai import ChatGoogleGenerativeAI

from doc_intel_mcp.agent import ask
from doc_intel_mcp.tools.documents import get_store

JUDGE_MODEL = "gemini-flash-lite-latest"

JUDGE_PROMPT = """You are an impartial evaluator of a retrieval-augmented QA system.
Given a QUESTION, the retrieved CONTEXT, and the system's ANSWER, score each metric
from 1 (poor) to 5 (excellent):

- faithfulness: is every claim in the ANSWER supported by the CONTEXT (no hallucination)?
- answer_relevance: does the ANSWER directly and completely address the QUESTION?
- context_relevance: is the retrieved CONTEXT relevant and sufficient for the QUESTION?

Return ONLY a JSON object:
{{"faithfulness": <int>, "answer_relevance": <int>, "context_relevance": <int>, "comment": "<one short sentence>"}}

QUESTION:
{question}

CONTEXT:
{context}

ANSWER:
{answer}
"""


def _text(resp) -> str:
    c = resp.content
    if isinstance(c, str):
        return c
    return "".join(b.get("text", "") for b in c if isinstance(b, dict))


def judge(llm, question: str, context: str, answer: str) -> dict:
    resp = llm.invoke(JUDGE_PROMPT.format(question=question, context=context, answer=answer))
    text = _text(resp)
    start, end = text.find("{"), text.rfind("}") + 1
    return json.loads(text[start:end])


def main() -> None:
    dataset = json.loads(Path("eval/dataset.json").read_text(encoding="utf-8"))
    store = get_store()
    llm = ChatGoogleGenerativeAI(model=JUDGE_MODEL, temperature=0, max_retries=5)

    rows = []
    for item in dataset:
        q = item["question"]
        print(f"\n> {q}")
        hits = store.search(q, n_results=5)
        context = "\n\n".join(
            f"[{h['metadata']['source']} #{h['metadata']['chunk']}] {h['text']}" for h in hits
        )
        answer = ask(q)
        scores = judge(llm, q, context, answer)
        print(f"  faithfulness={scores['faithfulness']} "
              f"answer_relevance={scores['answer_relevance']} "
              f"context_relevance={scores['context_relevance']}")
        print(f"  note: {scores.get('comment', '')}")
        rows.append(scores)
        time.sleep(30)  # stay under the free-tier rate limit

    print("\n=== AVERAGES ===")
    for metric in ("faithfulness", "answer_relevance", "context_relevance"):
        avg = sum(r[metric] for r in rows) / len(rows)
        print(f"{metric:18s}: {avg:.2f} / 5")


if __name__ == "__main__":
    main()