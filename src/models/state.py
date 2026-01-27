"""LangGraph state definition for research workflow."""
from typing import TypedDict, List, Annotated, Dict, Any
from operator import add
from .concept import Concept
from .relationship import Relationship


class ResearchState(TypedDict):
    """LangGraph state for research workflow."""

    # Input
    research_topic: str

    # Query Generation
    search_queries: Annotated[List[str], add]

    # Web Search
    search_results: Annotated[List[Dict[str, Any]], add]  # Raw search results

    # Entity Extraction
    concepts: Annotated[List[Concept], add]

    # Relationship Inference
    relationships: Annotated[List[Relationship], add]

    # Output Generation
    markdown_output: str
    output_path: str

    # Metadata
    errors: Annotated[List[str], add]
    step_count: int
