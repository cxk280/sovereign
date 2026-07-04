"""Retriever — ties an embedder to a store: index documents, search by query."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from rag.chunking import RawDoc, chunk_text
from rag.embeddings import Embedder
from rag.store import VectorStore


@dataclass
class Chunk:
    id: str
    text: str
    path: str
    title: str
    source_type: str
    score: float = 0.0


class Retriever:
    def __init__(self, embedder: Embedder, store: VectorStore) -> None:
        self._embedder = embedder
        self._store = store

    def index(self, docs: list[RawDoc]) -> int:
        ids: list[str] = []
        texts: list[str] = []
        payloads: list[dict[str, str]] = []
        for d in docs:
            for j, ch in enumerate(chunk_text(d.text)):
                ids.append(str(uuid.uuid5(uuid.NAMESPACE_URL, f"{d.path}#{j}")))
                texts.append(ch)
                payloads.append(
                    {"text": ch, "path": d.path, "title": d.title, "source_type": d.source_type}
                )
        if not texts:
            return 0
        self._store.upsert(ids, self._embedder.embed(texts), payloads)
        return len(texts)

    def search(self, query: str, k: int = 5, source_type: str | None = None) -> list[Chunk]:
        qv = self._embedder.embed([query])[0]
        return [
            Chunk(
                id=p.id,
                text=p.payload["text"],
                path=p.payload["path"],
                title=p.payload["title"],
                source_type=p.payload["source_type"],
                score=p.score,
            )
            for p in self._store.search(qv, k, source_type)
        ]
