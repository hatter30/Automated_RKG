"""Utilities for concept and citation management."""
from src.models.citation import Citation
from src.models.concept import Concept
from src.services.concept_normalizer import ConceptNormalizer


def create_citation_from_search_result(search_result: dict) -> Citation:
    """
    Create a Citation object from a search result dictionary.

    Args:
        search_result: Dictionary with 'url', 'title', 'description' keys

    Returns:
        Citation object
    """
    return Citation(
        url=search_result["url"],
        title=search_result["title"],
        snippet=search_result.get("description", ""),
    )


def merge_concepts(
    concepts: list[Concept], normalizer: ConceptNormalizer
) -> list[Concept]:
    """
    Merge and deduplicate concepts by canonical name.

    Merges concepts with the same canonical name, keeping:
    - Higher relevance score
    - Longer description
    - Combined aliases and citations
    - Detailed fields from either source

    Args:
        concepts: List of concepts to merge
        normalizer: ConceptNormalizer instance for name normalization

    Returns:
        Deduplicated list of merged concepts
    """
    concept_map: dict[str, Concept] = {}

    for concept in concepts:
        canonical = normalizer.normalize(concept.name)

        if canonical not in concept_map:
            # Set normalized name and add original to aliases if different
            if concept.name != canonical:
                concept.aliases.append(concept.name)
            concept.name = canonical
            concept_map[canonical] = concept
        else:
            # Merge with existing concept
            existing = concept_map[canonical]

            # Keep higher relevance score
            if concept.relevance_score > existing.relevance_score:
                existing.relevance_score = concept.relevance_score
                existing.description = concept.description
                existing.technical_details = concept.technical_details
                existing.key_components = concept.key_components
                existing.implementation_notes = concept.implementation_notes
                existing.use_cases = concept.use_cases
                # Also use code fields from higher relevance concept
                existing.code_snippets = concept.code_snippets
                existing.pseudocode = concept.pseudocode
                existing.logic_flow = concept.logic_flow
            else:
                # Merge code snippets and pseudocode from both sources
                existing.code_snippets.extend(concept.code_snippets)
                existing.pseudocode.extend(concept.pseudocode)
                # Keep existing logic_flow if present, otherwise use new one
                if not existing.logic_flow and concept.logic_flow:
                    existing.logic_flow = concept.logic_flow

            # Merge citations (avoid duplicates by URL)
            existing_urls = {c.url for c in existing.citations}
            for citation in concept.citations:
                if citation.url not in existing_urls:
                    existing.citations.append(citation)

            # Merge aliases
            if concept.name != canonical:
                existing.aliases.append(concept.name)
            existing.aliases.extend(concept.aliases)
            existing.aliases = list(set(existing.aliases))

    return list(concept_map.values())
