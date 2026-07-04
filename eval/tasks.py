"""Task definitions + loaders for the three evaluated capabilities."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

_DATA = Path(__file__).parent / "data"


@dataclass
class CodegenTask:
    id: str
    prompt: str
    entry_point: str
    test: str


@dataclass
class ReviewTask:
    id: str
    diff: str
    bug_keywords: list[str]


@dataclass
class TestgenTask:
    id: str
    prompt: str
    reference: str


def _load(name: str) -> list[dict]:
    return json.loads((_DATA / name).read_text())


def load_codegen() -> list[CodegenTask]:
    return [CodegenTask(**t) for t in _load("codegen.json")]


def load_review() -> list[ReviewTask]:
    return [ReviewTask(**t) for t in _load("review.json")]


def load_testgen() -> list[TestgenTask]:
    return [TestgenTask(**t) for t in _load("testgen.json")]
