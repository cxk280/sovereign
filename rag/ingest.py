"""Ingest sample_data/ into a vector store.

Maps each top-level folder to a context type (the four MCP surfaces), reads every
markdown/Python file, and indexes it. Run as a module to populate the production
Qdrant store:

    uv run python -m rag.ingest
"""

from __future__ import annotations

import os
from pathlib import Path

from rag.chunking import RawDoc
from rag.retrieval import Retriever

TYPE_MAP = {
    "services": "codebase",
    "runbooks": "runbooks",
    "incidents": "incidents",
    "architecture": "architecture",
}


def _title(text: str, fallback: str) -> str:
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("#"):
            return s.lstrip("# ").strip()
        if s.startswith('"""') and len(s) > 3:
            return s.strip('"').strip() or fallback
    return fallback


def load_docs(root: str = "sample_data") -> list[RawDoc]:
    root_path = Path(root)
    docs: list[RawDoc] = []
    for path in sorted(root_path.rglob("*")):
        if path.is_dir() or path.suffix not in {".md", ".py"}:
            continue
        rel = path.relative_to(root_path)
        text = path.read_text()
        docs.append(
            RawDoc(str(path), TYPE_MAP.get(rel.parts[0], "other"), _title(text, path.name), text)
        )
    return docs


def build_retriever_from_env() -> Retriever:
    """Production retriever: local sentence-transformers embeddings + Qdrant."""
    from rag.embeddings import SentenceTransformerEmbedder
    from rag.store import QdrantStore

    embedder = SentenceTransformerEmbedder(os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5"))
    store = QdrantStore(
        os.getenv("QDRANT_URL", "http://localhost:6333"),
        dim=embedder.dim,
        api_key=os.getenv("QDRANT_API_KEY") or None,
    )
    return Retriever(embedder, store)


def main() -> None:
    retriever = build_retriever_from_env()
    docs = load_docs(os.getenv("SOVEREIGN_SAMPLE_DATA", "sample_data"))
    n = retriever.index(docs)
    print(f"indexed {n} chunks from {len(docs)} documents")


if __name__ == "__main__":
    main()
