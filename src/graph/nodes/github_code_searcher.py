"""GitHub code search node for LangGraph workflow."""
from typing import Any
import logging
from src.models.state import ResearchState
from src.services.github_search_service import GitHubSearchService
from src.utils.state_utils import increment_step_count
from config.settings import get_settings

logger = logging.getLogger(__name__)


def create_github_code_searcher_node(github_service: GitHubSearchService):
    """
    Create a GitHub code search node function.

    Args:
        github_service: GitHub search service instance

    Returns:
        Node function for GitHub code search
    """

    def search_github_code_node(state: ResearchState) -> dict[str, Any]:
        """
        Search for code examples on GitHub.

        Args:
            state: Current research state

        Returns:
            Updated state with GitHub code results
        """
        topic = state["research_topic"]
        logger.info(f"Searching GitHub for code: {topic}")

        settings = get_settings()
        max_results = settings.max_github_code_results

        try:
            # Search for code related to the topic
            code_results = github_service.search_code(
                query=topic,
                language="python",
                max_results=max_results,
            )

            # Also search for relevant repositories
            repo_results = github_service.search_repositories(
                query=topic,
                language="python",
                max_results=2,
            )

            # Combine results
            all_results = []

            # Add code snippets
            for code in code_results:
                if code.get("content"):
                    # Limit content size to avoid huge files
                    content = code["content"]
                    if len(content) > 5000:
                        content = content[:5000] + "\n# ... (truncated)"

                    all_results.append({
                        "type": "code",
                        "name": code["name"],
                        "path": code["path"],
                        "repository": code["repository"],
                        "url": code["html_url"],
                        "content": content,
                        "language": code["language"],
                    })

            # Add repository info
            for repo in repo_results:
                all_results.append({
                    "type": "repository",
                    "name": repo["name"],
                    "full_name": repo["full_name"],
                    "description": repo["description"],
                    "url": repo["html_url"],
                    "stars": repo["stars"],
                })

            logger.info(f"Found {len(all_results)} GitHub results for: {topic}")

            return {
                "github_code_results": all_results,
                "step_count": increment_step_count(state),
            }

        except Exception as e:
            error_msg = f"GitHub code search failed: {str(e)}"
            logger.error(error_msg)
            return {
                "github_code_results": [],
                "errors": [error_msg],
                "step_count": increment_step_count(state),
            }

    return search_github_code_node
