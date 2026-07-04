"""Thin GitLab REST client — fetch a merge request's diff, post a note."""

from __future__ import annotations


class GitLabClient:
    def __init__(self, api_url: str, project_id: str, token: str, timeout: float = 30.0) -> None:
        self._api = api_url.rstrip("/")
        self._project = project_id
        self._headers = {"PRIVATE-TOKEN": token}
        self._timeout = timeout

    def get_mr_diff(self, mr_iid: str) -> str:
        import httpx

        resp = httpx.get(
            f"{self._api}/projects/{self._project}/merge_requests/{mr_iid}/changes",
            headers=self._headers,
            timeout=self._timeout,
        )
        resp.raise_for_status()
        changes = resp.json().get("changes", [])
        return "\n".join(
            f"--- {c.get('old_path')}\n+++ {c.get('new_path')}\n{c.get('diff', '')}"
            for c in changes
        )

    def post_note(self, mr_iid: str, body: str) -> None:
        import httpx

        resp = httpx.post(
            f"{self._api}/projects/{self._project}/merge_requests/{mr_iid}/notes",
            headers=self._headers,
            json={"body": body},
            timeout=self._timeout,
        )
        resp.raise_for_status()
