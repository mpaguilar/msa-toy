"""Wikipedia tool adapter for the multi-step agent."""

import logging
from typing import Optional

from langchain_community.retrievers import WikipediaRetriever

from msa.tools.base import ToolInterface, ToolResponse
from msa.tools.cache import CacheManager
from msa.tools.rate_limiter import RateLimiter, RateLimitConfig

log = logging.getLogger(__name__)


class WikipediaTool(ToolInterface):
    """Wikipedia search tool implementation."""

    def __init__(self, cache_manager: CacheManager = None, rate_limiter: RateLimiter = None) -> None:
        """Initialize Wikipedia tool.
        
        Args:
            cache_manager: Optional cache manager for caching results
            rate_limiter: Optional rate limiter for API compliance
        """
        _msg = "WikipediaTool.__init__ starting"
        log.debug(_msg)
        
        self.retriever = WikipediaRetriever()
        self.cache_manager = cache_manager or CacheManager()
        self.rate_limiter = rate_limiter or self._create_default_rate_limiter()
        
        _msg = "WikipediaTool.__init__ returning"
        log.debug(_msg)
        
    def _create_default_rate_limiter(self) -> RateLimiter:
        """Create a default rate limiter for Wikipedia searches.
        
        Returns:
            RateLimiter: Configured rate limiter instance
        """
        _msg = "WikipediaTool._create_default_rate_limiter starting"
        log.debug(_msg)
        
        # Default to 5 requests per second with a bucket capacity of 10
        config = RateLimitConfig(
            requests_per_second=5.0,
            bucket_capacity=10
        )
        rate_limiter = RateLimiter(config)
        
        _msg = "WikipediaTool._create_default_rate_limiter returning"
        log.debug(_msg)
        return rate_limiter

    def execute(self, query: str) -> ToolResponse:
        """Execute Wikipedia search with rate limiting.

        Args:
            query: The query string to search for on Wikipedia

        Returns:
            ToolResponse: Standardized response containing Wikipedia search results
        """
        _msg = f"WikipediaTool.execute starting with query: {query}"
        log.debug(_msg)

        def _perform_search() -> ToolResponse:
            # Check cache first
            cache_key = f"wikipedia_{self.cache_manager.normalize_query(query)}"
            cached_result = self.cache_manager.get(cache_key)
            if cached_result:
                _msg = "WikipediaTool returning cached result"
                log.debug(_msg)
                return ToolResponse(**cached_result)

            try:
                # Execute Wikipedia search
                documents = self.retriever.get_relevant_documents(query)

                # Process results into content string
                if not documents:
                    content = "No results found on Wikipedia."
                    metadata = {"results_count": 0}
                else:
                    # Combine the page content from all documents in Markdown format
                    content_parts = []
                    for i, doc in enumerate(documents):
                        title = doc.metadata.get("title", "Unknown")
                        content_parts.append(f"## Result {i + 1}: {title}\n\n{doc.page_content}")

                    content = "\n\n".join(content_parts)
                    metadata = {
                        "results_count": len(documents),
                        "sources": [
                            doc.metadata.get("title", "Unknown") for doc in documents
                        ],
                    }

                # Create raw response
                raw_response = {
                    "query": query,
                    "documents": [
                        {"page_content": doc.page_content, "metadata": doc.metadata}
                        for doc in documents
                    ],
                }

                response = ToolResponse(
                    content=content, metadata=metadata, raw_response=raw_response
                )

                # Cache the result
                self.cache_manager.set(cache_key, response.model_dump())

                _msg = f"WikipediaTool successfully executed query: {query}"
                log.debug(_msg)
                return response

            except Exception as e:
                _msg = f"Error executing WikipediaTool with query '{query}': {str(e)}"
                log.exception(_msg)

                # Return error response
                error_response = ToolResponse(
                    content=f"Error searching Wikipedia: {str(e)}",
                    metadata={"error": True, "results_count": 0},
                    raw_response={"error": str(e)},
                )
                return error_response

        # Execute with rate limiting
        result = self.rate_limiter.queue_request("wikipedia", _perform_search)
        
        _msg = "WikipediaTool.execute returning"
        log.debug(_msg)
        return result

    def validate_response(self, response: dict) -> bool:
        """Validate Wikipedia response.

        Args:
            response: The raw response dictionary to validate

        Returns:
            bool: True if response is valid, False otherwise
        """
        _msg = "WikipediaTool.validate_response starting"
        log.debug(_msg)

        # Check if response has the required structure
        if not isinstance(response, dict):
            _msg = "WikipediaTool.validate_response returning False (not dict)"
            log.debug(_msg)
            return False

        # For Wikipedia responses, we expect either documents or an error
        if "error" in response:
            _msg = "WikipediaTool.validate_response returning False (error in response)"
            log.debug(_msg)
            return False  # Error responses are not valid

        if "documents" in response:
            # Check if documents is a list
            if not isinstance(response["documents"], list):
                _msg = "WikipediaTool.validate_response returning False (documents not list)"
                log.debug(_msg)
                return False

            # If we have documents, they should have page_content
            for doc in response["documents"]:
                if not isinstance(doc, dict) or "page_content" not in doc:
                    _msg = "WikipediaTool.validate_response returning False (missing page_content)"
                    log.debug(_msg)
                    return False

            _msg = "WikipediaTool.validate_response returning True (valid documents)"
            log.debug(_msg)
            return True

        # If we have content, check if it's a string
        if "content" in response and isinstance(response["content"], str):
            _msg = "WikipediaTool.validate_response returning True (valid content)"
            log.debug(_msg)
            return True

        _msg = "WikipediaTool.validate_response returning False (no valid content)"
        log.debug(_msg)
        return False
