"""End-to-end gateway API tests with a zero-network fake backend."""

from typing import Any

from fastapi.testclient import TestClient

from gateway.app import create_app
from gateway.registry import ModelSpec, Registry, RoutingConfig


class FakeBackend:
    name = "ollama"

    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, Any]]] = []

    async def chat(self, model: str, payload: dict[str, Any]) -> dict[str, Any]:
        self.calls.append((model, payload))
        return {
            "id": "chatcmpl-fake",
            "object": "chat.completion",
            "model": model,
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": "ok"},
                    "finish_reason": "stop",
                }
            ],
            "usage": {"prompt_tokens": 5, "completion_tokens": 2},
        }

    async def completions(self, model: str, payload: dict[str, Any]) -> dict[str, Any]:
        self.calls.append((model, payload))
        return {
            "id": "cmpl-fake",
            "object": "text_completion",
            "model": model,
            "choices": [{"index": 0, "text": " world", "finish_reason": "stop"}],
        }

    async def health(self) -> bool:
        return True


def _client() -> tuple[TestClient, FakeBackend]:
    registry = Registry(
        models=[
            ModelSpec(name="coder", version="1", backend="ollama", tasks=["code-review", "chat"])
        ],
        routing=RoutingConfig(default="coder", by_task={"code-review": "coder"}),
    )
    fake = FakeBackend()
    return TestClient(create_app(registry, {"ollama": fake})), fake


def test_healthz() -> None:
    client, _ = _client()
    assert client.get("/healthz").json() == {"status": "ok"}


def test_list_models_exposes_registry_metadata() -> None:
    client, _ = _client()
    data = client.get("/v1/models").json()
    assert data["data"][0]["id"] == "coder"
    assert "code-review" in data["data"][0]["sovereign"]["tasks"]


def test_chat_completion_routes_task_to_model_and_proxies() -> None:
    client, fake = _client()
    resp = client.post(
        "/v1/chat/completions",
        json={"model": "code-review", "messages": [{"role": "user", "content": "hi"}]},
    )
    assert resp.status_code == 200
    assert resp.json()["choices"][0]["message"]["content"] == "ok"
    # router mapped the "code-review" task alias to the concrete "coder" model
    assert fake.calls[0][0] == "coder"


def test_completions_endpoint_proxies_fim() -> None:
    client, fake = _client()
    resp = client.post(
        "/v1/completions", json={"model": "code-review", "prompt": "hello", "suffix": "!"}
    )
    assert resp.status_code == 200
    assert resp.json()["choices"][0]["text"] == " world"
    # FIM suffix reached the backend payload
    assert fake.calls[0][1].get("suffix") == "!"


def test_unknown_model_returns_404() -> None:
    client, _ = _client()
    resp = client.post(
        "/v1/chat/completions",
        json={"model": "nope", "messages": [{"role": "user", "content": "hi"}]},
    )
    assert resp.status_code == 404


def test_metrics_endpoint_exposes_counters() -> None:
    client, _ = _client()
    client.post(
        "/v1/chat/completions",
        json={"model": "code-review", "messages": [{"role": "user", "content": "hi"}]},
    )
    body = client.get("/metrics").text
    assert "sovereign_gateway_requests_total" in body
