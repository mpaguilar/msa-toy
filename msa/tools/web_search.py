"""Web search tool adapter for the multi-step agent."""

import logging
import os

from serpapi import GoogleSearch

from msa.tools.base import ToolInterface, ToolResponse
from msa.tools.cache import CacheManager
from msa.tools.rate_limiter import RateLimitConfig, RateLimiter

log = logging.getLogger(__name__)


class WebSearchTool(ToolInterface):
    """Web search tool implementation."""

    def __init__(
        self,
        cache_manager: CacheManager = None,
        rate_limiter: RateLimiter = None,
    ) -> None:
        """Initialize web search tool.

        Args:
            cache_manager: Optional cache manager for caching results
            rate_limiter: Optional rate limiter for API compliance

        Notes:
            1. Retrieves the SERPAPI API key from the environment variable SERPER_API_KEY.
            2. Initializes the cache manager using the provided instance or creates a default CacheManager.
            3. Initializes the rate limiter using the provided instance or creates a default RateLimiter.
            4. Logs the start and end of initialization.

        """
        _msg = "WebSearchTool.__init__ starting"
        log.debug(_msg)

        self.api_key = os.getenv("SERPER_API_KEY")

        self.cache_manager = cache_manager or CacheManager()
        self.rate_limiter = rate_limiter or self._create_default_rate_limiter()

        _msg = "WebSearchTool.__init__ returning"
        log.debug(_msg)

    def _create_default_rate_limiter(self) -> RateLimiter:
        """Create a default rate limiter for web searches.

        Returns:
            RateLimiter: Configured rate limiter instance

        Notes:
            1. Creates a RateLimitConfig with 10 requests per second and a bucket capacity of 20.
            2. Instantiates a RateLimiter using the created config.
            3. Returns the configured RateLimiter instance.

        """
        _msg = "WebSearchTool._create_default_rate_limiter starting"
        log.debug(_msg)

        # Default to 10 requests per second with a bucket capacity of 20
        config = RateLimitConfig(requests_per_second=10.0, bucket_capacity=20)
        rate_limiter = RateLimiter(config)

        _msg = "WebSearchTool._create_default_rate_limiter returning"
        log.debug(_msg)
        return rate_limiter

    def execute(self, query: str) -> ToolResponse:
        """Execute web search with rate limiting.

        Args:
            query: The query string to search for on the web

        Returns:
            ToolResponse: Standardized response containing web search results.
                - If successful: content contains formatted results, metadata includes count and sources.
                - If API key missing: content contains error message, metadata indicates error.
                - If an exception occurs: content contains error message, metadata indicates error.

        Notes:
            1. Checks for the presence of the SERPAPI_KEY environment variable.
            2. If API key is missing, returns an error ToolResponse.
            3. Uses the cache manager to check if a result exists for the normalized query.
            4. If cached result exists, returns it directly.
            5. Otherwise, performs the web search using the SERPAPI client.
            6. Processes the search results into a formatted content string.
            7. Limits results to the top 5 and formats each result with title, link, and snippet.
            8. Constructs a ToolResponse with content, metadata (results count, sources), and raw response.
            9. Caches the response using the cache manager.
            10. Returns the constructed ToolResponse.

        """
        _msg = f"WebSearchTool.execute starting with query: {query}"
        log.debug(_msg)

        def _perform_search() -> ToolResponse:
            # Check if API key is available
            if not self.api_key:
                error_msg = (
                    "SERPAPI_KEY environment variable is required for web search"
                )
                _msg = f"WebSearchTool error: {error_msg}"
                log.error(_msg)

                # Return error response
                error_response = ToolResponse(
                    content=f"Error searching the web: {error_msg}",
                    metadata={"error": True, "results_count": 0},
                    raw_response={"error": error_msg},
                )
                return error_response

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
                    for i, item in enumerate(
                        search_results[:5],
                    ):  # Limit to top 5 results
                        title = item.get("title", "No title")
                        link = item.get("link", "No link")
                        snippet = item.get("snippet", "No snippet")
                        content_parts.append(
                            f"Result {i + 1}:\nTitle: {title}\nLink: {link}\nSnippet: {snippet}",
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
                    content=content,
                    metadata=metadata,
                    raw_response=raw_response,
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

        Notes:
            1. Checks if response is a dictionary.
            2. If response contains an "error" key, returns False.
            3. If response contains "organic_results" key, checks if it's a list; returns True if valid.
            4. If response contains "content" key and it's a string, returns True.
            5. Otherwise, returns False.

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
            return False

        if "organic_results" in response:
            # Check if organic_results is a list
            if not isinstance(response["organic_results"], list):
                _msg = "WebSearchTool.validate_response returning False (organic_results not list)"
                log.debug(_msg)
                return False
            _msg = (
                "WebSearchTool.validate_response returning True (valid organic_results)"
            )
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
