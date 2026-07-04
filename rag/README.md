# rag

Retrieval-augmented generation over internal knowledge, entirely local.

- Ingests [`sample_data/`](../sample_data) → chunks → embeddings with a **local** model
  (`BAAI/bge-small-en-v1.5`) → **Qdrant** vector store.
- Exposes a retrieval API consumed by the [`mcp`](../mcp) servers and the assistant.
- No embedding or retrieval call leaves the machine — core to the sovereignty guarantee.

Alternative vector store (pgvector) is covered in a [`docs/`](../docs) ADR.

_Built in build-order Step 2._
