"""Relationship inference node for LangGraph workflow."""
from typing import Any
import logging
from src.models.state import ResearchState
from src.models.relationship import Relationship, RelationType
from src.services.openai_service import OpenAIService
from src.prompts.relationship_inference import (
    RELATIONSHIP_INFERENCE_SYSTEM_PROMPT,
    RELATIONSHIP_INFERENCE_USER_PROMPT,
)
from src.utils.json_utils import parse_json_response
from src.utils.prompt_utils import format_search_results
from src.utils.state_utils import increment_step_count
from src.utils.concept_utils import create_citation_from_search_result

logger = logging.getLogger(__name__)


def create_relationship_inferrer_node(openai_service: OpenAIService):
    """
    Create a relationship inferrer node function.

    Args:
        openai_service: OpenAI service instance

    Returns:
        Node function for relationship inference
    """

    def infer_relationships_node(state: ResearchState) -> dict[str, Any]:
        """
        Infer relationships between extracted concepts.

        Args:
            state: Current research state

        Returns:
            Updated state with relationships populated
        """
        logger.info(f"Inferring relationships between {len(state['concepts'])} concepts")

        relationships: list[Relationship] = []
        errors: list[str] = []

        try:
            # Format concepts for prompt
            concepts_text = "\n".join(
                [
                    f"- {c.name} ({c.concept_type.value}): {c.description}"
                    for c in state["concepts"]
                ]
            )

            # Format search results context
            context_text = format_search_results(state["search_results"], limit=10)

            # Call OpenAI
            response = openai_service.generate_structured_output(
                system_prompt=RELATIONSHIP_INFERENCE_SYSTEM_PROMPT,
                user_prompt=RELATIONSHIP_INFERENCE_USER_PROMPT.format(
                    concepts=concepts_text, context=context_text
                ),
                temperature=0.5,
            )

            # Parse response
            relationships_data = parse_json_response(response)

            for rel_data in relationships_data.get("relationships", []):
                # Determine if relationship is fact or inference
                is_inferred = rel_data.get("is_inferred", True)

                # Create citations if provided
                citations = []
                if "source_urls" in rel_data:
                    for url in rel_data["source_urls"]:
                        # Find matching search result
                        matching = [r for r in state["search_results"] if r["url"] == url]
                        if matching:
                            citations.append(create_citation_from_search_result(matching[0]))

                relationship = Relationship(
                    source=rel_data["source"],
                    relation_type=RelationType(rel_data["relation_type"]),
                    target=rel_data["target"],
                    description=rel_data.get("description"),
                    citations=citations,
                    is_inferred=is_inferred,
                    confidence=rel_data.get("confidence", 0.8),
                )

                relationships.append(relationship)

            logger.info(f"Inferred {len(relationships)} relationships")

        except Exception as e:
            error_msg = f"Relationship inference failed: {str(e)}"
            logger.error(error_msg)
            errors.append(error_msg)

        return {
            "relationships": relationships,
            "errors": errors,
            "step_count": increment_step_count(state),
        }

    return infer_relationships_node
