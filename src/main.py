"""Main entry point for the automated research system."""
import logging
from pathlib import Path
from config.settings import get_settings
from src.services.openai_service import OpenAIService
from src.services.brave_search_service import BraveSearchService
from src.services.concept_normalizer import ConceptNormalizer
from src.graph.workflow import create_research_workflow
from src.models.state import ResearchState
from src.utils.logging_config import setup_logging

logger = logging.getLogger(__name__)


def run_research(topic: str, output_dir: str | None = None) -> str:
    """
    Run the complete research workflow for a given topic.

    Args:
        topic: Research topic (e.g., "GNN", "Transformer Architecture")
        output_dir: Optional output directory override

    Returns:
        Path to generated markdown file
    """
    # Load settings
    settings = get_settings()
    setup_logging(settings.log_level)

    logger.info(f"Starting research workflow for topic: {topic}")

    # Initialize services
    openai_service = OpenAIService(api_key=settings.openai_api_key, model=settings.openai_model)

    brave_service = BraveSearchService(
        api_key=settings.brave_search_api_key, max_results=settings.max_search_results
    )

    normalizer = ConceptNormalizer()

    # Determine output directory
    final_output_dir = output_dir or settings.output_dir

    # Create workflow
    workflow = create_research_workflow(
        openai_service=openai_service,
        brave_service=brave_service,
        normalizer=normalizer,
        output_dir=final_output_dir,
    )

    # Initialize state
    initial_state: ResearchState = {
        "research_topic": topic,
        "search_queries": [],
        "search_results": [],
        "concepts": [],
        "relationships": [],
        "markdown_output": "",
        "output_path": "",
        "errors": [],
        "step_count": 0,
    }

    try:
        # Execute workflow
        logger.info("Executing research workflow...")
        final_state = workflow.invoke(initial_state)

        logger.info(f"Research completed in {final_state['step_count']} steps")

        if final_state["errors"]:
            logger.warning(f"Encountered {len(final_state['errors'])} errors:")
            for error in final_state["errors"]:
                logger.warning(f"  - {error}")

        output_path = final_state["output_path"]
        logger.info(f"Output generated at: {output_path}")

        return output_path

    except Exception as e:
        logger.error(f"Research workflow failed: {e}")
        raise


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Automated Research & Knowledge Graph Generator")
    parser.add_argument("topic", type=str, help="Research topic to investigate")
    parser.add_argument(
        "--output-dir", type=str, default=None, help="Output directory for generated files"
    )

    args = parser.parse_args()

    try:
        output_path = run_research(args.topic, args.output_dir)
        print(f"\nResearch complete!")
        print(f"Output: {output_path}")
    except Exception as e:
        print(f"\nError: {e}")
        exit(1)


if __name__ == "__main__":
    main()
