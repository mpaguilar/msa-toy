"""Unit tests for the controller main module."""

from unittest.mock import Mock, patch

from msa.controller.components import Controller
from msa.controller.models import ActionSelection, CompletionDecision
from msa.tools.base import ToolResponse


def test_controller_initialization():
    """Test that Controller initializes correctly."""
    with (
        patch("msa.llm.client.get_llm_client"),
        patch("msa.controller.components.initialize_tools") as mock_init_tools,
    ):
        # Mock tools to avoid API key requirements
        mock_init_tools.return_value = {}
        controller = Controller()
        assert controller is not None
        assert controller.max_iterations == 10


def test_execute_tool_web_search():
    """Test executing web search tool."""
    with patch("msa.llm.client.get_llm_client"):
        # Create mock tool
        mock_web_search = Mock()
        mock_response = Mock()
        mock_response.content = "Test response"
        mock_web_search.execute.return_value = mock_response

        # Create controller and directly set the mock tool
        controller = Controller()
        controller.tools = {"web_search": mock_web_search}

        result = controller.execute_tool("web_search", "test query")
        assert result.content == "Test response"


def test_execute_tool_wikipedia():
    """Test executing Wikipedia tool."""
    with patch("msa.llm.client.get_llm_client"):
        # Create mock tool
        mock_wikipedia = Mock()
        mock_response = Mock()
        mock_response.content = "Test response"
        mock_wikipedia.execute.return_value = mock_response

        # Create controller and directly set the mock tool
        controller = Controller()
        controller.tools = {"wikipedia": mock_wikipedia}

        result = controller.execute_tool("wikipedia", "test query")
        assert result.content == "Test response"


def test_execute_tool_unknown():
    """Test executing unknown tool."""
    with patch("msa.llm.client.get_llm_client"):
        # Create controller with empty tools
        controller = Controller()
        controller.tools = {}

        result = controller.execute_tool("unknown_tool", "test query")
        assert "Error: Tool 'unknown_tool' not found" in result.content


def test_execute_tool_with_exception():
    """Test executing tool that raises exception."""
    with patch("msa.llm.client.get_llm_client"):
        # Create mock tool that raises exception
        mock_web_search = Mock()
        mock_web_search.execute.side_effect = Exception("Test exception")

        # Create controller and directly set the mock tool
        controller = Controller()
        controller.tools = {"web_search": mock_web_search}

        result = controller.execute_tool("web_search", "test query")
        assert "Error executing tool 'web_search'" in result.content


