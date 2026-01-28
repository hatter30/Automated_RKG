"""Component expander node for extracting key components as separate concepts."""
from typing import Dict, Any, List
import logging
import json
from src.models.state import ResearchState
from src.models.concept import Concept, ConceptType
from src.models.citation import Citation
from src.services.concept_normalizer import ConceptNormalizer
from src.services.openai_service import OpenAIService
from src.prompts.entity_extraction import (
    ENTITY_EXTRACTION_SYSTEM_PROMPT,
    ENTITY_EXTRACTION_USER_PROMPT,
)

logger = logging.getLogger(__name__)


def _enrich_components(
    components: List[Concept],
    search_results: List[Dict],
    openai_service: OpenAIService,
    research_topic: str,
) -> List[Concept]:
    """
    Enrich component concepts with detailed information from search results.
    Uses the same entity extraction prompt as the main entity extractor for consistency.

    Args:
        components: List of component concepts to enrich
        search_results: Search results to extract information from
        openai_service: OpenAI service for extraction
        research_topic: Main research topic for context

    Returns:
        Enriched component concepts
    """
    if not components:
        return components

    logger.info(f"Enriching {len(components)} component concepts with detailed information")

    enriched_components = []

    # Format search results once
    results_text = []
    for i, result in enumerate(search_results[:50], 1):  # Limit to 50 results
        results_text.append(
            f"Source: {result.get('title', 'No title')}\n"
            f"URL: {result.get('url', 'No URL')}\n"
            f"Content: {result.get('description', 'No description')}"
        )
    search_results_text = "\n\n".join(results_text)

    # Extract detailed information for each component using entity extraction prompt
    for component in components:
        try:
            logger.info(f"Extracting entity information for component: {component.name}")

            # Use the same prompt as entity_extractor
            user_prompt = ENTITY_EXTRACTION_USER_PROMPT.format(
                topic=component.name,
                search_results=search_results_text,
            )

            # Call OpenAI with entity extraction prompt
            response = openai_service.generate_structured_output(
                system_prompt=ENTITY_EXTRACTION_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                temperature=0.6,
            )

            # Parse response
            response_clean = response.strip()
            if response_clean.startswith("```json"):
                response_clean = response_clean[7:]
            if response_clean.startswith("```"):
                response_clean = response_clean[3:]
            if response_clean.endswith("```"):
                response_clean = response_clean[:-3]
            response_clean = response_clean.strip()

            result_data = json.loads(response_clean)
            concepts_data = result_data.get("concepts", [])

            # Find the matching concept in the response
            if concepts_data:
                # Take the first (most relevant) concept
                enriched_data = concepts_data[0]

                # Update component with enriched data
                if enriched_data.get("description"):
                    component.description = enriched_data["description"]
                if enriched_data.get("technical_details"):
                    component.technical_details = enriched_data["technical_details"]
                if enriched_data.get("key_components"):
                    component.key_components = enriched_data["key_components"]
                if enriched_data.get("implementation_notes"):
                    component.implementation_notes = enriched_data["implementation_notes"]
                if enriched_data.get("use_cases"):
                    component.use_cases = enriched_data["use_cases"]
                if enriched_data.get("aliases"):
                    component.aliases.extend(enriched_data["aliases"])
                    component.aliases = list(set(component.aliases))  # Remove duplicates

                logger.info(f"Successfully enriched component: {component.name}")
            else:
                logger.warning(f"No enrichment data found for component: {component.name}")

            enriched_components.append(component)

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response for {component.name}: {str(e)}")
            enriched_components.append(component)  # Keep original
        except Exception as e:
            logger.error(f"Failed to enrich component {component.name}: {str(e)}", exc_info=True)
            enriched_components.append(component)  # Keep original

    logger.info(f"Successfully enriched {len(enriched_components)} component concepts")
    return enriched_components


