"""Service for searching code on GitHub."""
import requests
from typing import Any
from tenacity import retry, stop_after_attempt, wait_exponential
import logging
import base64

logger = logging.getLogger(__name__)


class GitHubSearchService:
    """Service for searching code on GitHub."""

    def __init__(self, token: str | None = None):
        """
        Initialize GitHub search service.

        Args:
            token: GitHub personal access token (optional but recommended for higher rate limits)
        """
        self.token = token
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if token:
            self.headers["Authorization"] = f"Bearer {token}"

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def search_code(
        self,
        query: str,
        language: str = "python",
        max_results: int = 5,
    ) -> list[dict[str, Any]]:
        """
        Search for code on GitHub.

        Args:
            query: Search query (e.g., "quicksort algorithm")
            language: Programming language filter
            max_results: Maximum number of results to return

        Returns:
            List of code results with file content
        """
        # Build search query with language filter
        search_query = f"{query} language:{language}"

        params = {
            "q": search_query,
            "per_page": min(max_results, 30),  # GitHub max is 30 per page
            "sort": "indexed",  # Most recently indexed
        }

        try:
            response = requests.get(
                f"{self.base_url}/search/code",
                headers=self.headers,
                params=params,
                timeout=15,
            )

            # Check rate limit
            if response.status_code == 403:
                logger.warning("GitHub API rate limit exceeded")
                return []

            response.raise_for_status()
            data = response.json()

            results = []
            for item in data.get("items", [])[:max_results]:
                # Get file content
                content = self._get_file_content(item.get("url", ""))
                if content:
                    results.append({
                        "name": item.get("name", ""),
                        "path": item.get("path", ""),
                        "repository": item.get("repository", {}).get("full_name", ""),
                        "html_url": item.get("html_url", ""),
                        "content": content,
                        "language": language,
                    })

            logger.info(f"Found {len(results)} code results for: {query}")
            return results

        except Exception as e:
            logger.error(f"GitHub code search failed: {e}")
            return []

    def _get_file_content(self, api_url: str) -> str | None:
        """
        Fetch file content from GitHub API.

        Args:
            api_url: GitHub API URL for the file

        Returns:
            Decoded file content or None
        """
        if not api_url:
            return None

        try:
            response = requests.get(api_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Content is base64 encoded
            content_b64 = data.get("content", "")
            if content_b64:
                return base64.b64decode(content_b64).decode("utf-8")

        except Exception as e:
            logger.debug(f"Failed to fetch file content: {e}")

        return None

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def search_repositories(
        self,
        query: str,
        language: str = "python",
        max_results: int = 3,
    ) -> list[dict[str, Any]]:
        """
        Search for repositories on GitHub.

        Args:
            query: Search query
            language: Programming language filter
            max_results: Maximum number of results

        Returns:
            List of repository information
        """
        search_query = f"{query} language:{language}"

        params = {
            "q": search_query,
            "per_page": min(max_results, 10),
            "sort": "stars",
            "order": "desc",
        }

        try:
            response = requests.get(
                f"{self.base_url}/search/repositories",
                headers=self.headers,
                params=params,
                timeout=15,
            )

            if response.status_code == 403:
                logger.warning("GitHub API rate limit exceeded")
                return []

            response.raise_for_status()
            data = response.json()

            results = []
            for item in data.get("items", [])[:max_results]:
                results.append({
                    "name": item.get("name", ""),
                    "full_name": item.get("full_name", ""),
                    "description": item.get("description", ""),
                    "html_url": item.get("html_url", ""),
                    "stars": item.get("stargazers_count", 0),
                    "language": item.get("language", ""),
                })

            logger.info(f"Found {len(results)} repositories for: {query}")
            return results

        except Exception as e:
            logger.error(f"GitHub repository search failed: {e}")
            return []

    def get_readme(self, owner: str, repo: str) -> str | None:
        """
        Get README content from a repository.

        Args:
            owner: Repository owner
            repo: Repository name

        Returns:
            README content or None
        """
        try:
            response = requests.get(
                f"{self.base_url}/repos/{owner}/{repo}/readme",
                headers=self.headers,
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()

            content_b64 = data.get("content", "")
            if content_b64:
                return base64.b64decode(content_b64).decode("utf-8")

        except Exception as e:
            logger.debug(f"Failed to fetch README: {e}")

        return None
