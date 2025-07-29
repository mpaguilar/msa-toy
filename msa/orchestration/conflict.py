"""Conflict detection and resolution for multi-step agent."""

import logging
from typing import List, Dict, Any
from msa.memory.models import WorkingMemory, Fact

log = logging.getLogger(__name__)


class ConflictResolver:
    """Handles detection and resolution of contradictory information."""

    def __init__(self) -> None:
        """Initialize the conflict resolver."""
        _msg = "ConflictResolver.__init__ starting"
        log.debug(_msg)
        _msg = "ConflictResolver.__init__ returning"
        log.debug(_msg)

    def detect_conflicts(self, memory: WorkingMemory) -> List[Dict[str, Any]]:
        """
        Identify contradictory claims in the working memory.

        Args:
            memory: The working memory containing facts to check for conflicts

        Returns:
            A list of detected conflicts with details about contradictory facts
        """
        _msg = "ConflictResolver.detect_conflicts starting"
        log.debug(_msg)
        
        conflicts = []
        facts = list(memory.information_store.facts.values())
        
        # Compare each fact with every other fact to find contradictions
        for i, fact1 in enumerate(facts):
            for fact2 in facts[i+1:]:
                if self._are_contradictory(fact1, fact2):
                    conflicts.append({
                        "fact1": fact1,
                        "fact2": fact2,
                        "type": "contradiction",
                        "description": f"Contradiction between '{fact1.content}' and '{fact2.content}'"
                    })
        
        _msg = f"ConflictResolver.detect_conflicts returning with {len(conflicts)} conflicts found"
        log.debug(_msg)
        return conflicts

    def investigate_conflicts(self, conflicts: List[Dict[str, Any]], memory: WorkingMemory) -> List[Dict[str, Any]]:
        """
        Gather additional context to investigate detected conflicts.

        Args:
            conflicts: List of detected conflicts
            memory: The working memory containing facts

        Returns:
            A list of investigation results with additional context
        """
        _msg = "ConflictResolver.investigate_conflicts starting"
        log.debug(_msg)
        
        investigation_results = []
        
        for conflict in conflicts:
            # For now, we'll just return the conflict with additional metadata
            # In a real implementation, this would use tools to gather more information
            investigation_result = {
                "conflict": conflict,
                "investigation": "Investigation would use additional tools to gather context",
                "sources": [conflict["fact1"].source, conflict["fact2"].source]
            }
            investigation_results.append(investigation_result)
        
        _msg = f"ConflictResolver.investigate_conflicts returning with {len(investigation_results)} investigations"
        log.debug(_msg)
        return investigation_results

    def resolve_conflicts(self, investigations: List[Dict[str, Any]], memory: WorkingMemory) -> List[Dict[str, Any]]:
        """
        Weight and resolve contradictory information based on source reliability.

        Args:
            investigations: List of conflict investigations
            memory: The working memory containing facts

        Returns:
            A list of resolved conflicts with weighted decisions
        """
        _msg = "ConflictResolver.resolve_conflicts starting"
        log.debug(_msg)
        
        resolutions = []
        
        for investigation in investigations:
            conflict = investigation["conflict"]
            fact1 = conflict["fact1"]
            fact2 = conflict["fact2"]
            
            # Simple resolution based on confidence scores
            # In a real implementation, this would be more sophisticated
            if fact1.confidence > fact2.confidence:
                resolution = {
                    "preferred_fact": fact1,
                    "rejected_fact": fact2,
                    "reasoning": f"Fact 1 has higher confidence ({fact1.confidence}) than Fact 2 ({fact2.confidence})"
                }
            elif fact2.confidence > fact1.confidence:
                resolution = {
                    "preferred_fact": fact2,
                    "rejected_fact": fact1,
                    "reasoning": f"Fact 2 has higher confidence ({fact2.confidence}) than Fact 1 ({fact1.confidence})"
                }
            else:
                # Equal confidence - could use other criteria
                resolution = {
                    "preferred_fact": fact1,
                    "rejected_fact": fact2,
                    "reasoning": "Facts have equal confidence, keeping first encountered"
                }
            
            resolutions.append(resolution)
        
        _msg = f"ConflictResolver.resolve_conflicts returning with {len(resolutions)} resolutions"
        log.debug(_msg)
        return resolutions

    def synthesize_with_uncertainty(self, facts: List[Fact], conflicts: List[Dict[str, Any]]) -> str:
        """
        Create nuanced answers that acknowledge uncertainties.

        Args:
            facts: List of facts to synthesize
            conflicts: List of unresolved conflicts

        Returns:
            A synthesized answer that acknowledges uncertainties
        """
        _msg = "ConflictResolver.synthesize_with_uncertainty starting"
        log.debug(_msg)
        
        if not facts:
            return "No facts available to synthesize."
        
        # Create a basic synthesis
        synthesis = "Based on the available information:\n\n"
        
        for fact in facts:
            synthesis += f"- {fact.content} (confidence: {fact.confidence})\n"
        
        # Add uncertainty notes if there are conflicts
        if conflicts:
            synthesis += "\nNote: There are conflicting claims in the information gathered. "
            synthesis += "The confidence scores above indicate our assessment of reliability, "
            synthesis += "but you should verify critical information from authoritative sources."
        
        _msg = "ConflictResolver.synthesize_with_uncertainty returning"
        log.debug(_msg)
        return synthesis

    def _are_contradictory(self, fact1: Fact, fact2: Fact) -> bool:
        """
        Check if two facts are contradictory.

        Args:
            fact1: First fact to compare
            fact2: Second fact to compare

        Returns:
            True if facts are contradictory, False otherwise
        """
        # This is a simplified implementation
        # A real implementation would use more sophisticated NLP techniques
        content1 = fact1.content.lower()
        content2 = fact2.content.lower()
        
        # Simple keyword-based contradiction detection
        # This is just a placeholder - a real implementation would be much more complex
        contradictory_pairs = [
            ("is true", "is false"),
            ("did happen", "did not happen"),
            ("does exist", "does not exist"),
            ("is correct", "is incorrect"),
            ("is round", "is flat"),
            ("is flat", "is round")
        ]
        
        for pair in contradictory_pairs:
            if (pair[0] in content1 and pair[1] in content2) or \
               (pair[0] in content2 and pair[1] in content1):
                return True
        
        # Check for direct opposite concepts
        if "round" in content1 and "flat" in content2:
            return True
        if "flat" in content1 and "round" in content2:
            return True
            
        return False
