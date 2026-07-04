"""Turn documents into retrieval-sized chunks.

Paragraph-packing: keep whole paragraphs together up to ``max_chars``, hard-split
only paragraphs that are themselves too long. Good enough for markdown docs and
small source files; the embedder does the semantic work.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RawDoc:
    path: str
    source_type: str  # codebase | runbooks | incidents | architecture | other
    title: str
    text: str


def chunk_text(text: str, max_chars: int = 700, overlap: int = 120) -> list[str]:
    paras = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks: list[str] = []
    cur = ""
    for p in paras:
        if len(p) > max_chars:
            if cur:
                chunks.append(cur)
                cur = ""
            step = max(1, max_chars - overlap)
            for i in range(0, len(p), step):
                chunks.append(p[i : i + max_chars])
        elif len(cur) + len(p) + 2 <= max_chars:
            cur = f"{cur}\n\n{p}".strip()
        else:
            if cur:
                chunks.append(cur)
            cur = p
    if cur:
        chunks.append(cur)
    return chunks
