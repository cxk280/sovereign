"""Dashboard backend tests — real registry + sample_data, zero network."""

from pathlib import Path

from fastapi.testclient import TestClient

from dashboard_api.app import create_app
from dashboard_api.data import build_leaderboard
from gateway.registry import ModelSpec, Registry, RoutingConfig

REPO_ROOT = Path(__file__).resolve().parent.parent


def _registry() -> Registry:
    return Registry(
        models=[
            ModelSpec(
                name="qwen2.5-coder:1.5b",
                version="1.5b-instruct",
                backend="ollama",
                quantization="Q4_K_M",
                tasks=["code-gen", "code-review", "test-gen", "chat"],
            )
        ],
        routing=RoutingConfig(
            default="qwen2.5-coder:1.5b",
            by_task={"code-gen": "qwen2.5-coder:1.5b", "chat": "qwen2.5-coder:1.5b"},
        ),
    )


def _client() -> TestClient:
    return TestClient(create_app(_registry(), sample_data=REPO_ROOT / "sample_data"))


def test_healthz() -> None:
    assert _client().get("/healthz").json() == {"status": "ok"}


def test_overview_models_live_reflects_registry() -> None:
    body = _client().get("/api/overview").json()
    assert body["stats"][0]["label"] == "MODELS LIVE"
    assert body["stats"][0]["value"] == "1"  # one model in the test registry
    assert body["backend"]["model"] == "qwen2.5-coder:1.5b"
    assert len(body["requests_series"]) == 24


def test_registry_merges_active_and_candidates() -> None:
    body = _client().get("/api/registry").json()
    statuses = {m["name"]: m["status"] for m in body["models"]}
    assert statuses["qwen2.5-coder:1.5b"] == "active"
    assert statuses["qwen2.5-coder:7b"] == "candidate"
    # routing comes from the real registry routing config
    tasks = {r["task"] for r in body["routing"]}
    assert {"code-gen", "chat"} <= tasks


def test_leaderboard_is_ranked_and_marks_curated_winner() -> None:
    body = _client().get("/api/leaderboard").json()
    overalls = [r["overall"] for r in body["rows"]]
    assert overalls == sorted(overalls, reverse=True)  # ranked
    assert body["rows"][0]["name"] == "qwen2.5-coder:7b"
    assert body["rows"][0]["curated"] is True


def test_leaderboard_overall_is_mean_of_task_scores() -> None:
    lb = build_leaderboard()
    top = lb.rows[0]
    assert abs(top.overall - sum(top.scores.values()) / len(top.scores)) < 1e-9


def test_adoption_shape() -> None:
    body = _client().get("/api/adoption").json()
    assert len(body["stats"]) == 4
    assert len(body["usage_series"]) == 30
    assert sum(s["pct"] for s in body["by_surface"]) == 100


def test_context_inventory_counts_real_sample_data() -> None:
    body = _client().get("/api/context").json()
    by_name = {s["name"]: s for s in body["sources"]}
    # sample_data/runbooks has 3 markdown files in the repo
    assert by_name["Runbooks"]["docs_label"] == "3 docs"
    # retrieval hits reference real sample_data paths
    assert body["results"][0]["path"] == "runbooks/deploy-rollback.md"


# --- edge cases -------------------------------------------------------------
def test_overview_handles_empty_registry() -> None:
    empty = Registry(models=[], routing=RoutingConfig(default="none"))
    client = TestClient(create_app(empty, sample_data=REPO_ROOT / "sample_data"))
    body = client.get("/api/overview").json()
    assert body["stats"][0]["value"] == "0"  # models live
    assert body["backend"]["model"] == "—"  # no crash on empty registry


def test_context_handles_missing_sample_data(tmp_path: Path) -> None:
    client = TestClient(create_app(_registry(), sample_data=tmp_path / "does-not-exist"))
    body = client.get("/api/context").json()
    # sources still enumerated (from fixture meta), with zero real doc counts
    assert {s["name"] for s in body["sources"]} == {
        "Codebase",
        "Runbooks",
        "Incidents",
        "Architecture",
    }
    assert all(s["docs_label"].startswith("0 ") for s in body["sources"])
