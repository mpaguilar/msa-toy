"""
Unit tests for the working memory manager.
"""

import json
from datetime import datetime
from msa.memory.manager import WorkingMemoryManager


def test_working_memory_manager_initialization():
    """Test initialization of WorkingMemoryManager."""
    manager = WorkingMemoryManager("What is the weather in London?")

    assert manager.memory is not None
    assert manager.memory.query_state.original_query == "What is the weather in London?"
    assert isinstance(manager.memory.created_at, datetime)
    assert isinstance(manager.memory.updated_at, datetime)


def test_add_observation():
    """Test adding observations to working memory."""
    manager = WorkingMemoryManager("What is the weather in London?")

    observation = {
        "content": "London weather is sunny",
        "source": "weather_api",
        "confidence": 0.9,
        "source_credibility": 0.8,
    }

    manager.add_observation(observation)

    assert len(manager.memory.information_store.facts) == 1
    assert "fact_1" in manager.memory.information_store.facts
    assert (
        manager.memory.information_store.facts["fact_1"].content
        == "London weather is sunny"
    )
    assert manager.memory.information_store.facts["fact_1"].source == "weather_api"
    assert manager.memory.information_store.facts["fact_1"].confidence == 0.9


def test_get_relevant_facts():
    """Test retrieving relevant facts from working memory."""
    manager = WorkingMemoryManager("What is the weather in London?")

    # Add some observations
    observation1 = {
        "content": "London weather is sunny",
        "source": "weather_api",
        "confidence": 0.9,
        "source_credibility": 0.8,
    }

    observation2 = {
        "content": "New York weather is rainy",
        "source": "weather_service",
        "confidence": 0.85,
        "source_credibility": 0.75,
    }

    manager.add_observation(observation1)
    manager.add_observation(observation2)

    # Get relevant facts for London context
    relevant_facts = manager.get_relevant_facts("London")

    assert len(relevant_facts) == 1
    assert relevant_facts[0]["content"] == "London weather is sunny"


def test_update_confidence_scores():
    """Test updating confidence scores based on evidence."""
    manager = WorkingMemoryManager("What is the weather in London?")

    observation = {
        "content": "London weather is sunny",
        "source": "weather_api",
        "confidence": 0.9,
        "source_credibility": 0.8,
    }

    manager.add_observation(observation)

    # Store original confidence
    original_confidence = manager.memory.information_store.confidence_scores["fact_1"]

    # Update confidence scores
    manager.update_confidence_scores()

    # Check that confidence was updated
    updated_confidence = manager.memory.information_store.confidence_scores["fact_1"]
    assert updated_confidence != original_confidence
    # The new confidence should be the average of fact confidence and source credibility
    expected_confidence = (0.9 + 0.8) / 2
    assert abs(updated_confidence - expected_confidence) < 0.001


def test_serialize_and_deserialize():
    """Test serializing and deserializing working memory."""
    manager = WorkingMemoryManager("What is the weather in London?")

    # Add an observation
    observation = {
        "content": "London weather is sunny",
        "source": "weather_api",
        "confidence": 0.9,
        "source_credibility": 0.8,
    }

    manager.add_observation(observation)

    # Serialize
    serialized = manager.serialize()

    # Check that it's valid JSON
    parsed = json.loads(serialized)
    assert "query_state" in parsed
    assert "information_store" in parsed

    # Create a new manager and deserialize
    new_manager = WorkingMemoryManager()
    deserialized_memory = new_manager.deserialize(serialized)

    # Check that the deserialized memory matches the original
    assert (
        deserialized_memory.query_state.original_query
        == "What is the weather in London?"
    )
    assert len(deserialized_memory.information_store.facts) == 1
import pytest
from datetime import datetime, timedelta
from msa.memory.manager import WorkingMemoryManager
from msa.memory.models import Fact, SourceMetadata

def test_working_memory_initialization():
    """Test that working memory is initialized correctly."""
    manager = WorkingMemoryManager("test query")
    
    assert manager.memory.query_state.original_query == "test query"
    assert len(manager.memory.information_store.facts) == 0
    assert len(manager.memory.information_store.relationships) == 0
    assert len(manager.memory.information_store.sources) == 0

