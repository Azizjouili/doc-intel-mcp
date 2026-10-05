"""Build the demo index at image-build time: download a few public arXiv
papers and ingest them, so the deployed container ships with a ready index."""

import urllib.request

from doc_intel_mcp.config import DATA_DIR
from doc_intel_mcp.ingest import ingest

PAPERS = {
    "transformers.pdf": "https://arxiv.org/pdf/1706.03762",
    "rag.pdf": "https://arxiv.org/pdf/2005.11401",
    "self-rag.pdf": "https://arxiv.org/pdf/2310.11511",
    "ragas.pdf": "https://arxiv.org/pdf/2309.15217",
}


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    for name, url in PAPERS.items():
        dest = DATA_DIR / name
        if dest.exists():
            continue
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req) as r, open(dest, "wb") as f:
            f.write(r.read())
        print(f"downloaded {name}")
    ingest()


if __name__ == "__main__":
    main()