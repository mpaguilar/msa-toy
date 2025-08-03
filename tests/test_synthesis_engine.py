"""Unit tests for the synthesis engine."""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from langchain_core.prompts import PromptTemplate

from msa.orchestration.synthesis import SynthesisEngine
from msa.orchestration.models import SynthesizedAnswer
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
    engine = SynthesisEngine()
    assert engine is not None
    assert engine.confidence_scorer is not None
    assert engine.conflict_resolver is not None
    assert engine.completion_client is None
    assert engine.final_synthesis_prompt is None


def test_synthesis_engine_initialization_with_completion_client_and_prompt():
    """Test that SynthesisEngine initializes correctly with completion client and prompt."""
    mock_client = Mock()
    mock_prompt = Mock(spec=PromptTemplate)

    engine = SynthesisEngine(
        completion_client=mock_client, final_synthesis_prompt=mock_prompt,
    )

    assert engine is not None
    assert engine.confidence_scorer is not None
    assert engine.conflict_resolver is not None
    assert engine.completion_client == mock_client
    assert engine.final_synthesis_prompt == mock_prompt


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

    assert "Texas has 31 state senators" in narrative
    assert "The Texas Senate is the upper house of the Texas Legislature" in narrative


def test_construct_narrative_no_facts():
    """Test that construct_narrative handles empty facts list."""
    engine = SynthesisEngine()
    narrative = engine.construct_narrative([], "Some query")
    assert narrative == "No relevant information was found to answer the question."


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


def test_perform_final_reasoning():
    """Test that _perform_final_reasoning correctly processes facts with LLM."""
    # Create mock completion client that returns a successful response
    mock_client = Mock()
    mock_parsed_response = SynthesizedAnswer(
        answer="Texas has 31 state senators.",
        reasoning_steps=[
            "Identified the question asks for the number of Texas state senators",
            "Retrieved relevant facts about the Texas Senate",
            "Confirmed that Texas has 31 state senators",
        ],
        confidence=0.95,
    )
    mock_response = Mock()
    mock_response.parsed = mock_parsed_response
    mock_client.call.return_value = mock_response

    # Create mock prompt template
    mock_prompt = Mock(spec=PromptTemplate)
    mock_prompt.format.return_value = "Formatted prompt"

    # Create SynthesisEngine with completion client and prompt
    engine = SynthesisEngine(
        completion_client=mock_client, final_synthesis_prompt=mock_prompt,
    )

    # Create sample facts
    sample_facts = [
        Fact(
            id="1",
            content="Texas has 31 state senators",
            source="https://example.com/texas",
            confidence=0.9,
            timestamp=datetime.now().isoformat(),
        ),
    ]

    # Call _perform_final_reasoning
    result = engine._perform_final_reasoning(
        "How many state senators does Texas have?", sample_facts,
    )

    # Verify the result
    assert isinstance(result, SynthesizedAnswer)
    assert result.answer == "Texas has 31 state senators."
    assert len(result.reasoning_steps) == 3
    assert result.confidence == 0.95
    mock_prompt.format.assert_called_once()
    mock_client.call.assert_called_once()


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

        assert "Texas has 31 state senators" in result
        assert "Confidence: High" in result
        assert "## Sources:" in result
        assert "## Answer" in result


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


def test_synthesize_answer_with_completion_client_success():
    """Test synthesize_answer with successful completion client call."""
    # Create mock completion client that returns a successful response
    mock_client = Mock()
    mock_parsed_response = SynthesizedAnswer(
        answer="Synthesized answer from LLM",
        reasoning_steps=["Step 1", "Step 2"],
        confidence=0.9,
    )
    mock_response = Mock()
    mock_response.parsed = mock_parsed_response
    mock_client.call.return_value = mock_response

    # Create mock prompt template
    mock_prompt = Mock(spec=PromptTemplate)
    mock_prompt.format.return_value = "Formatted prompt"

    # Create SynthesisEngine with completion client and prompt
    engine = SynthesisEngine(
        completion_client=mock_client, final_synthesis_prompt=mock_prompt,
    )

    # Create mock memory with facts
    mock_memory = Mock(spec=WorkingMemory)
    mock_memory.information_store = Mock(spec=InformationStore)
    mock_fact = Mock(spec=Fact)
    mock_fact.content = "Test fact content"
    mock_fact.source = "test_source"
    mock_memory.information_store.facts = {"1": mock_fact}
    mock_memory.information_store.confidence_scores = {"1": 0.8}

    # Call synthesize_answer
    result = engine.synthesize_answer(mock_memory, "Test query")

    # Verify the result
    assert "Synthesized answer from LLM" in result
    assert "Reasoning Steps" in result
    assert "Step 1" in result
    assert "Step 2" in result
    assert "Confidence Report" in result
    assert "## Answer" in result
    mock_prompt.format.assert_called_once()
    mock_client.call.assert_called_once()


def test_synthesize_answer_with_completion_client_failure():
    """Test synthesize_answer with completion client failure."""
    # Create mock completion client that raises an exception
    mock_client = Mock()
    mock_client.call.side_effect = Exception("LLM call failed")

    # Create mock prompt template
    mock_prompt = Mock(spec=PromptTemplate)

    # Create SynthesisEngine with completion client and prompt
    engine = SynthesisEngine(
        completion_client=mock_client, final_synthesis_prompt=mock_prompt,
    )

    # Create mock memory with facts
    mock_memory = Mock(spec=WorkingMemory)
    mock_memory.information_store = Mock(spec=InformationStore)
    mock_fact = Mock(spec=Fact)
    mock_fact.content = "Test fact content"
    mock_fact.source = "test_source"
    mock_memory.information_store.facts = {"1": mock_fact}

    # Mock the confidence scorer to return a simple report
    with patch.object(
        engine.confidence_scorer,
        "generate_confidence_report",
        return_value="Confidence: High",
    ):
        # Call synthesize_answer (should fall back to rule-based approach)
        result = engine.synthesize_answer(mock_memory, "Test query")

        # Verify that we got a rule-based result (not the LLM result)
        assert "Test fact content" in result
        assert "## Answer" in result
        assert "## Confidence Report" in result