def test_add_observation():
    """Test adding observations to working memory."""
    manager = WorkingMemoryManager("test query")
    
    observation = {
        "content": "The sky is blue",
        "source": "web_search",
        "confidence": 0.8,
        "source_credibility": 0.9
    }
    
    manager.add_observation(observation)
    
    assert len(manager.memory.information_store.facts) == 1
    assert "fact_1" in manager.memory.information_store.facts
    assert manager.memory.information_store.facts["fact_1"].content == "The sky is blue"
    assert manager.memory.information_store.facts["fact_1"].source == "web_search"
    assert manager.memory.information_store.facts["fact_1"].confidence == 0.8

def test_get_relevant_facts():
    """Test retrieving relevant facts from working memory."""
    manager = WorkingMemoryManager("test query")
    
    # Add some observations
    observation1 = {
        "content": "The sky is blue",
        "source": "web_search",
        "confidence": 0.8
    }
    
    observation2 = {
        "content": "Grass is green",
        "source": "wikipedia",
        "confidence": 0.9
    }
    
    manager.add_observation(observation1)
    manager.add_observation(observation2)
    
    # Test relevance matching
    relevant_facts = manager.get_relevant_facts("sky")
    assert len(relevant_facts) == 1
    assert relevant_facts[0]["content"] == "The sky is blue"
    
    relevant_facts = manager.get_relevant_facts("green")
    assert len(relevant_facts) == 1
    assert relevant_facts[0]["content"] == "Grass is green"

def test_update_confidence_scores():
    """Test updating confidence scores based on source credibility."""
    manager = WorkingMemoryManager("test query")
    
    observation = {
        "content": "The sky is blue",
        "source": "web_search",
        "confidence": 0.8,
        "source_credibility": 0.9
    }
    
    manager.add_observation(observation)
    manager.update_confidence_scores()
    
    # Confidence should be updated based on source credibility
    updated_confidence = manager.memory.information_store.confidence_scores["fact_1"]
    # Average of original confidence (0.8) and source credibility (0.9) = 0.85
    assert updated_confidence == pytest.approx(0.85)

def test_serialize_deserialize():
    """Test serializing and deserializing working memory."""
    manager = WorkingMemoryManager("test query")
    
    observation = {
        "content": "The sky is blue",
        "source": "web_search",
        "confidence": 0.8
    }
    
    manager.add_observation(observation)
    
    # Serialize
    serialized = manager.serialize()
    assert isinstance(serialized, str)
    
    # Deserialize
    deserialized_memory = manager.deserialize(serialized)
    assert deserialized_memory.query_state.original_query == "test query"
    assert len(deserialized_memory.information_store.facts) == 1

def test_prune_memory():
    """Test memory pruning functionality."""
    manager = WorkingMemoryManager("test query")
    
    # Add more facts than the max limit (100)
    for i in range(110):
        observation = {
            "content": f"Fact {i}",
            "source": "test_source",
            "confidence": 0.5 if i < 10 else 0.9  # Make first 10 facts low confidence
        }
        manager.add_observation(observation)
    
    # Check that pruning occurred
    assert len(manager.memory.information_store.facts) <= 100
    
    # Check that high confidence facts were preserved
    high_confidence_count = sum(1 for fact in manager.memory.information_store.facts.values() 
                               if fact.confidence > 0.8)
    assert high_confidence_count > 0

def test_summarize_state():
    """Test memory state summarization."""
    manager = WorkingMemoryManager("What is the capital of France?")
    
    # Add some facts
    observation1 = {
        "content": "The capital of France is Paris",
        "source": "wikipedia",
        "confidence": 0.9
    }
    
    observation2 = {
        "content": "Paris is located in Europe",
        "source": "web_search",
        "confidence": 0.8
    }
    
    manager.add_observation(observation1)
    manager.add_observation(observation2)
    
    # Get summary
    summary = manager.summarize_state()
    
    # Check summary structure
    assert "query_state" in summary
    assert "reasoning_state" in summary
    assert "top_facts" in summary
    assert "memory_stats" in summary
    
    # Check that facts are included
    assert len(summary["top_facts"]) == 2
    assert summary["memory_stats"]["total_facts"] == 2
