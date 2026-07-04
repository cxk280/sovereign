"""Prompt builders for the AI CI jobs (pure functions, easy to test)."""

from __future__ import annotations


def build_review_prompt(diff: str) -> str:
    return (
        "You are a senior engineer reviewing a merge request. Review the diff below for "
        "correctness bugs, security issues, and clear style problems. Be concise and specific; "
        "cite file and line where possible. If it looks good, reply exactly 'LGTM'.\n\n"
        f"{diff}"
    )


def build_summary_prompt(diff: str) -> str:
    return (
        "Summarize this merge request for reviewers in 3–5 bullet points: what changed and why, "
        "and any risk to watch. Be terse.\n\n"
        f"{diff}"
    )


def build_testgen_prompt(diff: str) -> str:
    return (
        "Propose focused pytest tests for the changed code in this diff — cover the new behavior "
        "and one edge case per change. Return runnable test code only.\n\n"
        f"{diff}"
    )
