"""LangGraph state definition for research workflow."""
from typing import TypedDict, Annotated, Any
from operator import add
from .concept import Concept
from .relationship import Relationship


class ResearchState(TypedDict):
    """LangGraph state for research workflow."""

    # Input
    research_topic: str

    # Query Generation
    search_queries: Annotated[list[str], add]

    # Web Search
    search_results: Annotated[list[dict[str, Any]], add]  # Raw search results

    # GitHub Code Search
    github_code_results: Annotated[list[dict[str, Any]], add]  # Code from GitHub

    # Entity Extraction
    concepts: Annotated[list[Concept], add]

    # Relationship Inference
    relationships: Annotated[list[Relationship], add]

    # Output Generation
    markdown_output: str
    output_path: str

    # Metadata
    errors: Annotated[list[str], add]
    step_count: int
