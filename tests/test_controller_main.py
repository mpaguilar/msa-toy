"""Unit tests for the controller main module."""

import pytest
from unittest.mock import Mock, patch

from msa.controller.main import Controller
from msa.controller.models import ActionSelection, CompletionDecision
from msa.llm.client import LLMClient
from msa.memory.manager import WorkingMemoryManager


def test_controller_initialization():
    """Test that Controller initializes correctly."""
    with patch('msa.controller.main.LLMClient') as mock_llm_client:
        controller = Controller()
        assert controller is not None
        assert controller.max_iterations == 10


def test_execute_tool_web_search():
    """Test executing web search tool."""
    with patch('msa.controller.main.LLMClient'), \
         patch('msa.controller.main.WebSearchTool') as mock_web_search:
        controller = Controller()
        mock_response = Mock()
        mock_response.content = "Test response"
        mock_web_search.return_value.execute.return_value = mock_response
        
        result = controller.execute_tool("web_search", "test query")
        assert result.content == "Test response"


def test_execute_tool_wikipedia():
    """Test executing Wikipedia tool."""
    with patch('msa.controller.main.LLMClient'), \
         patch('msa.controller.main.WikipediaTool') as mock_wikipedia:
        controller = Controller()
        mock_response = Mock()
        mock_response.content = "Test response"
        mock_wikipedia.return_value.execute.return_value = mock_response
        
        result = controller.execute_tool("wikipedia", "test query")
        assert result.content == "Test response"


def test_execute_tool_unknown():
    """Test executing unknown tool."""
    with patch('msa.controller.main.LLMClient'):
        controller = Controller()
        result = controller.execute_tool("unknown_tool", "test query")
        assert "Error: Tool 'unknown_tool' not found" in result.content


def test_think_with_llm_response_object():
    """Test think method with LLMResponse object."""
    with patch('msa.controller.main.get_llm_client') as mock_get_llm_client, \
         patch('msa.controller.main.WorkingMemoryManager') as mock_memory_manager:
        controller = Controller()
        
        # Mock LLM response as an object with content attribute
        mock_response = Mock()
        mock_response.content = "Thought: This is a test thought"
        mock_llm_client = Mock()
        mock_llm_client.call.return_value = mock_response
        mock_get_llm_client.return_value = mock_llm_client
        
        # Mock memory manager
        mock_memory = Mock()
        mock_memory.serialize.return_value = "Test memory summary"
        mock_memory_manager_instance = Mock()
        mock_memory_manager_instance.get_memory.return_value = mock_memory
        mock_memory_manager.return_value = mock_memory_manager_instance
        
        result = controller.think("test query", mock_memory_manager_instance)
        assert result == "Thought: This is a test thought"


def test_think_with_dict_response():
    """Test think method with dictionary response."""
    with patch('msa.controller.main.get_llm_client') as mock_get_llm_client, \
         patch('msa.controller.main.WorkingMemoryManager') as mock_memory_manager:
        controller = Controller()
        
        # Mock LLM response as a dictionary
        mock_response = {"content": "Thought: This is a test thought from dict"}
        mock_llm_client = Mock()
        mock_llm_client.call.return_value = mock_response
        mock_get_llm_client.return_value = mock_llm_client
        
        # Mock memory manager
        mock_memory = Mock()
        mock_memory.serialize.return_value = "Test memory summary"
        mock_memory_manager_instance = Mock()
        mock_memory_manager_instance.get_memory.return_value = mock_memory
        mock_memory_manager.return_value = mock_memory_manager_instance
        
        result = controller.think("test query", mock_memory_manager_instance)
        assert result == "Thought: This is a test thought from dict"


def test_think_with_string_response():
    """Test think method with string response."""
    with patch('msa.controller.main.get_llm_client') as mock_get_llm_client, \
         patch('msa.controller.main.WorkingMemoryManager') as mock_memory_manager:
        controller = Controller()
        
        # Mock LLM response as a string
        mock_response = "Thought: This is a test thought from string"
        mock_llm_client = Mock()
        mock_llm_client.call.return_value = mock_response
        mock_get_llm_client.return_value = mock_llm_client
        
        # Mock memory manager
        mock_memory = Mock()
        mock_memory.serialize.return_value = "Test memory summary"
        mock_memory_manager_instance = Mock()
        mock_memory_manager_instance.get_memory.return_value = mock_memory
        mock_memory_manager.return_value = mock_memory_manager_instance
        
        result = controller.think("test query", mock_memory_manager_instance)
        assert result == "Thought: This is a test thought from string"


def test_act_with_action_selection_object():
    """Test act method with ActionSelection object."""
    with patch('msa.controller.main.get_llm_client') as mock_get_llm_client:
        controller = Controller()
        
        # Mock ActionSelection response
        mock_action = ActionSelection(
            action_type="tool",
            action_name="web_search",
            reasoning="Need to search the web",
            confidence=0.8
        )
        mock_llm_client = Mock()
        mock_llm_client.call.return_value = mock_action
        mock_get_llm_client.return_value = mock_llm_client
        
        result = controller.act("test thoughts")
        assert isinstance(result, ActionSelection)
        assert result.action_type == "tool"
        assert result.action_name == "web_search"


def test_act_with_dict_response():
    """Test act method with dictionary response."""
    with patch('msa.controller.main.get_llm_client') as mock_get_llm_client:
        controller = Controller()
        
        # Mock dictionary response
        mock_response = {
            "action_type": "tool",
            "action_name": "web_search",
            "reasoning": "Need to search the web",
            "confidence": 0.8
        }
        mock_llm_client = Mock()
        mock_llm_client.call.return_value = mock_response
        mock_get_llm_client.return_value = mock_llm_client
        
        result = controller.act("test thoughts")
        assert isinstance(result, ActionSelection)
        assert result.action_type == "tool"
        assert result.action_name == "web_search"


