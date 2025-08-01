"""
Unit tests for the working memory models.
"""

from datetime import datetime
from msa.memory.models import (
    QueryState,
    QueryRefinement,
    ExecutionHistory,
    ActionRecord,
    ToolCall,
    ToolResponse,
    InformationStore,
    Fact,
    Relationship,
    SourceMetadata,
    ReasoningState,
    WorkingMemory,
)


def test_query_state_creation():
    """Test creation of QueryState model."""
    query_refinement = QueryRefinement(
        original="What is the weather?",
        refined="Current weather in London",
        reason="Need to specify location",
    )

    query_state = QueryState(
        original_query="What is the weather?",
        refined_queries=["Current weather in London"],
        query_history=[query_refinement],
        current_focus="weather data",
    )

    assert query_state.original_query == "What is the weather?"
    assert len(query_state.refined_queries) == 1
    assert len(query_state.query_history) == 1
    assert query_state.current_focus == "weather data"


def test_execution_history_creation():
    """Test creation of ExecutionHistory model."""
    action = ActionRecord(
        action_type="web_search",
        timestamp=datetime.now(),
        parameters={"query": "London weather"},
    )

    tool_call = ToolCall(
        tool_name="google_search",
        parameters={"q": "London weather"},
        timestamp=datetime.now(),
    )

    tool_response = ToolResponse(
        tool_name="google_search",
        response_data={"results": ["sunny", "20°C"]},
        timestamp=datetime.now(),
        metadata={"source": "api"},
    )

    execution_history = ExecutionHistory(
        actions_taken=[action],
        timestamps={"start": datetime.now()},
        tool_call_sequence=[tool_call],
        intermediate_results=[tool_response],
    )

    assert len(execution_history.actions_taken) == 1
    assert len(execution_history.tool_call_sequence) == 1
    assert len(execution_history.intermediate_results) == 1


def test_information_store_creation():
    """Test creation of InformationStore model."""
    fact = Fact(
        id="fact_1",
        content="London weather is sunny",
        source="google_search",
        timestamp=datetime.now(),
        confidence=0.9,
    )

    relationship = Relationship(
        id="rel_1",
        subject="London",
        predicate="has_weather",
        object="sunny",
        confidence=0.8,
    )

    source = SourceMetadata(
        id="src_1",
        url="https://weather.com",
        credibility=0.95,
        retrieval_date=datetime.now(),
    )

    information_store = InformationStore(
        facts={"fact_1": fact},
        relationships={"rel_1": relationship},
        sources={"src_1": source},
        confidence_scores={"fact_1": 0.9},
    )

    assert len(information_store.facts) == 1
    assert len(information_store.relationships) == 1
    assert len(information_store.sources) == 1
    assert len(information_store.confidence_scores) == 1


def test_reasoning_state_creation():
    """Test creation of ReasoningState model."""
    reasoning_state = ReasoningState(
        current_hypothesis="Weather in London is sunny",
        answer_draft="Based on the search results, London has sunny weather.",
        information_gaps=["temperature", "forecast"],
        next_steps=["search for temperature", "get forecast"],
        termination_criteria_met=False,
    )

    assert reasoning_state.current_hypothesis == "Weather in London is sunny"
    assert len(reasoning_state.information_gaps) == 2
    assert len(reasoning_state.next_steps) == 2
    assert reasoning_state.termination_criteria_met is False


def test_working_memory_creation():
    """Test creation of WorkingMemory model."""
    # Create required components
    query_state = QueryState(
        original_query="What is the weather in London?",
        refined_queries=["Current London weather"],
        query_history=[],
        current_focus="weather",
    )

    execution_history = ExecutionHistory(
        actions_taken=[],
        timestamps={},
        tool_call_sequence=[],
        intermediate_results=[],
    )

    information_store = InformationStore(
        facts={},
        relationships={},
        sources={},
        confidence_scores={},
    )

    reasoning_state = ReasoningState(
        current_hypothesis="",
        answer_draft="",
        information_gaps=[],
        next_steps=[],
        termination_criteria_met=False,
    )

    now = datetime.now()
    working_memory = WorkingMemory(
        query_state=query_state,
        execution_history=execution_history,
        information_store=information_store,
        reasoning_state=reasoning_state,
        created_at=now,
        updated_at=now,
    )

    assert working_memory.query_state.original_query == "What is the weather in London?"
    assert isinstance(working_memory.execution_history, ExecutionHistory)
    assert isinstance(working_memory.information_store, InformationStore)
    assert isinstance(working_memory.reasoning_state, ReasoningState)
