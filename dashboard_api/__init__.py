"""Read-only backend for the operator **dashboard** (build-order Step 5).

Aggregates data the five dashboard views render — model registry, evaluation
leaderboard, platform overview, adoption metrics, and the context inventory —
behind a small FastAPI app that mirrors the gateway's conventions
(``create_app`` + ``app_factory``). It reads real repo data where it exists
(``gateway/registry.yaml``, ``sample_data/``) and illustrative fixtures elsewhere,
so the public-repo, near-$0 build renders exactly like the approved Figma mocks.
"""
