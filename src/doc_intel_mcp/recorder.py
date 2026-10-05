"""In-process recorder of the context the agent actually retrieved during a run.

The evaluation harness uses this to judge faithfulness and context-relevance
against what the agent really saw — not a separate fixed top-k query. Reset at
the start of each ask() so it only holds the current question's retrievals.
"""

RETRIEVED: list[str] = []


def record(text: str) -> None:
    RETRIEVED.append(text)


def reset() -> None:
    RETRIEVED.clear()


def dump() -> str:
    return "\n\n".join(RETRIEVED)