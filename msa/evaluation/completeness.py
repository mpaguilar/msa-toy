"""
Information completeness assessment for the multi-step agent evaluation framework.
"""
import logging
from typing import List, Dict, Any, Set
from collections import Counter

log = logging.getLogger(__name__)


def assess_completeness(collected_facts: List[Dict[str, Any]], 
                       expected_topics: List[str]) -> Dict[str, Any]:
    """Assess the completeness of collected information against expected topics.
    
    Args:
        collected_facts: List of facts collected by the agent
        expected_topics: List of topics that should be covered
        
    Returns:
        Dict containing completeness metrics including:
        - coverage_ratio: Float between 0-1 indicating topic coverage
        - fact_diversity: Float between 0-1 indicating diversity of sources
        - information_density: Float indicating average facts per topic
        - completeness_score: Weighted combination of metrics
    """
    _msg = "assess_completeness starting"
    log.debug(_msg)
    
    if not expected_topics:
        return {
            "coverage_ratio": 1.0,
            "fact_diversity": 1.0 if collected_facts else 0.0,
            "information_density": float(len(collected_facts)),
            "completeness_score": 1.0
        }
    
    # Calculate topic coverage
    covered_topics = _calculate_topic_coverage(collected_facts, expected_topics)
    coverage_ratio = len(covered_topics) / len(expected_topics)
    
    # Calculate source diversity
    fact_diversity = _calculate_source_diversity(collected_facts)
    
    # Calculate information density
    information_density = len(collected_facts) / len(expected_topics) if expected_topics else 0.0
    
    # Calculate completeness score (weighted average)
    completeness_score = (
        0.5 * coverage_ratio + 
        0.3 * fact_diversity + 
        0.2 * min(information_density / 5.0, 1.0)  # Normalize density to 0-1 range
    )
    
    result = {
        "coverage_ratio": coverage_ratio,
        "fact_diversity": fact_diversity,
        "information_density": information_density,
        "completeness_score": completeness_score,
        "covered_topics": list(covered_topics)
    }
    
    _msg = "assess_completeness returning"
    log.debug(_msg)
    return result


def _calculate_topic_coverage(collected_facts: List[Dict[str, Any]], 
                            expected_topics: List[str]) -> Set[str]:
    """Calculate which expected topics are covered by collected facts.
    
    Args:
        collected_facts: List of facts collected by the agent
        expected_topics: List of topics that should be covered
        
    Returns:
        Set of covered topics
    """
    _msg = "_calculate_topic_coverage starting"
    log.debug(_msg)
    
    covered_topics = set()
    fact_contents = [fact.get("content", "").lower() for fact in collected_facts]
    
    for topic in expected_topics:
        topic_lower = topic.lower()
        for content in fact_contents:
            if topic_lower in content:
                covered_topics.add(topic)
                break
    
    _msg = "_calculate_topic_coverage returning"
    log.debug(_msg)
    return covered_topics


def _calculate_source_diversity(collected_facts: List[Dict[str, Any]]) -> float:
    """Calculate the diversity of sources in collected facts.
    
    Args:
        collected_facts: List of facts collected by the agent
        
    Returns:
        Float between 0-1 indicating source diversity
    """
    _msg = "_calculate_source_diversity starting"
    log.debug(_msg)
    
    if not collected_facts:
        return 0.0
    
    sources = [fact.get("source", "unknown") for fact in collected_facts]
    source_counts = Counter(sources)
    
    # Calculate diversity using inverse of the most common source proportion
    total_facts = len(sources)
    max_source_count = max(source_counts.values())
    diversity = 1.0 - (max_source_count / total_facts)
    
    _msg = "_calculate_source_diversity returning"
    log.debug(_msg)
    return diversity
