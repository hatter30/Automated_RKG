"""Utilities for parsing and handling code-related data."""
from src.models.code_block import CodeBlock, AlgorithmStep, LogicFlow, CodeLanguage


def parse_code_blocks(code_data: list[dict] | None) -> list[CodeBlock]:
    """
    Parse code block data from OpenAI response.

    Args:
        code_data: List of code block dictionaries

    Returns:
        List of CodeBlock objects
    """
    if not code_data:
        return []

    blocks = []
    for item in code_data:
        try:
            block = CodeBlock(
                language=CodeLanguage.from_string(item.get("language", "pseudocode")),
                code=item.get("code", ""),
                description=item.get("description"),
                source_url=item.get("source_url"),
                is_pseudocode=item.get("is_pseudocode", False),
            )
            if block.code.strip():  # Only add non-empty code blocks
                blocks.append(block)
        except Exception:
            continue  # Skip malformed entries

    return blocks


def parse_logic_flow(flow_data: dict | None) -> LogicFlow | None:
    """
    Parse logic flow data from OpenAI response.

    Args:
        flow_data: Logic flow dictionary

    Returns:
        LogicFlow object or None
    """
    if not flow_data:
        return None

    try:
        # Parse algorithm steps
        steps = []
        for step_data in flow_data.get("algorithm_steps", []):
            step = AlgorithmStep(
                step_number=step_data.get("step_number", len(steps) + 1),
                action=step_data.get("action", ""),
                details=step_data.get("details"),
            )
            if step.action.strip():
                steps.append(step)

        flow = LogicFlow(
            input_spec=flow_data.get("input_spec", []),
            output_spec=flow_data.get("output_spec", []),
            algorithm_steps=steps,
            dependencies=flow_data.get("dependencies", []),
            complexity=flow_data.get("complexity"),
        )

        # Only return if there's meaningful content
        if flow.algorithm_steps or flow.input_spec or flow.output_spec:
            return flow
        return None

    except Exception:
        return None


def sanitize_code_for_markdown(code: str) -> str:
    """
    Sanitize code string for safe markdown embedding.

    Args:
        code: Raw code string

    Returns:
        Sanitized code safe for markdown
    """
    # Escape triple backticks within code
    code = code.replace("```", "\\`\\`\\`")
    # Normalize line endings
    code = code.replace("\r\n", "\n").replace("\r", "\n")
    return code
