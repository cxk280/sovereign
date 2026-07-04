"""Eval harness end-to-end with deterministic stub models (no network)."""

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
