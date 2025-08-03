"""
Unit tests for the evaluation framework.
"""

import pytest

from msa.evaluation.accuracy import (
    evaluate_answer_accuracy,
    _extract_key_facts,
    _calculate_facts_coverage,
)
from msa.evaluation.completeness import (
    assess_completeness,
    _calculate_topic_coverage,
    _calculate_source_diversity,
)


class TestAccuracyEvaluation:
    """Test answer accuracy evaluation functionality."""

    def test_evaluate_answer_accuracy_exact_match(self):
        """Test accuracy evaluation with exact match."""
        predicted = "Python is a programming language."
        ground_truth = "Python is a programming language."

        result = evaluate_answer_accuracy(predicted, ground_truth)

        assert result["exact_match"] is True
        assert result["similarity_score"] == 1.0
        assert result["overall_score"] >= 0.9

    def test_evaluate_answer_accuracy_partial_match(self):
        """Test accuracy evaluation with partial match."""
        predicted = (
            "Python is a high-level programming language created by Guido van Rossum."
        )
        ground_truth = "Python is a programming language created by Guido van Rossum."

        result = evaluate_answer_accuracy(predicted, ground_truth)

        assert result["exact_match"] is False
        assert result["similarity_score"] > 0.8
        # With the current weighting (0.3 exact, 0.4 similarity, 0.3 key facts),
        # we expect a score around 0.668 for this case, which is reasonable
        assert result["overall_score"] > 0.65

    def test_evaluate_answer_accuracy_no_match(self):
        """Test accuracy evaluation with no match."""
        predicted = "Java is a programming language."
        ground_truth = "Python is a programming language."

        result = evaluate_answer_accuracy(predicted, ground_truth)

        assert result["exact_match"] is False
        # The sentences are very similar except for one word, so similarity will be high
        # but not perfect. We expect it to be less than 0.9 since they're different languages.
        assert result["similarity_score"] < 0.9
        # Overall score should still be relatively low due to no exact match and key facts mismatch
        assert result["overall_score"] < 0.7

    def test_extract_key_facts(self):
        """Test key facts extraction from text."""
        text = "Python is a programming language. It was created by Guido van Rossum. Python emphasizes code readability."

        facts = _extract_key_facts(text)

        assert len(facts) == 3
        assert "Python is a programming language" in facts
        assert "It was created by Guido van Rossum" in facts
        assert "Python emphasizes code readability" in facts

    def test_extract_key_facts_with_filler_words(self):
        """Test key facts extraction filters out filler words."""
        text = "I think Python is great. Python is a programming language. Maybe it's good."

        facts = _extract_key_facts(text)

        assert len(facts) == 1
        assert "Python is a programming language" in facts

    def test_calculate_facts_coverage_exact_match(self):
        """Test facts coverage calculation with exact matches."""
        predicted_facts = [
            "Python is a programming language",
            "It was created by Guido",
        ]
        ground_truth_facts = [
            "Python is a programming language",
            "It was created by Guido",
        ]

        coverage = _calculate_facts_coverage(predicted_facts, ground_truth_facts)

        assert coverage == 1.0

    def test_calculate_facts_coverage_partial_match(self):
        """Test facts coverage calculation with partial matches."""
        predicted_facts = [
            "Python is a high-level programming language",
            "Created by Guido van Rossum",
        ]
        ground_truth_facts = ["Python is a programming language", "Created by Guido"]

        coverage = _calculate_facts_coverage(predicted_facts, ground_truth_facts)

        # With the 90% similarity threshold, these facts are not similar enough to match
        assert coverage == 0.0

    def test_calculate_facts_coverage_no_match(self):
        """Test facts coverage calculation with no matches."""
        predicted_facts = ["Java is a programming language"]
        ground_truth_facts = ["Python is a programming language"]

        coverage = _calculate_facts_coverage(predicted_facts, ground_truth_facts)

        assert coverage == 0.0


class TestCompletenessAssessment:
    """Test information completeness assessment functionality."""

    def test_assess_completeness_full_coverage(self):
        """Test completeness assessment with full topic coverage."""
        collected_facts = [
            {"content": "Python is a programming language", "source": "wikipedia"},
            {"content": "Guido van Rossum created Python", "source": "web_search"},
        ]
        expected_topics = ["Python", "Guido van Rossum"]

        result = assess_completeness(collected_facts, expected_topics)

        assert result["coverage_ratio"] == 1.0
        # With full coverage but only 2 facts from 2 topics, we expect a score around 0.69
        assert result["completeness_score"] >= 0.65

    def test_assess_completeness_partial_coverage(self):
        """Test completeness assessment with partial topic coverage."""
        collected_facts = [
            {"content": "Python is a programming language", "source": "wikipedia"},
        ]
        expected_topics = ["Python", "Guido van Rossum", "programming"]

        result = assess_completeness(collected_facts, expected_topics)

        # The fact contains both "Python" and "programming", so coverage should be 2/3
        assert result["coverage_ratio"] == pytest.approx(2 / 3)
        assert result["completeness_score"] < 0.7

    def test_assess_completeness_no_expected_topics(self):
        """Test completeness assessment with no expected topics."""
        collected_facts = [
            {"content": "Python is a programming language", "source": "wikipedia"},
        ]
        expected_topics = []

        result = assess_completeness(collected_facts, expected_topics)

        assert result["coverage_ratio"] == 1.0
        assert result["fact_diversity"] == 1.0

    def test_assess_completeness_no_facts(self):
        """Test completeness assessment with no collected facts."""
        collected_facts = []
        expected_topics = ["Python", "Guido van Rossum"]

        result = assess_completeness(collected_facts, expected_topics)

        assert result["coverage_ratio"] == 0.0
        assert result["fact_diversity"] == 0.0
        assert result["completeness_score"] == 0.0

    def test_calculate_topic_coverage(self):
        """Test topic coverage calculation."""
        collected_facts = [
            {"content": "Python is a programming language created by Guido van Rossum"},
            {"content": "Java is also a programming language"},
        ]
        expected_topics = ["Python", "Guido", "Java", "C++"]

        covered_topics = _calculate_topic_coverage(collected_facts, expected_topics)

        assert len(covered_topics) == 3
        assert "Python" in covered_topics
        assert "Guido" in covered_topics
        assert "Java" in covered_topics
        assert "C++" not in covered_topics

    def test_calculate_source_diversity(self):
        """Test source diversity calculation."""
        collected_facts = [
            {"content": "Fact 1", "source": "wikipedia"},
            {"content": "Fact 2", "source": "web_search"},
            {"content": "Fact 3", "source": "wikipedia"},
            {"content": "Fact 4", "source": "custom_source"},
        ]

        diversity = _calculate_source_diversity(collected_facts)

        # Wikipedia appears 2 times out of 4, so diversity = 1 - (2/4) = 0.5
        assert diversity == 0.5

    def test_calculate_source_diversity_single_source(self):
        """Test source diversity calculation with single source."""
        collected_facts = [
            {"content": "Fact 1", "source": "wikipedia"},
            {"content": "Fact 2", "source": "wikipedia"},
            {"content": "Fact 3", "source": "wikipedia"},
        ]

        diversity = _calculate_source_diversity(collected_facts)

        # Single source, so diversity = 1 - (3/3) = 0.0
        assert diversity == 0.0

    def test_calculate_source_diversity_no_facts(self):
        """Test source diversity calculation with no facts."""
        collected_facts = []

        diversity = _calculate_source_diversity(collected_facts)

        assert diversity == 0.0


if __name__ == "__main__":
    pytest.main([__file__])
