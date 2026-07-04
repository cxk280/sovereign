"""Vector stores — hold embeddings and answer nearest-neighbour queries.

``InMemoryStore`` is pure-Python (cosine over normalized vectors) for zero-setup
dev and tests. ``QdrantStore`` is the production path. Both satisfy
``VectorStore``, so callers never change.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass
class ScoredPoint:
    id: str
    score: float
    payload: dict[str, Any]


class VectorStore(Protocol):
    def upsert(
        self, ids: list[str], vectors: list[list[float]], payloads: list[dict[str, Any]]
    ) -> None: ...

    def search(
        self, vector: list[float], k: int = 5, source_type: str | None = None
    ) -> list[ScoredPoint]: ...


def _cosine(a: list[float], b: list[float]) -> float:
    # vectors are normalized upstream, so dot product == cosine similarity
    return sum(x * y for x, y in zip(a, b, strict=False))


class InMemoryStore:
    def __init__(self) -> None:
        self._ids: list[str] = []
        self._vecs: list[list[float]] = []
        self._payloads: list[dict[str, Any]] = []

    def upsert(
        self, ids: list[str], vectors: list[list[float]], payloads: list[dict[str, Any]]
    ) -> None:
        self._ids.extend(ids)
        self._vecs.extend(vectors)
        self._payloads.extend(payloads)

    def search(
        self, vector: list[float], k: int = 5, source_type: str | None = None
    ) -> list[ScoredPoint]:
        scored = [
            ScoredPoint(i, _cosine(vector, v), p)
            for i, v, p in zip(self._ids, self._vecs, self._payloads, strict=False)
            if source_type is None or p.get("source_type") == source_type
        ]
        scored.sort(key=lambda s: s.score, reverse=True)
        return scored[:k]


class QdrantStore:
    def __init__(
        self,
        url: str,
        collection: str = "sovereign",
        dim: int = 384,
        api_key: str | None = None,
    ) -> None:
        from qdrant_client import QdrantClient
        from qdrant_client.models import Distance, VectorParams

        self._client = QdrantClient(url=url, api_key=api_key)
        self._collection = collection
        if not self._client.collection_exists(collection):
            self._client.create_collection(
                collection, vectors_config=VectorParams(size=dim, distance=Distance.COSINE)
            )

    def upsert(
        self, ids: list[str], vectors: list[list[float]], payloads: list[dict[str, Any]]
    ) -> None:
        from qdrant_client.models import PointStruct

        points = [
            PointStruct(id=i, vector=v, payload=p)
            for i, v, p in zip(ids, vectors, payloads, strict=False)
        ]
        self._client.upsert(self._collection, points=points)

    def search(
        self, vector: list[float], k: int = 5, source_type: str | None = None
    ) -> list[ScoredPoint]:
        from qdrant_client.models import FieldCondition, Filter, MatchValue

        flt = (
            Filter(must=[FieldCondition(key="source_type", match=MatchValue(value=source_type))])
            if source_type
            else None
        )
        hits = self._client.search(self._collection, query_vector=vector, limit=k, query_filter=flt)
        return [ScoredPoint(str(h.id), float(h.score), h.payload or {}) for h in hits]
