"""Relationship data model for connections between concepts."""
from pydantic import BaseModel, Field
from enum import Enum
from .citation import Citation


class RelationType(str, Enum):
    """Types of relationships between concepts."""

    IS_A = "is_a"  # Inheritance/type relationship
    USES = "uses"  # Usage relationship
    PART_OF = "part_of"  # Component relationship
    DEVELOPED_BY = "developed_by"  # Attribution
    APPLIED_TO = "applied_to"  # Application domain
    IMPROVES = "improves"  # Enhancement relationship
    RELATED_TO = "related_to"  # Generic relationship


class Relationship(BaseModel):
    """Represents a relationship between two concepts."""

    source: str = Field(..., description="Source concept name")
    relation_type: RelationType
    target: str = Field(..., description="Target concept name")
    description: str | None = None
    citations: list[Citation] = Field(default_factory=list)
    is_inferred: bool = False
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)

    def to_markdown(self) -> str:
        """Format relationship as markdown."""
        fact_type = "**Inferred**" if self.is_inferred else "**Fact**"
        rel_str = f"[[{self.source}]] {self.relation_type.value} [[{self.target}]]"

        parts = [f"{fact_type}: {rel_str}"]
        if self.description:
            parts.append(f"  - {self.description}")
        if self.citations:
            citations_str = ", ".join(c.to_markdown() for c in self.citations)
            parts.append(f"  - Sources: {citations_str}")

        return "\n".join(parts)
