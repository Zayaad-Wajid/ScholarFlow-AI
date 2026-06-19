"""External research search service."""

from typing import Any

import requests

from app.core.config import settings

TAVILY_SEARCH_URL = "https://api.tavily.com/search"
VALID_SEARCH_DEPTHS = {"basic", "advanced"}


class ExternalSearchError(Exception):
    """Raised when an external search provider fails."""


def _normalize_tavily_result(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "title": str(item.get("title") or "Untitled result"),
        "url": str(item.get("url") or "").strip(),
        "snippet": str(item.get("content") or "").strip() or None,
        "score": float(item["score"]) if item.get("score") is not None else None,
        "source_name": str(item.get("source") or "").strip() or None,
        "published_date": str(item.get("published_date") or "").strip() or None,
    }


def tavily_search(
    query: str,
    *,
    max_results: int | None = None,
    search_depth: str = "advanced",
) -> list[dict[str, Any]]:
    api_key = (settings.tavily_api_key or "").strip()
    if not api_key:
        raise ExternalSearchError("TAVILY_API_KEY is not configured")

    query_text = query.strip()
    if not query_text:
        raise ValueError("Query cannot be empty")

    limit = max_results or settings.tavily_max_results
    depth = search_depth if search_depth in VALID_SEARCH_DEPTHS else "advanced"

    payload = {
        "api_key": api_key,
        "query": query_text,
        "topic": "general",
        "search_depth": depth,
        "max_results": limit,
        "include_answer": False,
        "include_raw_content": False,
    }

    try:
        response = requests.post(TAVILY_SEARCH_URL, json=payload, timeout=20)
        response.raise_for_status()
    except requests.HTTPError as exc:
        detail = "Tavily search failed"
        try:
            data = response.json()
            detail = str(data.get("detail") or data.get("message") or detail)
        except ValueError:
            pass
        raise ExternalSearchError(detail) from exc
    except requests.RequestException as exc:
        raise ExternalSearchError("Failed to reach Tavily search service") from exc

    try:
        data = response.json()
    except ValueError as exc:
        raise ExternalSearchError("Tavily returned an invalid response") from exc

    normalized_results = []
    for item in data.get("results") or []:
        result = _normalize_tavily_result(item)
        if result["url"]:
            normalized_results.append(result)

    return normalized_results
