"""Scorers — define "correct" for each task and check the model's output.

code-gen and test-gen are checked by **executing** code in a subprocess sandbox
(timeout-bounded); code-review uses a keyword judge over the planted-bug terms
(a real deployment swaps in an LLM-as-judge — see ``judge_review_with_model``).
"""

from __future__ import annotations

import importlib.util
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

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


def _pytest_available() -> bool:
    return importlib.util.find_spec("pytest") is not None


def _run_pytest(src: str, timeout: float = 15.0) -> bool:
    """Run generated tests under real pytest; pass = exit 0 (all collected tests green).

    The prompt asks for *pytest-style* tests, so idiomatic output (``import pytest``,
    ``@pytest.mark.parametrize``, ``pytest.raises``) must actually execute — running the
    file with plain ``python`` would ``NameError`` on those and fail a correct test set.
    pytest's exit 5 ("no tests collected") is non-zero, so an empty/uncollectable file
    correctly **fails** rather than passing vacuously; exit 2 (collection error) fails too.
    """
    d = tempfile.mkdtemp(prefix="testgen_")
    try:
        (Path(d) / "test_generated.py").write_text(src)
        proc = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", d],
            capture_output=True,
            timeout=timeout,
            text=True,
        )
        return proc.returncode == 0
    except subprocess.TimeoutExpired:
        return False
    finally:
        shutil.rmtree(d, ignore_errors=True)


def score_codegen(task: CodegenTask, output: str) -> bool:
    return _run(f"{extract_code(output)}\n\n{task.test}\n")


def score_testgen(task: TestgenTask, output: str) -> bool:
    generated = extract_code(output)
    if _pytest_available():
        # Keep the model's ``import pytest`` / decorators intact — pytest is present, so
        # they run as written. The reference impl is prepended so the tests can call it.
        return _run_pytest(f"{task.reference}\n\n{generated}\n")
    # Degraded fallback for an environment without pytest: strip the import and run each
    # test_* directly. Plain assert-style tests still work; pytest-only constructs won't.
    legacy = generated.replace("import pytest", "")
    return _run(f"{task.reference}\n\n{legacy}\n{_TESTGEN_HARNESS}")


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
