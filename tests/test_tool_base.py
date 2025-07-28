"""Unit tests for the tool base interface and response models."""

import pytest
from msa.tools.base import ToolInterface, ToolResponse


class MockTool(ToolInterface):
    """Mock implementation of ToolInterface for testing."""

    def execute(self, query: str) -> ToolResponse:
        """Mock execute implementation."""
        return ToolResponse(
            content=f"Mock response for: {query}",
            metadata={"tool_name": "mock_tool"},
            raw_response={"query": query, "result": "mock_result"},
        )

    def validate_response(self, response: dict) -> bool:
        """Mock validate_response implementation."""
        return "result" in response


def test_tool_response_model():
    """Test ToolResponse model creation and attributes."""
    content = "Test content"
    metadata = {"source": "test", "reliability": 0.9}
    raw_response = {"data": "test_data"}

    response = ToolResponse(
        content=content, metadata=metadata, raw_response=raw_response
    )

    assert response.content == content
    assert response.metadata == metadata
    assert response.raw_response == raw_response


def test_tool_interface_abstract_methods():
    """Test that ToolInterface cannot be instantiated directly."""
    with pytest.raises(TypeError):
        ToolInterface()


def test_mock_tool_implementation():
    """Test mock tool implementation."""
    tool = MockTool()

    # Test execute method
    query = "test query"
    response = tool.execute(query)

    assert isinstance(response, ToolResponse)
    assert response.content == f"Mock response for: {query}"
    assert response.metadata["tool_name"] == "mock_tool"
    assert response.raw_response["query"] == query

    # Test validate_response method
    valid_response = {"result": "data"}
    invalid_response = {"error": "something went wrong"}

    assert tool.validate_response(valid_response) is True
    assert tool.validate_response(invalid_response) is False
