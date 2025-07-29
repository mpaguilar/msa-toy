"""Unit tests for the Wikipedia tool adapter."""

from unittest.mock import patch, MagicMock
from msa.tools.wikipedia import WikipediaTool
from msa.tools.base import ToolResponse
from msa.tools.cache import CacheManager
from msa.tools.rate_limiter import RateLimiter, RateLimitConfig


def test_wikipedia_tool_initialization_with_cache():
    """Test WikipediaTool initialization with custom cache manager."""
    cache_manager = CacheManager()
    tool = WikipediaTool(cache_manager=cache_manager)

    assert hasattr(tool, "retriever")
    assert tool.retriever is not None
    assert tool.cache_manager == cache_manager
    assert isinstance(tool.cache_manager, CacheManager)
    assert isinstance(tool.rate_limiter, RateLimiter)


def test_wikipedia_tool_initialization_with_rate_limiter():
    """Test WikipediaTool initialization with custom rate limiter."""
    config = RateLimitConfig(requests_per_second=1.0, bucket_capacity=5)
    rate_limiter = RateLimiter(config)
    tool = WikipediaTool(rate_limiter=rate_limiter)

    assert hasattr(tool, "retriever")
    assert tool.retriever is not None
    assert tool.rate_limiter == rate_limiter
    assert isinstance(tool.rate_limiter, RateLimiter)


@patch("msa.tools.wikipedia.WikipediaRetriever")
def test_wikipedia_tool_execute_success(mock_retriever_class):
    """Test WikipediaTool execute method with successful search."""
    # Setup mock
    mock_document = MagicMock()
    mock_document.page_content = "This is a test Wikipedia page content."
    mock_document.metadata = {"title": "Test Page"}

    mock_retriever_instance = MagicMock()
    mock_retriever_instance.get_relevant_documents.return_value = [mock_document]
    mock_retriever_class.return_value = mock_retriever_instance

    # Create tool and execute
    tool = WikipediaTool()
    response = tool.execute("test query")

    # Verify response
    assert isinstance(response, ToolResponse)
    assert "This is a test Wikipedia page content." in response.content
    assert "## Result 1: Test Page" in response.content
    assert response.metadata["results_count"] == 1
    assert "Test Page" in response.metadata["sources"]
    assert response.raw_response["query"] == "test query"


@patch("msa.tools.wikipedia.WikipediaRetriever")
def test_wikipedia_tool_execute_no_results(mock_retriever_class):
    """Test WikipediaTool execute method with no results."""
    # Setup mock
    mock_retriever_instance = MagicMock()
    mock_retriever_instance.get_relevant_documents.return_value = []
    mock_retriever_class.return_value = mock_retriever_instance

    # Create tool and execute
    tool = WikipediaTool()
    response = tool.execute("nonexistent query")

    # Verify response
    assert isinstance(response, ToolResponse)
    assert response.content == "No results found on Wikipedia."
    assert response.metadata["results_count"] == 0
    assert "sources" not in response.metadata


@patch("msa.tools.wikipedia.WikipediaRetriever")
def test_wikipedia_tool_execute_exception(mock_retriever_class):
    """Test WikipediaTool execute method with exception."""
    # Setup mock to raise exception
    mock_retriever_instance = MagicMock()
    mock_retriever_instance.get_relevant_documents.side_effect = Exception(
        "Network error"
    )
    mock_retriever_class.return_value = mock_retriever_instance

    # Create tool and execute
    tool = WikipediaTool()
    response = tool.execute("exception test query")

    # Verify response
    assert isinstance(response, ToolResponse)
    assert "Error searching Wikipedia" in response.content
    assert response.metadata["error"] is True


def test_wikipedia_tool_validate_response_valid():
    """Test WikipediaTool validate_response method with valid response."""
    tool = WikipediaTool()

    # Valid response with documents
    valid_response = {
        "documents": [{"page_content": "Test content", "metadata": {"title": "Test"}}]
    }

    assert tool.validate_response(valid_response) is True

    # Valid response with content
    valid_response2 = {"content": "Test content"}

    assert tool.validate_response(valid_response2) is True


def test_wikipedia_tool_validate_response_invalid():
    """Test WikipediaTool validate_response method with invalid response."""
    tool = WikipediaTool()

    # Invalid response - not a dict
    assert tool.validate_response("not a dict") is False

    # Invalid response - error response
    invalid_response = {"error": "Something went wrong"}

    assert tool.validate_response(invalid_response) is False

    # Invalid response - malformed documents
    invalid_response2 = {"documents": "not a list"}

    assert tool.validate_response(invalid_response2) is False

    # Invalid response - document missing page_content
    invalid_response3 = {
        "documents": [
            {
                "metadata": {"title": "Test"}
                # Missing page_content
            }
        ]
    }

    assert tool.validate_response(invalid_response3) is False


@patch("msa.tools.wikipedia.WikipediaRetriever")
@patch("msa.tools.cache.CacheManager.get")
def test_wikipedia_tool_execute_with_cache_hit(mock_cache_get, mock_retriever_class):
    """Test WikipediaTool execute method with cache hit."""
    # Setup cache mock to return cached result
    cached_response = {
        "content": "Cached Wikipedia content",
        "metadata": {"results_count": 1},
        "raw_response": {"query": "test query"}
    }
    mock_cache_get.return_value = cached_response

    # Create tool and execute
    tool = WikipediaTool()
    response = tool.execute("test query")

    # Verify response comes from cache
    assert isinstance(response, ToolResponse)
    assert response.content == "Cached Wikipedia content"
    assert response.metadata["results_count"] == 1
    mock_cache_get.assert_called_once()
    # Note: WikipediaRetriever is instantiated during __init__, so it will be called
    # We're testing that it's not called during execute when cache hit occurs
    # Check that get_relevant_documents was not called
    mock_retriever_class.return_value.get_relevant_documents.assert_not_called()


@patch("msa.tools.wikipedia.WikipediaRetriever")
@patch("msa.tools.cache.CacheManager.get")
@patch("msa.tools.cache.CacheManager.set")
def test_wikipedia_tool_execute_with_cache_miss(mock_cache_set, mock_cache_get, mock_retriever_class):
    """Test WikipediaTool execute method with cache miss."""
    # Setup cache mock to return None (cache miss)
    mock_cache_get.return_value = None
    
    # Setup retriever mock
    mock_document = MagicMock()
    mock_document.page_content = "Fresh Wikipedia content."
    mock_document.metadata = {"title": "Fresh Page"}
    mock_retriever_instance = MagicMock()
    mock_retriever_instance.get_relevant_documents.return_value = [mock_document]
    mock_retriever_class.return_value = mock_retriever_instance

    # Create tool and execute
    tool = WikipediaTool()
    response = tool.execute("fresh query")

    # Verify response comes from fresh search and is cached
    assert isinstance(response, ToolResponse)
    assert "Fresh Wikipedia content." in response.content
    assert response.metadata["results_count"] == 1
    mock_cache_get.assert_called_once()
    mock_cache_set.assert_called_once()
