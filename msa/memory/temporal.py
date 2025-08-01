"""Temporal reasoning operations for the multi-step agent."""

import logging
from typing import Any

from msa.memory.models import Fact, WorkingMemory

log = logging.getLogger(__name__)


class TemporalReasoner:
    """Handles temporal reasoning operations for working memory."""

    def __init__(self) -> None:
        """Initialize temporal reasoner.

        Notes:
            1. Initializes the temporal reasoner with no state.
            2. No configuration or external dependencies are required.

        """
        _msg = "TemporalReasoner.__init__ starting"
        log.debug(_msg)

        _msg = "TemporalReasoner.__init__ returning"
        log.debug(_msg)

    def correlate_temporal_facts(self, facts: list[Fact]) -> list[dict[str, Any]]:
        """Correlate facts based on temporal relationships.

        Args:
            facts: List of Fact objects to analyze for temporal correlations.

        Returns:
            List of dictionaries describing temporal relationships between facts.
            Each dictionary contains:
                - type: Always "temporal"
                - fact1_id: ID of the first fact
                - fact2_id: ID of the second fact
                - relationship: "before" if fact1 occurred earlier, "after" otherwise
                - confidence: Confidence score (0.8) for the temporal ordering

        Notes:
            1. Iterates through all pairs of facts in the input list.
            2. Compares the timestamps of each pair of facts.
            3. If fact1's timestamp is earlier than fact2's, adds a "before" relationship.
            4. If fact1's timestamp is later than fact2's, adds an "after" relationship.
            5. The confidence score is fixed at 0.8 for all relationships.
            6. Returns the accumulated list of relationships.

        """
        _msg = "TemporalReasoner.correlate_temporal_facts starting"
        log.debug(_msg)

        relationships = []

        # Simple temporal correlation based on timestamps
        for i, fact1 in enumerate(facts):
            for j, fact2 in enumerate(facts[i + 1 :], i + 1):
                # Use the timestamp attribute directly from the Fact model
                timestamp1 = fact1.timestamp
                timestamp2 = fact2.timestamp

                # Determine temporal relationship
                if timestamp1 < timestamp2:
                    relationship = {
                        "type": "temporal",
                        "fact1_id": fact1.id,
                        "fact2_id": fact2.id,
                        "relationship": "before",
                        "confidence": 0.8,
                    }
                    relationships.append(relationship)
                elif timestamp1 > timestamp2:
                    relationship = {
                        "type": "temporal",
                        "fact1_id": fact1.id,
                        "fact2_id": fact2.id,
                        "relationship": "after",
                        "confidence": 0.8,
                    }
                    relationships.append(relationship)

        _msg = "TemporalReasoner.correlate_temporal_facts returning"
        log.debug(_msg)
        return relationships

    def detect_causality(
        self,
        facts: list[Fact],
        memory: WorkingMemory,
    ) -> list[dict[str, Any]]:
        """Detect potential causal relationships between facts.

        Args:
            facts: List of Fact objects to analyze for causal relationships.
            memory: Current working memory state used for context (not directly used in this implementation).

        Returns:
            List of dictionaries describing potential causal relationships.
            Each dictionary contains:
                - type: Always "causal"
                - fact1_id: ID of the first fact
                - fact2_id: ID of the second fact
                - relationship: Always "causal"
                - confidence: Confidence score (0.6) for the causal link
                - indicator: The keyword that triggered the causal detection

        Notes:
            1. Iterates through all pairs of facts in the input list.
            2. Calculates the time difference between the timestamps of each pair.
            3. If the time difference is less than or equal to 86400 seconds (24 hours), proceeds to check for causal keywords.
            4. Checks if any of the defined causal indicators are present in either fact's content.
            5. If a causal indicator is found, adds a causal relationship with the detected keyword.
            6. The confidence score is fixed at 0.6 for all relationships.
            7. Returns the accumulated list of causal relationships.

        """
        _msg = "TemporalReasoner.detect_causality starting"
        log.debug(_msg)

        causal_relationships = []

        # Simple causality detection based on temporal proximity and content keywords
        for i, fact1 in enumerate(facts):
            for j, fact2 in enumerate(facts[i + 1 :], i + 1):
                # Check for temporal proximity (within 24 hours)
                timestamp1 = fact1.timestamp
                timestamp2 = fact2.timestamp
                time_diff = abs((timestamp2 - timestamp1).total_seconds())

                # If facts are temporally close, check for causal keywords
                if time_diff <= 86400:  # 24 hours in seconds
                    # Simple keyword-based causality detection
                    causal_indicators = [
                        "because",
                        "due to",
                        "caused by",
                        "leads to",
                        "results in",
                    ]
                    content1 = fact1.content.lower()
                    content2 = fact2.content.lower()

                    for indicator in causal_indicators:
                        if indicator in content1 or indicator in content2:
                            causal_relationships.append(
                                {
                                    "type": "causal",
                                    "fact1_id": fact1.id,
                                    "fact2_id": fact2.id,
                                    "relationship": "causal",
                                    "confidence": 0.6,
                                    "indicator": indicator,
                                },
                            )
                            break

        _msg = "TemporalReasoner.detect_causality returning"
        log.debug(_msg)
        return causal_relationships

    def get_temporal_context(self, memory: WorkingMemory) -> dict[str, Any]:
        """Extract temporal context from working memory.

        Args:
            memory: Current working memory state containing facts to analyze.

        Returns:
            Dictionary containing temporal context information with the following keys:
                - earliest_timestamp: ISO-formatted timestamp of the earliest fact, or None if no facts exist
                - latest_timestamp: ISO-formatted timestamp of the latest fact, or None if no facts exist
                - temporal_facts: List of dictionaries containing ID, timestamp, and content of each fact,
                    sorted chronologically by timestamp

        Notes:
            1. Extracts all facts from the working memory's information store.
            2. Converts each fact into a dictionary with ID, timestamp (as ISO string), and content.
            3. Sorts the list of fact dictionaries by timestamp in ascending order.
            4. If there are no facts, sets earliest_timestamp and latest_timestamp to None.
            5. Otherwise, sets earliest_timestamp to the first (oldest) fact's timestamp and latest_timestamp to the last (newest).
            6. Returns the constructed context dictionary.

        """
        _msg = "TemporalReasoner.get_temporal_context starting"
        log.debug(_msg)

        # Extract temporal information from facts
        temporal_facts = []
        for fact in memory.information_store.facts.values():
            temporal_facts.append(
                {
                    "id": fact.id,
                    "timestamp": fact.timestamp.isoformat(),
                    "content": fact.content,
                },
            )

        # Sort by timestamp
        temporal_facts.sort(key=lambda x: x["timestamp"])

        temporal_context = {
            "earliest_timestamp": temporal_facts[0]["timestamp"]
            if temporal_facts
            else None,
            "latest_timestamp": temporal_facts[-1]["timestamp"]
            if temporal_facts
            else None,
            "temporal_facts": temporal_facts,
        }

        _msg = "TemporalReasoner.get_temporal_context returning"
        log.debug(_msg)
        return temporal_context
