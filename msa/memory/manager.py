"""
Working memory management implementation.
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List

from msa.memory.models import (
    ExecutionHistory,
    Fact,
    InformationStore,
    QueryState,
    ReasoningState,
    SourceMetadata,
    WorkingMemory,
)

log = logging.getLogger(__name__)


class WorkingMemoryManager:
    """Manages the working memory operations for the multi-step agent."""

    def __init__(self, initial_query: str = "") -> None:
        """
        Initialize memory manager.

        Args:
            initial_query: The initial query to start with
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
                facts={}, relationships={}, sources={}, confidence_scores={}
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

        _msg = "WorkingMemoryManager.__init__ returning"
        log.debug(_msg)

    def add_observation(self, observation: Dict[str, Any]) -> None:
        """
        Add new observation to working memory.

        Args:
            observation: Dictionary containing observation data with keys:
                - content: The observed fact content
                - source: Source of the observation
                - confidence: Confidence score (0.0-1.0)
                - metadata: Additional metadata about the observation
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

        _msg = "WorkingMemoryManager.add_observation returning"
        log.debug(_msg)

    def get_relevant_facts(self, context: str) -> List[Dict[str, Any]]:
        """
        Retrieve relevant facts based on context.

        Args:
            context: Context string to match against facts

        Returns:
            List of relevant facts as dictionaries
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
                    }
                )

        _msg = "WorkingMemoryManager.get_relevant_facts returning"
        log.debug(_msg)
        return relevant_facts

    def update_confidence_scores(self) -> None:
        """
        Update confidence scores based on new evidence and source credibility.
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
        """
        Serialize memory to JSON string.

        Returns:
            JSON string representation of the working memory
        """
        _msg = "WorkingMemoryManager.serialize starting"
        log.debug(_msg)

        # Convert to dict and then to JSON
        serialized = self.memory.model_dump_json()

        _msg = "WorkingMemoryManager.serialize returning"
        log.debug(_msg)
        return serialized

    def deserialize(self, data: str) -> WorkingMemory:
        """
        Deserialize memory from JSON string.

        Args:
            data: JSON string representation of working memory

        Returns:
            WorkingMemory object
        """
        _msg = "WorkingMemoryManager.deserialize starting"
        log.debug(_msg)

        # Parse JSON and create WorkingMemory object
        memory_dict = json.loads(data)
        working_memory = WorkingMemory.model_validate(memory_dict)

        # Update the current memory
        self.memory = working_memory

        _msg = "WorkingMemoryManager.deserialize returning"
        log.debug(_msg)
        return working_memory