def create_component_expander_node(openai_service: OpenAIService):
    """
    Create a component expander node function.

    This node extracts key_components from existing concepts and creates
    separate Concept entities for each component with high relevance scores,
    then enriches them with detailed information from search results.

    Args:
        openai_service: OpenAI service for enriching component details

    Returns:
        Node function for component expansion
    """
    normalizer = ConceptNormalizer()

    def expand_components_node(state: ResearchState) -> Dict[str, Any]:
        """
        Expand key components into separate concepts.

        Only expands components for the main research topic (query entity).

        Args:
            state: Current research state with extracted concepts

        Returns:
            Updated state with expanded component concepts
        """
        logger.info("Expanding key components into separate concepts")

        try:
            existing_concepts = state.get("concepts", [])
            research_topic = state.get("research_topic", "")
            new_components = []

            # Normalize research topic for comparison
            normalized_topic = normalizer.normalize(research_topic)
            logger.info(f"Only expanding components for query entity: {research_topic}")

            # Extract components from each concept
            for concept in existing_concepts:
                if not concept.key_components:
                    continue

                # Only expand components for the main research topic (query entity)
                normalized_concept = normalizer.normalize(concept.name)
                if normalized_concept != normalized_topic:
                    logger.debug(f"Skipping key_components for non-query entity: {concept.name}")
                    continue

                logger.info(f"Expanding key_components for query entity: {concept.name}")

                for component_str in concept.key_components:
                    # Parse component string: "Component Name: explanation"
                    if ":" not in component_str:
                        logger.warning(f"Invalid component format (missing ':'): {component_str}")
                        continue

                    component_name, component_desc = component_str.split(":", 1)
                    component_name = component_name.strip()
                    component_desc = component_desc.strip()

                    # Remove parentheses like "(ViT)" for cleaner names
                    if "(" in component_name:
                        # Keep the part before parentheses as main name
                        clean_name = component_name.split("(")[0].strip()
                        # Extract alias from parentheses
                        alias_match = component_name[component_name.find("(")+1:component_name.find(")")]
                        aliases = [alias_match] if alias_match else []
                    else:
                        clean_name = component_name
                        aliases = []

                    # Create new Concept for this component
                    component_concept = Concept(
                        name=clean_name,
                        concept_type=ConceptType.TECHNOLOGY,  # Default to technology
                        description=component_desc,
                        relevance_score=0.85,  # High priority for key components
                        aliases=aliases,
                        citations=concept.citations,  # Inherit parent's citations
                    )

                    new_components.append(component_concept)
                    logger.debug(f"Created component concept: {clean_name} (score: 0.85)")

            logger.info(f"Extracted {len(new_components)} component concepts")

            # Enrich components with detailed information from search results
            if new_components:
                search_results = state.get("search_results", [])
                enriched_components = _enrich_components(
                    new_components, search_results, openai_service, research_topic
                )
                new_components = enriched_components

            # Merge with existing concepts using normalizer
            all_concepts = existing_concepts + new_components
            merged_concepts = {}

            for concept in all_concepts:
                canonical = normalizer.normalize(concept.name)

                if canonical not in merged_concepts:
                    merged_concepts[canonical] = concept
                else:
                    # Merge: keep higher relevance score and more detailed content
                    existing = merged_concepts[canonical]

                    # Keep higher relevance score
                    if concept.relevance_score > existing.relevance_score:
                        existing.relevance_score = concept.relevance_score

                    # Merge aliases
                    existing.aliases = list(set(existing.aliases + concept.aliases))

                    # Keep more detailed description
                    if len(concept.description) > len(existing.description):
                        existing.description = concept.description

                    # Preserve detailed fields if existing doesn't have them
                    if concept.technical_details and not existing.technical_details:
                        existing.technical_details = concept.technical_details
                    if concept.key_components and not existing.key_components:
                        existing.key_components = concept.key_components
                    if concept.implementation_notes and not existing.implementation_notes:
                        existing.implementation_notes = concept.implementation_notes
                    if concept.use_cases and not existing.use_cases:
                        existing.use_cases = concept.use_cases

                    # Merge citations
                    existing_urls = {c.url for c in existing.citations}
                    for citation in concept.citations:
                        if citation.url not in existing_urls:
                            existing.citations.append(citation)

            final_concepts = list(merged_concepts.values())

            # Sort by relevance score
            final_concepts.sort(key=lambda c: c.relevance_score, reverse=True)

            logger.info(f"After merging: {len(final_concepts)} total concepts")
            logger.info(
                f"Top concepts: {', '.join(f'{c.name}({c.relevance_score:.2f})' for c in final_concepts[:10])}"
            )

            return {
                "concepts": final_concepts,
                "step_count": state.get("step_count", 0) + 1,
            }

        except Exception as e:
            error_msg = f"Component expansion failed: {str(e)}"
            logger.error(error_msg)
            return {
                "errors": [error_msg],
                "step_count": state.get("step_count", 0) + 1,
            }

    return expand_components_node