def test_process_query_with_completion():
    """Test process_query method with completion."""
    with (
        patch(
            "msa.controller.components.initialize_llm_clients",
        ) as mock_init_llm_clients,
        patch("msa.controller.components.initialize_tools") as mock_init_tools,
        patch(
            "msa.controller.components.create_prompt_templates",
        ) as mock_create_prompts,
        patch("msa.controller.components.process_thoughts") as mock_process_thoughts,
        patch(
            "msa.controller.components.process_action_selection",
        ) as mock_process_action,
        patch(
            "msa.controller.components.process_completion_decision",
        ) as mock_process_completion,
        patch("msa.controller.components.handle_tool_execution") as mock_handle_tool,
        patch(
            "msa.controller.observation_handler.process_observation",
        ) as mock_process_observation,
    ):
        # Mock the LLM clients
        mock_thinking_client = Mock()
        mock_action_client = Mock()
        mock_completion_client = Mock()

        mock_init_llm_clients.return_value = {
            "thinking": mock_thinking_client,
            "action": mock_action_client,
            "completion": mock_completion_client,
        }

        # Mock tools initialization with a mock web_search tool
        mock_web_search_tool = Mock()
        mock_tool_response = ToolResponse(
            content="Search results for test query",
            metadata={"source": "web_search", "timestamp": "2025-07-30T00:00:00"},
            success=True,
            error=None,
        )
        mock_web_search_tool.execute.return_value = mock_tool_response
        mock_init_tools.return_value = {"web_search": mock_web_search_tool}

        # Mock prompt templates
        mock_think_prompt = Mock()
        mock_action_prompt = Mock()
        mock_completion_prompt = Mock()
        mock_create_prompts.return_value = {
            "think": mock_think_prompt,
            "action": mock_action_prompt,
            "completion": mock_completion_prompt,
        }

        # Mock process_thoughts to return just the thoughts string
        mock_process_thoughts.return_value = (
            "I need to search for information about the test query"
        )

        # Mock process_action_selection to return an ActionSelection object
        mock_process_action.return_value = ActionSelection(
            action_type="tool",
            action_name="web_search",
            reasoning="Need to search for information",
            confidence=0.8,
        )

        # Mock handle_tool_execution to return the tool response
        mock_handle_tool.return_value = mock_tool_response

        # Mock process_observation to return processed observation
        mock_process_observation.return_value = (
            "Processed: Search results for test query"
        )

        # First call returns incomplete, second call returns complete
        mock_process_completion.side_effect = [
            CompletionDecision(
                is_complete=False,
                answer="",
                confidence=0.3,
                reasoning="Need more information",
                remaining_tasks=["analyze results"],
            ),
            CompletionDecision(
                is_complete=True,
                answer="Based on the search results, here is the answer",
                confidence=0.9,
                reasoning="I have gathered sufficient information",
                remaining_tasks=[],
            ),
        ]

        # Create controller and mock the synthesis engine directly on the instance
        controller = Controller()
        mock_synthesis_engine = Mock()
        mock_synthesis_engine.synthesize_answer.return_value = (
            "Final synthesized answer"
        )
        controller.synthesis_engine = mock_synthesis_engine

        result = controller.process_query("test query")
        assert result == "Final synthesized answer"


def test_process_query_with_max_iterations():
    """Test process_query method reaching max iterations."""
    with (
        patch("msa.llm.client.get_llm_client") as mock_get_llm_client,
        patch(
            "msa.controller.components.initialize_llm_clients",
        ) as mock_init_llm_clients,
        patch("msa.controller.components.initialize_tools") as mock_init_tools,
        patch(
            "msa.controller.components.create_prompt_templates",
        ) as mock_create_prompts,
        patch("msa.controller.components.process_thoughts") as mock_process_thoughts,
        patch(
            "msa.controller.action_handler.process_action_selection",
        ) as mock_process_action_selection,
        patch(
            "msa.controller.components.process_completion_decision",
        ) as mock_process_completion_decision,
        patch(
            "msa.controller.observation_handler.process_observation",
        ) as mock_process_observation,
    ):
        # Mock the LLM clients
        mock_thinking_client = Mock()
        mock_action_client = Mock()
        mock_completion_client = Mock()
        mock_init_llm_clients.return_value = {
            "thinking": mock_thinking_client,
            "action": mock_action_client,
            "completion": mock_completion_client,
        }

        # Mock tools initialization
        mock_init_tools.return_value = {}

        # Mock prompt templates
        mock_think_prompt = Mock()
        mock_action_prompt = Mock()
        mock_completion_prompt = Mock()
        mock_create_prompts.return_value = {
            "think": mock_think_prompt,
            "action": mock_action_prompt,
            "completion": mock_completion_prompt,
        }

        # Mock the components to never complete
        mock_process_thoughts.return_value = "Test thought"
        mock_process_action_selection.return_value = ActionSelection(
            action_type="tool",
            action_name="web_search",
            reasoning="Need to search",
            confidence=0.8,
        )
        mock_process_completion_decision.return_value = CompletionDecision(
            is_complete=False,
            answer="",
            confidence=0.0,
            reasoning="Not complete",
            remaining_tasks=["task1"],
        )
        mock_process_observation.return_value = "Test observation"

        controller = Controller()
        controller.max_iterations = 2  # Set to small number for testing
        result = controller.process_query("test query")
        assert result == "Reached maximum iterations without completing the task."
