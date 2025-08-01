"""Pydantic models for the working memory components."""

import logging
from datetime import datetime
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, ConfigDict

log = logging.getLogger(__name__)

if TYPE_CHECKING:
    pass


class QueryRefinement(BaseModel):
    """Represents a refinement of a query."""

    original: str
    """The original query string before refinement."""

    refined: str
    """The refined version of the query, optimized for better retrieval or understanding."""

    reason: str
    """Explanation for why the query was refined in this way."""


class QueryState(BaseModel):
    """Track query management state."""

    original_query: str
    """The initial query provided by the user."""

    refined_queries: list[str]
    """List of refined versions of the original query, generated during query expansion or iteration."""

    query_history: list[QueryRefinement]
    """History of query refinements, including original, refined version, and reasoning."""

    current_focus: str
    """The current focus of the query, indicating the most relevant direction of inquiry."""


class ActionRecord(BaseModel):
    """Represents a recorded action."""

    action_type: str
    """The type of action performed (e.g., 'tool_call', 'query_refinement', 'synthesis')."""

    timestamp: datetime
    """The time at which the action was executed."""

    parameters: dict[str, Any]
    """A dictionary of parameters passed to the action."""

    result: Any | None = None
    """The result of the action, if available. May be None if no result was returned."""


class ToolCall(BaseModel):
    """Represents a tool call."""

    tool_name: str
    """The name of the tool being called."""

    parameters: dict[str, Any]
    """The parameters passed to the tool during the call."""

    timestamp: datetime
    """The time at which the tool call was made."""


class ToolResponse(BaseModel):
    """Represents a response from a tool."""

    tool_name: str
    """The name of the tool that generated the response."""

    response_data: dict[str, Any]
    """The actual data returned by the tool."""

    timestamp: datetime
    """The time at which the response was received."""

    metadata: dict[str, Any]
    """Additional metadata associated with the response (e.g., latency, status codes)."""


class Fact(BaseModel):
    """Represents a fact in the information store."""

    id: str
    """A unique identifier for the fact."""

    content: str
    """The textual content or statement of the fact."""

    source: str
    """The identifier of the source from which the fact was derived."""

    timestamp: datetime
    """The time at which the fact was added or extracted."""

    confidence: float
    """A score between 0 and 1 indicating the reliability or certainty of the fact."""


class Relationship(BaseModel):
    """Represents a relationship between facts."""

    id: str
    """A unique identifier for the relationship."""

    subject: str
    """The ID of the fact that serves as the subject of the relationship."""

    predicate: str
    """The nature of the relationship (e.g., 'causes', 'located_in', 'related_to')."""

    object: str
    """The ID of the fact that serves as the object of the relationship."""

    confidence: float
    """A score between 0 and 1 indicating the reliability of the relationship."""


class SourceMetadata(BaseModel):
    """Metadata about an information source."""

    id: str
    """A unique identifier for the source."""

    url: str | None = None
    """The URL of the source, if available."""

    credibility: float
    """A score between 0 and 1 indicating the trustworthiness of the source."""

    retrieval_date: datetime
    """The date and time when the source was retrieved."""


class InformationStore(BaseModel):
    """Store facts, relationships, and sources."""

    facts: dict[str, Fact]
    """A dictionary mapping fact IDs to their Fact objects."""

    relationships: dict[str, Relationship]
    """A dictionary mapping relationship IDs to their Relationship objects."""

    sources: dict[str, SourceMetadata]
    """A dictionary mapping source IDs to their SourceMetadata objects."""

    confidence_scores: dict[str, float]
    """A dictionary mapping entity IDs (facts, relationships) to confidence scores."""


class ReasoningState(BaseModel):
    """Track reasoning process state."""

    current_hypothesis: str
    """The currently active hypothesis being evaluated or tested."""

    answer_draft: str
    """A draft of the final answer being constructed during reasoning."""

    information_gaps: list[str]
    """List of topics or facts that are missing and required to complete reasoning."""

    next_steps: list[str]
    """A list of actions or steps to be taken next in the reasoning process."""

    termination_criteria_met: bool
    """Indicates whether all conditions for ending reasoning have been satisfied."""

    temporal_context: dict[str, Any] = {}
    """A context dictionary preserving temporal or state information relevant to reasoning."""


class ExecutionHistory(BaseModel):
    """Track execution history."""

    actions_taken: list[ActionRecord]
    """List of all actions that have been executed during the current session."""

    timestamps: dict[str, datetime]
    """Dictionary mapping action types or IDs to their execution timestamps."""

    tool_call_sequence: list[ToolCall]
    """Sequence of tool calls in chronological order."""

    intermediate_results: list[ToolResponse]
    """List of responses received from tools during execution."""


class WorkingMemory(BaseModel):
    """Main container for all memory components."""

    query_state: QueryState
    """Current state of the query, including original, refined versions, and history."""

    execution_history: "ExecutionHistory"
    """History of all actions, tool calls, and intermediate results during execution."""

    information_store: InformationStore
    """Central repository for facts, relationships, and source metadata."""

    reasoning_state: ReasoningState
    """Current state of the reasoning process, including hypothesis, gaps, and steps."""

    created_at: datetime
    """Timestamp when the WorkingMemory instance was created."""

    updated_at: datetime
    """Timestamp when the WorkingMemory instance was last updated."""

    model_config = ConfigDict(arbitrary_types_allowed=True)
