"""Conflict detection and resolution for multi-step agent."""

import logging
from typing import Any, Dict, List

from msa.memory.models import Fact, WorkingMemory

log = logging.getLogger(__name__)


class ConflictResolver:
    """Handles detection and resolution of contradictory information."""

    def __init__(self) -> None:
        """Initialize the conflict resolver.

        Notes:
            1. Initialize the conflict resolver instance.
            2. Log the start of initialization.
            3. Log the completion of initialization.

        """
        _msg = "ConflictResolver.__init__ starting"
        log.debug(_msg)
        _msg = "ConflictResolver.__init__ returning"
        log.debug(_msg)

    def detect_conflicts(self, memory: WorkingMemory) -> list[dict[str, Any]]:
        """Identify contradictory claims in the working memory.

        Args:
            memory: The working memory containing facts to check for conflicts

        Returns:
            A list of detected conflicts with details about contradictory facts.
            Each conflict is a dictionary with keys:
                - fact1: The first conflicting fact (Fact)
                - fact2: The second conflicting fact (Fact)
                - type: The type of conflict (str)
                - description: A human-readable description of the contradiction (str)

        Notes:
            1. Retrieve all facts from the working memory's information store.
            2. Compare each fact with every other fact in the list.
            3. For each pair of facts, check if they are contradictory using _are_contradictory.
            4. If a contradiction is found, create a conflict dictionary and add it to the list.
            5. Return the list of detected conflicts.

        """
        _msg = "ConflictResolver.detect_conflicts starting"
        log.debug(_msg)

        conflicts = []
        facts = list(memory.information_store.facts.values())

        # Compare each fact with every other fact to find contradictions
        for i, fact1 in enumerate(facts):
            for fact2 in facts[i + 1 :]:
                if self._are_contradictory(fact1, fact2):
                    conflicts.append(
                        {
                            "fact1": fact1,
                            "fact2": fact2,
                            "type": "contradiction",
                            "description": f"Contradiction between '{fact1.content}' and '{fact2.content}'",
                        },
                    )

        _msg = f"ConflictResolver.detect_conflicts returning with {len(conflicts)} conflicts found"
        log.debug(_msg)
        return conflicts

    def investigate_conflicts(
        self,
        conflicts: list[dict[str, Any]],
        memory: WorkingMemory,
    ) -> list[dict[str, Any]]:
        """Gather additional context to investigate detected conflicts.

        Args:
            conflicts: List of detected conflicts to investigate
            memory: The working memory containing facts

        Returns:
            A list of investigation results with additional context.
            Each result is a dictionary with keys:
                - conflict: The original conflict dictionary
                - investigation: A description of the investigation performed (str)
                - sources: List of source identifiers for the conflicting facts (List[str])

        Notes:
            1. Iterate over each conflict in the provided list.
            2. For each conflict, create an investigation result dictionary.
            3. In this implementation, the investigation is simulated.
            4. The sources are taken directly from the conflicting facts.
            5. Return the list of investigation results.

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
                "sources": [conflict["fact1"].source, conflict["fact2"].source],
            }
            investigation_results.append(investigation_result)

        _msg = f"ConflictResolver.investigate_conflicts returning with {len(investigation_results)} investigations"
        log.debug(_msg)
        return investigation_results

    def resolve_conflicts(
        self,
        investigations: list[dict[str, Any]],
        memory: WorkingMemory,
    ) -> list[dict[str, Any]]:
        """Weight and resolve contradictory information based on source reliability.

        Args:
            investigations: List of conflict investigations with additional context
            memory: The working memory containing facts

        Returns:
            A list of resolved conflicts with weighted decisions.
            Each resolution is a dictionary with keys:
                - preferred_fact: The fact selected as correct (Fact)
                - rejected_fact: The fact selected as incorrect (Fact)
                - reasoning: Explanation for the selection (str)

        Notes:
            1. Iterate over each investigation result.
            2. Extract the conflicting facts from the investigation.
            3. Compare the confidence scores of the two facts.
            4. If one fact has higher confidence, select it as preferred.
            5. If confidence scores are equal, prefer the first encountered fact.
            6. Generate a reasoning string explaining the decision.
            7. Create a resolution dictionary and add it to the list.
            8. Return the list of resolutions.

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
                    "reasoning": f"Fact 1 has higher confidence ({fact1.confidence}) than Fact 2 ({fact2.confidence})",
                }
            elif fact2.confidence > fact1.confidence:
                resolution = {
                    "preferred_fact": fact2,
                    "rejected_fact": fact1,
                    "reasoning": f"Fact 2 has higher confidence ({fact2.confidence}) than Fact 1 ({fact1.confidence})",
                }
            else:
                # Equal confidence - could use other criteria
                resolution = {
                    "preferred_fact": fact1,
                    "rejected_fact": fact2,
                    "reasoning": "Facts have equal confidence, keeping first encountered",
                }

            resolutions.append(resolution)

        _msg = f"ConflictResolver.resolve_conflicts returning with {len(resolutions)} resolutions"
        log.debug(_msg)
        return resolutions

    def synthesize_with_uncertainty(
        self,
        facts: list[Fact],
        conflicts: list[dict[str, Any]],
    ) -> str:
        """Create nuanced answers that acknowledge uncertainties.

        Args:
            facts: List of facts to synthesize
            conflicts: List of unresolved conflicts

        Returns:
            A synthesized answer that acknowledges uncertainties.
            The string contains a bullet list of facts with confidence scores,
            followed by a note about conflicting claims if conflicts exist.

        Notes:
            1. If no facts are provided, return a default message.
            2. Start with a header line.
            3. Add each fact as a bullet point with confidence score.
            4. If conflicts exist, append a note about uncertainty and verification recommendation.
            5. Return the synthesized string.

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
            synthesis += (
                "\nNote: There are conflicting claims in the information gathered. "
            )
            synthesis += (
                "The confidence scores above indicate our assessment of reliability, "
            )
            synthesis += (
                "but you should verify critical information from authoritative sources."
            )

        _msg = "ConflictResolver.synthesize_with_uncertainty returning"
        log.debug(_msg)
        return synthesis

    def _are_contradictory(self, fact1: Fact, fact2: Fact) -> bool:
        """Check if two facts are contradictory.

        Args:
            fact1: First fact to compare
            fact2: Second fact to compare

        Returns:
            True if facts are contradictory, False otherwise

        Notes:
            1. Convert both fact contents to lowercase for case-insensitive comparison.
            2. Check for predefined contradictory keyword pairs.
            3. If a matching pair is found, return True.
            4. Check for direct opposite concepts (e.g., "round" vs "flat").
            5. If no contradiction is found, return False.

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
            ("is flat", "is round"),
        ]

        for pair in contradictory_pairs:
            if (pair[0] in content1 and pair[1] in content2) or (
                pair[0] in content2 and pair[1] in content1
            ):
                return True

        # Check for direct opposite concepts
        if "round" in content1 and "flat" in content2:
            return True
        if "flat" in content1 and "round" in content2:
            return True

        return False
