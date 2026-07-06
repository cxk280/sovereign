"""Eval harness end-to-end with deterministic stub models (no network)."""

import json
from pathlib import Path

import pytest

from eval import __main__ as eval_main
from eval.client import StubClient
from eval.leaderboard import build_leaderboard, to_markdown
from eval.runner import run_suite
from eval.scorers import score_codegen, score_review, score_testgen
from eval.tasks import load_codegen, load_review, load_testgen


def _good(prompt: str) -> str:
    p = prompt
    if "sum_list" in p:
        return "```python\ndef sum_list(xs):\n    return sum(xs)\n```"
    if "fizzbuzz" in p:
        return (
            "```python\ndef fizzbuzz(n):\n"
            "    if n % 15 == 0: return 'FizzBuzz'\n"
            "    if n % 3 == 0: return 'Fizz'\n"
            "    if n % 5 == 0: return 'Buzz'\n"
            "    return str(n)\n```"
        )
    if "unique_sorted" in p:
        return "```python\ndef unique_sorted(xs):\n    return sorted(set(xs))\n```"
    if "is_even" in p:
        return "```python\ndef test_even():\n    assert is_even(2)\n    assert not is_even(3)\n```"
    if "clamp" in p:
        return (
            "```python\ndef test_clamp():\n"
            "    assert clamp(5, 0, 10) == 5\n"
            "    assert clamp(-1, 0, 10) == 0\n"
            "    assert clamp(20, 0, 10) == 10\n```"
        )
    if "xs[len(xs)]" in p:
        return "This indexes out of range; use len(xs) - 1 or [-1]."
    if "bucket=[]" in p:
        return "Mutable default argument; use bucket=None."
    if "except:" in p:
        return "Bare except is too broad; catch ValueError."
    return ""


def _bad(prompt: str) -> str:
    return "I'm not sure."


def test_good_model_beats_bad_across_the_board() -> None:
    lb = build_leaderboard(run_suite([StubClient("good", _good), StubClient("bad", _bad)]))
    assert lb["good"]["overall"] == 1.0
    assert lb["bad"]["overall"] == 0.0
    assert lb["good"]["code-gen"] == 1.0


def test_leaderboard_markdown_ranks_winner_first() -> None:
    lb = build_leaderboard(run_suite([StubClient("good", _good), StubClient("bad", _bad)]))
    md = to_markdown(lb)
    assert md.index("good") < md.index("bad")


def test_scorers_distinguish_correct_from_incorrect() -> None:
    cg = load_codegen()[0]
    assert score_codegen(cg, "```python\ndef sum_list(xs):\n    return sum(xs)\n```")
    assert not score_codegen(cg, "def sum_list(xs):\n    return 0")

    rv = load_review()[0]
    assert score_review(rv, "index out of range here")
    assert not score_review(rv, "looks fine to me")

    tg = load_testgen()[0]
    assert score_testgen(tg, "```python\ndef test_e():\n    assert is_even(2)\n```")
    assert not score_testgen(tg, "```python\ndef test_e():\n    assert is_even(3)\n```")


# --- CLI provenance: --bench-host writes bench.meta.json (no network) --------
def _stub_gateway(monkeypatch: pytest.MonkeyPatch) -> None:
    """Replace the networked GatewayClient with an offline stub for CLI runs."""
    monkeypatch.setattr(
        eval_main,
        "GatewayClient",
        lambda gateway, name, timeout=120.0: StubClient(name, lambda p: "one two three"),
    )


def test_bench_host_records_provenance(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _stub_gateway(monkeypatch)
    eval_main.main(
        [
            "--models",
            "m",
            "--gateway",
            "http://x",
            "--out",
            str(tmp_path),
            "--bench",
            "--bench-host",
            "vultr-cpu",
        ]
    )
    assert json.loads((tmp_path / "bench.meta.json").read_text()) == {"host": "vultr-cpu"}


def test_bench_without_host_defaults_to_local(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _stub_gateway(monkeypatch)
    eval_main.main(["--models", "m", "--gateway", "http://x", "--out", str(tmp_path), "--bench"])
    assert json.loads((tmp_path / "bench.meta.json").read_text()) == {"host": "local"}


def test_no_bench_flag_writes_no_meta(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _stub_gateway(monkeypatch)
    eval_main.main(["--models", "m", "--gateway", "http://x", "--out", str(tmp_path)])
    assert not (tmp_path / "bench.meta.json").exists()


def test_bench_clears_stale_meta_on_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """EC-1: an interrupted bench must never leave fresh numbers beside a stale host.

    Seed a prior run's vultr-a16 provenance, then have benchmarking blow up. The run
    must have cleared the stale meta up front, so the dashboard can't label whatever
    numbers exist as A16.
    """
    _stub_gateway(monkeypatch)
    (tmp_path / "bench.meta.json").write_text(json.dumps({"host": "vultr-a16"}))

    def _boom(*_a: object, **_k: object) -> object:
        raise RuntimeError("benchmark interrupted")

    monkeypatch.setattr(eval_main, "benchmark", _boom)
    with pytest.raises(RuntimeError):
        eval_main.main(
            [
                "--models",
                "m",
                "--gateway",
                "http://x",
                "--out",
                str(tmp_path),
                "--bench",
                "--bench-host",
                "vultr-cpu",
            ]
        )
    # Stale A16 provenance is gone → no chance of mislabeling later numbers as A16.
    assert not (tmp_path / "bench.meta.json").exists()


def test_eval_timeout_parsing(monkeypatch: pytest.MonkeyPatch) -> None:
    """EC-2: a missing/empty/garbage SOVEREIGN_EVAL_TIMEOUT falls back, never crashes."""
    monkeypatch.delenv("SOVEREIGN_EVAL_TIMEOUT", raising=False)
    assert eval_main._eval_timeout() == 120.0
    monkeypatch.setenv("SOVEREIGN_EVAL_TIMEOUT", "")
    assert eval_main._eval_timeout() == 120.0
    monkeypatch.setenv("SOVEREIGN_EVAL_TIMEOUT", "not-a-number")
    assert eval_main._eval_timeout() == 120.0
    monkeypatch.setenv("SOVEREIGN_EVAL_TIMEOUT", "600")
    assert eval_main._eval_timeout() == 600.0
