"""Tests for the confidence scorer module."""

import pytest
from msa.orchestration.confidence import ConfidenceScorer
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
def confidence_scorer():
    """Create a ConfidenceScorer instance for testing."""
    return ConfidenceScorer()


@pytest.fixture
def sample_facts():
    """Create sample facts for testing."""
    return [
        Fact(
            id="1",
            content="Fact 1",
            confidence=0.9,
            source="wiki1",
            timestamp="2023-01-01T00:00:00Z"
        ),
        Fact(
            id="2",
            content="Fact 2",
            confidence=0.8,
            source="news1",
            timestamp="2023-01-01T00:00:00Z"
        )
    ]


def test_calculate_source_credibility(confidence_scorer):
    """Test source credibility calculation."""
    # Test Wikipedia source
    wiki_credibility = confidence_scorer.calculate_source_credibility("wiki1")
    assert wiki_credibility == 0.85
    
    # Test unknown source
    unknown_credibility = confidence_scorer.calculate_source_credibility("unknown_source")
    assert unknown_credibility == 0.5


def test_calculate_temporal_consistency(confidence_scorer, sample_facts):
    """Test temporal consistency calculation."""
    consistency = confidence_scorer.calculate_temporal_consistency(sample_facts)
    assert consistency == 0.9


def test_calculate_consistency_score(confidence_scorer, sample_facts):
    """Test consistency score calculation."""
    # Test with multiple facts
    consistency = confidence_scorer.calculate_consistency_score(sample_facts)
    assert consistency == 0.85
    
    # Test with single fact
    single_fact = [sample_facts[0]]
    consistency = confidence_scorer.calculate_consistency_score(single_fact)
    assert consistency == 1.0


def test_calculate_completeness_score(confidence_scorer, sample_facts):
    """Test completeness score calculation."""
    # Test with 2 facts
    completeness = confidence_scorer.calculate_completeness_score(sample_facts, "Test query")
    assert completeness == 0.4  # 2/5 = 0.4
    
    # Test with 5 facts (complete)
    many_facts = sample_facts * 3  # 6 facts
    completeness = confidence_scorer.calculate_completeness_score(many_facts, "Test query")
    assert completeness == 1.0  # Capped at 1.0


def test_calculate_confidence_score(confidence_scorer, sample_facts):
    """Test overall confidence score calculation."""
    # Create a working memory with sample facts
    information_store = InformationStore(
        facts={"1": sample_facts[0], "2": sample_facts[1]},
        relationships={},
        sources={
            "wiki1": SourceMetadata(id="wiki1", url="https://example.com", credibility=0.85, retrieval_date="2023-01-01T00:00:00Z"),
            "news1": SourceMetadata(id="news1", url="https://example.com", credibility=0.9, retrieval_date="2023-01-01T00:00:00Z")
        },
        confidence_scores={"1": 0.9, "2": 0.8}
    )
    
    # Create minimal instances of required models instead of None
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
    
    memory = WorkingMemory(
        query_state=query_state,
        execution_history=execution_history,
        information_store=information_store,
        reasoning_state=reasoning_state,
        created_at="2023-01-01T00:00:00Z",
        updated_at="2023-01-01T00:00:00Z"
    )
    
    confidence_data = confidence_scorer.calculate_confidence_score(memory, "Test query")
    
    # Check that all expected keys are present
    assert "overall_confidence" in confidence_data
    assert "source_credibility" in confidence_data
    assert "temporal_consistency" in confidence_data
    assert "cross_source_consistency" in confidence_data
    assert "completeness" in confidence_data
    
    # Check that values are in expected ranges
    assert 0 <= confidence_data["overall_confidence"] <= 100
    assert 0 <= confidence_data["source_credibility"] <= 100
    assert 0 <= confidence_data["temporal_consistency"] <= 100
    assert 0 <= confidence_data["cross_source_consistency"] <= 100
    assert 0 <= confidence_data["completeness"] <= 100


def test_calculate_confidence_score_no_facts(confidence_scorer):
    """Test confidence score calculation with no facts."""
    # Create a working memory with no facts
    information_store = InformationStore(
        facts={},
        relationships={},
        sources={},
        confidence_scores={}
    )
    
    # Create minimal instances of required models instead of None
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
    
    memory = WorkingMemory(
        query_state=query_state,
        execution_history=execution_history,
        information_store=information_store,
        reasoning_state=reasoning_state,
        created_at="2023-01-01T00:00:00Z",
        updated_at="2023-01-01T00:00:00Z"
    )
    
    confidence_data = confidence_scorer.calculate_confidence_score(memory, "Test query")
    
    # All scores should be 0.0 when there are no facts
    assert confidence_data["overall_confidence"] == 0.0
    assert confidence_data["source_credibility"] == 0.0
    assert confidence_data["temporal_consistency"] == 0.0
    assert confidence_data["cross_source_consistency"] == 0.0
    assert confidence_data["completeness"] == 0.0


def test_generate_confidence_report(confidence_scorer):
    """Test confidence report generation."""
    confidence_data = {
        "overall_confidence": 85.5,
        "source_credibility": 90.0,
        "temporal_consistency": 80.0,
        "cross_source_consistency": 85.0,
        "completeness": 75.0
    }
    
    report = confidence_scorer.generate_confidence_report(confidence_data)
    
    # Check that report contains expected information
    assert "Confidence Report:" in report
    assert "Overall Confidence: 85.5%" in report
    assert "Source Credibility: 90.0%" in report
    assert "Temporal Consistency: 80.0%" in report
    assert "Cross-Source Consistency: 85.0%" in report
    assert "Completeness: 75.0%" in report
