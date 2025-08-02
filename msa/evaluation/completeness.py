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
        collected_facts: List of facts collected by the agent. Each fact is a dictionary
            containing at minimum a "content" field with the text of the fact and optionally
            a "source" field indicating the origin of the fact.
        expected_topics: List of topics that should be covered by the collected facts.
            These are strings representing the key topics the agent was expected to address.
    
    Returns:
        A dictionary containing the following metrics:
        - coverage_ratio: Float between 0 and 1 indicating the proportion of expected
            topics that were covered by the collected facts.
        - fact_diversity: Float between 0 and 1 indicating the diversity of sources
            used to collect facts (higher values indicate more diverse sources).
        - information_density: Float indicating the average number of facts collected
            per expected topic.
        - completeness_score: Weighted combination of coverage_ratio (50%), fact_diversity (30%),
            and normalized information_density (20%), resulting in a score between 0 and 1.
        - covered_topics: List of topic strings that were actually covered by the collected facts.
    
    Notes:
        1. If expected_topics is empty, return full coverage (1.0 for coverage_ratio),
           zero diversity if no facts exist, and zero information density.
        2. Calculate covered_topics by checking if any fact's content contains any
           expected topic (case-insensitive).
        3. Compute coverage_ratio as the number of covered topics divided by total expected topics.
        4. Compute fact_diversity as 1 minus the proportion of the most common source.
        5. Compute information_density as total facts divided by number of expected topics.
        6. Calculate completeness_score as a weighted average using fixed weights: 0.5 for coverage,
           0.3 for diversity, and 0.2 for normalized density (capped at 1.0).
        7. Return the full result dictionary.
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
        collected_facts: List of facts collected by the agent. Each fact must have a "content"
            field (string) that may contain references to expected topics.
        expected_topics: List of topics that should be covered by the collected facts.
            These are strings to be matched against fact content.
    
    Returns:
        A set of topic strings from expected_topics that were found in any fact's content
        (case-insensitive match). Each topic appears at most once.
    
    Notes:
        1. Create a list of all fact contents in lowercase for case-insensitive comparison.
        2. For each expected topic, convert it to lowercase and check if it appears in any
           fact's content.
        3. If a match is found, add the original (unmodified) topic to the covered_topics set.
        4. Return the set of all matched topics.
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
        collected_facts: List of facts collected by the agent. Each fact may have a "source"
            field indicating the origin of the fact (e.g., "Wikipedia", "Reddit").
    
    Returns:
        A float between 0 and 1 representing source diversity, where:
        - 0 means all facts came from the same source
        - 1 means all facts came from different sources
        The value is computed as 1 minus the proportion of the most frequent source.
    
    Notes:
        1. If no facts are provided, return 0.0 (no diversity).
        2. Extract the source from each fact (default to "unknown" if not present).
        3. Count the frequency of each source using Counter.
        4. Find the maximum frequency among all sources.
        5. Compute diversity as 1 minus (max frequency / total number of facts).
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
