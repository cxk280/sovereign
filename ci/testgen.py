"""GitLab CI job: AI test generation for the changed code."""

from __future__ import annotations

from ci import _job
from ci.prompts import build_testgen_prompt


def main() -> None:
    _job.run_from_env(
        title="🤖 sovereign — suggested tests",
        prompt_builder=build_testgen_prompt,
        task="test-gen",
    )


if __name__ == "__main__":
    main()
