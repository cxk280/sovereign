# eval

Evaluate and **curate** candidate open models for engineering tasks — the evidence behind which model
the registry routes each task to.

Tasks scored:
- **code-gen** — a HumanEval-style subset (generated code must run and pass tests).
- **code-review** — LLM-as-judge over seeded buggy diffs (did the model catch the planted defect?).
- **test-gen** — generated tests must execute and pass against a reference implementation.

Outputs a **leaderboard** (`results/*.json`), a markdown report, and rendered comparison **charts**
(pixel-verified) that feed the dashboard's leaderboard view.

_Built in build-order Step 3._
