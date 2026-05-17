"""Schemas for Vapi webhook requests and responses."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class VapiFunctionCall(BaseModel):
    """Function payload nested inside a Vapi tool call."""

    name: str
    arguments: dict[str, Any] | str | None = None


class VapiToolCall(BaseModel):
    """A single tool call requested by a Vapi assistant."""

    id: str
    function: VapiFunctionCall


class VapiCall(BaseModel):
    """Vapi call metadata included with webhook messages."""

    id: str | None = None


class VapiMessage(BaseModel):
    """Vapi webhook message payload."""

    type: str
    call: VapiCall | None = None
    tool_calls: list[VapiToolCall] = Field(default_factory=list, alias="toolCalls")

    model_config = ConfigDict(populate_by_name=True)


class VapiWebhookPayload(BaseModel):
    """Top-level Vapi webhook payload."""

    message: VapiMessage


class VapiToolResult(BaseModel):
    """Result returned for a Vapi tool call."""

    tool_call_id: str = Field(alias="toolCallId")
    result: dict[str, Any]

    model_config = ConfigDict(populate_by_name=True)


class VapiWebhookResponse(BaseModel):
    """Vapi webhook response containing tool call results."""

    results: list[VapiToolResult]
