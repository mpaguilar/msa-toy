"""Unit tests for the synthesis engine."""

import pytest
from unittest.mock import patch
from datetime import datetime

from msa.orchestration.synthesis import SynthesisEngine
from msa.memory.models import (
    WorkingMemory,
    InformationStore,
    Fact,
    QueryState,
    ExecutionHistory,
    ReasoningState,
)


@pytest.fixture
def sample_facts():
    """Create sample facts for testing."""
    return [
        Fact(
            id="1",
            content="Texas has 31 state senators",
            source="https://example.com/texas",
            confidence=0.9,
            timestamp=datetime.now().isoformat(),
        ),
        Fact(
            id="2",
            content="The Texas Senate is the upper house of the Texas Legislature",
            source="https://example.com/texas_senate",
            confidence=0.8,
            timestamp=datetime.now().isoformat(),
        ),
    ]


@pytest.fixture
def sample_memory(sample_facts):
    """Create a sample working memory for testing."""
    memory = WorkingMemory(
        query_state=QueryState(
            original_query="How many state senators does Texas have?",
            refined_queries=[],
            query_history=[],
            current_focus="Texas state senators",
        ),
        execution_history=ExecutionHistory(
            actions_taken=[],
            tool_call_sequence=[],
            intermediate_results=[],
            timestamps={},
        ),
        information_store=InformationStore(
            facts={},
            relationships={},
            sources={},
            confidence_scores={},
        ),
        reasoning_state=ReasoningState(
            current_hypothesis="",
            answer_draft="",
            information_gaps=[],
            next_steps=[],
            termination_criteria_met=False,
        ),
        created_at=datetime.now().isoformat(),
        updated_at=datetime.now().isoformat(),
    )
    for fact in sample_facts:
        memory.information_store.facts[fact.id] = fact
    return memory


def test_synthesis_engine_initialization():
    """Test that SynthesisEngine initializes correctly."""
    with patch("msa.orchestration.synthesis.ConfidenceScorer") as mock_scorer:
        engine = SynthesisEngine()
        assert engine is not None
        assert engine.confidence_scorer is not None


def test_eliminate_redundancy(sample_facts):
    """Test that eliminate_redundancy returns facts unchanged (placeholder implementation)."""
    engine = SynthesisEngine()
    result = engine.eliminate_redundancy(sample_facts)
    assert result == sample_facts


def test_construct_narrative_with_facts(sample_facts):
    """Test that construct_narrative creates a proper narrative from facts."""
    engine = SynthesisEngine()
    query = "How many state senators does Texas have?"
    narrative = engine.construct_narrative(sample_facts, query)

    assert "Based on the information gathered:" in narrative
    assert "Texas has 31 state senators" in narrative
    assert "The Texas Senate is the upper house of the Texas Legislature" in narrative


def test_construct_narrative_no_facts():
    """Test that construct_narrative handles empty facts list."""
    engine = SynthesisEngine()
    narrative = engine.construct_narrative([], "Some query")
    assert narrative == "No relevant information found."


def test_generate_citations_with_sources(sample_facts):
    """Test that generate_citations creates proper citations."""
    engine = SynthesisEngine()
    citations = engine.generate_citations(sample_facts)

    assert "## Sources:" in citations
    assert "https://example.com/texas" in citations
    assert "https://example.com/texas_senate" in citations
    assert "(Retrieved:" in citations


def test_generate_citations_no_facts():
    """Test that generate_citations handles empty facts list."""
    engine = SynthesisEngine()
    citations = engine.generate_citations([])
    assert citations == ""


def test_synthesize_answer(sample_memory):
    """Test that synthesize_answer combines all components correctly."""
    engine = SynthesisEngine()

    # Mock the confidence scorer to return a simple report
    with patch.object(
        engine.confidence_scorer,
        "generate_confidence_report",
        return_value="Confidence: High",
    ):
        result = engine.synthesize_answer(
            sample_memory,
            "How many state senators does Texas have?",
        )

        assert "Based on the information gathered:" in result
        assert "Texas has 31 state senators" in result
        assert "Confidence: High" in result
        assert "## Sources:" in result


def test_synthesize_answer_no_facts():
    """Test that synthesize_answer handles memory with no facts."""
    empty_memory = WorkingMemory(
        query_state=QueryState(
            original_query="Some query",
            refined_queries=[],
            query_history=[],
            current_focus="Some query",
        ),
        execution_history=ExecutionHistory(
            actions_taken=[],
            tool_call_sequence=[],
            intermediate_results=[],
            timestamps={},
        ),
        information_store=InformationStore(
            facts={},
            relationships={},
            sources={},
            confidence_scores={},
        ),
        reasoning_state=ReasoningState(
            current_hypothesis="",
            answer_draft="",
            information_gaps=[],
            next_steps=[],
            termination_criteria_met=False,
        ),
        created_at=datetime.now().isoformat(),
        updated_at=datetime.now().isoformat(),
    )

    engine = SynthesisEngine()
    result = engine.synthesize_answer(empty_memory, "Some query")

    assert "Unable to synthesize an answer: No information was gathered." in result
