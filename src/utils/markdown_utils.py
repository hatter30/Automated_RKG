"""Utilities for markdown formatting."""
from typing import Dict, List, Any
import re


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a string to be safe for use as a filename.

    Args:
        filename: String to sanitize

    Returns:
        Safe filename string
    """
    # Replace invalid characters with underscores
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Replace multiple underscores/spaces with single underscore
    filename = re.sub(r'[_\s]+', '_', filename)
    # Remove leading/trailing underscores
    filename = filename.strip('_')
    # Limit length
    return filename[:200] if len(filename) > 200 else filename


def format_logseq_page(
    title: str, sections: Dict[str, List[str]], metadata: Dict[str, Any] = None
) -> str:
    """
    Format a Logseq page with proper structure.

    Args:
        title: Page title
        sections: Dict of section_name -> list of content lines
        metadata: Optional metadata dict

    Returns:
        Formatted markdown string
    """
    lines = [f"# {title}", ""]

    if metadata:
        for key, value in metadata.items():
            lines.append(f"**{key}**: {value}")
        lines.append("")

    for section_name, content in sections.items():
        lines.append(f"## {section_name}")
        lines.extend(content)
        lines.append("")

    return "\n".join(lines)


def escape_markdown(text: str) -> str:
    """
    Escape special markdown characters.

    Args:
        text: Text to escape

    Returns:
        Escaped text
    """
    special_chars = ["*", "_", "[", "]", "(", ")", "#", "+", "-", "!"]
    for char in special_chars:
        text = text.replace(char, f"\\{char}")
    return text
