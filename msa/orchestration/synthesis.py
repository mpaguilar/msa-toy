"""Result synthesis engine for combining facts into coherent answers."""

import logging

from msa.memory.models import Fact, WorkingMemory
from msa.orchestration.confidence import ConfidenceScorer

log = logging.getLogger(__name__)


class SynthesisEngine:
    """Synthesizes answers from collected facts with confidence scoring and conflict resolution."""

    def __init__(self) -> None:
        """Initialize the synthesis engine.

        Notes:
            1. Logs a debug message indicating initialization has started.
            2. Initializes the ConfidenceScorer instance for use in confidence calculations.
            3. Logs a debug message indicating initialization has completed.

        """
        _msg = "SynthesisEngine initializing"
        log.debug(_msg)

        self.confidence_scorer = ConfidenceScorer()

        _msg = "SynthesisEngine initialized"
        log.debug(_msg)

    def synthesize_answer(self, memory: WorkingMemory, query: str) -> str:
        """Generate an answer from collected facts.

        Args:
            memory: The working memory containing collected facts
            query: The original query to answer

        Returns:
            A synthesized answer string with confidence scoring and citations.
            If no facts are available, returns a default message indicating no information was gathered.

        Notes:
            1. Logs a debug message indicating the synthesis process has started.
            2. Retrieves all facts from the memory's information store.
            3. If no facts are found, returns a default message and exits.
            4. Eliminates duplicate facts using the eliminate_redundancy method.
            5. Constructs a narrative from the unique facts using the construct_narrative method.
            6. Generates citations for the facts using the generate_citations method.
            7. Calculates confidence scores for the answer using the confidence scorer.
            8. Generates a confidence report based on the calculated scores.
            9. Combines the narrative, confidence report, and citations into a single answer string.
            10. Logs a debug message indicating the synthesis process has completed.
            11. Returns the final synthesized answer.

        """
        _msg = "synthesize_answer starting"
        log.debug(_msg)

        # Get all facts from memory
        facts = list(memory.information_store.facts.values())

        if not facts:
            _msg = "No facts available for synthesis"
            log.debug(_msg)
            return "Unable to synthesize an answer: No information was gathered."

        # Eliminate redundancy
        unique_facts = self.eliminate_redundancy(facts)

        # Construct narrative
        narrative = self.construct_narrative(unique_facts, query)

        # Generate citations
        citations = self.generate_citations(unique_facts)

        # Calculate confidence score
        confidence_data = self.confidence_scorer.calculate_confidence_score(
            memory,
            query,
        )
        confidence_report = self.confidence_scorer.generate_confidence_report(
            confidence_data,
        )

        # Combine everything into final answer
        answer = f"{narrative}\n\n{confidence_report}\n\n{citations}"

        _msg = "synthesize_answer returning"
        log.debug(_msg)
        return answer

    def eliminate_redundancy(self, facts: list[Fact]) -> list[Fact]:
        """Remove duplicate information from collected facts.

        Args:
            facts: List of facts to process

        Returns:
            List of unique facts with redundancy removed.

        Notes:
            1. Currently returns all input facts without any deduplication.
            2. Intended to be extended with logic to identify and eliminate duplicate facts.

        """
        _msg = "eliminate_redundancy starting"
        log.debug(_msg)

        # For now, return all facts - could implement deduplication logic later
        unique_facts = facts

        _msg = "eliminate_redundancy returning"
        log.debug(_msg)
        return unique_facts

    def construct_narrative(self, facts: list[Fact], query: str) -> str:
        """Build a coherent response from discrete facts.

        Args:
            facts: List of facts to construct narrative from
            query: The original query to answer

        Returns:
            A coherent narrative string summarizing the facts.
            If no facts are provided, returns a default message indicating no information was found.

        Notes:
            1. Checks if the list of facts is empty and returns a default message if so.
            2. Creates a list of formatted fact strings using a bullet point format.
            3. Combines the bullet points into a single narrative string.
            4. Returns the narrative string.

        """
        _msg = "construct_narrative starting"
        log.debug(_msg)

        # Simple implementation - just list the facts
        if not facts:
            return "No relevant information found."

        fact_strings = [f"- {fact.content}" for fact in facts]
        narrative = "Based on the information gathered:\n" + "\n".join(fact_strings)

        _msg = "construct_narrative returning"
        log.debug(_msg)
        return narrative

    def generate_citations(self, facts: list[Fact]) -> str:
        """Create source attributions for claims with timestamp tracking.

        Args:
            facts: List of facts to generate citations for

        Returns:
            Formatted citations string including source names and retrieval timestamps.
            Returns an empty string if no facts are provided.

        Notes:
            1. Checks if the list of facts is empty and returns an empty string if so.
            2. Initializes a list with the header "## Sources:".
            3. For each fact, appends a citation entry with source name and timestamp (if available).
            4. Joins all citation entries into a single string, skipping the header if no citations were added.
            5. Returns the formatted citations string.

        """
        _msg = "generate_citations starting"
        log.debug(_msg)

        if not facts:
            return ""

        citations = ["## Sources:"]
        for i, fact in enumerate(facts, 1):
            if fact.source:
                citation = f"{i}. {fact.source}"
                if fact.timestamp:
                    citation += f" (Retrieved: {fact.timestamp})"
                citations.append(citation)

        result = "\n".join(citations) if len(citations) > 1 else ""

        _msg = "generate_citations returning"
        log.debug(_msg)
        return result
