# ide

Developer tooling backed by the internal, OpenAI-compatible [`gateway`](../gateway) — a private,
in-house alternative to cloud coding assistants. All three surfaces the platform targets:

- **`sov` CLI** — `sov chat "..."`, `sov review <file>`, `sov test <file>` from the terminal.
  Installed as a console script (`uv run sov ...` or `sov ...` once installed).
- **Continue** — [`continue/config.json`](./continue/config.json): chat **and** tab-autocomplete
  pointed at the gateway (`allowAnonymousTelemetry: false`).
- **Cursor** — [`cursor/README.md`](./cursor/README.md): override Cursor's OpenAI base URL to the
  gateway.
- **VS Code extension** — [`vscode/`](./vscode): a **Copilot alternative** — an inline
  fill-in-middle completion provider (via `/v1/completions`) plus a "Review Selection" command.

Autocomplete is backed by the gateway's `/v1/completions` (FIM) endpoint added in this step.

_Built in build-order Step 6._
