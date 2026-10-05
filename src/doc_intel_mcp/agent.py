import os
import sys

from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI

from doc_intel_mcp.tools.answer import answer_with_citations as _answer
from doc_intel_mcp.tools.documents import list_documents as _list
from doc_intel_mcp.tools.documents import read_chunk as _read
from doc_intel_mcp.tools.search import search_documents as _search

list_documents = tool(_list)
search_documents = tool(_search)
read_chunk = tool(_read)
answer_with_citations = tool(_answer)

TOOLS = [list_documents, search_documents, read_chunk, answer_with_citations]

SYSTEM_PROMPT = (
    "You answer questions about a collection of documents. "
    "Always ground your answer in the documents by calling the tools: "
    "search for relevant passages, read more if needed, then answer. "
    "Cite every claim as [source #chunk]. "
    "If the documents do not contain the answer, say so plainly instead of guessing."
)


def build_agent():
    llm = ChatGoogleGenerativeAI(
        model="gemini-flash-lite-latest",
        temperature=0,
        max_retries=5,
    )
    return create_agent(model=llm, tools=TOOLS, system_prompt=SYSTEM_PROMPT)

def _extract_text(content) -> str:
    """gemini-3.x returns content as a list of blocks; older models as a string."""
    if isinstance(content, str):
        return content
    parts = []
    for block in content:
        if isinstance(block, dict) and block.get("type") == "text":
            parts.append(block["text"])
        elif isinstance(block, str):
            parts.append(block)
    return "\n".join(parts)


def ask(question: str) -> str:
    from doc_intel_mcp import recorder
    recorder.reset()
    agent = build_agent()
    callbacks = []
    if os.environ.get("LANGFUSE_PUBLIC_KEY"):
        from langfuse.langchain import CallbackHandler
        callbacks.append(CallbackHandler())
    result = agent.invoke(
        {"messages": [("user", question)]},
        config={"callbacks": callbacks},
    )
    return _extract_text(result["messages"][-1].content)

if __name__ == "__main__":
    
    if len(sys.argv) < 2:
        print('Usage: python -m doc_intel_mcp.agent "your question"')
        sys.exit(1)
    if os.environ.get("LANGFUSE_PUBLIC_KEY"):
        from langfuse import get_client
        get_client().flush()
    from langfuse import get_client
    print(ask(" ".join(sys.argv[1:])))
    get_client().flush()