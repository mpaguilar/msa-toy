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


def test_synthesized_answer_empty_fields():
    """Test SynthesizedAnswer with empty fields."""
    synthesized = SynthesizedAnswer(
        answer="",
        reasoning_steps=[],
        confidence=0.5
    )
    
    assert synthesized.answer == ""
    assert synthesized.reasoning_steps == []
    assert synthesized.confidence == 0.5


def test_synthesized_answer_zero_confidence():
    """Test SynthesizedAnswer with zero confidence."""
    synthesized = SynthesizedAnswer(
        answer="Test answer",
        reasoning_steps=["Step 1"],
        confidence=0.0
    )
    
    assert synthesized.answer == "Test answer"
    assert len(synthesized.reasoning_steps) == 1
    assert synthesized.confidence == 0.0


def test_synthesized_answer_full_confidence():
    """Test SynthesizedAnswer with full confidence."""
    synthesized = SynthesizedAnswer(
        answer="Test answer",
        reasoning_steps=["Step 1", "Step 2", "Step 3"],
        confidence=1.0
    )
    
    assert synthesized.answer == "Test answer"
    assert len(synthesized.reasoning_steps) == 3
    assert synthesized.confidence == 1.0


def test_synthesized_answer_many_steps():
    """Test SynthesizedAnswer with many reasoning steps."""
    many_steps = [f"Step {i}" for i in range(100)]
    
    synthesized = SynthesizedAnswer(
        answer="Complex answer",
        reasoning_steps=many_steps,
        confidence=0.75
    )
    
    assert synthesized.answer == "Complex answer"
    assert len(synthesized.reasoning_steps) == 100
    assert synthesized.confidence == 0.75


def test_synthesized_answer_special_characters():
    """Test SynthesizedAnswer with special characters."""
    answer = "Answer with symbols: @#$%^&*()"
    steps = ["Step with unicode: 你好", "Another step: café"]
    
    synthesized = SynthesizedAnswer(
        answer=answer,
        reasoning_steps=steps,
        confidence=0.88
    )
    
    assert synthesized.answer == answer
    assert synthesized.reasoning_steps == steps
    assert synthesized.confidence == 0.88


def test_synthesized_answer_multiline_content():
    """Test SynthesizedAnswer with multiline content."""
    answer = """This is a multiline
    answer that spans
    several lines"""
    
    steps = [
        """First step with
        multiple lines""",
        "Second step"
    ]
    
    synthesized = SynthesizedAnswer(
        answer=answer,
        reasoning_steps=steps,
        confidence=0.92
    )
    
    assert synthesized.answer == answer
    assert synthesized.reasoning_steps == steps
    assert synthesized.confidence == 0.92


def test_synthesized_answer_type_validation():
    """Test that SynthesizedAnswer enforces correct types."""
    # This should work fine
    synthesized = SynthesizedAnswer(
        answer="Test",
        reasoning_steps=["Step"],
        confidence=0.5
    )
    
    assert isinstance(synthesized.answer, str)
    assert isinstance(synthesized.reasoning_steps, list)
    assert isinstance(synthesized.confidence, float)


def test_synthesized_answer_dict_conversion():
    """Test converting SynthesizedAnswer to dict."""
    synthesized = SynthesizedAnswer(
        answer="Test answer",
        reasoning_steps=["Step 1", "Step 2"],
        confidence=0.8
    )
    
    result_dict = synthesized.model_dump()
    
    assert isinstance(result_dict, dict)
    assert result_dict["answer"] == "Test answer"
    assert result_dict["reasoning_steps"] == ["Step 1", "Step 2"]
    assert result_dict["confidence"] == 0.8


def test_synthesized_answer_json_conversion():
    """Test converting SynthesizedAnswer to JSON."""
    synthesized = SynthesizedAnswer(
        answer="Test answer",
        reasoning_steps=["Step 1"],
        confidence=0.9
    )
    
    json_result = synthesized.model_dump_json()
    
    assert isinstance(json_result, str)
    assert "Test answer" in json_result
    assert "Step 1" in json_result
    assert "0.9" in json_result
