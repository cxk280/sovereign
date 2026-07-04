"""Request schemas.

Deliberately permissive: we validate the fields the gateway *routes* on
(``model``, ``messages``) and pass every other OpenAI parameter through to the
backend untouched (``extra="allow"``), so the gateway never lags the OpenAI API.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict


class ChatMessage(BaseModel):
    model_config = ConfigDict(extra="allow")

    role: str
    content: Any


class ChatCompletionRequest(BaseModel):
    model_config = ConfigDict(extra="allow")

    # `model` may be a registered model name, a task alias, "auto", or omitted.
    model: str | None = None
    messages: list[ChatMessage]
