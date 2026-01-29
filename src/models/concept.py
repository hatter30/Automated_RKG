"""Concept data model for extracted entities."""
from pydantic import BaseModel, Field
from enum import Enum
from .citation import Citation
from .code_block import CodeBlock, LogicFlow


class ConceptType(str, Enum):
    """Types of concepts extracted."""

    TECHNOLOGY = "technology"
    METHOD = "method"
    PERSON = "person"
    ORGANIZATION = "organization"
    FIELD = "field"
    APPLICATION = "application"
    METRIC = "metric"
    LIBRARY = "library"
    FRAMEWORK = "framework"
    PROJECT = "project"
    CONCEPT = "concept"
    TOOL = "tool"
    LANGUAGE = "language"
    ALGORITHM = "algorithm"
    PATTERN = "pattern"

    @classmethod
    def from_string(cls, value: str) -> "ConceptType":
        """
        Convert string to ConceptType with fallback handling.

        Args:
            value: String value to convert

        Returns:
            Matching ConceptType or CONCEPT as default
        """
        value_lower = value.lower().strip()

        # Try direct match
        for member in cls:
            if member.value == value_lower:
                return member

        # Mapping for common variations
        mapping = {
            "lib": cls.LIBRARY,
            "package": cls.LIBRARY,
            "module": cls.LIBRARY,
            "sdk": cls.LIBRARY,
            "api": cls.TECHNOLOGY,
            "platform": cls.TECHNOLOGY,
            "system": cls.TECHNOLOGY,
            "service": cls.APPLICATION,
            "technique": cls.METHOD,
            "approach": cls.METHOD,
            "process": cls.METHOD,
            "standard": cls.CONCEPT,
            "principle": cls.CONCEPT,
            "theory": cls.CONCEPT,
            "model": cls.METHOD,
            "architecture": cls.PATTERN,
            "design": cls.PATTERN,
            "company": cls.ORGANIZATION,
            "institute": cls.ORGANIZATION,
            "university": cls.ORGANIZATION,
        }

        if value_lower in mapping:
            return mapping[value_lower]

        # Default fallback
        return cls.CONCEPT


class Concept(BaseModel):
    """Represents an extracted concept/entity."""

    name: str = Field(..., description="Canonical concept name")
    concept_type: ConceptType
    description: str
    citations: list[Citation] = Field(default_factory=list)
    aliases: list[str] = Field(default_factory=list)
    is_inferred: bool = False  # True if inferred, False if directly extracted
    relevance_score: float = Field(default=0.5, ge=0.0, le=1.0, description="Relevance to research topic (0.0-1.0)")

    # Detailed sections for learning/implementation
    technical_details: str | None = Field(default=None, description="Technical details and how it works")
    key_components: list[str] | None = Field(default=None, description="Key components or characteristics")
    implementation_notes: str | None = Field(default=None, description="Implementation guidance and notes")
    use_cases: list[str] | None = Field(default=None, description="Practical use cases or applications")

    # Code storage fields for re-implementation
    code_snippets: list[CodeBlock] = Field(default_factory=list, description="Actual code examples")
    pseudocode: list[CodeBlock] = Field(default_factory=list, description="Pseudocode/algorithm representations")
    logic_flow: LogicFlow | None = Field(default=None, description="Core logic flow for re-implementation")

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

        # Core Logic Flow section (most important for re-implementation)
        if self.logic_flow:
            lines.extend(
                [
                    "## Core Logic Flow",
                    "",
                    self.logic_flow.to_markdown(),
                ]
            )

        # Python Implementation section
        if self.pseudocode:
            lines.extend(
                [
                    "## Python Implementation",
                    "",
                ]
            )
            for idx, block in enumerate(self.pseudocode, 1):
                if len(self.pseudocode) > 1:
                    lines.append(f"### Algorithm {idx}")
                    lines.append("")
                lines.append(block.to_markdown())
                lines.append("")

        # Code Examples section
        if self.code_snippets:
            lines.extend(
                [
                    "## Code Examples",
                    "",
                ]
            )
            for idx, block in enumerate(self.code_snippets, 1):
                if len(self.code_snippets) > 1:
                    lines.append(f"### Example {idx}")
                    lines.append("")
                lines.append(block.to_markdown())
                lines.append("")

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
