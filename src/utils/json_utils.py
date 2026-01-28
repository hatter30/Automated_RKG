"""Utilities for JSON parsing and processing."""
import json
import logging
from typing import Any

logger = logging.getLogger(__name__)


def parse_json_response(response: str) -> dict[str, Any]:
    """
    Parse JSON response from LLM, handling markdown code fences.

    Args:
        response: Raw response string that may contain JSON

    Returns:
        Parsed JSON as dictionary

    Raises:
        json.JSONDecodeError: If JSON parsing fails
    """
    response_clean = response.strip()

    # Remove markdown code fences if present
    if response_clean.startswith("```json"):
        response_clean = response_clean[7:]
    if response_clean.startswith("```"):
        response_clean = response_clean[3:]
    if response_clean.endswith("```"):
        response_clean = response_clean[:-3]

    response_clean = response_clean.strip()

    return json.loads(response_clean)
