"""
End-to-end integration tests for the Multi-Step Agent.

These tests verify the correct functionality of the agent's components
working together without making actual network calls.
"""

import pytest
from unittest.mock import Mock, patch
import logging

# Import the main components to test
from msa.controller.components import Controller
from msa.memory.manager import WorkingMemoryManager
from msa.tools.base import ToolResponse
from msa.controller.models import ActionSelection, CompletionDecision


def setup_module():
    """Setup logging for tests"""
    logging.basicConfig(level=logging.DEBUG)


class TestControllerIntegration:
    """Test the Controller's integration with all components"""

    @pytest.fixture
    def mock_llm_client(self):
        """Create a mock LLM client that returns predictable responses"""
        client = Mock()
        client.call = Mock()
        return client

    @pytest.fixture
    def mock_tool(self):
        """Create a mock tool that returns predictable responses"""
        tool = Mock()
        tool.execute = Mock()
        tool.validate_response = Mock(return_value=True)
        return tool

    @pytest.fixture
    def controller_with_mocks(self, mock_llm_client, mock_tool):
        """Create a controller with mocked dependencies"""
        with (
            patch("msa.controller.components.initialize_llm_clients") as mock_llms,
            patch("msa.controller.components.initialize_tools") as mock_tools,
            patch("msa.controller.components.create_prompt_templates") as mock_prompts,
        ):
            # Setup mock LLM clients
            mock_llms.return_value = {
                "thinking": mock_llm_client,
                "action": mock_llm_client,
                "completion": mock_llm_client,
            }

            # Setup mock tools
            mock_tools.return_value = {"web_search": mock_tool, "wikipedia": mock_tool}

            # Setup mock prompts
            mock_prompts.return_value = {
                "think": Mock(),
                "action": Mock(),
                "completion": Mock(),
            }

            controller = Controller()
            return controller, mock_llm_client, mock_tool

    def test_controller_initialization(self):
        """Test that controller initializes with all required components"""
        controller = Controller()

        # Check that all components are initialized
        assert hasattr(controller, "thinking_client")
        assert hasattr(controller, "action_client")
        assert hasattr(controller, "completion_client")
        assert hasattr(controller, "tools")
        assert hasattr(controller, "synthesis_engine")
        assert hasattr(controller, "think_prompt")
        assert hasattr(controller, "action_prompt")
        assert hasattr(controller, "completion_prompt")

    def test_process_simple_query_success(self, controller_with_mocks):
        """Test successful processing of a simple query"""
        controller, mock_llm_client, mock_tool = controller_with_mocks

        # Setup mock responses for LLM calls
        # We need to provide enough responses for the ReAct cycle
        mock_llm_client.call.side_effect = [
            # First iteration
            # Thought response (thinking client)
            {
                "content": "Need to search for information about Python",
                "parsed": None,
                "metadata": {},
            },
            # Action selection response (action client) - needs to be parsed as ActionSelection
            {
                "content": '{"action_type": "tool", "action_name": "web_search", "reasoning": "Search the web", "confidence": 0.9}',
                "parsed": ActionSelection(
                    action_type="tool",
                    action_name="web_search",
                    reasoning="Search the web",
                    confidence=0.9,
                ),
                "metadata": {},
            },
            # Completion decision response (completion client)
            {
                "content": '{"is_complete": false, "answer": "", "confidence": 0.3, "reasoning": "Need more information", "remaining_tasks": ["Find more details"]}',
                "parsed": CompletionDecision(
                    is_complete=False,
                    answer="",
                    confidence=0.3,
                    reasoning="Need more information",
                    remaining_tasks=["Find more details"],
                ),
                "metadata": {},
            },
            # Second iteration
            # Thought response
            {
                "content": "Got some information, need to search more",
                "parsed": None,
                "metadata": {},
            },
            # Action selection response - this should be another ActionSelection, not CompletionDecision
            {
                "content": '{"action_type": "tool", "action_name": "wikipedia", "reasoning": "Search Wikipedia for more details", "confidence": 0.8}',
                "parsed": ActionSelection(
                    action_type="tool",
                    action_name="wikipedia",
                    reasoning="Search Wikipedia for more details",
                    confidence=0.8,
                ),
                "metadata": {},
            },
            # Completion decision response - now complete
            {
                "content": '{"is_complete": true, "answer": "Python is a programming language", "confidence": 0.9, "reasoning": "Sufficient information gathered", "remaining_tasks": []}',
                "parsed": CompletionDecision(
                    is_complete=True,
                    answer="Python is a programming language",
                    confidence=0.9,
                    reasoning="Sufficient information gathered",
                    remaining_tasks=[],
                ),
                "metadata": {},
            },
        ]

        # Setup mock tool response
        mock_tool.execute.return_value = ToolResponse(
            tool_name="web_search",
            response_data={"results": ["Python is a programming language"]},
            content="Python is a programming language",
            metadata={"source": "web"},
        )

        # Process the query
        result = controller.process_query("What is Python?")

        # Verify the result
        assert result is not None
        assert mock_tool.execute.called
        # Note: The exact result content depends on the synthesis engine which we're not fully mocking
        # but the test should at least complete without errors

    def test_process_query_with_tool_error(self, controller_with_mocks):
        """Test query processing when a tool fails"""
        controller, mock_llm_client, mock_tool = controller_with_mocks

        # Setup mock responses - provide enough for multiple iterations
        mock_responses = []
        
        # First iteration
        mock_responses.extend([
            # Thought response
            {
                "content": "Need to search for information",
                "parsed": None,
                "metadata": {},
            },
            # Action selection response
            {
                "content": '{"action_type": "tool", "action_name": "web_search", "reasoning": "Search the web", "confidence": 0.9}',
                "parsed": ActionSelection(
                    action_type="tool",
                    action_name="web_search",
                    reasoning="Search the web",
                    confidence=0.9,
                ),
                "metadata": {},
            },
            # Completion decision - not complete
            {
                "content": '{"is_complete": false, "answer": "", "confidence": 0.2, "reasoning": "Need more information", "remaining_tasks": ["Try another source"]}',
                "parsed": CompletionDecision(
                    is_complete=False,
                    answer="",
                    confidence=0.2,
                    reasoning="Need more information",
                    remaining_tasks=["Try another source"],
                ),
                "metadata": {},
            },
        ])
        
        # Second iteration (controller might try again)
        mock_responses.extend([
            # Thought response
            {
                "content": "Tool failed, trying different approach",
                "parsed": None,
                "metadata": {},
            },
            # Action selection response - try to stop or ask
            {
                "content": '{"action_type": "stop", "action_name": "stop", "reasoning": "Cannot proceed due to tool error", "confidence": 0.8}',
                "parsed": ActionSelection(
                    action_type="stop",
                    action_name="stop",
                    reasoning="Cannot proceed due to tool error",
                    confidence=0.8,
                ),
                "metadata": {},
            },
            # Completion decision - not complete
            {
                "content": '{"is_complete": false, "answer": "", "confidence": 0.1, "reasoning": "Tool failure prevents completion", "remaining_tasks": []}',
                "parsed": CompletionDecision(
                    is_complete=False,
                    answer="",
                    confidence=0.1,
                    reasoning="Tool failure prevents completion",
                    remaining_tasks=[],
                ),
                "metadata": {},
            },
        ])

        mock_llm_client.call.side_effect = mock_responses

        # Setup tool to raise an exception
        mock_tool.execute.side_effect = Exception("Network error")

        # Process the query
        result = controller.process_query("What is Python?")

        # Should handle the error gracefully and return a result
        assert result is not None
        # The controller should return a message indicating it couldn't proceed due to tool failures
        assert "Unable to complete task due to tool failures" in result or "Maximum iterations" in result

    def test_max_iterations_reached(self, controller_with_mocks):
        """Test that controller stops after maximum iterations"""
        controller, mock_llm_client, mock_tool = controller_with_mocks

        # Setup mock responses that never complete
        mock_llm_client.call.side_effect = [
            # Thought response
            {"content": "Thinking...", "parsed": None, "metadata": {}},
            # Action selection response
            {
                "content": '{"action_type": "tool", "action_name": "web_search", "reasoning": "Search", "confidence": 0.9}',
                "parsed": None,
                "metadata": {},
            },
            # Completion decision - always not complete
            {
                "content": '{"is_complete": false, "answer": "", "confidence": 0.1, "reasoning": "Not enough", "remaining_tasks": ["More info"]}',
                "parsed": CompletionDecision(
                    is_complete=False,
                    answer="",
                    confidence=0.1,
                    reasoning="Not enough",
                    remaining_tasks=["More info"],
                ),
                "metadata": {},
            },
        ] * 15  # More than max iterations

        # Setup tool response
        mock_tool.execute.return_value = ToolResponse(
            tool_name="web_search",
            response_data={"results": ["Some data"]},
            content="Some data",
            metadata={"source": "web"},
        )

        # Process the query
        result = controller.process_query("What is Python?")

        # Should stop after max iterations
        assert "Reached maximum iterations" in result
        assert (
            mock_llm_client.call.call_count <= 30
        )  # 3 calls per iteration * 10 max iterations


