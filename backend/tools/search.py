"""Tavily web search wrapper."""

from __future__ import annotations

from typing import Any

from config import TAVILY_API_KEY


class TavilySearchTool:
    """Graceful Tavily client with an offline fallback."""

    def __init__(self) -> None:
        self.client: Any | None = None
        if TAVILY_API_KEY:
            try:
                from tavily import TavilyClient

                self.client = TavilyClient(api_key=TAVILY_API_KEY)
            except Exception:
                self.client = None

    def search(self, query: str, max_results: int = 3) -> list[dict[str, str]]:
        """Search Tavily or return a clear unavailable response."""
        if not self.client:
            return [
                {
                    "title": "Search unavailable",
                    "url": "",
                    "content": "Search unavailable - set TAVILY_API_KEY",
                }
            ]
        try:
            response = self.client.search(query=query, max_results=max_results)
            results = response.get("results", [])
            return [
                {
                    "title": str(item.get("title", "Untitled")),
                    "url": str(item.get("url", "")),
                    "content": str(item.get("content", "")),
                }
                for item in results[:max_results]
            ]
        except Exception as exc:
            return [{"title": "Search error", "url": "", "content": str(exc)}]

