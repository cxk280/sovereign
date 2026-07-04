# Cursor → sovereign

Point Cursor at the internal gateway so its AI features run on your models:

1. **Cursor Settings → Models → OpenAI API Key**: set any non-empty key (e.g. `none`).
2. **Override OpenAI Base URL**: `http://localhost:8080/v1` (or your deployed gateway URL).
3. Add a custom model named `chat` (and `code-gen` for completion).

Cursor now sends chat/edit requests to the gateway's OpenAI-compatible endpoint — nothing leaves your
infrastructure. For a fully offline setup, ensure the gateway's backend is the local Ollama/llama.cpp
model, not a remote vLLM.
