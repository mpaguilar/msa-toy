"""Unit tests for temporal reasoning operations."""

import pytest
from datetime import datetime, timedelta
from msa.memory.temporal import TemporalReasoner
from msa.memory.models import Fact, WorkingMemory, QueryState, InformationStore, ExecutionHistory, ReasoningState

import logging

logging.getLogger().setLevel(logging.DEBUG)

def test_temporal_reasoner_initialization():
    """Test TemporalReasoner initialization."""
    reasoner = TemporalReasoner()
    assert isinstance(reasoner, TemporalReasoner)


def test_correlate_temporal_facts():
    """Test temporal fact correlation."""
    reasoner = TemporalReasoner()
    
    # Create facts with timestamps
    timestamp1 = datetime.now()
    timestamp2 = datetime.now() + timedelta(hours=1)
    
    fact1 = Fact(
        id="fact1",
        content="Event A occurred",
        source="test",
        timestamp=timestamp1,
        confidence=0.9,
        metadata={"timestamp": timestamp1.isoformat()}
    )
    
    fact2 = Fact(
        id="fact2",
        content="Event B occurred",
        source="test",
        timestamp=timestamp2,
        confidence=0.8,
        metadata={"timestamp": timestamp2.isoformat()}
    )
    
    facts = [fact1, fact2]
    relationships = reasoner.correlate_temporal_facts(facts)
    
    assert len(relationships) == 1
    assert relationships[0]["type"] == "temporal"
    assert relationships[0]["fact1_id"] == "fact1"
    assert relationships[0]["fact2_id"] == "fact2"
    assert relationships[0]["relationship"] == "before"
    assert relationships[0]["confidence"] == 0.8


def test_detect_causality():
    """Test causality detection."""
    reasoner = TemporalReasoner()
    
    # Create facts with timestamps and causal content
    timestamp1 = datetime.now()
    timestamp2 = datetime.now() + timedelta(minutes=30)
    
    fact1 = Fact(
        id="fact1",
        content="The storm caused power outage",
        source="test",
        timestamp=timestamp1,
        confidence=0.9,
        metadata={"timestamp": timestamp1.isoformat()}
    )
    
    fact2 = Fact(
        id="fact2",
        content="People used candles because of no electricity",
        source="test",
        timestamp=timestamp2,
        confidence=0.8,
        metadata={"timestamp": timestamp2.isoformat()}
    )
    
    facts = [fact1, fact2]
    memory = WorkingMemory(
        query_state=QueryState(
            original_query="test",
            refined_queries=[],
            query_history=[],
            current_focus="test"
        ),
        information_store=InformationStore(facts={}, relationships={}, sources={}, confidence_scores={}),
        execution_history=ExecutionHistory(actions_taken=[], timestamps={}, tool_call_sequence=[], intermediate_results=[]),
        reasoning_state=ReasoningState(current_hypothesis="", answer_draft="", information_gaps=[], next_steps=[], termination_criteria_met=False),
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    causal_relationships = reasoner.detect_causality(facts, memory)
    
    assert len(causal_relationships) == 1
    assert causal_relationships[0]["type"] == "causal"
    assert causal_relationships[0]["fact1_id"] == "fact1"
    assert causal_relationships[0]["fact2_id"] == "fact2"
    assert causal_relationships[0]["relationship"] == "causal"
    assert causal_relationships[0]["confidence"] == 0.6


def test_get_temporal_context():
    """Test temporal context extraction."""
    reasoner = TemporalReasoner()
    
    # Create working memory with temporal facts
    timestamp1 = datetime.now()
    timestamp2 = datetime.now() + timedelta(hours=1)
    
    fact1 = Fact(
        id="fact1",
        content="First event",
        source="test",
        timestamp=timestamp1,
        confidence=0.9,
        metadata={"timestamp": timestamp1.isoformat()}
    )
    
    fact2 = Fact(
        id="fact2",
        content="Second event",
        source="test",
        timestamp=timestamp2,
        confidence=0.8,
        metadata={"timestamp": timestamp2.isoformat()}
    )
    
    memory = WorkingMemory(
        query_state=QueryState(original_query="test", refined_queries=[], query_history=[], current_focus=""),
        information_store=InformationStore(facts={}, relationships={}, sources={}, confidence_scores={}),
        execution_history=ExecutionHistory(actions_taken=[], timestamps={}, tool_call_sequence=[], intermediate_results=[]),
        reasoning_state=ReasoningState(current_hypothesis="", answer_draft="", information_gaps=[], next_steps=[], termination_criteria_met=False),
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    memory.information_store.facts[fact1.id] = fact1
    memory.information_store.facts[fact2.id] = fact2
    
    temporal_context = reasoner.get_temporal_context(memory)
    
    assert "earliest_timestamp" in temporal_context
    assert "latest_timestamp" in temporal_context
    assert "temporal_facts" in temporal_context
    assert len(temporal_context["temporal_facts"]) == 2
    assert temporal_context["temporal_facts"][0]["timestamp"] == timestamp1.isoformat()
    assert temporal_context["temporal_facts"][1]["timestamp"] == timestamp2.isoformat()
