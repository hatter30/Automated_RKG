"""LangGraph workflow orchestration for research pipeline."""
from langgraph.graph import StateGraph, END
import logging
from ..models.state import ResearchState
from ..services.openai_service import OpenAIService
from ..services.brave_search_service import BraveSearchService
from ..services.concept_normalizer import ConceptNormalizer
from .nodes.query_generator import create_query_generator_node
from .nodes.web_searcher import create_web_searcher_node
from .nodes.entity_extractor import create_entity_extractor_node
from .nodes.component_expander import create_component_expander_node
from .nodes.relationship_inferrer import create_relationship_inferrer_node
from .nodes.markdown_generator import create_markdown_generator_node

logger = logging.getLogger(__name__)


def create_research_workflow(
    openai_service: OpenAIService,
    brave_service: BraveSearchService,
    normalizer: ConceptNormalizer,
    output_dir: str,
):
    """
    Create the LangGraph workflow for research.

    Workflow:
    1. generate_queries -> Generate search queries from topic
    2. search_web -> Execute searches via Brave API
    3. extract_entities -> Extract concepts from results (query entity only)
    4. expand_components -> Expand key components into separate entities
    5. infer_relationships -> Identify relationships between concepts
    6. generate_markdown -> Create Logseq-compatible output

    Args:
        openai_service: OpenAI service instance
        brave_service: Brave Search service instance
        normalizer: Concept normalizer instance
        output_dir: Directory for output files

    Returns:
        Compiled LangGraph workflow
    """
    # Create node functions with injected services
    query_generator = create_query_generator_node(openai_service)
    web_searcher = create_web_searcher_node(brave_service)
    entity_extractor = create_entity_extractor_node(openai_service, normalizer)
    component_expander = create_component_expander_node(openai_service)
    relationship_inferrer = create_relationship_inferrer_node(openai_service)
    markdown_generator = create_markdown_generator_node(output_dir)

    # Build workflow graph
    workflow = StateGraph(ResearchState)

    # Add nodes
    workflow.add_node("generate_queries", query_generator)
    workflow.add_node("search_web", web_searcher)
    workflow.add_node("extract_entities", entity_extractor)
    workflow.add_node("expand_components", component_expander)
    workflow.add_node("infer_relationships", relationship_inferrer)
    workflow.add_node("generate_markdown", markdown_generator)

    # Define edges
    workflow.set_entry_point("generate_queries")

    workflow.add_edge("generate_queries", "search_web")
    workflow.add_edge("search_web", "extract_entities")
    workflow.add_edge("extract_entities", "expand_components")
    workflow.add_edge("expand_components", "infer_relationships")
    workflow.add_edge("infer_relationships", "generate_markdown")
    workflow.add_edge("generate_markdown", END)

    logger.info("Research workflow created successfully")

    return workflow.compile()
