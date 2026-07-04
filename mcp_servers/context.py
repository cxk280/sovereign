"""Shared context tools behind every MCP server — retrieval + safe file reads.

Deliberately free of any MCP SDK import so it can be unit-tested directly. The
retriever is built once, lazily. By default it uses the zero-setup in-memory
backend (so a server runs offline with no Qdrant), and switches to the
production Qdrant + sentence-transformers backend when
``SOVEREIGN_RAG_BACKEND=qdrant``.
"""

from __future__ import annotations

import os
from pathlib import Path

from rag.retrieval import Chunk, Retriever

_SAMPLE_ROOT = Path(os.getenv("SOVEREIGN_SAMPLE_DATA", "sample_data")).resolve()
_retriever: Retriever | None = None


def build_retriever() -> Retriever:
    if os.getenv("SOVEREIGN_RAG_BACKEND", "memory") == "qdrant":
        from rag.ingest import build_retriever_from_env

        return build_retriever_from_env()
    # Zero-setup default: hashed embeddings + in-memory index over sample_data.
    from rag.embeddings import HashEmbedder
    from rag.ingest import load_docs
    from rag.store import InMemoryStore

    retriever = Retriever(HashEmbedder(), InMemoryStore())
    retriever.index(load_docs(str(_SAMPLE_ROOT)))
    return retriever


def get_retriever() -> Retriever:
    global _retriever
    if _retriever is None:
        _retriever = build_retriever()
    return _retriever


def _format(chunks: list[Chunk]) -> str:
    if not chunks:
        return "No matching results."
    return "\n\n---\n\n".join(f"### {c.title}  ·  {c.path}\n{c.text}" for c in chunks)


def _search(query: str, source_type: str, k: int) -> str:
    return _format(get_retriever().search(query, k=k, source_type=source_type))


# --- codebase ---
def search_code(query: str, k: int = 5) -> str:
    return _search(query, "codebase", k)


# --- runbooks ---
def search_runbooks(query: str, k: int = 5) -> str:
    return _search(query, "runbooks", k)


# --- incidents ---
def query_incidents(query: str, k: int = 5) -> str:
    return _search(query, "incidents", k)


# --- architecture ---
def search_arch_docs(query: str, k: int = 5) -> str:
    return _search(query, "architecture", k)


def get_file(path: str) -> str:
    """Read a file, sandboxed to the sample-data root (no path traversal out)."""
    target = (_SAMPLE_ROOT / path).resolve()
    if target != _SAMPLE_ROOT and _SAMPLE_ROOT not in target.parents:
        return "Access denied: path is outside the internal knowledge root."
    if not target.is_file():
        return f"Not found: {path}"
    return target.read_text()
