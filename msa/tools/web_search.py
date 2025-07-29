"""Web search tool adapter for the multi-step agent."""

import logging
import os
from typing import Optional

from serpapi import GoogleSearch

from msa.tools.base import ToolInterface, ToolResponse
from msa.tools.cache import CacheManager
from msa.tools.rate_limiter import RateLimiter, RateLimitConfig

log = logging.getLogger(__name__)


class WebSearchTool(ToolInterface):
    """Web search tool implementation."""

    def __init__(self, cache_manager: CacheManager = None, rate_limiter: RateLimiter = None) -> None:
        """Initialize web search tool.
        
        Args:
            cache_manager: Optional cache manager for caching results
            rate_limiter: Optional rate limiter for API compliance
        """
        _msg = "WebSearchTool.__init__ starting"
        log.debug(_msg)
        
        self.api_key = os.getenv("SERPAPI_API_KEY")
        if not self.api_key:
            raise ValueError("SERPAPI_API_KEY environment variable is required")
        
        self.cache_manager = cache_manager or CacheManager()
        self.rate_limiter = rate_limiter or self._create_default_rate_limiter()

        _msg = "WebSearchTool.__init__ returning"
        log.debug(_msg)
        
    def _create_default_rate_limiter(self) -> RateLimiter:
        """Create a default rate limiter for web searches.
        
        Returns:
            RateLimiter: Configured rate limiter instance
        """
        _msg = "WebSearchTool._create_default_rate_limiter starting"
        log.debug(_msg)
        
        # Default to 10 requests per second with a bucket capacity of 20
        config = RateLimitConfig(
            requests_per_second=10.0,
            bucket_capacity=20
        )
        rate_limiter = RateLimiter(config)
        
        _msg = "WebSearchTool._create_default_rate_limiter returning"
        log.debug(_msg)
        return rate_limiter

    def execute(self, query: str) -> ToolResponse:
        """Execute web search with rate limiting.

        Args:
            query: The query string to search for on the web

        Returns:
            ToolResponse: Standardized response containing web search results
        """
        _msg = f"WebSearchTool.execute starting with query: {query}"
        log.debug(_msg)

        def _perform_search() -> ToolResponse:
            # Check cache first
            cache_key = f"web_search_{self.cache_manager.normalize_query(query)}"
            cached_result = self.cache_manager.get(cache_key)
            if cached_result:
                _msg = "WebSearchTool returning cached result"
                log.debug(_msg)
                return ToolResponse(**cached_result)

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

                # Cache the result
                self.cache_manager.set(cache_key, response.dict())

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

        # Execute with rate limiting
        result = self.rate_limiter.queue_request("serpapi", _perform_search)
        
        _msg = "WebSearchTool.execute returning"
        log.debug(_msg)
        return result

    def validate_response(self, response: dict) -> bool:
        """Validate web search response.

        Args:
            response: The raw response dictionary to validate

        Returns:
            bool: True if response is valid, False otherwise
        """
        _msg = "WebSearchTool.validate_response starting"
        log.debug(_msg)

        # Check if response has the required structure
        if not isinstance(response, dict):
            _msg = "WebSearchTool.validate_response returning False (not dict)"
            log.debug(_msg)
            return False

        # For web search responses, we expect either organic_results or an error
        if "error" in response:
            _msg = "WebSearchTool.validate_response returning False (error in response)"
            log.debug(_msg)
            return False  # Error responses are not valid

        if "organic_results" in response:
            # Check if organic_results is a list
            if not isinstance(response["organic_results"], list):
                _msg = "WebSearchTool.validate_response returning False (organic_results not list)"
                log.debug(_msg)
                return False
            _msg = "WebSearchTool.validate_response returning True (valid organic_results)"
            log.debug(_msg)
            return True

        # If we have content, check if it's a string
        if "content" in response and isinstance(response["content"], str):
            _msg = "WebSearchTool.validate_response returning True (valid content)"
            log.debug(_msg)
            return True

        _msg = "WebSearchTool.validate_response returning False (no valid content)"
        log.debug(_msg)
        return False
