"""AI CI jobs with fake gateway + GitLab clients (no network)."""

from ci import _job
from ci.prompts import build_review_prompt, build_summary_prompt, build_testgen_prompt


class FakeGateway:
    def __init__(self, response: str) -> None:
        self.response = response
        self.calls: list[tuple[str, str | None]] = []

    def complete(self, prompt: str, task: str | None = None) -> str:
        self.calls.append((prompt, task))
        return self.response


class FakeGitLab:
    def __init__(self, diff: str) -> None:
        self.diff = diff
        self.notes: list[tuple[str, str]] = []

    def get_mr_diff(self, mr_iid: str) -> str:
        return self.diff

    def post_note(self, mr_iid: str, body: str) -> None:
        self.notes.append((mr_iid, body))


def test_review_job_posts_a_note_with_the_model_output() -> None:
    gw = FakeGateway("Bug: off-by-one on line 3.")
    gl = FakeGitLab("diff --git a/x.py b/x.py\n+ bad code")
    body = _job.run(
        gw, gl, "7", title="AI review", prompt_builder=build_review_prompt, task="code-review"
    )
    assert body is not None and "off-by-one" in body
    assert gl.notes == [("7", body)]
    # routed to the code-review task and the diff reached the prompt
    assert gw.calls[0][1] == "code-review"
    assert "diff --git" in gw.calls[0][0]


def test_empty_diff_skips_posting() -> None:
    gw = FakeGateway("unused")
    gl = FakeGitLab("   \n  ")
    assert _job.run(gw, gl, "7", title="t", prompt_builder=build_summary_prompt) is None
    assert gl.notes == []


def test_prompt_builders_embed_the_diff() -> None:
    for builder in (build_review_prompt, build_summary_prompt, build_testgen_prompt):
        assert "DIFFMARKER" in builder("DIFFMARKER")
