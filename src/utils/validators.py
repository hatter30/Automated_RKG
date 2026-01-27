"""Validation utilities for data quality."""
from typing import List
from ..models.concept import Concept
from ..models.relationship import Relationship


def validate_concepts(concepts: List[Concept]) -> List[str]:
    """
    Validate extracted concepts and return list of issues.

    Args:
        concepts: List of concepts to validate

    Returns:
        List of validation error messages
    """
    issues = []

    for concept in concepts:
        if not concept.name:
            issues.append("Concept with empty name found")
        if not concept.description:
            issues.append(f"Concept '{concept.name}' missing description")
        if not concept.citations and not concept.is_inferred:
            issues.append(f"Concept '{concept.name}' missing citations")

    return issues


def validate_relationships(
    relationships: List[Relationship], concepts: List[Concept]
) -> List[str]:
    """
    Validate relationships reference valid concepts.

    Args:
        relationships: List of relationships to validate
        concepts: List of valid concepts

    Returns:
        List of validation error messages
    """
    issues = []
    concept_names = {c.name for c in concepts}

    for rel in relationships:
        if rel.source not in concept_names:
            issues.append(f"Relationship references unknown source: {rel.source}")
        if rel.target not in concept_names:
            issues.append(f"Relationship references unknown target: {rel.target}")
        if not rel.is_inferred and not rel.citations:
            issues.append(
                f"Non-inferred relationship missing citations: {rel.source} -> {rel.target}"
            )

    return issues
