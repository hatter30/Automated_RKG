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
            github_code = state.get("github_code_results", [])

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

                # Core Logic Flow section (most important for re-implementation)
                if main_concept.logic_flow:
                    lines.extend([
                        "## Core Logic Flow",
                        "",
                        main_concept.logic_flow.to_markdown(),
                    ])

                # Python Implementation section
                if main_concept.pseudocode:
                    lines.extend([
                        "## Python Implementation",
                        "",
                    ])
                    for idx, block in enumerate(main_concept.pseudocode, 1):
                        if len(main_concept.pseudocode) > 1:
                            lines.append(f"### Algorithm {idx}")
                            lines.append("")
                        lines.append(block.to_markdown())
                        lines.append("")

                # Code Examples section (from entity extraction - may not be accurate)
                if main_concept.code_snippets:
                    lines.extend([
                        "## Code Examples",
                        "",
                    ])
                    for idx, block in enumerate(main_concept.code_snippets, 1):
                        if len(main_concept.code_snippets) > 1:
                            lines.append(f"### Example {idx}")
                            lines.append("")
                        lines.append(block.to_markdown())
                        lines.append("")

            # GitHub Code Examples section (real code from GitHub)
            code_items = [item for item in github_code if item.get("type") == "code"]
            if code_items:
                lines.extend([
                    "## GitHub Code Examples",
                    "",
                    "*실제 GitHub 저장소에서 가져온 코드입니다.*",
                    "",
                ])
                for idx, item in enumerate(code_items, 1):
                    lines.append(f"### {item.get('name', f'Example {idx}')}")
                    lines.append("")
                    lines.append(f"**Repository**: [{item.get('repository', 'Unknown')}]({item.get('url', '#')})")
                    lines.append(f"**Path**: `{item.get('path', '')}`")
                    lines.append("")
                    lines.append(f"```{item.get('language', 'python')}")
                    lines.append(item.get("content", ""))
                    lines.append("```")
                    lines.append("")

            # GitHub Repositories section
            repo_items = [item for item in github_code if item.get("type") == "repository"]
            if repo_items:
                lines.extend([
                    "## Related GitHub Repositories",
                    "",
                ])
                for repo in repo_items:
                    stars = repo.get("stars", 0)
                    desc = repo.get("description", "")[:100] if repo.get("description") else ""
                    lines.append(f"- [{repo.get('full_name', '')}]({repo.get('url', '#')}) ⭐ {stars}")
                    if desc:
                        lines.append(f"  - {desc}")
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
