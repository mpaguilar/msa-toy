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
