"""Markdown generation node for LangGraph workflow."""
from typing import Any
import logging
from pathlib import Path
from datetime import datetime
from src.models.state import ResearchState
from src.utils.markdown_utils import sanitize_filename
from src.utils.state_utils import increment_step_count

logger = logging.getLogger(__name__)


def create_markdown_generator_node(output_dir: str):
    """
    Create a markdown generator node function.

    Args:
        output_dir: Directory to write output files

    Returns:
        Node function for markdown generation
    """

    def generate_markdown_node(state: ResearchState) -> dict[str, Any]:
        """
        Generate Logseq-compatible markdown from concepts and relationships.

        Args:
            state: Current research state

        Returns:
            Updated state with markdown_output and output_path
        """
        logger.info("Generating Logseq markdown")

        try:
            # Generate main topic page
            topic = state["research_topic"]
            concepts = state["concepts"]
            relationships = state["relationships"]

            # Find main concept (query entity - highest relevance or first)
            main_concept = concepts[0] if concepts else None

            # Build markdown content
            lines = [
                f"# {topic}",
                "",
                f"*Research conducted: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}*",
                "",
            ]

            # Add main concept details
            if main_concept:
                lines.extend([
                    "## Description",
                    main_concept.description,
                    "",
                ])

                if main_concept.technical_details:
                    lines.extend([
                        "## Technical Details",
                        main_concept.technical_details,
                        "",
                    ])

                if main_concept.key_components:
                    lines.extend([
                        "## Key Components",
                        "",
                    ])
                    for component in main_concept.key_components:
                        lines.append(f"- {component}")
                    lines.append("")

                if main_concept.implementation_notes:
                    lines.extend([
                        "## Implementation Notes",
                        main_concept.implementation_notes,
                        "",
                    ])

                if main_concept.use_cases:
                    lines.extend([
                        "## Use Cases",
                        "",
                    ])
                    for use_case in main_concept.use_cases:
                        lines.append(f"- {use_case}")
                    lines.append("")

            # Add related concepts section (sub-concepts excluding main)
            main_name = main_concept.name if main_concept else ""
            sub_concepts = [c for c in concepts if c.name != main_name]
            if sub_concepts:
                lines.extend([
                    "## Related Concepts",
                    "",
                ])
                for concept in sorted(sub_concepts, key=lambda c: c.relevance_score, reverse=True):
                    desc_text = concept.description[:100] + "..." if len(concept.description) > 100 else concept.description
                    lines.append(f"- {concept.to_wikilink()}: {desc_text}")
                lines.append("")

            # Add relationships section
            lines.extend(
                [
                    "## Relationships",
                    "",
                    "### Facts (Extracted from Sources)",
                ]
            )

            fact_relationships = [r for r in relationships if not r.is_inferred]
            for rel in fact_relationships:
                lines.append(f"- {rel.to_markdown()}")

            lines.extend(
                [
                    "",
                    "### Inferred Relationships",
                ]
            )

            inferred_relationships = [r for r in relationships if r.is_inferred]
            for rel in inferred_relationships:
                lines.append(f"- {rel.to_markdown()}")

            lines.extend(
                [
                    "",
                    "## Sources",
                    "",
                ]
            )

            # Collect all unique citations
            all_citations = set()
            for concept in concepts:
                for citation in concept.citations:
                    all_citations.add((str(citation.url), citation.title))

            for url, title in sorted(all_citations, key=lambda x: x[1]):
                lines.append(f"- [{title}]({url})")

            lines.append("")

            # Generate individual concept pages
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            # Write main page
            main_file = output_path / f"{sanitize_filename(topic)}.md"
            markdown_content = "\n".join(lines)
            main_file.write_text(markdown_content, encoding="utf-8")

            # Write individual concept pages (skip main concept to avoid overwriting)
            main_filename = sanitize_filename(topic)
            for concept in concepts:
                concept_filename = sanitize_filename(concept.name)
                # Skip if this would overwrite the main topic page
                if concept_filename == main_filename:
                    continue

                concept_file = output_path / f"{concept_filename}.md"
                concept_markdown = concept.to_markdown_page()

                # Add relationships involving this concept
                concept_relationships = [
                    r
                    for r in relationships
                    if r.source == concept.name or r.target == concept.name
                ]

                if concept_relationships:
                    concept_markdown += "\n## Relationships\n\n"
                    for rel in concept_relationships:
                        concept_markdown += f"- {rel.to_markdown()}\n"

                concept_file.write_text(concept_markdown, encoding="utf-8")

            logger.info(f"Generated markdown at {main_file}")

            return {
                "markdown_output": markdown_content,
                "output_path": str(main_file),
                "step_count": increment_step_count(state),
            }

        except Exception as e:
            error_msg = f"Markdown generation failed: {str(e)}"
            logger.error(error_msg)
            return {
                "errors": [error_msg],
                "markdown_output": "",
                "output_path": "",
                "step_count": increment_step_count(state),
            }

    return generate_markdown_node