class TestWorkingMemoryIntegration:
    """Test WorkingMemory integration with controller components"""

    def test_memory_initialization(self):
        """Test that working memory is properly initialized"""
        memory_manager = WorkingMemoryManager("Test query")
        memory = memory_manager.get_memory()

        # Check that all components are initialized
        assert memory.query_state.original_query == "Test query"
        assert memory.reasoning_state.current_hypothesis == ""
        assert memory.reasoning_state.answer_draft == ""
        assert len(memory.information_store.facts) == 0
        assert len(memory.execution_history.actions_taken) == 0

    def test_adding_observations_to_memory(self):
        """Test that observations are correctly added to memory"""
        memory_manager = WorkingMemoryManager("Test query")

        # Add an observation
        observation = "Python is a programming language created by Guido van Rossum"
        memory_manager.add_observation({
            "content": observation,
            "source": "observation",
            "confidence": 0.8,
            "metadata": {}
        })

        # Check that the fact was added
        memory = memory_manager.get_memory()
        facts = list(memory.information_store.facts.values())
        assert len(facts) == 1
        assert facts[0].content == observation
        assert facts[0].source == "observation"

    def test_memory_pruning(self):
        """Test that memory pruning works correctly"""
        memory_manager = WorkingMemoryManager("Test query")

        # Add many observations to trigger pruning
        for i in range(150):  # More than max_facts (100)
            observation = f"Fact {i}"
            memory_manager.add_observation({
                "content": observation,
                "source": "test",
                "confidence": 0.8,
                "metadata": {}
            })

        # Check that pruning occurred
        memory = memory_manager.get_memory()
        facts = list(memory.information_store.facts.values())
        assert len(facts) <= 100  # Should be at or below max_facts


