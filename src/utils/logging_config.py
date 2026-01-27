"""Logging configuration for the application."""
import logging
import sys
import io


def setup_logging(level: str = "INFO") -> None:
    """
    Configure logging for the application.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # Configure UTF-8 encoding for Windows console
    # Wrap stdout with UTF-8 encoding to handle unicode characters
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

    # Create handlers with UTF-8 encoding
    console_handler = logging.StreamHandler(sys.stdout)
    file_handler = logging.FileHandler("research.log", encoding='utf-8', errors='replace')

    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[console_handler, file_handler],
    )

    # Suppress noisy loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
