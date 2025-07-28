"""Web search tool adapter for the multi-step agent."""

import logging
import os

from serpapi import GoogleSearch

from msa.tools.base import ToolInterface, ToolResponse

log = logging.getLogger(__name__)


class WebSearchTool(ToolInterface):
    """Web search tool implementation."""

    def __init__(self) -> None:
        """Initialize web search tool."""
        self.api_key = os.getenv("SERPAPI_API_KEY")
        if not self.api_key:
            raise ValueError("SERPAPI_API_KEY environment variable is required")

        _msg = "WebSearchTool initialized"
        log.debug(_msg)

    def execute(self, query: str) -> ToolResponse:
        """Execute web search.

        Args:
            query: The query string to search for on the web

        Returns:
            ToolResponse: Standardized response containing web search results
        """
        _msg = f"WebSearchTool executing query: {query}"
        log.debug(_msg)

        try:
            # Execute web search
            search = GoogleSearch({"q": query, "api_key": self.api_key})
            result = search.get_dict()

            # Process results into content string
            search_results = result.get("organic_results", [])
            if not search_results:
                content = "No results found on the web."
                metadata = {"results_count": 0}
            else:
                # Combine the search results into a formatted string
                content_parts = []
                for i, item in enumerate(search_results[:5]):  # Limit to top 5 results
                    title = item.get("title", "No title")
                    link = item.get("link", "No link")
                    snippet = item.get("snippet", "No snippet")
                    content_parts.append(
                        f"Result {i + 1}:\nTitle: {title}\nLink: {link}\nSnippet: {snippet}"
                    )

                content = "\n\n".join(content_parts)
                metadata = {
                    "results_count": len(search_results),
                    "sources": [
                        item.get("link", "Unknown") for item in search_results[:5]
                    ],
                }

            # Create raw response
            raw_response = result

            response = ToolResponse(
                content=content, metadata=metadata, raw_response=raw_response
            )

            _msg = f"WebSearchTool successfully executed query: {query}"
            log.debug(_msg)
            return response

        except Exception as e:
            _msg = f"Error executing WebSearchTool with query '{query}': {str(e)}"
            log.exception(_msg)

            # Return error response
            error_response = ToolResponse(
                content=f"Error searching the web: {str(e)}",
                metadata={"error": True, "results_count": 0},
                raw_response={"error": str(e)},
            )
            return error_response

    def validate_response(self, response: dict) -> bool:
        """Validate web search response.

        Args:
            response: The raw response dictionary to validate

        Returns:
            bool: True if response is valid, False otherwise
        """
        _msg = "WebSearchTool validating response"
        log.debug(_msg)

        # Check if response has the required structure
        if not isinstance(response, dict):
            return False

        # For web search responses, we expect either organic_results or an error
        if "error" in response:
            return False  # Error responses are not valid

        if "organic_results" in response:
            # Check if organic_results is a list
            if not isinstance(response["organic_results"], list):
                return False
            return True

        # If we have content, check if it's a string
        if "content" in response and isinstance(response["content"], str):
            return True

        return False
