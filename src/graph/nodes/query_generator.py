"""Query generation node for LangGraph workflow."""
from typing import Any
import json
import logging
from src.models.state import ResearchState
from src.services.openai_service import OpenAIService
from src.prompts.query_generation import (
    QUERY_GENERATION_SYSTEM_PROMPT,
    QUERY_GENERATION_USER_PROMPT,
)

logger = logging.getLogger(__name__)


def create_query_generator_node(openai_service: OpenAIService):
    """
    Create a query generator node function.

    Args:
        openai_service: OpenAI service instance

    Returns:
        Node function for query generation
    """

    def generate_queries_node(state: ResearchState) -> dict[str, Any]:
        """
        Generate search queries from the research topic.

        Args:
            state: Current research state

        Returns:
            Updated state with search_queries populated
        """
        logger.info(f"Generating queries for topic: {state['research_topic']}")

        try:
            # Use OpenAI to generate diverse search queries
            response = openai_service.generate_structured_output(
                system_prompt=QUERY_GENERATION_SYSTEM_PROMPT,
                user_prompt=QUERY_GENERATION_USER_PROMPT.format(
                    topic=state["research_topic"]
                ),
                temperature=0.8,
            )

            # Parse JSON response
            queries_data = json.loads(response)
            queries = queries_data.get("queries", [])

            logger.info(f"Generated {len(queries)} queries")

            return {"search_queries": queries, "step_count": state.get("step_count", 0) + 1}

        except Exception as e:
            logger.error(f"Query generation failed: {e}")
            return {
                "errors": [f"Query generation error: {str(e)}"],
                "search_queries": [state["research_topic"]],  # Fallback to topic itself
                "step_count": state.get("step_count", 0) + 1,
            }

    return generate_queries_node
