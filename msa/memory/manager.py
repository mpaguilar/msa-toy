"""Working memory management implementation."""

import json
import logging
from datetime import datetime
from typing import Any

from msa.memory.models import (
    ExecutionHistory,
    Fact,
    InformationStore,
    QueryState,
    ReasoningState,
    SourceMetadata,
    WorkingMemory,
)
from msa.memory.temporal import TemporalReasoner

log = logging.getLogger(__name__)


class WorkingMemoryManager:
    """Manages the working memory operations for the multi-step agent."""

    def __init__(self, initial_query: str = "") -> None:
        """Initialize memory manager.

        Args:
            initial_query: The initial query to start with, used to initialize the query state.

        Returns:
            None

        Notes:
            1. Creates a new empty working memory structure with default values.
            2. Initializes the temporal reasoner to handle temporal reasoning.
            3. Sets memory management settings: maximum number of facts and confidence threshold for pruning.
            4. Logs the initialization start and completion.

        """
        _msg = "WorkingMemoryManager.__init__ starting"
        log.debug(_msg)

        # Create empty working memory structure
        self.memory = WorkingMemory(
            query_state=QueryState(
                original_query=initial_query,
                refined_queries=[],
                query_history=[],
                current_focus=initial_query,
            ),
            execution_history=ExecutionHistory(
                actions_taken=[],
                timestamps={"created": datetime.now()},
                tool_call_sequence=[],
                intermediate_results=[],
            ),
            information_store=InformationStore(
                facts={},
                relationships={},
                sources={},
                confidence_scores={},
            ),
            reasoning_state=ReasoningState(
                current_hypothesis="",
                answer_draft="",
                information_gaps=[],
                next_steps=[],
                termination_criteria_met=False,
            ),
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        self.temporal_reasoner = TemporalReasoner()

        # Memory management settings
        self.max_facts = 100  # Maximum number of facts to keep
        self.prune_threshold = 0.3  # Confidence threshold for pruning

        _msg = "WorkingMemoryManager.__init__ returning"
        log.debug(_msg)

    def add_observation(self, observation: dict[str, Any]) -> None:
        """Add new observation to working memory.

        Args:
            observation: Dictionary containing observation data with keys:
                - content: The observed fact content
                - source: Source of the observation
                - confidence: Confidence score (0.0-1.0)
                - metadata: Additional metadata about the observation

        Returns:
            None

        Notes:
            1. Generates a unique fact ID based on the current number of facts.
            2. Creates a new Fact object from the observation data.
            3. Adds the fact to the information store.
            4. Adds confidence score to the confidence scores dictionary.
            5. If source is not already in sources, creates a new SourceMetadata object and adds it.
            6. Updates the last updated timestamp.
            7. Checks if the number of facts exceeds the maximum, and if so, triggers pruning.

        """
        _msg = "WorkingMemoryManager.add_observation starting"
        log.debug(_msg)

        # Create a new fact from the observation
        fact_id = f"fact_{len(self.memory.information_store.facts) + 1}"
        timestamp = datetime.now()

        fact = Fact(
            id=fact_id,
            content=observation.get("content", ""),
            source=observation.get("source", "unknown"),
            timestamp=timestamp,
            confidence=observation.get("confidence", 0.0),
        )

        # Add fact to information store
        self.memory.information_store.facts[fact_id] = fact

        # Add confidence score
        self.memory.information_store.confidence_scores[fact_id] = fact.confidence

        # Add source metadata if provided
        source_id = observation.get("source", "unknown")
        if source_id not in self.memory.information_store.sources:
            source_metadata = SourceMetadata(
                id=source_id,
                credibility=observation.get("source_credibility", 0.5),
                retrieval_date=timestamp,
            )
            self.memory.information_store.sources[source_id] = source_metadata

        # Update timestamp
        self.memory.updated_at = timestamp

        # Check if we need to prune memory
        if len(self.memory.information_store.facts) > self.max_facts:
            self.prune_memory()

        _msg = "WorkingMemoryManager.add_observation returning"
        log.debug(_msg)

    def get_relevant_facts(self, context: str) -> list[dict[str, Any]]:
        """Retrieve relevant facts based on context.

        Args:
            context: Context string to match against facts for relevance.

        Returns:
            List of relevant facts as dictionaries with keys:
                - id: The fact ID
                - content: The fact content
                - source: The source of the fact
                - confidence: The confidence score of the fact
                - timestamp: The timestamp of the fact in ISO format

        Notes:
            1. Converts the context to lowercase for case-insensitive matching.
            2. Iterates through all facts in the information store.
            3. Checks if the context appears in the fact content or source.
            4. If a match is found, constructs a dictionary with fact details and adds it to the result list.
            5. Returns the list of relevant facts.

        """
        _msg = "WorkingMemoryManager.get_relevant_facts starting"
        log.debug(_msg)

        relevant_facts = []

        # Simple keyword matching for relevance (in a real implementation,
        # this would use more sophisticated methods like embeddings)
        context_lower = context.lower()
        for fact_id, fact in self.memory.information_store.facts.items():
            if (
                context_lower in fact.content.lower()
                or context_lower in fact.source.lower()
            ):
                relevant_facts.append(
                    {
                        "id": fact.id,
                        "content": fact.content,
                        "source": fact.source,
                        "confidence": fact.confidence,
                        "timestamp": fact.timestamp.isoformat(),
                    },
                )

        _msg = "WorkingMemoryManager.get_relevant_facts returning"
        log.debug(_msg)
        return relevant_facts

    def infer_relationships(self) -> None:
        """Infer relationships between facts in working memory.

        Args:
            None

        Returns:
            None

        Notes:
            1. Retrieves all facts from the information store.
            2. Uses the temporal reasoner to correlate temporal facts and detect causal relationships.
            3. Combines the temporal and causal relationships into a single list.
            4. Adds each relationship to the information store's relationships dictionary.
            5. Updates the temporal context in the reasoning state using the temporal reasoner.

        """
        _msg = "WorkingMemoryManager.infer_relationships starting"
        log.debug(_msg)

        # Get all facts
        facts = list(self.memory.information_store.facts.values())

        # Infer temporal relationships
        temporal_relationships = self.temporal_reasoner.correlate_temporal_facts(facts)

        # Infer causal relationships
        causal_relationships = self.temporal_reasoner.detect_causality(
            facts,
            self.memory,
        )

        # Add relationships to information store
        all_relationships = temporal_relationships + causal_relationships
        for relationship in all_relationships:
            relationship_id = f"{relationship['type']}_{relationship['fact1_id']}_{relationship['fact2_id']}"
            self.memory.information_store.relationships[relationship_id] = relationship  # type: ignore

        # Update temporal context in reasoning state
        temporal_context = self.temporal_reasoner.get_temporal_context(self.memory)
        self.memory.reasoning_state.temporal_context = temporal_context

        _msg = "WorkingMemoryManager.infer_relationships returning"
        log.debug(_msg)

    def update_confidence_scores(self) -> None:
        """Update confidence scores based on new evidence and source credibility.

        Args:
            None

        Returns:
            None

        Notes:
            1. Iterates through all facts in the information store.
            2. Retrieves the source metadata for each fact's source.
            3. If source metadata exists, calculates a new confidence score as the average of the fact's current confidence and the source's credibility.
            4. Updates the confidence score in both the confidence scores dictionary and the fact object.
            5. Updates the last updated timestamp.

        """
        _msg = "WorkingMemoryManager.update_confidence_scores starting"
        log.debug(_msg)

        # Update confidence scores based on source credibility
        for fact_id, fact in self.memory.information_store.facts.items():
            source = self.memory.information_store.sources.get(fact.source)
            if source:
                # Adjust confidence based on source credibility
                updated_confidence = (fact.confidence + source.credibility) / 2
                self.memory.information_store.confidence_scores[fact_id] = (
                    updated_confidence
                )
                # Update the fact's confidence as well
                fact.confidence = updated_confidence

        self.memory.updated_at = datetime.now()

        _msg = "WorkingMemoryManager.update_confidence_scores returning"
        log.debug(_msg)

    def serialize(self) -> str:
        """Serialize memory to JSON string.

        Args:
            None

        Returns:
            JSON string representation of the working memory object.

        Notes:
            1. Uses the model_dump_json method to convert the memory object to a JSON string.
            2. Returns the serialized string.

        """
        _msg = "WorkingMemoryManager.serialize starting"
        log.debug(_msg)

        # Convert to dict and then to JSON
        serialized = self.memory.model_dump_json()

        _msg = "WorkingMemoryManager.serialize returning"
        log.debug(_msg)
        return serialized

    def deserialize(self, data: str) -> WorkingMemory:
        """Deserialize memory from JSON string.

        Args:
            data: JSON string representation of working memory.

        Returns:
            WorkingMemory object reconstructed from the JSON string.

        Notes:
            1. Parses the JSON string into a dictionary.
            2. Uses the model_validate method to create a WorkingMemory object from the dictionary.
            3. Updates the current memory object and the temporal reasoner to match the deserialized state.

        """
        _msg = "WorkingMemoryManager.deserialize starting"
        log.debug(_msg)

        # Parse JSON and create WorkingMemory object
        memory_dict = json.loads(data)
        working_memory = WorkingMemory.model_validate(memory_dict)

        # Update the current memory
        self.memory = working_memory
        self.temporal_reasoner = TemporalReasoner()

        _msg = "WorkingMemoryManager.deserialize returning"
        log.debug(_msg)
        return working_memory

    def prune_memory(self) -> None:
        """Prune memory by removing least relevant facts based on confidence and recency.

        Args:
            None

        Returns:
            None

        Notes:
            1. Retrieves the current list of facts.
            2. If the number of facts is below the maximum, return without pruning.
            3. Scores each fact based on confidence and recency, with confidence weighted more heavily.
            4. Sorts the facts by combined score in descending order.
            5. Determines how many facts to remove based on exceeding the maximum capacity.
            6. Removes the lowest-scoring facts from the information store.
            7. Updates the last updated timestamp.

        """
        _msg = "WorkingMemoryManager.prune_memory starting"
        log.debug(_msg)

        # Get current facts
        facts = list(self.memory.information_store.facts.values())

        # If we're under the threshold, no pruning needed
        if len(facts) <= self.max_facts:
            _msg = "WorkingMemoryManager.prune_memory returning - no pruning needed"
            log.debug(_msg)
            return

        # Score facts based on confidence and recency
        fact_scores = []
        current_time = datetime.now()

        for fact in facts:
            # Calculate recency score (newer facts get higher scores)
            time_diff = (current_time - fact.timestamp).total_seconds()
            # Normalize time difference to a score between 0 and 1 (newer = higher)
            recency_score = max(
                0,
                1 - (time_diff / (24 * 60 * 60)),
            )  # Normalize to 24 hours

            # Get confidence score
            confidence_score = fact.confidence

            # Combined score (weighted average)
            combined_score = 0.7 * confidence_score + 0.3 * recency_score

            fact_scores.append((fact.id, combined_score))

        # Sort by score (highest first)
        fact_scores.sort(key=lambda x: x[1], reverse=True)

        # Determine how many facts to remove
        facts_to_remove = len(facts) - self.max_facts

        # Remove lowest scoring facts
        for i in range(facts_to_remove):
            fact_id = fact_scores[-(i + 1)][0]  # Get the fact ID with lowest score
            if fact_id in self.memory.information_store.facts:
                del self.memory.information_store.facts[fact_id]
            if fact_id in self.memory.information_store.confidence_scores:
                del self.memory.information_store.confidence_scores[fact_id]

        # Update timestamp
        self.memory.updated_at = datetime.now()

        _msg = f"WorkingMemoryManager.prune_memory returning - removed {facts_to_remove} facts"
        log.debug(_msg)

    def get_memory(self) -> WorkingMemory:
        """Get the working memory object.

        Args:
            None

        Returns:
            The WorkingMemory object currently managed by this instance.

        Notes:
            1. Returns the internal memory object stored in the instance.
            2. This allows external access to the full memory state.

        """
        _msg = "WorkingMemoryManager.get_memory starting"
        log.debug(_msg)

        _msg = "WorkingMemoryManager.get_memory returning"
        log.debug(_msg)
        return self.memory

    def summarize_state(self) -> dict[str, Any]:
        """Create a summary of the current memory state for LLM context window management.

        Args:
            None

        Returns:
            Dictionary containing a concise summary of the working memory state with keys:
                - query_state: Dictionary with original_query and current_focus
                - reasoning_state: Dictionary with current_hypothesis, answer_draft, and information_gaps
                - top_facts: List of up to 10 most confident facts with content, confidence, and source
                - memory_stats: Dictionary with total_facts, total_relationships, created_at, and updated_at

        Notes:
            1. Retrieves all facts and sorts them by confidence in descending order.
            2. Takes the top 10 most confident facts for the summary.
            3. Creates a dictionary with the current query state, reasoning state, top facts, and memory statistics.
            4. Limits the number of information gaps to 5 for brevity.
            5. Returns the constructed summary dictionary.

        """
        _msg = "WorkingMemoryManager.summarize_state starting"
        log.debug(_msg)

        # Get top facts by confidence
        facts = list(self.memory.information_store.facts.values())
        facts.sort(key=lambda x: x.confidence, reverse=True)

        # Take top 10 most confident facts
        top_facts = facts[:10]
        fact_summaries = [
            {
                "content": fact.content,
                "confidence": fact.confidence,
                "source": fact.source,
            }
            for fact in top_facts
        ]

        # Create summary
        summary = {
            "query_state": {
                "original_query": self.memory.query_state.original_query,
                "current_focus": self.memory.query_state.current_focus,
            },
            "reasoning_state": {
                "current_hypothesis": self.memory.reasoning_state.current_hypothesis,
                "answer_draft": self.memory.reasoning_state.answer_draft,
                "information_gaps": self.memory.reasoning_state.information_gaps[
                    :5
                ],  # Limit to top 5
            },
            "top_facts": fact_summaries,
            "memory_stats": {
                "total_facts": len(self.memory.information_store.facts),
                "total_relationships": len(self.memory.information_store.relationships),
                "created_at": self.memory.created_at.isoformat(),
                "updated_at": self.memory.updated_at.isoformat(),
            },
        }

        _msg = "WorkingMemoryManager.summarize_state returning"
        log.debug(_msg)
        return summary
