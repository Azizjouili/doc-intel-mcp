"""Hugging Face Space entrypoint — a themed Gradio chat over the doc-intel agent."""

import os
import sys

# make the src-layout package importable without installing it
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

import gradio as gr  # noqa: E402

from doc_intel_mcp.agent import ask  # noqa: E402
from doc_intel_mcp.tools.documents import get_store  # noqa: E402

# Build the index on first boot if it's empty (downloads a few papers + embeds them).
if get_store().count() == 0:
    import scripts.prepare_demo as prepare_demo

    prepare_demo.main()


def respond(message, history):
    return ask(message)


THEME = gr.themes.Soft(
    primary_hue=gr.themes.colors.teal,
    secondary_hue=gr.themes.colors.teal,
    neutral_hue=gr.themes.colors.slate,
    font=[gr.themes.GoogleFont("Inter"), "system-ui", "sans-serif"],
).set(
    body_background_fill="#0c1413",
    body_background_fill_dark="#0c1413",
    block_background_fill="#111b19",
    block_border_color="#223029",
    body_text_color="#e9f1ee",
    button_primary_background_fill="linear-gradient(135deg,#3cc2ad,#0f6b5e)",
    button_primary_text_color="#05221d",
)

CSS = """
.gradio-container{max-width:860px !important;margin:0 auto !important}
footer{display:none !important}
#title{text-align:center}
#title h1{font-weight:800;letter-spacing:-.02em;margin-bottom:4px}
#title p{color:#93a59f;margin-top:0}
"""

with gr.Blocks(theme=THEME, css=CSS, title="doc-intel") as demo:
    gr.HTML(
        '<div id="title"><h1>doc-intel</h1>'
        '<p>Agentic RAG over AI/ML papers &middot; LangGraph &middot; MCP &middot; FastAPI &middot; '
        '<a href="https://github.com/Azizjouili/doc-intel-mcp" target="_blank" '
        'style="color:#8fe6d7">GitHub</a></p></div>'
    )
    gr.ChatInterface(
        respond,
        description=(
            "An AI agent searches a corpus of AI/ML research papers, reads the relevant "
            "passages, and answers with citations — or tells you when the documents "
            "don't cover it."
        ),
        examples=[
            "How does Self-RAG differ from standard RAG?",
            "What metrics does RAGAS use to evaluate RAG systems?",
            "What problem does retrieval-augmented generation solve?",
            "What is the capital of France?",
        ],
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)