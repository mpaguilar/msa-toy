"""Unit tests for action handler parsing logic."""

import logging
from unittest.mock import Mock


from msa.controller.action_handler import process_action_selection
from msa.controller.models import ActionSelection

# Configure logging for tests
logging.basicConfig(level=logging.DEBUG)


def test_process_action_selection_with_parsed_field():
    """Test action selection when response contains 'parsed' field."""
    thoughts = "Need to search for Texas state senators"
    action_client = Mock()
    action_prompt = Mock()
    tools = {"web_search": Mock(), "wikipedia": Mock()}

    # Mock response with parsed field
    mock_response = {
        "parsed": {
            "action_type": "tool",
            "action_name": "web_search",
            "reasoning": "Searching for official Texas state senate website",
            "confidence": 0.9,
        },
    }
    action_client.call.return_value = mock_response

    action_prompt.format.return_value = "formatted prompt"

    result = process_action_selection(thoughts, action_client, action_prompt, tools)

    assert isinstance(result, ActionSelection)
    assert result.action_type == "tool"
    assert result.action_name == "web_search"
    assert result.reasoning == "Searching for official Texas state senate website"
    assert result.confidence == 0.9


def test_process_action_selection_with_content_field_json():
    """Test action selection when response contains 'content' field with valid JSON."""
    thoughts = "Need to search for Texas state senators"
    action_client = Mock()
    action_prompt = Mock()
    tools = {"web_search": Mock(), "wikipedia": Mock()}

    # Mock response with content field containing valid JSON
    mock_response = {
        "content": '{"action_type": "tool", "action_name": "web_search", "reasoning": "Searching for official Texas state senate website", "confidence": 0.9}',
    }
    action_client.call.return_value = mock_response

    action_prompt.format.return_value = "formatted prompt"

    result = process_action_selection(thoughts, action_client, action_prompt, tools)

    assert isinstance(result, ActionSelection)
    assert result.action_type == "tool"
    assert result.action_name == "web_search"
    assert result.reasoning == "Searching for official Texas state senate website"
    assert result.confidence == 0.9


def test_process_action_selection_with_content_field_wrapped_json():
    """Test action selection when response contains 'content' field with JSON wrapped in text."""
    thoughts = "Need to search for Texas state senators"
    action_client = Mock()
    action_prompt = Mock()
    tools = {"web_search": Mock(), "wikipedia": Mock()}

    # Mock response with content field containing JSON wrapped in other text
    mock_response = {
        "content": 'Here is my action selection:\n```json\n{"action_type": "tool", "action_name": "web_search", "reasoning": "Searching for official Texas state senate website", "confidence": 0.9}\n```\nLet me know if you need anything else.',
    }
    action_client.call.return_value = mock_response

    action_prompt.format.return_value = "formatted prompt"

    result = process_action_selection(thoughts, action_client, action_prompt, tools)

    assert isinstance(result, ActionSelection)
    assert result.action_type == "tool"
    assert result.action_name == "web_search"
    assert result.reasoning == "Searching for official Texas state senate website"
    assert result.confidence == 0.9


def test_process_action_selection_with_direct_action_selection():
    """Test action selection when response is already an ActionSelection object."""
    thoughts = "Need to search for Texas state senators"
    action_client = Mock()
    action_prompt = Mock()
    tools = {"web_search": Mock(), "wikipedia": Mock()}

    # Mock response as ActionSelection object
    mock_response = ActionSelection(
        action_type="tool",
        action_name="web_search",
        reasoning="Searching for official Texas state senate website",
        confidence=0.9,
    )
    action_client.call.return_value = mock_response

    action_prompt.format.return_value = "formatted prompt"

    result = process_action_selection(thoughts, action_client, action_prompt, tools)

    assert isinstance(result, ActionSelection)
    assert result.action_type == "tool"
    assert result.action_name == "web_search"
    assert result.reasoning == "Searching for official Texas state senate website"
    assert result.confidence == 0.9


def test_process_action_selection_fallback_on_error():
    """Test that fallback action is used when parsing fails."""
    thoughts = "Need to search for Texas state senators"
    action_client = Mock()
    action_prompt = Mock()
    tools = {"web_search": Mock(), "wikipedia": Mock()}

    # Mock response that will cause parsing to fail
    mock_response = {"content": "This is not valid JSON at all"}
    action_client.call.return_value = mock_response

    action_prompt.format.return_value = "formatted prompt"

    result = process_action_selection(thoughts, action_client, action_prompt, tools)

    assert isinstance(result, ActionSelection)
    assert result.action_type == "tool"
    assert result.action_name == "web_search"
    assert "Error in LLM action selection" in result.reasoning
    assert result.confidence == 0.5


def test_process_action_selection_invalid_action_type_fallback():
    """Test that fallback action is used when action type is invalid."""
    thoughts = "Need to search for Texas state senators"
    action_client = Mock()
    action_prompt = Mock()
    tools = {"web_search": Mock(), "wikipedia": Mock()}

    # Mock response with invalid action type
    mock_response = {
        "parsed": {
            "action_type": "invalid_type",
            "action_name": "web_search",
            "reasoning": "Searching for official Texas state senate website",
            "confidence": 0.9,
        },
    }
    action_client.call.return_value = mock_response

    action_prompt.format.return_value = "formatted prompt"

    result = process_action_selection(thoughts, action_client, action_prompt, tools)

    # Should still return a valid ActionSelection with fallback values
    assert isinstance(result, ActionSelection)
    assert result.action_type == "tool"  # Should fallback to "tool"
    assert result.action_name == "web_search"
    assert result.confidence == 0.5  # Should fallback to 0.5


def test_process_action_selection_fallback_on_exception():
    """Test that fallback action is used when LLM call raises exception."""
    thoughts = "Need to search for Texas state senators"
    action_client = Mock()
    action_prompt = Mock()
    tools = {"web_search": Mock(), "wikipedia": Mock()}

    # Mock LLM call raising exception
    action_client.call.side_effect = Exception("LLM call failed")

    action_prompt.format.return_value = "formatted prompt"

    result = process_action_selection(thoughts, action_client, action_prompt, tools)

    assert isinstance(result, ActionSelection)
    assert result.action_type == "tool"
    assert result.action_name == "web_search"
    assert "Error in LLM action selection" in result.reasoning
    assert result.confidence == 0.5
