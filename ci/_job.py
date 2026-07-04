"""Shared job flow: fetch MR diff → ask the gateway → post a note.

``run`` takes injected clients (duck-typed) so jobs are unit-tested with fakes;
``run_from_env`` wires the real clients from GitLab CI variables.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any


def run(
    gateway: Any,
    gitlab: Any,
    mr_iid: str,
    *,
    title: str,
    prompt_builder: Callable[[str], str],
    task: str | None = None,
) -> str | None:
    diff = gitlab.get_mr_diff(mr_iid)
    if not diff.strip():
        return None
    answer = gateway.complete(prompt_builder(diff), task=task)
    body = f"## {title}\n\n{answer}"
    gitlab.post_note(mr_iid, body)
    return body


def run_from_env(
    *, title: str, prompt_builder: Callable[[str], str], task: str | None = None
) -> None:
    from ci.config import from_env
    from ci.gitlab import GitLabClient
    from ci.llm import GatewayClient

    cfg = from_env()
    run(
        GatewayClient(cfg.gateway_url),
        GitLabClient(cfg.api_url, cfg.project_id, cfg.token),
        cfg.mr_iid,
        title=title,
        prompt_builder=prompt_builder,
        task=task,
    )
