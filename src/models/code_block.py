"""Code block data models for storing code snippets and algorithms."""
from pydantic import BaseModel, Field
from enum import Enum


class CodeLanguage(str, Enum):
    """Programming languages for code blocks."""

    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    CPP = "cpp"
    C = "c"
    GO = "go"
    RUST = "rust"
    SQL = "sql"
    BASH = "bash"
    PSEUDOCODE = "pseudocode"
    OTHER = "other"

    @classmethod
    def from_string(cls, value: str) -> "CodeLanguage":
        """Convert string to CodeLanguage with fallback handling."""
        value_lower = value.lower().strip()
        for member in cls:
            if member.value == value_lower:
                return member
        return cls.OTHER


class CodeBlock(BaseModel):
    """Represents a code snippet or pseudocode block."""

    language: CodeLanguage = Field(
        default=CodeLanguage.PSEUDOCODE,
        description="Programming language of the code",
    )
    code: str = Field(..., description="The actual code content")
    description: str | None = Field(
        default=None,
        description="Brief explanation of what this code does",
    )
    source_url: str | None = Field(
        default=None,
        description="URL where this code was found",
    )
    is_pseudocode: bool = Field(
        default=False,
        description="True if this is pseudocode/algorithm, not executable code",
    )

    def to_markdown(self) -> str:
        """Format code block as markdown."""
        lang_tag = "pseudocode" if self.is_pseudocode else self.language.value
        lines = []
        if self.description:
            lines.append(f"*{self.description}*")
            lines.append("")
        lines.append(f"```{lang_tag}")
        lines.append(self.code)
        lines.append("```")
        if self.source_url:
            lines.append(f"*Source: {self.source_url}*")
        return "\n".join(lines)


class AlgorithmStep(BaseModel):
    """Represents a step in an algorithm."""

    step_number: int = Field(..., description="Step order (1-indexed)")
    action: str = Field(..., description="Description of this step")
    details: str | None = Field(
        default=None,
        description="Additional technical details for this step",
    )


class LogicFlow(BaseModel):
    """Represents the core logic flow for re-implementation."""

    input_spec: list[str] = Field(
        default_factory=list,
        description="Input parameters/data requirements",
    )
    output_spec: list[str] = Field(
        default_factory=list,
        description="Output format/return values",
    )
    algorithm_steps: list[AlgorithmStep] = Field(
        default_factory=list,
        description="Ordered algorithm steps",
    )
    dependencies: list[str] = Field(
        default_factory=list,
        description="Required libraries/modules/concepts",
    )
    complexity: str | None = Field(
        default=None,
        description="Time/space complexity if applicable",
    )

    def to_markdown(self) -> str:
        """Format logic flow as markdown."""
        lines = []

        if self.input_spec:
            lines.append("**Inputs:**")
            for inp in self.input_spec:
                lines.append(f"- {inp}")
            lines.append("")

        if self.output_spec:
            lines.append("**Outputs:**")
            for out in self.output_spec:
                lines.append(f"- {out}")
            lines.append("")

        if self.algorithm_steps:
            lines.append("**Algorithm Steps:**")
            for step in self.algorithm_steps:
                step_text = f"{step.step_number}. {step.action}"
                lines.append(step_text)
                if step.details:
                    lines.append(f"   - {step.details}")
            lines.append("")

        if self.dependencies:
            lines.append("**Dependencies:**")
            for dep in self.dependencies:
                lines.append(f"- `{dep}`")
            lines.append("")

        if self.complexity:
            lines.append(f"**Complexity:** {self.complexity}")
            lines.append("")

        return "\n".join(lines)