class TestToolIntegration:
    """Test integration of tools with the controller"""

    def test_web_search_tool_execution(self):
        """Test web search tool execution through controller"""
        controller = Controller()

        # Execute the tool directly
        result = controller.execute_tool("web_search", "Python programming")

        # Should return a ToolResponse even in error state
        assert isinstance(result, ToolResponse)
        # In real implementation, this would make a network call, but in test
        # it should handle the missing API key gracefully

    def test_wikipedia_tool_execution(self):
        """Test Wikipedia tool execution through controller"""
        controller = Controller()

        # Execute the tool directly
        result = controller.execute_tool("wikipedia", "Python programming language")

        # Should return a ToolResponse even in error state
        assert isinstance(result, ToolResponse)

    def test_invalid_tool_execution(self):
        """Test execution of non-existent tool"""
        controller = Controller()

        # Execute a non-existent tool
        result = controller.execute_tool("nonexistent_tool", "Some query")

        # Should return error response
        assert isinstance(result, ToolResponse)
        assert "Error" in result.content


class TestSynthesisIntegration:
    """Test the synthesis engine integration"""

    def test_synthesis_with_facts(self):
        """Test that synthesis engine creates coherent answers from facts"""
        memory_manager = WorkingMemoryManager("Tell me about Python")

        # Add some facts
        facts = [
            "Python is a high-level programming language",
            "Python was created by Guido van Rossum",
            "Python emphasizes code readability",
        ]

        for fact in facts:
            memory_manager.add_observation({
                "content": fact,
                "source": "test",
                "confidence": 0.9,
                "metadata": {}
            })

        # Test synthesis (this would normally be done by the controller)
        from msa.orchestration.synthesis import SynthesisEngine

        engine = SynthesisEngine()

        result = engine.synthesize_answer(
            memory_manager.get_memory(), "Tell me about Python",
        )

        # Check that the result contains the facts
        assert result is not None
        for fact in facts:
            assert fact in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
