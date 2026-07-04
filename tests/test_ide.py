"""`sov` CLI dispatch with a fake gateway client."""

from ide.cli import build_prompt, dispatch


class FakeClient:
    def __init__(self) -> None:
        self.last_task: str | None = None
        self.last_prompt: str | None = None

    def complete(self, prompt: str, task: str | None = None) -> str:
        self.last_prompt = prompt
        self.last_task = task
        return f"[{task}] done"


def test_review_prompt_includes_the_code() -> None:
    assert "def foo(): pass" in build_prompt("review", "def foo(): pass")


def test_dispatch_routes_each_command_to_its_task() -> None:
    c = FakeClient()
    assert "done" in dispatch("review", "code", c)
    assert c.last_task == "code-review"
    dispatch("test", "code", c)
    assert c.last_task == "test-gen"
    dispatch("chat", "hi", c)
    assert c.last_task == "chat"
    assert c.last_prompt == "hi"
