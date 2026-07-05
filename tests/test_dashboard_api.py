"""Dashboard backend tests — real registry + sample_data, zero network."""

import json
from pathlib import Path

from fastapi.testclient import TestClient

from dashboard_api.app import create_app
from dashboard_api.data import build_leaderboard
from gateway.registry import ModelSpec, Registry, RoutingConfig

REPO_ROOT = Path(__file__).resolve().parent.parent

_MEASURED_MODEL = "Qwen/Qwen2.5-Coder-7B-Instruct-AWQ"


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


# --- measured eval results (eval/results/) ----------------------------------
def _client_with_results(tmp_path: Path) -> TestClient:
    return TestClient(
        create_app(_registry(), sample_data=REPO_ROOT / "sample_data", results_dir=tmp_path)
    )


def test_overview_uses_measured_bench_when_present(tmp_path: Path) -> None:
    (tmp_path / "bench.json").write_text(
        json.dumps(
            [{"model": _MEASURED_MODEL, "requests": 8, "avg_latency_s": 1.84, "tokens_per_s": 74.2}]
        )
    )
    body = _client_with_results(tmp_path).get("/api/overview").json()
    tiles = {s["label"]: s for s in body["stats"]}
    assert tiles["TOKENS / SEC"]["value"] == "74"
    assert tiles["TOKENS / SEC"]["delta"] == "measured"
    # the P50 tile is relabelled to the honestly-named measured average
    assert "AVG LATENCY" in tiles
    assert tiles["AVG LATENCY"]["value"] == "1.84 s"
    assert tiles["AVG LATENCY"]["delta"] == "measured"
    assert "measured" in body["backend"]["note"].lower()


def test_overview_falls_back_to_fixtures_when_results_absent(tmp_path: Path) -> None:
    body = _client_with_results(tmp_path).get("/api/overview").json()  # empty dir
    tiles = {s["label"]: s for s in body["stats"]}
    assert tiles["P50 LATENCY"]["value"] == "310 ms"  # fixture value, unchanged
    assert "AVG LATENCY" not in tiles


def test_overview_survives_malformed_bench_json(tmp_path: Path) -> None:
    (tmp_path / "bench.json").write_text("{ this is not valid json")
    body = _client_with_results(tmp_path).get("/api/overview").json()  # no 500
    tiles = {s["label"]: s for s in body["stats"]}
    assert tiles["P50 LATENCY"]["value"] == "310 ms"  # graceful fixture fallback


def test_leaderboard_overlays_measured_rows(tmp_path: Path) -> None:
    (tmp_path / "leaderboard.json").write_text(
        json.dumps(
            {
                _MEASURED_MODEL: {
                    "code-gen": 0.9,
                    "code-review": 0.8,
                    "test-gen": 0.7,
                    "overall": 0.8,
                }
            }
        )
    )
    body = _client_with_results(tmp_path).get("/api/leaderboard").json()
    measured = [r for r in body["rows"] if r["measured"]]
    assert len(measured) == 1
    row = measured[0]
    assert row["name"] == _MEASURED_MODEL
    assert row["scores"] == {"code-gen": 0.9, "code-review": 0.8, "test-gen": 0.7}
    assert row["overall"] == 0.8
    # illustrative fixture candidates remain as comparison context
    assert any(not r["measured"] for r in body["rows"])


def test_leaderboard_all_fixtures_when_results_absent(tmp_path: Path) -> None:
    body = _client_with_results(tmp_path).get("/api/leaderboard").json()
    assert all(r["measured"] is False for r in body["rows"])


def test_overview_empty_bench_list_falls_back_to_fixtures(tmp_path: Path) -> None:
    (tmp_path / "bench.json").write_text("[]")  # present but no rows
    body = _client_with_results(tmp_path).get("/api/overview").json()
    tiles = {s["label"]: s for s in body["stats"]}
    assert tiles["P50 LATENCY"]["value"] == "310 ms"  # unchanged fixture


def test_overview_sub_second_latency_formats_as_ms(tmp_path: Path) -> None:
    (tmp_path / "bench.json").write_text(
        json.dumps(
            [{"model": _MEASURED_MODEL, "requests": 8, "avg_latency_s": 0.42, "tokens_per_s": 88.0}]
        )
    )
    body = _client_with_results(tmp_path).get("/api/overview").json()
    tiles = {s["label"]: s for s in body["stats"]}
    assert tiles["AVG LATENCY"]["value"] == "420 ms"  # GPU-speed latency reads in ms
