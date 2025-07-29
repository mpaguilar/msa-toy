"""Unit tests for the Web Search tool adapter."""

import os
import pytest
from unittest.mock import patch, MagicMock
from msa.tools.web_search import WebSearchTool
from msa.tools.base import ToolResponse
from msa.tools.cache import CacheManager
from msa.tools.rate_limiter import RateLimiter, RateLimitConfig


def test_web_search_tool_initialization_with_cache():
    """Test WebSearchTool initialization with custom cache manager."""
    with patch.dict(os.environ, {"SERPAPI_API_KEY": "test-key"}):
        cache_manager = CacheManager()
        tool = WebSearchTool(cache_manager=cache_manager)
        assert tool.api_key == "test-key"
        assert tool.cache_manager == cache_manager
        assert isinstance(tool.cache_manager, CacheManager)
        assert isinstance(tool.rate_limiter, RateLimiter)


def test_web_search_tool_initialization_with_rate_limiter():
    """Test WebSearchTool initialization with custom rate limiter."""
    with patch.dict(os.environ, {"SERPAPI_API_KEY": "test-key"}):
        config = RateLimitConfig(requests_per_second=1.0, bucket_capacity=5)
        rate_limiter = RateLimiter(config)
        tool = WebSearchTool(rate_limiter=rate_limiter)
        assert tool.api_key == "test-key"
        assert tool.rate_limiter == rate_limiter
        assert isinstance(tool.rate_limiter, RateLimiter)


def test_web_search_tool_initialization_failure():
    """Test failure when SERPAPI_API_KEY is not set."""
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(
            ValueError, match="SERPAPI_API_KEY environment variable is required"
        ):
            WebSearchTool()


@patch("msa.tools.web_search.GoogleSearch")
def test_web_search_tool_execute_success(mock_google_search):
    """Test WebSearchTool execute method with successful search."""
    # Setup mock
    mock_response = {
        "organic_results": [
            {
                "title": "Test Result 1",
                "link": "https://example.com/1",
                "snippet": "This is test result 1",
            },
            {
                "title": "Test Result 2",
                "link": "https://example.com/2",
                "snippet": "This is test result 2",
            },
        ]
    }

    mock_search_instance = MagicMock()
    mock_search_instance.get_dict.return_value = mock_response
    mock_google_search.return_value = mock_search_instance

    # Create tool and execute
    with patch.dict(os.environ, {"SERPAPI_API_KEY": "test-key"}):
        tool = WebSearchTool()
        response = tool.execute("test query")

    # Verify response
    assert isinstance(response, ToolResponse)
    assert "Test Result 1" in response.content
    assert "Test Result 2" in response.content
    assert response.metadata["results_count"] == 2
    assert "https://example.com/1" in response.metadata["sources"]
    assert response.raw_response["organic_results"][0]["title"] == "Test Result 1"


@patch("msa.tools.web_search.GoogleSearch")
def test_web_search_tool_execute_no_results(mock_google_search):
    """Test WebSearchTool execute method with no results."""
    # Setup mock
    mock_response = {"organic_results": []}

    mock_search_instance = MagicMock()
    mock_search_instance.get_dict.return_value = mock_response
    mock_google_search.return_value = mock_search_instance

    # Create tool and execute
    with patch.dict(os.environ, {"SERPAPI_API_KEY": "test-key"}):
        tool = WebSearchTool()
        response = tool.execute("nonexistent query")

    # Verify response
    assert isinstance(response, ToolResponse)
    assert response.content == "No results found on the web."
    assert response.metadata["results_count"] == 0
    assert "sources" not in response.metadata


@patch("msa.tools.web_search.GoogleSearch")
def test_web_search_tool_execute_exception(mock_google_search):
    """Test WebSearchTool execute method with exception."""
    # Setup mock to raise exception
    mock_search_instance = MagicMock()
    mock_search_instance.get_dict.side_effect = Exception("Network error")
    mock_google_search.return_value = mock_search_instance

    # Create tool and execute
    with patch.dict(os.environ, {"SERPAPI_API_KEY": "test-key"}):
        tool = WebSearchTool()
        response = tool.execute("exception test query")

    # Verify response
    assert isinstance(response, ToolResponse)
    assert "Error searching the web" in response.content
    assert response.metadata["error"] is True


def test_web_search_tool_validate_response_valid():
    """Test WebSearchTool validate_response method with valid response."""
    with patch.dict(os.environ, {"SERPAPI_API_KEY": "test-key"}):
        tool = WebSearchTool()

    # Valid response with organic_results
    valid_response = {
        "organic_results": [
            {
                "title": "Test Result",
                "link": "https://example.com",
                "snippet": "Test snippet",
            }
        ]
    }

    assert tool.validate_response(valid_response) is True

    # Valid response with content
    valid_response2 = {"content": "Test content"}

    assert tool.validate_response(valid_response2) is True


def test_web_search_tool_validate_response_invalid():
    """Test WebSearchTool validate_response method with invalid response."""
    with patch.dict(os.environ, {"SERPAPI_API_KEY": "test-key"}):
        tool = WebSearchTool()

    # Invalid response - not a dict
    assert tool.validate_response("not a dict") is False

    # Invalid response - error response
    invalid_response = {"error": "Something went wrong"}

    assert tool.validate_response(invalid_response) is False

    # Invalid response - malformed organic_results
    invalid_response2 = {"organic_results": "not a list"}

    assert tool.validate_response(invalid_response2) is False