def test_act_with_invalid_dict_response():
    """Test act method with invalid dictionary response."""
    with patch('msa.controller.main.get_llm_client') as mock_get_llm_client:
        controller = Controller()
        
        # Mock invalid dictionary response
        mock_response = {
            "invalid_field": "invalid_value"
        }
        mock_llm_client = Mock()
        mock_llm_client.call.return_value = mock_response
        mock_get_llm_client.return_value = mock_llm_client
        
        result = controller.act("test thoughts")
        assert isinstance(result, ActionSelection)
        assert result.action_type == "error"
        assert result.action_name == "none"


def test_act_with_string_response():
    """Test act method with string response."""
    with patch('msa.controller.main.get_llm_client') as mock_get_llm_client:
        controller = Controller()
        
        # Mock string response
        mock_response = "This is not a valid response"
        mock_llm_client = Mock()
        mock_llm_client.call.return_value = mock_response
        mock_get_llm_client.return_value = mock_llm_client
        
        result = controller.act("test thoughts")
        assert isinstance(result, ActionSelection)
        assert result.action_type == "error"
        assert result.action_name == "none"


def test_check_completion_with_completion_decision_object():
    """Test check_completion method with CompletionDecision object."""
    with patch('msa.controller.main.get_llm_client') as mock_get_llm_client, \
         patch('msa.controller.main.WorkingMemoryManager') as mock_memory_manager:
        controller = Controller()
        
        # Mock CompletionDecision response
        mock_completion = CompletionDecision(
            is_complete=True,
            answer="Test answer",
            confidence=0.9,
            reasoning="Task is complete",
            remaining_tasks=[]
        )
        mock_llm_client = Mock()
        mock_llm_client.call.return_value = mock_completion
        mock_get_llm_client.return_value = mock_llm_client
        
        # Mock memory manager
        mock_memory = Mock()
        mock_memory.information_store = "Test info store"
        mock_memory_manager_instance = Mock()
        mock_memory_manager_instance.get_memory.return_value = mock_memory
        mock_memory_manager.return_value = mock_memory_manager_instance
        
        result = controller.check_completion("test query", mock_memory_manager_instance)
        assert isinstance(result, CompletionDecision)
        assert result.is_complete is True
        assert result.answer == "Test answer"


def test_check_completion_with_dict_response():
    """Test check_completion method with dictionary response."""
    with patch('msa.controller.main.get_llm_client') as mock_get_llm_client, \
         patch('msa.controller.main.WorkingMemoryManager') as mock_memory_manager:
        controller = Controller()
        
        # Mock dictionary response
        mock_response = {
            "is_complete": True,
            "answer": "Test answer from dict",
            "confidence": 0.9,
            "reasoning": "Task is complete",
            "remaining_tasks": []
        }
        mock_llm_client = Mock()
        mock_llm_client.call.return_value = mock_response
        mock_get_llm_client.return_value = mock_llm_client
        
        # Mock memory manager
        mock_memory = Mock()
        mock_memory.information_store = "Test info store"
        mock_memory_manager_instance = Mock()
        mock_memory_manager_instance.get_memory.return_value = mock_memory
        mock_memory_manager.return_value = mock_memory_manager_instance
        
        result = controller.check_completion("test query", mock_memory_manager_instance)
        assert isinstance(result, CompletionDecision)
        assert result.is_complete is True
        assert result.answer == "Test answer from dict"


def test_check_completion_with_invalid_dict_response():
    """Test check_completion method with invalid dictionary response."""
    with patch('msa.controller.main.get_llm_client') as mock_get_llm_client, \
         patch('msa.controller.main.WorkingMemoryManager') as mock_memory_manager:
        controller = Controller()
        
        # Mock invalid dictionary response
        mock_response = {
            "invalid_field": "invalid_value"
        }
        mock_llm_client = Mock()
        mock_llm_client.call.return_value = mock_response
        mock_get_llm_client.return_value = mock_llm_client
        
        # Mock memory manager
        mock_memory = Mock()
        mock_memory.information_store = "Test info store"
        mock_memory_manager_instance = Mock()
        mock_memory_manager_instance.get_memory.return_value = mock_memory
        mock_memory_manager.return_value = mock_memory_manager_instance
        
        result = controller.check_completion("test query", mock_memory_manager_instance)
        assert isinstance(result, CompletionDecision)
        assert result.is_complete is False
        assert result.answer == ""


def test_check_completion_with_string_response():
    """Test check_completion method with string response."""
    with patch('msa.controller.main.get_llm_client') as mock_get_llm_client, \
         patch('msa.controller.main.WorkingMemoryManager') as mock_memory_manager:
        controller = Controller()
        
        # Mock string response
        mock_response = "This is not a valid response"
        mock_llm_client = Mock()
        mock_llm_client.call.return_value = mock_response
        mock_get_llm_client.return_value = mock_llm_client
        
        # Mock memory manager
        mock_memory = Mock()
        mock_memory.information_store = "Test info store"
        mock_memory_manager_instance = Mock()
        mock_memory_manager_instance.get_memory.return_value = mock_memory
        mock_memory_manager.return_value = mock_memory_manager_instance
        
        result = controller.check_completion("test query", mock_memory_manager_instance)
        assert isinstance(result, CompletionDecision)
        assert result.is_complete is False
        assert result.answer == ""
