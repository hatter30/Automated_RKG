"""Utilities for formatting prompts and search results."""


def format_search_results(
    results: list[dict], limit: int | None = None
) -> str:
    """
    Format search results for use in LLM prompts.

    Args:
        results: List of search result dictionaries with 'title', 'url', 'description'
        limit: Optional limit on number of results to format

    Returns:
        Formatted string of search results
    """
    if limit:
        results = results[:limit]

    formatted = []
    for result in results:
        formatted.append(
            f"Source: {result.get('title', 'No title')}\n"
            f"URL: {result.get('url', 'No URL')}\n"
            f"Content: {result.get('description', 'No description')}"
        )

    return "\n\n".join(formatted)
