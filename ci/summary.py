"""GitLab CI job: AI merge-request summary."""

from __future__ import annotations

from ci import _job
from ci.prompts import build_summary_prompt


def main() -> None:
    _job.run_from_env(
        title="🤖 sovereign — MR summary",
        prompt_builder=build_summary_prompt,
        task="chat",
    )


if __name__ == "__main__":
    main()
