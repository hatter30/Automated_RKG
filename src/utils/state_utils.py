"""Utilities for state management in LangGraph nodes."""
from typing import Any


def increment_step_count(state: dict[str, Any]) -> int:
    """
    Get incremented step count from state.

    Args:
        state: Current research state

    Returns:
        Incremented step count
    """
    return state.get("step_count", 0) + 1
