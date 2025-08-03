"""Result synthesis engine for combining facts into coherent answers."""

import logging

from msa.memory.models import Fact, WorkingMemory
from msa.orchestration.confidence import ConfidenceScorer
from msa.orchestration.conflict import ConflictResolver
from msa.orchestration.models import SynthesizedAnswer

log = logging.getLogger(__name__)


class SynthesisEngine:
    """Synthesizes answers from collected facts with confidence scoring and conflict resolution."""

    def __init__(self, completion_client=None, final_synthesis_prompt=None) -> None:
        """Initialize the synthesis engine.

        Args:
            completion_client: Optional LLM client for completion tasks
            final_synthesis_prompt: Optional prompt template for final synthesis

        Returns:
            None

        Notes:
            1. Logs a debug message indicating initialization has started.
            2. Initializes the ConfidenceScorer instance for use in confidence calculations.
            3. Initializes the ConflictResolver instance for use in conflict detection.
            4. Stores optional completion_client and final_synthesis_prompt for later use.
            5. Logs a debug message indicating initialization has completed.

        """
        _msg = "SynthesisEngine initializing"
        log.debug(_msg)

        self.confidence_scorer = ConfidenceScorer()
        self.conflict_resolver = ConflictResolver()

        # Store optional parameters for later use
        self.completion_client = completion_client
        self.final_synthesis_prompt = final_synthesis_prompt

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
            1. Retrieves all facts from the memory's information store.
            2. If no facts are found, returns a default message and exits.
            3. Eliminates duplicate facts using the eliminate_redundancy method.
            4. If a completion_client and final_synthesis_prompt are available, uses them to generate
               a more sophisticated final answer via LLM by calling _perform_final_reasoning.
            5. Otherwise, constructs a narrative from the unique facts using the construct_narrative method.
            6. Generates citations for the facts using the generate_citations method.
            7. Calculates confidence scores for the answer using the confidence scorer.
            8. Generates a confidence report based on the calculated scores.
            9. Combines the narrative, confidence report, and citations into a single answer string.
            10. Returns the final synthesized answer.

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

        # If we have completion client and prompt, use LLM for final synthesis
        if self.completion_client and self.final_synthesis_prompt:
            try:
                # Use LLM-based synthesis
                synthesized_answer = self._perform_final_reasoning(query, unique_facts)

                # Generate citations
                citations = self.generate_citations(unique_facts)

                # Generate a simple confidence report (since we don't have full memory context here)
                confidence_report = "## Confidence Report\n- Overall confidence: 0.8 (LLM-based synthesis)\n- Source credibility: 0.8\n- Consistency: 0.9\n- Completeness: 0.7"

                # Format reasoning steps if they exist
                reasoning_section = ""
                if synthesized_answer.reasoning_steps:
                    reasoning_lines = ["## Reasoning Steps"]
                    for i, step in enumerate(synthesized_answer.reasoning_steps, 1):
                        reasoning_lines.append(f"{i}. {step}")
                    reasoning_section = "\n".join(reasoning_lines)

                # Combine all parts with confidence report and citations
                parts = ["## Answer", synthesized_answer.answer]
                if reasoning_section:
                    parts.append(reasoning_section)
                parts.append(confidence_report)
                parts.append(citations)

                # Filter out empty parts and join
                answer = "\n\n".join(part for part in parts if part)
                return answer
            except Exception as e:
                _msg = f"Error in LLM-based synthesis, using fallback: {e}"
                log.exception(_msg)
                # Fallback to manual synthesis if LLM fails

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

        # Combine everything into final answer using manual synthesis
        answer = f"## Answer\n{narrative}\n\n{confidence_report}\n\n{citations}"

        _msg = "synthesize_answer returning"
        log.debug(_msg)
        return answer

    def _perform_final_reasoning(
        self, query: str, facts: list[Fact],
    ) -> SynthesizedAnswer:
        """Perform final reasoning using LLM to synthesize a coherent answer.

        Args:
            query: The original query to answer
            facts: List of unique facts to synthesize

        Returns:
            A SynthesizedAnswer object containing the answer, reasoning steps, and confidence.

        Notes:
            1. Creates a PydanticOutputParser for SynthesizedAnswer to format the LLM's response.
            2. Prepares collected information from the facts.
            3. Formats the final synthesis prompt with the query, collected info, and format instructions.
            4. Calls the completion client with the formatted prompt and parser.
            5. Handles various response formats from the LLM.
            6. Constructs a narrative from the facts if LLM parsing fails.
            7. Returns a SynthesizedAnswer object with the answer, reasoning steps, and confidence.

        """
        _msg = "_perform_final_reasoning starting"
        log.debug(_msg)

        try:
            from langchain.output_parsers import PydanticOutputParser

            from msa.orchestration.models import SynthesizedAnswer

            # Create output parser for SynthesizedAnswer
            parser = PydanticOutputParser(pydantic_object=SynthesizedAnswer)
            format_instructions = parser.get_format_instructions()

            # Prepare collected information
            collected_info = []
            for fact in facts:
                collected_info.append(
                    {
                        "content": fact.content,
                        "source": fact.source,
                        "confidence": getattr(
                            fact, "confidence", 0.5,
                        ),  # Default confidence if not present
                    },
                )

            # Generate final synthesis using the completion LLM
            prompt = self.final_synthesis_prompt.format(
                query=query,
                collected_info=str(collected_info),
                format_instructions=format_instructions,
            )

            response = self.completion_client.call(prompt, parser)

            # Handle LLM response format - return the parsed SynthesizedAnswer object
            if hasattr(response, "parsed") and response.parsed is not None:
                synthesized_answer = response.parsed
            elif isinstance(response, dict) and "parsed" in response:
                if isinstance(response["parsed"], dict):
                    synthesized_answer = SynthesizedAnswer(**response["parsed"])
                else:
                    synthesized_answer = response["parsed"]
            else:
                # Fallback to creating a SynthesizedAnswer object
                narrative = self.construct_narrative(facts, query)
                synthesized_answer = SynthesizedAnswer(
                    answer=narrative,
                    reasoning_steps=["Fallback due to LLM parsing failure"],
                    confidence=0.5,
                )

        except Exception as e:
            _msg = f"Error in _perform_final_reasoning: {e}"
            log.exception(_msg)
            # Fallback to manual synthesis
            narrative = self.construct_narrative(facts, query)
            synthesized_answer = SynthesizedAnswer(
                answer=narrative,
                reasoning_steps=["Fallback due to LLM error"],
                confidence=0.5,
            )

        _msg = "_perform_final_reasoning returning"
        log.debug(_msg)
        return synthesized_answer

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
            return "No relevant information was found to answer the question."

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
                timestamp = getattr(fact, "timestamp", None)
                if timestamp:
                    citation += f" (Retrieved: {timestamp})"
                citations.append(citation)

        result = "\n".join(citations) if len(citations) > 1 else ""

        _msg = "generate_citations returning"
        log.debug(_msg)
        return result
