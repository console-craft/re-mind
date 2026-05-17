"""Helpers for Vapi tool calls."""

import json
from typing import Any

from app.vapi.schemas import VapiToolCall


def parse_tool_arguments(tool_call: VapiToolCall) -> dict[str, Any]:
    """Parse tool arguments supplied by Vapi.

    Args:
        tool_call: Vapi tool call payload.

    Returns:
        Parsed tool arguments.

    Raises:
        ValueError: If the arguments are not an object or JSON object string.
    """

    arguments = tool_call.function.arguments

    if arguments is None:
        return {}

    if isinstance(arguments, dict):
        return arguments

    try:
        parsed_arguments = json.loads(arguments)
    except json.JSONDecodeError as error:
        raise ValueError("Tool arguments must be a JSON object") from error

    if not isinstance(parsed_arguments, dict):
        raise ValueError("Tool arguments must be a JSON object")

    return parsed_arguments
