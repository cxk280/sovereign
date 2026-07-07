"""Eval harness end-to-end with deterministic stub models (no network)."""

import json
from pathlib import Path

import pytest

from eval import __main__ as eval_main
from eval.client import StubClient
from eval.leaderboard import build_leaderboard, to_markdown
from eval.runner import CODEGEN, Result, _score_review, run_suite
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


# --- test-gen scored under real pytest (idiomatic pytest tests must run) ------
def test_testgen_pytest_idioms_pass_when_correct() -> None:
    """The core bug fix: a correct *pytest-style* test set (import pytest + @parametrize)
    must PASS. The old harness stripped the import but left the decorator, so it
    NameError'd and failed every idiomatic submission regardless of correctness."""
    tg = load_testgen()[0]  # is_even
    out = (
        "```python\n"
        "import pytest\n\n"
        "@pytest.mark.parametrize('n', [2, 4, 0, -2])\n"
        "def test_even(n):\n"
        "    assert is_even(n)\n\n"
        "@pytest.mark.parametrize('n', [1, 3, -1])\n"
        "def test_odd(n):\n"
        "    assert not is_even(n)\n"
        "```"
    )
    assert score_testgen(tg, out)


def test_testgen_failing_assertion_fails() -> None:
    tg = load_testgen()[0]  # is_even
    assert not score_testgen(tg, "```python\ndef test_wrong():\n    assert is_even(3)\n```")


def test_testgen_no_tests_collected_is_a_fail() -> None:
    """pytest exit 5 (no test_* collected) must FAIL, never pass vacuously."""
    tg = load_testgen()[0]
    assert not score_testgen(tg, "```python\nx = 1  # no test functions here\n```")


def test_testgen_falls_back_when_pytest_absent(monkeypatch: pytest.MonkeyPatch) -> None:
    """Degraded environment without pytest: plain assert-style tests still score via the
    legacy harness (correct → pass, wrong → fail)."""
    import eval.scorers as scorers

    monkeypatch.setattr(scorers, "_pytest_available", lambda: False)
    tg = load_testgen()[0]  # is_even
    assert score_testgen(tg, "```python\ndef test_e():\n    assert is_even(2)\n```")
    assert not score_testgen(tg, "```python\ndef test_e():\n    assert is_even(3)\n```")


# --- code-review via LLM-as-judge, with keyword fallback ----------------------
def test_judge_overrides_a_keyword_false_positive() -> None:
    """A review that MISSES the bug but contains a keyword fools the substring scorer;
    the judge (answering NO) correctly fails it — the whole point of the swap."""
    rv = load_review()[0]  # off_by_one, keyword list includes 'index'
    assert score_review(rv, "the index")  # keyword scorer is fooled
    assert not _score_review(rv, "the index", StubClient("judge", lambda p: "NO"))
    assert _score_review(rv, "found the real bug", StubClient("judge", lambda p: "YES"))


def test_judge_failure_falls_back_to_keyword_scorer() -> None:
    """An unreachable/throwing judge must not zero out review — fall back to keywords."""
    rv = load_review()[0]

    def _boom(_p: str) -> str:
        raise RuntimeError("judge unreachable")

    judge = StubClient("judge", _boom)
    assert _score_review(rv, "index out of range", judge)  # keyword match → pass
    assert not _score_review(rv, "looks fine", judge)  # no match → fail


def test_no_judge_uses_keyword_scorer() -> None:
    rv = load_review()[0]
    assert _score_review(rv, "index out of range", None)
    assert not _score_review(rv, "looks fine", None)


# --- multi-sample scoring (variance reduction) --------------------------------
def test_samples_emit_one_result_per_generation() -> None:
    one = run_suite([StubClient("good", _good)], samples=1)
    three = run_suite([StubClient("good", _good)], samples=3)
    assert len(three) == 3 * len(one)  # each task emitted once per sample


def test_leaderboard_turns_samples_into_a_fractional_rate() -> None:
    """3 samples of one task, 2 pass + 1 fail → the existing passed/total aggregation
    yields 2/3 with no change to leaderboard.py."""
    rows = [
        Result("m", CODEGEN, "t1", True, 0.0),
        Result("m", CODEGEN, "t1", True, 0.0),
        Result("m", CODEGEN, "t1", False, 0.0),
    ]
    assert abs(build_leaderboard(rows)["m"]["code-gen"] - 2 / 3) < 1e-9


# --- CLI wiring for --samples / --judge-model ---------------------------------
def test_samples_flag_rejects_non_positive() -> None:
    for bad in ("0", "-1"):
        with pytest.raises(SystemExit):
            eval_main.main(["--models", "m", "--samples", bad])


def test_cli_wires_samples_and_judge_into_run_suite(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _stub_gateway(monkeypatch)
    monkeypatch.setattr(eval_main, "render_leaderboard_chart", lambda *a, **k: None)
    captured: dict[str, object] = {}

    def _fake_run_suite(clients: object, *, samples: int = 1, judge: object = None) -> list:
        captured["samples"] = samples
        captured["has_judge"] = judge is not None
        return [Result("m", CODEGEN, "t", True, 0.1)]

    monkeypatch.setattr(eval_main, "run_suite", _fake_run_suite)
    eval_main.main(
        ["--models", "m", "--gateway", "http://x", "--out", str(tmp_path)]
        + ["--samples", "3", "--judge-model", "judge-m"]
    )
    assert captured == {"samples": 3, "has_judge": True}

    captured.clear()
    eval_main.main(["--models", "m", "--gateway", "http://x", "--out", str(tmp_path)])
    assert captured == {"samples": 1, "has_judge": False}
