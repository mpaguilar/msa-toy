"""Integration tests for the refactored controller components."""

from unittest.mock import Mock, patch

from msa.controller.components import Controller
from msa.controller.components import (
    initialize_llm_clients,
    initialize_tools,
    create_prompt_templates,
)
from msa.controller.action_handler import process_action_selection
from msa.controller.observation_handler import process_observation
from msa.controller.models import ActionSelection
from msa.tools.base import ToolResponse


def test_controller_full_integration():
    """Test the complete controller integration."""
    with (
        patch("msa.controller.components.WorkingMemoryManager") as mock_memory_manager,
        patch("msa.controller.components.SynthesisEngine") as mock_synthesis_engine,
    ):
        # Setup mocks
        mock_memory_manager_instance = Mock()
        mock_memory_manager.return_value = mock_memory_manager_instance

        mock_synthesis_result = {"answer": "Final synthesized answer"}
        mock_synthesis_engine_instance = Mock()
        mock_synthesis_engine_instance.synthesize_answer.return_value = (
            mock_synthesis_result
        )
        mock_synthesis_engine.return_value = mock_synthesis_engine_instance

        # Test controller initialization
        controller = Controller()
        assert controller is not None

        # Verify components were initialized correctly
        assert hasattr(controller, "thinking_client")
        assert hasattr(controller, "action_client")
        assert hasattr(controller, "completion_client")
        assert hasattr(controller, "tools")
        assert hasattr(controller, "think_prompt")
        assert hasattr(controller, "action_prompt")
        assert hasattr(controller, "completion_prompt")


def test_component_initialization():
    """Test that all components initialize correctly."""
    # Test LLM client initialization
    with patch("msa.controller.components.get_llm_client") as mock_get_llm_client:
        mock_client = Mock()
        mock_get_llm_client.return_value = mock_client

        clients = initialize_llm_clients()
        assert "thinking" in clients
        assert "action" in clients
        assert "completion" in clients

    # Test tool initialization
    with (
        patch("msa.controller.components.WebSearchTool") as mock_web_search,
        patch("msa.controller.components.WikipediaTool") as mock_wikipedia,
    ):
        mock_web_search_instance = Mock()
        mock_wikipedia_instance = Mock()
        mock_web_search.return_value = mock_web_search_instance
        mock_wikipedia.return_value = mock_wikipedia_instance

        tools = initialize_tools()
        assert "web_search" in tools
        assert "wikipedia" in tools

    # Test prompt template creation
    templates = create_prompt_templates()
    assert "think" in templates
    assert "action" in templates
    assert "completion" in templates


def test_action_handler_integration():
    """Test action handler integration with controller."""
    with patch("msa.controller.action_handler.parse_json_markdown") as mock_parse_json:
        mock_parse_json.return_value = {
            "action_type": "tool",
            "action_name": "web_search",
            "reasoning": "Test reasoning",
            "confidence": 0.8,
        }

        mock_action_client = Mock()
        mock_response = Mock()
        mock_response.content = "test response"
        mock_action_client.call.return_value = mock_response

        mock_tools = {"web_search": Mock(), "wikipedia": Mock()}

        result = process_action_selection(
            thoughts="test thoughts",
            action_client=mock_action_client,
            action_prompt=Mock(),
            tools=mock_tools,
        )

        assert isinstance(result, ActionSelection)
        assert result.action_type == "tool"
        assert result.action_name == "web_search"


def test_observation_handler_integration():
    """Test observation handler integration."""
    mock_response = ToolResponse(
        tool_name="web_search",
        content="Test search results",
        metadata={},
        raw_response={},
        timestamp="2023-01-01",
    )

    result = process_observation(mock_response)
    assert isinstance(result, str)
    assert result == "Observed: Test search results"
