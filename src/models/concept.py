"""Concept data model for extracted entities."""
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum
from .citation import Citation


class ConceptType(str, Enum):
    """Types of concepts extracted."""

    TECHNOLOGY = "technology"
    METHOD = "method"
    PERSON = "person"
    ORGANIZATION = "organization"
    FIELD = "field"
    APPLICATION = "application"
    METRIC = "metric"


class Concept(BaseModel):
    """Represents an extracted concept/entity."""

    name: str = Field(..., description="Canonical concept name")
    concept_type: ConceptType
    description: str
    citations: List[Citation] = Field(default_factory=list)
    aliases: List[str] = Field(default_factory=list)
    is_inferred: bool = False  # True if inferred, False if directly extracted
    relevance_score: float = Field(default=0.5, ge=0.0, le=1.0, description="Relevance to research topic (0.0-1.0)")

    # Detailed sections for learning/implementation
    technical_details: Optional[str] = Field(default=None, description="Technical details and how it works")
    key_components: Optional[List[str]] = Field(default=None, description="Key components or characteristics")
    implementation_notes: Optional[str] = Field(default=None, description="Implementation guidance and notes")
    use_cases: Optional[List[str]] = Field(default=None, description="Practical use cases or applications")

    def to_wikilink(self) -> str:
        """Format as Logseq wikilink."""
        return f"[[{self.name}]]"

    def to_markdown_page(self) -> str:
        """Generate full markdown page for this concept."""
        lines = [
            f"# {self.name}",
            "",
            f"**Type**: {self.concept_type.value}",
            "",
            "## Description",
            self.description,
            "",
        ]

        # Technical Details section
        if self.technical_details:
            lines.extend(
                [
                    "## Technical Details",
                    self.technical_details,
                    "",
                ]
            )

        # Key Components section
        if self.key_components:
            lines.extend(
                [
                    "## Key Components",
                    *[f"- {component}" for component in self.key_components],
                    "",
                ]
            )

        # Implementation Notes section
        if self.implementation_notes:
            lines.extend(
                [
                    "## Implementation Notes",
                    self.implementation_notes,
                    "",
                ]
            )

        # Use Cases section
        if self.use_cases:
            lines.extend(
                [
                    "## Use Cases",
                    *[f"- {use_case}" for use_case in self.use_cases],
                    "",
                ]
            )

        if self.aliases:
            lines.extend(
                [
                    "## Aliases",
                    ", ".join(f"`{alias}`" for alias in self.aliases),
                    "",
                ]
            )

        if self.citations:
            lines.extend(
                [
                    "## Sources",
                    *[f"- {citation.to_markdown()}" for citation in self.citations],
                    "",
                ]
            )

        return "\n".join(lines)
