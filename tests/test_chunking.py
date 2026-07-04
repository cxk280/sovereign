"""Chunking keeps paragraphs whole and respects the size cap."""

from rag.chunking import chunk_text


def test_short_text_is_one_chunk() -> None:
    assert chunk_text("hello world") == ["hello world"]


def test_paragraphs_pack_and_split() -> None:
    text = "\n\n".join([f"paragraph number {i} with some words" for i in range(20)])
    chunks = chunk_text(text, max_chars=120)
    assert len(chunks) > 1
    assert all(len(c) <= 120 for c in chunks)


def test_oversized_paragraph_is_hard_split() -> None:
    chunks = chunk_text("x" * 2000, max_chars=500, overlap=50)
    assert len(chunks) >= 4
    assert all(len(c) <= 500 for c in chunks)
