"""Vapi webhook routes."""

import os
from hmac import compare_digest
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException

from app.vapi import tools
from app.vapi.schemas import VapiToolCall, VapiToolResult, VapiWebhookPayload, VapiWebhookResponse

router = APIRouter(prefix="/vapi", tags=["vapi"])


async def handle_tool_call(
    tool_call: VapiToolCall,
    source_call_id: str | None,
) -> VapiToolResult:
    """Handle one Vapi tool call.

    Args:
        tool_call: Vapi tool call payload.
        source_call_id: Vapi call identifier attached to created reminders.

    Returns:
        Tool result keyed by the original Vapi tool call identifier.
    """

    if tool_call.function.name == "create_reminder":
        result = await tools.handle_create_reminder(tool_call, source_call_id)
    elif tool_call.function.name == "check_reminder_conflicts":
        result = await tools.handle_check_reminder_conflicts(tool_call)
    elif tool_call.function.name == "list_reminders":
        result = await tools.handle_list_reminders(tool_call)
    elif tool_call.function.name == "get_reminder":
        result = await tools.handle_get_reminder(tool_call)
    elif tool_call.function.name == "update_reminder":
        result = await tools.handle_update_reminder(tool_call)
    elif tool_call.function.name == "delete_reminder":
        result = await tools.handle_delete_reminder(tool_call)
    else:
        result = {"success": False, "error": f"Unsupported tool: {tool_call.function.name}"}

    return VapiToolResult(toolCallId=tool_call.id, result=result)


def read_vapi_webhook_secret() -> str:
    """Read the configured Vapi webhook secret.

    Returns:
        The configured webhook secret.

    Raises:
        HTTPException: If the webhook secret is not configured.
    """

    secret = os.getenv("VAPI_WEBHOOK_SECRET")

    if not secret:
        raise HTTPException(status_code=503, detail="Vapi webhook secret is not configured")

    return secret


def extract_bearer_token(authorization: str | None) -> str | None:
    """Extract a bearer token from an Authorization header.

    Args:
        authorization: Raw Authorization header value.

    Returns:
        The bearer token, or None when the header is missing or not bearer auth.
    """

    if authorization is None:
        return None

    scheme, _, token = authorization.partition(" ")

    if scheme.lower() != "bearer" or not token:
        return None

    return token


def require_vapi_secret(
    authorization: Annotated[str | None, Header()] = None,
    x_vapi_secret: Annotated[str | None, Header()] = None,
) -> None:
    """Validate the Vapi webhook secret from supported headers.

    Args:
        authorization: Optional Authorization header value.
        x_vapi_secret: Optional X-Vapi-Secret header value.

    Raises:
        HTTPException: If the supplied secret is missing or invalid.
    """

    expected_secret = read_vapi_webhook_secret()
    provided_secret = extract_bearer_token(authorization) or x_vapi_secret

    if provided_secret is None or not compare_digest(provided_secret, expected_secret):
        raise HTTPException(status_code=401, detail="Invalid Vapi webhook secret")


@router.post("/webhook", response_model=VapiWebhookResponse)
async def receive_vapi_webhook(
    payload: VapiWebhookPayload,
    _: Annotated[None, Depends(require_vapi_secret)],
) -> VapiWebhookResponse:
    """Receive Vapi webhook messages and execute supported tool calls.

    Args:
        payload: Vapi webhook payload.
        _: Secret validation dependency.

    Returns:
        Vapi tool results for tool-call messages, or an empty result list otherwise.
    """

    if payload.message.type != "tool-calls":
        return VapiWebhookResponse(results=[])

    source_call_id = payload.message.call.id if payload.message.call is not None else None
    results = [
        await handle_tool_call(tool_call, source_call_id)
        for tool_call in payload.message.tool_calls
    ]

    return VapiWebhookResponse(results=results)
