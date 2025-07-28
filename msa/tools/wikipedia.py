"""Wikipedia tool adapter for the multi-step agent."""

import logging

from langchain_community.retrievers import WikipediaRetriever

from msa.tools.base import ToolInterface, ToolResponse

log = logging.getLogger(__name__)


class WikipediaTool(ToolInterface):
    """Wikipedia search tool implementation."""

    def __init__(self) -> None:
        """Initialize Wikipedia tool."""
        self.retriever = WikipediaRetriever()
        _msg = "WikipediaTool initialized"
        log.debug(_msg)

    def execute(self, query: str) -> ToolResponse:
        """Execute Wikipedia search.

        Args:
            query: The query string to search for on Wikipedia

        Returns:
            ToolResponse: Standardized response containing Wikipedia search results
        """
        _msg = f"WikipediaTool executing query: {query}"
        log.debug(_msg)

        try:
            # Execute Wikipedia search
            documents = self.retriever.get_relevant_documents(query)

            # Process results into content string
            if not documents:
                content = "No results found on Wikipedia."
                metadata = {"results_count": 0}
            else:
                # Combine the page content from all documents
                content_parts = []
                for i, doc in enumerate(documents):
                    content_parts.append(f"Result {i + 1}:\n{doc.page_content}")

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

    def validate_response(self, response: dict) -> bool:
        """Validate Wikipedia response.

        Args:
            response: The raw response dictionary to validate

        Returns:
            bool: True if response is valid, False otherwise
        """
        _msg = "WikipediaTool validating response"
        log.debug(_msg)

        # Check if response has the required structure
        if not isinstance(response, dict):
            return False

        # For Wikipedia responses, we expect either documents or an error
        if "error" in response:
            return False  # Error responses are not valid

        if "documents" in response:
            # Check if documents is a list
            if not isinstance(response["documents"], list):
                return False

            # If we have documents, they should have page_content
            for doc in response["documents"]:
                if not isinstance(doc, dict) or "page_content" not in doc:
                    return False

            return True

        # If we have content, check if it's a string
        if "content" in response and isinstance(response["content"], str):
            return True

        return False
