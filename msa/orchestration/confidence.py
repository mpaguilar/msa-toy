"""Confidence scoring model for the multi-step agent."""

import logging
from typing import Dict, Any, List
from msa.memory.models import WorkingMemory, Fact

log = logging.getLogger(__name__)


class ConfidenceScorer:
    """Calculates confidence scores for facts and answers based on multiple factors."""

    def __init__(self) -> None:
        """Initialize the confidence scorer with default weights and source categories."""
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
            "unknown": 0.5
        }
        
        # Source categories for different types of sources
        self.source_categories = {
            "wikipedia": "wikipedia",
            "wiki": "wikipedia",
            "gov": "government",
            "edu": "educational",
            "news": "news_organization"
        }
        
        _msg = "ConfidenceScorer.__init__ returning"
        log.debug(_msg)

    def calculate_source_credibility(self, source_name: str) -> float:
        """
        Rate source reliability based on source type.
        
        Args:
            source_name: Name of the source
            
        Returns:
            Credibility score between 0.0 and 1.0
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

    def calculate_temporal_consistency(self, facts: List[Fact]) -> float:
        """
        Handle time-sensitive information consistency.
        
        Args:
            facts: List of facts to check for temporal consistency
            
        Returns:
            Temporal consistency score between 0.0 and 1.0
        """
        _msg = "ConfidenceScorer.calculate_temporal_consistency starting"
        log.debug(_msg)
        
        # For now, we'll return a default score
        # A real implementation would check timestamps and temporal relationships
        consistency = 0.9
        
        _msg = f"ConfidenceScorer.calculate_temporal_consistency returning with consistency: {consistency}"
        log.debug(_msg)
        return consistency

    def calculate_consistency_score(self, facts: List[Fact]) -> float:
        """
        Evaluate consistency across multiple sources.
        
        Args:
            facts: List of facts to check for consistency
            
        Returns:
            Consistency score between 0.0 and 1.0
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

    def calculate_completeness_score(self, facts: List[Fact], query: str) -> float:
        """
        Assess answer coverage and completeness.
        
        Args:
            facts: List of facts related to the query
            query: The original query
            
        Returns:
            Completeness score between 0.0 and 1.0
        """
        _msg = "ConfidenceScorer.calculate_completeness_score starting"
        log.debug(_msg)
        
        # For now, we'll return a default score based on number of facts
        # A real implementation would analyze query coverage
        completeness = min(1.0, len(facts) / 5.0)  # Assume 5 facts is complete
        
        _msg = f"ConfidenceScorer.calculate_completeness_score returning with completeness: {completeness}"
        log.debug(_msg)
        return completeness

    def calculate_confidence_score(self, memory: WorkingMemory, query: str) -> Dict[str, Any]:
        """
        Calculate overall confidence score for the current state.
        
        Args:
            memory: Current working memory state
            query: The original query
            
        Returns:
            Dictionary with confidence metrics and overall score
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
                "completeness": 0.0
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
        
        source_credibility = sum(source_scores) / len(source_scores) if source_scores else 0.0
        
        temporal_consistency = self.calculate_temporal_consistency(facts)
        cross_source_consistency = self.calculate_consistency_score(facts)
        completeness = self.calculate_completeness_score(facts, query)
        
        # Weighted average for overall confidence
        overall_confidence = (
            source_credibility * 0.4 +
            temporal_consistency * 0.2 +
            cross_source_consistency * 0.2 +
            completeness * 0.2
        ) * 100  # Convert to 0-100 scale
        
        result = {
            "overall_confidence": overall_confidence,
            "source_credibility": source_credibility * 100,
            "temporal_consistency": temporal_consistency * 100,
            "cross_source_consistency": cross_source_consistency * 100,
            "completeness": completeness * 100
        }
        
        _msg = f"ConfidenceScorer.calculate_confidence_score returning with result: {result}"
        log.debug(_msg)
        return result

    def generate_confidence_report(self, confidence_data: Dict[str, Any]) -> str:
        """
        Generate a detailed explanation of confidence scores.
        
        Args:
            confidence_data: Dictionary with confidence metrics
            
        Returns:
            Human-readable confidence report
        """
        _msg = "ConfidenceScorer.generate_confidence_report starting"
        log.debug(_msg)
        
        report = f"""Confidence Report:
- Overall Confidence: {confidence_data['overall_confidence']:.1f}%
- Source Credibility: {confidence_data['source_credibility']:.1f}%
- Temporal Consistency: {confidence_data['temporal_consistency']:.1f}%
- Cross-Source Consistency: {confidence_data['cross_source_consistency']:.1f}%
- Completeness: {confidence_data['completeness']:.1f}%"""
        
        _msg = "ConfidenceScorer.generate_confidence_report returning"
        log.debug(_msg)
        return report
