"""Unit tests for cache manager datetime serialization."""

import logging
from datetime import datetime


from msa.tools.cache import CacheManager
from msa.tools.base import ToolResponse

# Configure logging for tests
logging.basicConfig(level=logging.DEBUG)


def test_cache_manager_datetime_serialization():
    """Test that CacheManager can handle datetime objects in ToolResponse."""
    # Create a cache manager
    cache_manager = CacheManager()

    # Create a ToolResponse with datetime timestamp (this is what happens in practice)
    tool_response = ToolResponse(
        tool_name="web_search",
        content="Test content",
        metadata={"test": "data"},
        raw_response={"raw": "data"},
    )

    # Convert to dict (this is what happens in web_search.py)
    response_dict = tool_response.model_dump()

    # Verify that the dict contains a datetime object
    assert isinstance(response_dict["timestamp"], datetime)

    # This should not raise an exception - datetime objects should be automatically converted
    cache_key = "test_key"
    cache_manager.set(cache_key, response_dict)

    # Verify we can retrieve it
    retrieved = cache_manager.get(cache_key)
    assert retrieved is not None
    assert retrieved["tool_name"] == "web_search"
    assert retrieved["content"] == "Test content"

    # Verify that the datetime was converted to ISO string format
    # The timestamp in the retrieved content should be a string now
    assert isinstance(retrieved["timestamp"], str)


def test_cache_manager_with_nested_datetime_objects():
    """Test that CacheManager can handle nested datetime objects."""
    # Create a cache manager
    cache_manager = CacheManager()

    # Create a response with nested datetime objects
    response_dict = {
        "tool_name": "test_tool",
        "content": "Test content",
        "metadata": {"created_at": datetime.now(), "updated_at": datetime.now()},
        "raw_response": {"nested_data": {"timestamp": datetime.now()}},
    }

    # This should not raise an exception
    cache_key = "test_key_nested"
    cache_manager.set(cache_key, response_dict)

    # Verify we can retrieve it
    retrieved = cache_manager.get(cache_key)
    assert retrieved is not None
    assert retrieved["tool_name"] == "test_tool"
    assert retrieved["content"] == "Test content"

    # Verify that all datetime objects were converted to ISO strings
    assert isinstance(retrieved["metadata"]["created_at"], str)
    assert isinstance(retrieved["metadata"]["updated_at"], str)
    assert isinstance(retrieved["raw_response"]["nested_data"]["timestamp"], str)
