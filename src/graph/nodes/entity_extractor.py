"""Entity extraction node for LangGraph workflow."""
from typing import Any
import logging
import asyncio
from src.models.state import ResearchState
from src.models.concept import Concept, ConceptType
from src.services.openai_service import OpenAIService
from src.services.concept_normalizer import ConceptNormalizer
from src.prompts.entity_extraction import (
    ENTITY_EXTRACTION_SYSTEM_PROMPT,
    ENTITY_EXTRACTION_USER_PROMPT,
)
from src.utils.json_utils import parse_json_response
from src.utils.prompt_utils import format_search_results
from src.utils.state_utils import increment_step_count
from src.utils.concept_utils import create_citation_from_search_result, merge_concepts
from config.settings import get_settings

logger = logging.getLogger(__name__)


def create_entity_extractor_node(
    openai_service: OpenAIService, normalizer: ConceptNormalizer
):
    """
    Create an entity extractor node function.

    Args:
        openai_service: OpenAI service instance
        normalizer: Concept normalizer instance

    Returns:
        Node function for entity extraction
    """

    async def process_batch_async(batch: list[dict], batch_index: int, topic: str) -> tuple[list[Concept], list[str]]:
        """
        Process a single batch of search results asynchronously.

        Args:
            batch: List of search results to process
            batch_index: Index of the batch for error reporting
            topic: Research topic

        Returns:
            Tuple of (extracted concepts, errors)
        """
        batch_concepts: list[Concept] = []
        batch_errors: list[str] = []

        try:
            # Format batch for prompt
            batch_text = format_search_results(batch)

            # Call OpenAI asynchronously
            response = await openai_service.generate_structured_output_async(
                system_prompt=ENTITY_EXTRACTION_SYSTEM_PROMPT,
                user_prompt=ENTITY_EXTRACTION_USER_PROMPT.format(
                    topic=topic, search_results=batch_text
                ),
                temperature=0.6,  # Increased for more diverse concept extraction
            )

            # Parse response
            extracted_data = parse_json_response(response)

            for concept_data in extracted_data.get("concepts", []):
                # Normalize concept name
                canonical_name = normalizer.normalize(concept_data["name"])

                # Create concept with citations
                citations = [
                    create_citation_from_search_result(r)
                    for r in batch
                    if concept_data["name"].lower() in r["description"].lower()
                ]

                concept = Concept(
                    name=canonical_name,
                    concept_type=ConceptType.from_string(concept_data["type"]),
                    description=concept_data["description"],
                    citations=citations,
                    aliases=concept_data.get("aliases", []),
                    is_inferred=False,
                    relevance_score=concept_data.get("relevance_score", 0.5),
                    technical_details=concept_data.get("technical_details"),
                    key_components=concept_data.get("key_components"),
                    implementation_notes=concept_data.get("implementation_notes"),
                    use_cases=concept_data.get("use_cases"),
                )

                batch_concepts.append(concept)

        except Exception as e:
            error_msg = f"Entity extraction failed for batch {batch_index}: {str(e)}"
            logger.error(error_msg)
            batch_errors.append(error_msg)

        return batch_concepts, batch_errors

    def extract_entities_node(state: ResearchState) -> dict[str, Any]:
        """
        Extract concepts/entities from search results with parallel processing.

        Args:
            state: Current research state

        Returns:
            Updated state with concepts populated
        """
        logger.info(f"Extracting entities from {len(state['search_results'])} search results")

        # Get batch size from settings
        settings = get_settings()
        batch_size = settings.entity_batch_size
        results = state["search_results"]

        # Create batches
        batches = [results[i : i + batch_size] for i in range(0, len(results), batch_size)]
        logger.info(f"Processing {len(batches)} batches in parallel (batch_size={batch_size})")

        # Process all batches in parallel using asyncio
        async def process_all_batches():
            tasks = [
                process_batch_async(batch, idx, state["research_topic"])
                for idx, batch in enumerate(batches)
            ]
            return await asyncio.gather(*tasks)

        # Run async processing
        batch_results = asyncio.run(process_all_batches())

        # Collect all concepts and errors
        concepts: list[Concept] = []
        errors: list[str] = []

        for batch_concepts, batch_errors in batch_results:
            concepts.extend(batch_concepts)
            errors.extend(batch_errors)

        logger.info(f"Extracted {len(concepts)} concepts (before deduplication)")

        # Deduplicate concepts using shared utility
        deduplicated = merge_concepts(concepts, normalizer)
        logger.info(f"After deduplication: {len(deduplicated)} concepts")

        # Filter to keep ONLY the query entity (exact match with research_topic)
        normalized_topic = normalizer.normalize(state["research_topic"])
        filtered = [c for c in deduplicated if normalizer.normalize(c.name) == normalized_topic]
        logger.info(f"After filtering (query entity only, matching '{state['research_topic']}'): {len(filtered)} concepts")

        # Handle case where query entity was not extracted
        if not filtered:
            logger.warning(f"Query entity '{state['research_topic']}' not found in extracted concepts")
            logger.info(f"Available extracted concepts: {[f'{c.name}({c.relevance_score:.2f})' for c in deduplicated[:10]]}")

            # Fallback: Use highest relevance concept if it's close enough (>= 0.8)
            if deduplicated and deduplicated[0].relevance_score >= 0.8:
                logger.info(f"Using fallback: highest relevance concept '{deduplicated[0].name}' (score: {deduplicated[0].relevance_score:.2f})")
                filtered = [deduplicated[0]]
            else:
                logger.error("No suitable query entity found. Continuing with empty entity list.")
                errors.append(f"Query entity '{state['research_topic']}' not extracted from search results")

        # Sort by relevance score
        sorted_concepts = sorted(filtered, key=lambda c: c.relevance_score, reverse=True)
        top_concepts = sorted_concepts  # Keep only query entity
        logger.info(f"Query entity concepts: {[f'{c.name}({c.relevance_score:.2f})' for c in top_concepts]}")

        return {
            "concepts": top_concepts,
            "errors": errors,
            "step_count": increment_step_count(state),
        }

    return extract_entities_node
