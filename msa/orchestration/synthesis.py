"""Result synthesis engine for combining facts into coherent answers."""

import logging
from typing import List

from msa.memory.models import WorkingMemory, Fact
from msa.orchestration.confidence import ConfidenceScorer

log = logging.getLogger(__name__)


class SynthesisEngine:
    """Synthesizes answers from collected facts with confidence scoring and conflict resolution."""

    def __init__(self) -> None:
        """Initialize the synthesis engine."""
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
            A synthesized answer string with confidence scoring and citations
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
        confidence_report = self.confidence_scorer.generate_confidence_report(memory, query)
        
        # Combine everything into final answer
        answer = f"{narrative}\n\n{confidence_report}\n\n{citations}"
        
        _msg = "synthesize_answer returning"
        log.debug(_msg)
        return answer

    def eliminate_redundancy(self, facts: List[Fact]) -> List[Fact]:
        """Remove duplicate information from collected facts.
        
        Args:
            facts: List of facts to process
            
        Returns:
            List of unique facts with redundancy removed
        """
        _msg = "eliminate_redundancy starting"
        log.debug(_msg)
        
        # For now, return all facts - could implement deduplication logic later
        unique_facts = facts
        
        _msg = "eliminate_redundancy returning"
        log.debug(_msg)
        return unique_facts

    def construct_narrative(self, facts: List[Fact], query: str) -> str:
        """Build a coherent response from discrete facts.
        
        Args:
            facts: List of facts to construct narrative from
            query: The original query to answer
            
        Returns:
            A coherent narrative string
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

    def generate_citations(self, facts: List[Fact]) -> str:
        """Create source attributions for claims with timestamp tracking.
        
        Args:
            facts: List of facts to generate citations for
            
        Returns:
            Formatted citations string
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
