"""Temporal reasoning operations for the multi-step agent."""

import logging
from typing import List, Dict, Any
from datetime import datetime
from msa.memory.models import Fact, WorkingMemory

log = logging.getLogger(__name__)


class TemporalReasoner:
    """Handles temporal reasoning operations for working memory."""

    def __init__(self) -> None:
        """Initialize temporal reasoner."""
        _msg = "TemporalReasoner.__init__ starting"
        log.debug(_msg)
        
        _msg = "TemporalReasoner.__init__ returning"
        log.debug(_msg)

    def correlate_temporal_facts(self, facts: List[Fact]) -> List[Dict[str, Any]]:
        """Correlate facts based on temporal relationships.
        
        Args:
            facts: List of facts to analyze for temporal correlations
            
        Returns:
            List of temporal relationships between facts
        """
        _msg = "TemporalReasoner.correlate_temporal_facts starting"
        log.debug(_msg)
        
        relationships = []
        
        # Simple temporal correlation based on timestamps
        for i, fact1 in enumerate(facts):
            for j, fact2 in enumerate(facts[i+1:], i+1):
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
                        "confidence": 0.8
                    }
                    relationships.append(relationship)
                elif timestamp1 > timestamp2:
                    relationship = {
                        "type": "temporal",
                        "fact1_id": fact1.id,
                        "fact2_id": fact2.id,
                        "relationship": "after",
                        "confidence": 0.8
                    }
                    relationships.append(relationship)
        
        _msg = "TemporalReasoner.correlate_temporal_facts returning"
        log.debug(_msg)
        return relationships

    def detect_causality(self, facts: List[Fact], memory: WorkingMemory) -> List[Dict[str, Any]]:
        """Detect potential causal relationships between facts.
        
        Args:
            facts: List of facts to analyze for causal relationships
            memory: Current working memory state
            
        Returns:
            List of potential causal relationships
        """
        _msg = "TemporalReasoner.detect_causality starting"
        log.debug(_msg)
        
        causal_relationships = []
        
        # Simple causality detection based on temporal proximity and content keywords
        for i, fact1 in enumerate(facts):
            for j, fact2 in enumerate(facts[i+1:], i+1):
                # Check for temporal proximity (within 24 hours)
                timestamp1 = fact1.timestamp
                timestamp2 = fact2.timestamp
                time_diff = abs((timestamp2 - timestamp1).total_seconds())
                
                # If facts are temporally close, check for causal keywords
                if time_diff <= 86400:  # 24 hours in seconds
                    # Simple keyword-based causality detection
                    causal_indicators = ["because", "due to", "caused by", "leads to", "results in"]
                    content1 = fact1.content.lower()
                    content2 = fact2.content.lower()
                    
                    for indicator in causal_indicators:
                        if indicator in content1 or indicator in content2:
                            causal_relationships.append({
                                "type": "causal",
                                "fact1_id": fact1.id,
                                "fact2_id": fact2.id,
                                "relationship": "causal",
                                "confidence": 0.6,
                                "indicator": indicator
                            })
                            break
        
        _msg = "TemporalReasoner.detect_causality returning"
        log.debug(_msg)
        return causal_relationships

    def get_temporal_context(self, memory: WorkingMemory) -> Dict[str, Any]:
        """Extract temporal context from working memory.
        
        Args:
            memory: Current working memory state
            
        Returns:
            Dictionary containing temporal context information
        """
        _msg = "TemporalReasoner.get_temporal_context starting"
        log.debug(_msg)
        
        # Extract temporal information from facts
        temporal_facts = []
        for fact in memory.information_store.facts.values():
            temporal_facts.append({
                "id": fact.id,
                "timestamp": fact.timestamp.isoformat(),
                "content": fact.content
            })
        
        # Sort by timestamp
        temporal_facts.sort(key=lambda x: x["timestamp"])
        
        temporal_context = {
            "earliest_timestamp": temporal_facts[0]["timestamp"] if temporal_facts else None,
            "latest_timestamp": temporal_facts[-1]["timestamp"] if temporal_facts else None,
            "temporal_facts": temporal_facts
        }
        
        _msg = "TemporalReasoner.get_temporal_context returning"
        log.debug(_msg)
        return temporal_context
