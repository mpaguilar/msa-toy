"""Confidence scoring model for the multi-step agent."""

import logging
from typing import Any

from msa.memory.models import Fact, WorkingMemory

log = logging.getLogger(__name__)


class ConfidenceScorer:
    """Calculates confidence scores for facts and answers based on multiple factors."""

    def __init__(self) -> None:
        """Initialize the confidence scorer with default weights and source categories.

        Notes:
            1. Initializes the source credibility weights for different source types.
            2. Sets up keyword-based categorization for source names.
            3. Logs initialization start and completion.

        """
        _msg = "ConfidenceScorer.__init__ starting"
        log.debug(_msg)

        # Source credibility weights (0-1 scale)
        self.source_weights = {
            "peer_reviewed": 1.0,
            "government": 0.95,
            "news_organization": 0.9,
            "wikipedia": 0.85,
            "educational": 0.8,
            "blog": 0.6,
            "social_media": 0.4,
            "unknown": 0.5,
        }

        # Source categories for different types of sources
        self.source_categories = {
            "wikipedia": "wikipedia",
            "wiki": "wikipedia",
            "gov": "government",
            "edu": "educational",
            "news": "news_organization",
        }

        _msg = "ConfidenceScorer.__init__ returning"
        log.debug(_msg)

    def calculate_source_credibility(self, source_name: str) -> float:
        """Rate source reliability based on source type.

        Args:
            source_name: The name or identifier of the source (str)

        Returns:
            A float between 0.0 and 1.0 representing the credibility score of the source.

        Notes:
            1. Converts the source name to lowercase for case-insensitive matching.
            2. Uses keyword matching to categorize the source into one of the predefined categories.
            3. Retrieves the credibility weight for the matched category or defaults to "unknown".
            4. Returns the credibility score.

        """
        _msg = f"ConfidenceScorer.calculate_source_credibility starting with source: {source_name}"
        log.debug(_msg)

        # Simple keyword matching for source categorization
        source_lower = source_name.lower()
        category = "unknown"

        for key, cat in self.source_categories.items():
            if key in source_lower:
                category = cat
                break

        credibility = self.source_weights.get(category, self.source_weights["unknown"])

        _msg = f"ConfidenceScorer.calculate_source_credibility returning with credibility: {credibility}"
        log.debug(_msg)
        return credibility

    def calculate_temporal_consistency(self, facts: list[Fact]) -> float:
        """Handle time-sensitive information consistency.

        Args:
            facts: List of Fact objects to evaluate for temporal consistency.

        Returns:
            A float between 0.0 and 1.0 representing the temporal consistency score.

        Notes:
            1. Initializes the consistency score to a default value of 0.9.
            2. In a real implementation, this would check timestamps and temporal relationships between facts.
            3. Returns the default consistency score for now.

        """
        _msg = "ConfidenceScorer.calculate_temporal_consistency starting"
        log.debug(_msg)

        # For now, we'll return a default score
        # A real implementation would check timestamps and temporal relationships
        consistency = 0.9

        _msg = f"ConfidenceScorer.calculate_temporal_consistency returning with consistency: {consistency}"
        log.debug(_msg)
        return consistency

    def calculate_consistency_score(self, facts: list[Fact]) -> float:
        """Evaluate consistency across multiple sources.

        Args:
            facts: List of Fact objects to evaluate for consistency between sources.

        Returns:
            A float between 0.0 and 1.0 representing the cross-source consistency score.

        Notes:
            1. If fewer than two facts are present, returns 1.0 (perfect consistency by default).
            2. In a real implementation, this would compare the content of facts for similarity.
            3. Returns a default score of 0.85 for now.

        """
        _msg = "ConfidenceScorer.calculate_consistency_score starting"
        log.debug(_msg)

        if len(facts) < 2:
            return 1.0  # Perfect consistency with only one fact

        # For now, we'll return a default score
        # A real implementation would compare fact contents for similarity
        consistency = 0.85

        _msg = f"ConfidenceScorer.calculate_consistency_score returning with consistency: {consistency}"
        log.debug(_msg)
        return consistency

    def calculate_completeness_score(self, facts: list[Fact], query: str) -> float:
        """Assess answer coverage and completeness.

        Args:
            facts: List of Fact objects related to the query.
            query: The original user query (str) used to assess completeness.

        Returns:
            A float between 0.0 and 1.0 representing the completeness score.

        Notes:
            1. Uses the number of facts as a proxy for completeness.
            2. Assumes that up to 5 facts represent full completeness.
            3. Returns the ratio of facts to 5, capped at 1.0.

        """
        _msg = "ConfidenceScorer.calculate_completeness_score starting"
        log.debug(_msg)

        # For now, we'll return a default score based on number of facts
        # A real implementation would analyze query coverage
        completeness = min(1.0, len(facts) / 5.0)  # Assume 5 facts is complete

        _msg = f"ConfidenceScorer.calculate_completeness_score returning with completeness: {completeness}"
        log.debug(_msg)
        return completeness

    def calculate_confidence_score(
        self,
        memory: WorkingMemory,
        query: str,
    ) -> dict[str, Any]:
        """Calculate overall confidence score for the current state.

        Args:
            memory: The current working memory state containing facts and sources.
            query: The original query (str) to assess confidence against.

        Returns:
            A dictionary containing:
                - overall_confidence: float (0-100) representing the final confidence score.
                - source_credibility: float (0-100) representing the average source credibility.
                - temporal_consistency: float (0-100) representing temporal consistency.
                - cross_source_consistency: float (0-100) representing consistency between sources.
                - completeness: float (0-100) representing completeness of answer.

        Notes:
            1. Extracts all facts from the working memory.
            2. If no facts exist, returns a result with all scores set to 0.0.
            3. For each fact, retrieves its source and calculates credibility.
            4. Computes average source credibility from all facts.
            5. Calculates temporal consistency, cross-source consistency, and completeness.
            6. Combines scores using weighted averaging (source: 40%, temporal: 20%, cross-source: 20%, completeness: 20%).
            7. Scales the overall confidence to 0-100 scale and returns all metrics.

        """
        _msg = "ConfidenceScorer.calculate_confidence_score starting"
        log.debug(_msg)

        facts = list(memory.information_store.facts.values())

        if not facts:
            result = {
                "overall_confidence": 0.0,
                "source_credibility": 0.0,
                "temporal_consistency": 0.0,
                "cross_source_consistency": 0.0,
                "completeness": 0.0,
            }
            _msg = "ConfidenceScorer.calculate_confidence_score returning with no facts"
            log.debug(_msg)
            return result

        # Calculate individual components
        source_scores = []
        for fact in facts:
            if fact.source and fact.source in memory.information_store.sources:
                source_metadata = memory.information_store.sources[fact.source]
                # Use the source ID for credibility calculation since there's no name field
                source_name = source_metadata.id if source_metadata.id else "unknown"
            else:
                source_name = "unknown"
            source_scores.append(self.calculate_source_credibility(source_name))

        source_credibility = (
            sum(source_scores) / len(source_scores) if source_scores else 0.0
        )

        temporal_consistency = self.calculate_temporal_consistency(facts)
        cross_source_consistency = self.calculate_consistency_score(facts)
        completeness = self.calculate_completeness_score(facts, query)

        # Weighted average for overall confidence
        overall_confidence = (
            source_credibility * 0.4
            + temporal_consistency * 0.2
            + cross_source_consistency * 0.2
            + completeness * 0.2
        ) * 100  # Convert to 0-100 scale

        result = {
            "overall_confidence": overall_confidence,
            "source_credibility": source_credibility * 100,
            "temporal_consistency": temporal_consistency * 100,
            "cross_source_consistency": cross_source_consistency * 100,
            "completeness": completeness * 100,
        }

        _msg = f"ConfidenceScorer.calculate_confidence_score returning with result: {result}"
        log.debug(_msg)
        return result

    def generate_confidence_report(self, confidence_data: dict[str, Any]) -> str:
        """Generate a detailed explanation of confidence scores.

        Args:
            confidence_data: Dictionary containing confidence metrics from calculate_confidence_score.

        Returns:
            A formatted string report showing all confidence metrics with percentages.

        Notes:
            1. Constructs a multi-line string with each metric on a separate line.
            2. Formats all values to one decimal place for readability.
            3. Returns the completed report string.

        """
        _msg = "ConfidenceScorer.generate_confidence_report starting"
        log.debug(_msg)

        report = f"""Confidence Report:
- Overall Confidence: {confidence_data["overall_confidence"]:.1f}%
- Source Credibility: {confidence_data["source_credibility"]:.1f}%
- Temporal Consistency: {confidence_data["temporal_consistency"]:.1f}%
- Cross-Source Consistency: {confidence_data["cross_source_consistency"]:.1f}%
- Completeness: {confidence_data["completeness"]:.1f}%"""

        _msg = "ConfidenceScorer.generate_confidence_report returning"
        log.debug(_msg)
        return report
