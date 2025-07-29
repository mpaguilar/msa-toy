"""Tests for the conflict resolver module."""

import pytest
from msa.orchestration.conflict import ConflictResolver
from msa.memory.models import (
    WorkingMemory, 
    InformationStore, 
    Fact, 
    SourceMetadata,
    QueryState,
    ExecutionHistory,
    ReasoningState
)


@pytest.fixture
def conflict_resolver():
    """Create a ConflictResolver instance for testing."""
    return ConflictResolver()


@pytest.fixture
def sample_memory():
    """Create a sample working memory with some facts."""
    fact1 = Fact(
        id="1",
        content="The Earth is round",
        confidence=0.9,
        source="wiki1",
        timestamp="2023-01-01T00:00:00Z"
    )
    
    fact2 = Fact(
        id="2",
        content="The Earth is flat",
        confidence=0.3,
        source="blog1",
        timestamp="2023-01-01T00:00:00Z"
    )
    
    fact3 = Fact(
        id="3",
        content="Water boils at 100°C at sea level",
        confidence=0.95,
        source="wiki2",
        timestamp="2023-01-01T00:00:00Z"
    )
    
    information_store = InformationStore(
        facts={"1": fact1, "2": fact2, "3": fact3},
        relationships={},
        sources={
            "wiki1": SourceMetadata(id="wiki1", url="https://example.com", credibility=0.85, retrieval_date="2023-01-01T00:00:00Z"),
            "blog1": SourceMetadata(id="blog1", url="https://example.com", credibility=0.3, retrieval_date="2023-01-01T00:00:00Z"),
            "wiki2": SourceMetadata(id="wiki2", url="https://example.com", credibility=0.85, retrieval_date="2023-01-01T00:00:00Z")
        },
        confidence_scores={"1": 0.9, "2": 0.3, "3": 0.95}
    )
    
    query_state = QueryState(
        original_query="Test query",
        refined_queries=[],
        query_history=[],
        current_focus=""
    )
    
    execution_history = ExecutionHistory(
        actions_taken=[],
        timestamps={},
        tool_call_sequence=[],
        intermediate_results=[]
    )
    
    reasoning_state = ReasoningState(
        current_hypothesis="",
        answer_draft="",
        information_gaps=[],
        next_steps=[],
        termination_criteria_met=False
    )
    
    return WorkingMemory(
        query_state=query_state,
        execution_history=execution_history,
        information_store=information_store,
        reasoning_state=reasoning_state,
        created_at="2023-01-01T00:00:00Z",
        updated_at="2023-01-01T00:00:00Z"
    )


def test_detect_conflicts(conflict_resolver, sample_memory):
    """Test detecting conflicts in working memory."""
    conflicts = conflict_resolver.detect_conflicts(sample_memory)
    
    # Should detect one conflict between the contradictory facts
    assert len(conflicts) == 1
    assert conflicts[0]["fact1"].id == "1"
    assert conflicts[0]["fact2"].id == "2"


def test_investigate_conflicts(conflict_resolver, sample_memory):
    """Test investigating detected conflicts."""
    conflicts = conflict_resolver.detect_conflicts(sample_memory)
    investigations = conflict_resolver.investigate_conflicts(conflicts, sample_memory)
    
    # Should have one investigation result
    assert len(investigations) == 1
    assert "conflict" in investigations[0]
    assert "sources" in investigations[0]


def test_resolve_conflicts(conflict_resolver, sample_memory):
    """Test resolving conflicts based on confidence scores."""
    conflicts = conflict_resolver.detect_conflicts(sample_memory)
    investigations = conflict_resolver.investigate_conflicts(conflicts, sample_memory)
    resolutions = conflict_resolver.resolve_conflicts(investigations, sample_memory)
    
    # Should resolve in favor of the higher confidence fact
    assert len(resolutions) == 1
    assert resolutions[0]["preferred_fact"].id == "1"  # Higher confidence fact
    assert resolutions[0]["rejected_fact"].id == "2"   # Lower confidence fact


def test_synthesize_with_uncertainty(conflict_resolver, sample_memory):
    """Test synthesizing answers with uncertainty acknowledgment."""
    facts = list(sample_memory.information_store.facts.values())
    conflicts = conflict_resolver.detect_conflicts(sample_memory)
    
    synthesis = conflict_resolver.synthesize_with_uncertainty(facts, conflicts)
    
    # Should contain the facts and a note about conflicts
    assert "Earth is round" in synthesis
    assert "Earth is flat" in synthesis
    assert "conflicting claims" in synthesis


def test_synthesize_without_conflicts(conflict_resolver, sample_memory):
    """Test synthesizing answers without conflicts."""
    # Remove conflicting facts for this test
    facts = [fact for fact in sample_memory.information_store.facts.values() 
             if fact.id == "3"]  # Only the non-conflicting fact
    conflicts = []  # No conflicts
    
    synthesis = conflict_resolver.synthesize_with_uncertainty(facts, conflicts)
    
    # Should contain the facts but no conflict note
    assert "Water boils at 100°C" in synthesis
    assert "conflicting claims" not in synthesis
