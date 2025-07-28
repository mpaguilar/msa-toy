"""Unit tests for controller models."""

import pytest
from msa.controller.models import ActionSelection, QueryRefinement, CompletionDecision


def test_action_selection_creation() -> None:
    """Test creation of ActionSelection model."""
    action = ActionSelection(
        action_type="tool_call",
        action_name="web_search",
        reasoning="Need to search for current information",
        confidence=0.8
    )
    
    assert action.action_type == "tool_call"
    assert action.action_name == "web_search"
    assert action.reasoning == "Need to search for current information"
    assert action.confidence == 0.8


def test_action_selection_validation() -> None:
    """Test validation of ActionSelection model."""
    # Test valid confidence values
    action1 = ActionSelection(
        action_type="tool_call",
        action_name="web_search",
        reasoning="Test",
        confidence=0.0
    )
    assert action1.confidence == 0.0
    
    action2 = ActionSelection(
        action_type="tool_call",
        action_name="web_search",
        reasoning="Test",
        confidence=1.0
    )
    assert action2.confidence == 1.0
    
    # Test invalid confidence values
    with pytest.raises(ValueError):
        ActionSelection(
            action_type="tool_call",
            action_name="web_search",
            reasoning="Test",
            confidence=-0.1
        )
        
    with pytest.raises(ValueError):
        ActionSelection(
            action_type="tool_call",
            action_name="web_search",
            reasoning="Test",
            confidence=1.1
        )


def test_query_refinement_creation() -> None:
    """Test creation of QueryRefinement model."""
    refinement = QueryRefinement(
        original_query="What is the weather?",
        refined_query="Current weather in New York City",
        reasoning="Need to specify location for weather query",
        context="User is located in New York"
    )
    
    assert refinement.original_query == "What is the weather?"
    assert refinement.refined_query == "Current weather in New York City"
    assert refinement.reasoning == "Need to specify location for weather query"
    assert refinement.context == "User is located in New York"


def test_query_refinement_optional_context() -> None:
    """Test QueryRefinement model with optional context."""
    refinement = QueryRefinement(
        original_query="What is the weather?",
        refined_query="Current weather in New York City",
        reasoning="Need to specify location for weather query"
    )
    
    assert refinement.context is None


def test_completion_decision_creation() -> None:
    """Test creation of CompletionDecision model."""
    decision = CompletionDecision(
        is_complete=True,
        answer="The weather in New York is sunny.",
        confidence=0.95,
        reasoning="Found the requested information",
        remaining_tasks=[]
    )
    
    assert decision.is_complete is True
    assert decision.answer == "The weather in New York is sunny."
    assert decision.confidence == 0.95
    assert decision.reasoning == "Found the requested information"
    assert decision.remaining_tasks == []


def test_completion_decision_incomplete() -> None:
    """Test CompletionDecision model for incomplete tasks."""
    decision = CompletionDecision(
        is_complete=False,
        confidence=0.3,
        reasoning="Need more information",
        remaining_tasks=["Search for weather data", "Check forecast"]
    )
    
    assert decision.is_complete is False
    assert decision.answer == ""
    assert decision.confidence == 0.3
    assert decision.reasoning == "Need more information"
    assert decision.remaining_tasks == ["Search for weather data", "Check forecast"]


def test_completion_decision_validation() -> None:
    """Test validation of CompletionDecision model."""
    # Test valid confidence values
    decision1 = CompletionDecision(
        is_complete=True,
        answer="Test",
        confidence=0.0,
        reasoning="Test"
    )
    assert decision1.confidence == 0.0
    
    decision2 = CompletionDecision(
        is_complete=True,
        answer="Test",
        confidence=1.0,
        reasoning="Test"
    )
    assert decision2.confidence == 1.0
    
    # Test invalid confidence values
    with pytest.raises(ValueError):
        CompletionDecision(
            is_complete=True,
            answer="Test",
            confidence=-0.1,
            reasoning="Test"
        )
        
    with pytest.raises(ValueError):
        CompletionDecision(
            is_complete=True,
            answer="Test",
            confidence=1.1,
            reasoning="Test"
        )
