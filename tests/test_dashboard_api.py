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


# --- leaderboard note provenance (honesty invariant) ------------------------
def _write_leaderboard(tmp_path: Path, host: str | None) -> None:
    scores = {"code-gen": 0.9, "code-review": 0.8, "test-gen": 0.7, "overall": 0.8}
    (tmp_path / "leaderboard.json").write_text(json.dumps({_MEASURED_MODEL: scores}))
    if host is not None:
        (tmp_path / "bench.meta.json").write_text(json.dumps({"host": host}))


def test_leaderboard_note_has_no_benchmark_host_claim_when_all_fixtures(tmp_path: Path) -> None:
    # With nothing measured, the note must not claim any benchmark ran at all —
    # in particular never "Vultr A16", which used to be hardcoded in the fixture.
    note = _client_with_results(tmp_path).get("/api/leaderboard").json()["note"]
    assert "A16" not in note and "Benchmarked" not in note
    assert "measured" not in note.lower()


def test_leaderboard_note_labels_local_provenance_never_a16(tmp_path: Path) -> None:
    # The exact bug: a real *local* measured row must never sit under a "Vultr A16" claim.
    _write_leaderboard(tmp_path, host="local")
    note = _client_with_results(tmp_path).get("/api/leaderboard").json()["note"]
    assert "locally on this machine" in note
    assert "A16" not in note and "Vultr" not in note and "GPU" not in note


def test_leaderboard_note_labels_vultr_cpu_provenance(tmp_path: Path) -> None:
    _write_leaderboard(tmp_path, host="vultr-cpu")
    note = _client_with_results(tmp_path).get("/api/leaderboard").json()["note"]
    assert "Vultr CPU compute" in note
    assert "A16" not in note and "GPU" not in note


def test_leaderboard_note_labels_vultr_a16_only_with_a16_provenance(tmp_path: Path) -> None:
    _write_leaderboard(tmp_path, host="vultr-a16")
    note = _client_with_results(tmp_path).get("/api/leaderboard").json()["note"]
    assert "Vultr A16 GPU" in note


def test_leaderboard_note_unknown_host_stays_generic(tmp_path: Path) -> None:
    _write_leaderboard(tmp_path, host="some-other-cloud")
    note = _client_with_results(tmp_path).get("/api/leaderboard").json()["note"]
    assert note.endswith("Rows marked measured come from a real eval run.")
    assert "A16" not in note


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


# --- honest provenance labels (bench.meta.json "host") ----------------------
def _write_bench(tmp_path: Path, host: str | None) -> None:
    (tmp_path / "bench.json").write_text(
        json.dumps(
            [{"model": _MEASURED_MODEL, "requests": 8, "avg_latency_s": 4.6, "tokens_per_s": 11.0}]
        )
    )
    if host is not None:
        (tmp_path / "bench.meta.json").write_text(json.dumps({"host": host}))


def test_overview_labels_vultr_cpu_from_provenance(tmp_path: Path) -> None:
    _write_bench(tmp_path, host="vultr-cpu")
    body = _client_with_results(tmp_path).get("/api/overview").json()
    backend = body["backend"]
    assert backend["serving"] == "Ollama · Vultr CPU"
    assert backend["note"] == "Latency & tokens/sec measured on Vultr CPU compute"
    # The A16 GPU must never be implied for a CPU run.
    assert "A16" not in backend["note"] and "GPU" not in backend["note"]


def test_overview_host_is_trimmed_before_lookup(tmp_path: Path) -> None:
    # EC-3: whitespace around a known host still resolves to the honest CPU label.
    _write_bench(tmp_path, host="  vultr-cpu  ")
    backend = _client_with_results(tmp_path).get("/api/overview").json()["backend"]
    assert backend["serving"] == "Ollama · Vultr CPU"


def test_overview_labels_vultr_a16_from_provenance(tmp_path: Path) -> None:
    _write_bench(tmp_path, host="vultr-a16")
    backend = _client_with_results(tmp_path).get("/api/overview").json()["backend"]
    assert backend["serving"] == "vLLM · Vultr A16"
    assert backend["note"] == "Latency & tokens/sec measured on Vultr A16"


def test_overview_cpu_numbers_never_mislabeled_as_a16_even_with_stale_expectations(
    tmp_path: Path,
) -> None:
    # A local-registry (ollama) box: without provenance the note is generic, and
    # with vultr-cpu provenance it is CPU — never A16, which is the whole point.
    _write_bench(tmp_path, host=None)
    note_no_host = _client_with_results(tmp_path).get("/api/overview").json()["backend"]["note"]
    assert note_no_host == "Latency & tokens/sec measured from a real eval run"
    _write_bench(tmp_path, host="vultr-cpu")
    note_cpu = _client_with_results(tmp_path).get("/api/overview").json()["backend"]["note"]
    assert "A16" not in note_no_host and "A16" not in note_cpu


def test_overview_unknown_host_falls_back_to_generic_measured_note(tmp_path: Path) -> None:
    _write_bench(tmp_path, host="some-other-cloud")
    backend = _client_with_results(tmp_path).get("/api/overview").json()["backend"]
    # Unknown host: honest-but-generic, serving stays the registry-derived label.
    assert backend["note"] == "Latency & tokens/sec measured from a real eval run"
    assert backend["serving"] == "Ollama · local"


def test_overview_survives_malformed_bench_meta(tmp_path: Path) -> None:
    _write_bench(tmp_path, host=None)
    (tmp_path / "bench.meta.json").write_text("{ not valid json")
    backend = _client_with_results(tmp_path).get("/api/overview").json()["backend"]  # no 500
    assert backend["note"] == "Latency & tokens/sec measured from a real eval run"


def test_unknown_provenance_never_inherits_a16_pill_from_vllm_registry(tmp_path: Path) -> None:
    # Airtight-invariant guard: even if a vLLM model were the active one (its label is
    # "vLLM · Vultr A16"), measured numbers with absent/unknown provenance must NOT be
    # shown under a Vultr/GPU serving pill.
    vllm_registry = Registry(
        models=[
            ModelSpec(name="qwen2.5-coder:7b", version="7b", backend="vllm", quantization="AWQ")
        ],
        routing=RoutingConfig(default="qwen2.5-coder:7b"),
    )
    client = TestClient(
        create_app(vllm_registry, sample_data=REPO_ROOT / "sample_data", results_dir=tmp_path)
    )
    _write_bench(tmp_path, host=None)  # measured numbers, provenance unknown
    backend = client.get("/api/overview").json()["backend"]
    assert "A16" not in backend["serving"] and "Vultr" not in backend["serving"]
    assert "A16" not in backend["note"] and "GPU" not in backend["note"]
