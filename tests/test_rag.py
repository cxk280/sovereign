"""RAG pipeline end-to-end over the real sample_data, deterministic (no network).

Uses the zero-dep HashEmbedder + InMemoryStore so retrieval is reproducible in CI.
"""

from rag.embeddings import HashEmbedder
from rag.ingest import load_docs
from rag.retrieval import Retriever
from rag.store import InMemoryStore


def _retriever() -> Retriever:
    r = Retriever(HashEmbedder(), InMemoryStore())
    assert r.index(load_docs("sample_data")) > 0
    return r


def test_incident_query_is_grounded_in_the_right_doc() -> None:
    hits = _retriever().search("database connection pool exhaustion", k=3, source_type="incidents")
    assert hits, "expected at least one incident hit"
    assert any("INC-2025-002" in h.path for h in hits)


def test_source_type_filter_scopes_results() -> None:
    hits = _retriever().search("orders", k=5, source_type="runbooks")
    assert hits
    assert all(h.source_type == "runbooks" for h in hits)
