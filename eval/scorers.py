"""Scorers — define "correct" for each task and check the model's output.

code-gen and test-gen are checked by **executing** code in a subprocess sandbox
(timeout-bounded); code-review uses a keyword judge over the planted-bug terms
(a real deployment swaps in an LLM-as-judge — see ``judge_review_with_model``).
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile

from eval.client import ModelClient
from eval.tasks import CodegenTask, ReviewTask, TestgenTask

_FENCE = re.compile(r"```(?:python)?\s*\n(.*?)```", re.S)

_TESTGEN_HARNESS = (
    "\n_ns = dict(globals())\n"
    "for _n, _f in list(_ns.items()):\n"
    "    if _n.startswith('test_') and callable(_f):\n"
    "        _f()\n"
    "print('OK')\n"
)


def extract_code(text: str) -> str:
    m = _FENCE.search(text)
    return (m.group(1) if m else text).strip()


def _run(src: str, timeout: float = 10.0) -> bool:
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
        f.write(src)
        path = f.name
    try:
        proc = subprocess.run(
            [sys.executable, path], capture_output=True, timeout=timeout, text=True
        )
        return proc.returncode == 0
    except subprocess.TimeoutExpired:
        return False
    finally:
        os.unlink(path)


def score_codegen(task: CodegenTask, output: str) -> bool:
    return _run(f"{extract_code(output)}\n\n{task.test}\n")


def score_testgen(task: TestgenTask, output: str) -> bool:
    generated = extract_code(output).replace("import pytest", "")
    return _run(f"{task.reference}\n\n{generated}\n{_TESTGEN_HARNESS}")


def score_review(task: ReviewTask, output: str) -> bool:
    low = output.lower()
    return any(k.lower() in low for k in task.bug_keywords)


def judge_review_with_model(task: ReviewTask, output: str, judge: ModelClient) -> bool:
    """LLM-as-judge alternative to the keyword scorer (used when a judge model is available)."""
    verdict = judge.complete(
        "A reviewer was shown this diff:\n\n"
        f"{task.diff}\n\nTheir review:\n\n{output}\n\n"
        "Did the review correctly identify the real bug? Answer strictly YES or NO.",
    )
    return verdict.strip().upper().startswith("YES")
