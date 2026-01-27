"""Service for interacting with Brave Search API."""
import requests
from typing import List, Dict, Optional, Any
from tenacity import retry, stop_after_attempt, wait_exponential
import logging

logger = logging.getLogger(__name__)


class BraveSearchService:
    """Service for interacting with Brave Search API."""

    def __init__(self, api_key: str, max_results: int = 10):
        self.api_key = api_key
        self.max_results = max_results
        self.base_url = "https://api.search.brave.com/res/v1/web/search"

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def search(self, query: str, count: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Execute a search query and return results.

        Args:
            query: Search query string
            count: Number of results to return (uses max_results if not specified)

        Returns:
            List of dicts with keys: title, url, description, query
        """
        headers = {"Accept": "application/json", "X-Subscription-Token": self.api_key}

        params = {"q": query, "count": count or self.max_results}

        try:
            response = requests.get(self.base_url, headers=headers, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            results = []

            for item in data.get("web", {}).get("results", []):
                results.append(
                    {
                        "title": item.get("title", ""),
                        "url": item.get("url", ""),
                        "description": item.get("description", ""),
                        "query": query,  # Track which query produced this result
                    }
                )

            logger.info(f"Found {len(results)} results for query: {query}")
            return results

        except Exception as e:
            logger.error(f"Search failed for query '{query}': {e}")
            raise
