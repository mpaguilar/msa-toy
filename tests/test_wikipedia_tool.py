"""Unit tests for the Wikipedia tool adapter."""

from unittest.mock import patch, MagicMock
from msa.tools.wikipedia import WikipediaTool
from msa.tools.base import ToolResponse


def test_wikipedia_tool_initialization():
    """Test WikipediaTool initialization."""
    tool = WikipediaTool()

    assert hasattr(tool, "retriever")
    assert tool.retriever is not None


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
    response = tool.execute("test query")

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
