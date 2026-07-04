"""GitLab CI job: AI code review on a merge request."""

from __future__ import annotations

from ci import _job
from ci.prompts import build_review_prompt


def main() -> None:
    _job.run_from_env(
        title="🤖 sovereign — AI code review",
        prompt_builder=build_review_prompt,
        task="code-review",
    )


if __name__ == "__main__":
    main()
