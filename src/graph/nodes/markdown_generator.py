"""Markdown generation node for LangGraph workflow."""
from typing import Dict, Any
import logging
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from src.models.state import ResearchState
from src.utils.markdown_utils import sanitize_filename

logger = logging.getLogger(__name__)


def create_markdown_generator_node(output_dir: str):
    """
    Create a markdown generator node function.

    Args:
        output_dir: Directory to write output files

    Returns:
        Node function for markdown generation
    """

    def generate_markdown_node(state: ResearchState) -> Dict[str, Any]:
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

            # Build markdown content
            lines = [
                f"# {topic}",
                "",
                f"*Research conducted: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}*",
                "",
                "## Overview",
                f"This knowledge graph was automatically generated for the research topic: **{topic}**",
                "",
                "## Key Concepts",
                "",
            ]

            # Group concepts by type
            concepts_by_type = defaultdict(list)
            for concept in concepts:
                concepts_by_type[concept.concept_type].append(concept)

            for concept_type, concept_list in sorted(concepts_by_type.items()):
                lines.append(f"### {concept_type.value.title()}s")
                for concept in sorted(concept_list, key=lambda c: c.name):
                    lines.append(f"- {concept.to_wikilink()}")
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

            # Write individual concept pages
            for concept in concepts:
                concept_file = output_path / f"{sanitize_filename(concept.name)}.md"
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
                "step_count": state.get("step_count", 0) + 1,
            }

        except Exception as e:
            error_msg = f"Markdown generation failed: {str(e)}"
            logger.error(error_msg)
            return {
                "errors": [error_msg],
                "markdown_output": "",
                "output_path": "",
                "step_count": state.get("step_count", 0) + 1,
            }

    return generate_markdown_node
