"""Web search node for LangGraph workflow."""
from typing import Any
import logging
from src.models.state import ResearchState
from src.services.brave_search_service import BraveSearchService
from src.utils.state_utils import increment_step_count

logger = logging.getLogger(__name__)


def create_web_searcher_node(brave_service: BraveSearchService):
    """
    Create a web searcher node function.

    Args:
        brave_service: Brave Search service instance

    Returns:
        Node function for web searching
    """

    def search_web_node(state: ResearchState) -> dict[str, Any]:
        """
        Execute web searches for all generated queries.

        Args:
            state: Current research state

        Returns:
            Updated state with search_results populated
        """
        logger.info(f"Searching web for {len(state['search_queries'])} queries")

        all_results: list[dict[str, Any]] = []
        errors: list[str] = []

        for query in state["search_queries"]:
            try:
                results = brave_service.search(query)
                all_results.extend(results)
                logger.info(f"Query '{query}' returned {len(results)} results")
            except Exception as e:
                error_msg = f"Search failed for query '{query}': {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)

        logger.info(f"Total search results collected: {len(all_results)}")

        return {
            "search_results": all_results,
            "errors": errors,
            "step_count": increment_step_count(state),
        }

    return search_web_node
