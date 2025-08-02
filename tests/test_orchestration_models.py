import pytest
from msa.orchestration.models import SynthesizedAnswer


def test_synthesized_answer_creation():
    """Test creating a SynthesizedAnswer instance."""
    answer = "The capital of France is Paris."
    reasoning_steps = [
        "Identified the question asks for the capital of France",
        "Retrieved relevant geographical facts",
        "Confirmed Paris is the capital of France"
    ]
    confidence = 0.95
    
    synthesized = SynthesizedAnswer(
        answer=answer,
        reasoning_steps=reasoning_steps,
        confidence=confidence
    )
    
    assert synthesized.answer == answer
    assert synthesized.reasoning_steps == reasoning_steps
    assert synthesized.confidence == confidence


def test_synthesized_answer_validation():
    """Test SynthesizedAnswer validation."""
    # Test valid instance
    valid_answer = SynthesizedAnswer(
        answer="Test answer",
        reasoning_steps=["Step 1", "Step 2"],
        confidence=0.8
    )
    assert valid_answer.answer == "Test answer"
    assert len(valid_answer.reasoning_steps) == 2
    assert valid_answer.confidence == 0.8
    
    # Test confidence boundary values
    low_confidence = SynthesizedAnswer(
        answer="Test",
        reasoning_steps=[],
        confidence=0.0
    )
    high_confidence = SynthesizedAnswer(
        answer="Test",
        reasoning_steps=[],
        confidence=1.0
    )
    assert low_confidence.confidence == 0.0
    assert high_confidence.confidence == 1.0
import pytest
from msa.orchestration.models import SynthesizedAnswer


def test_synthesized_answer_creation():
    """Test creating a SynthesizedAnswer instance."""
    answer = "The capital of France is Paris."
    reasoning_steps = [
        "Identified the question asks for the capital of France",
        "Retrieved relevant geographical facts",
        "Confirmed Paris is the capital of France"
    ]
    confidence = 0.95
    
    synthesized = SynthesizedAnswer(
        answer=answer,
        reasoning_steps=reasoning_steps,
        confidence=confidence
    )
    
    assert synthesized.answer == answer
    assert synthesized.reasoning_steps == reasoning_steps
    assert synthesized.confidence == confidence


def test_synthesized_answer_validation():
    """Test SynthesizedAnswer validation."""
    # Test valid instance
    valid_answer = SynthesizedAnswer(
        answer="Test answer",
        reasoning_steps=["Step 1", "Step 2"],
        confidence=0.8
    )
    assert valid_answer.answer == "Test answer"
    assert len(valid_answer.reasoning_steps) == 2
    assert valid_answer.confidence == 0.8
    
    # Test confidence boundary values
    low_confidence = SynthesizedAnswer(
        answer="Test",
        reasoning_steps=[],
        confidence=0.0
    )
    high_confidence = SynthesizedAnswer(
        answer="Test",
        reasoning_steps=[],
        confidence=1.0
    )
    assert low_confidence.confidence == 0.0
    assert high_confidence.confidence == 1.0
