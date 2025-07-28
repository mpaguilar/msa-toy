"""
Pydantic models for the working memory components.
"""

import logging
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict

log = logging.getLogger(__name__)

if TYPE_CHECKING:
    pass


class QueryRefinement(BaseModel):
    """Represents a refinement of a query."""

    original: str
    refined: str
    reason: str


class QueryState(BaseModel):
    """Track query management state."""

    original_query: str
    refined_queries: List[str]
    query_history: List[QueryRefinement]
    current_focus: str


class ActionRecord(BaseModel):
    """Represents a recorded action."""

    action_type: str
    timestamp: datetime
    parameters: Dict[str, Any]
    result: Optional[Any] = None


class ToolCall(BaseModel):
    """Represents a tool call."""

    tool_name: str
    parameters: Dict[str, Any]
    timestamp: datetime


class ToolResponse(BaseModel):
    """Represents a response from a tool."""

    tool_name: str
    response_data: Dict[str, Any]
    timestamp: datetime
    metadata: Dict[str, Any]


class Fact(BaseModel):
    """Represents a fact in the information store."""

    id: str
    content: str
    source: str
    timestamp: datetime
    confidence: float


class Relationship(BaseModel):
    """Represents a relationship between facts."""

    id: str
    subject: str
    predicate: str
    object: str
    confidence: float


class SourceMetadata(BaseModel):
    """Metadata about an information source."""

    id: str
    url: Optional[str] = None
    credibility: float
    retrieval_date: datetime


class InformationStore(BaseModel):
    """Store facts, relationships, and sources."""

    facts: Dict[str, Fact]
    relationships: Dict[str, Relationship]
    sources: Dict[str, SourceMetadata]
    confidence_scores: Dict[str, float]


class ReasoningState(BaseModel):
    """Track reasoning process state."""

    current_hypothesis: str
    answer_draft: str
    information_gaps: List[str]
    next_steps: List[str]
    termination_criteria_met: bool


class ExecutionHistory(BaseModel):
    """Track execution history."""

    actions_taken: List[ActionRecord]
    timestamps: Dict[str, datetime]
    tool_call_sequence: List[ToolCall]
    intermediate_results: List[ToolResponse]


class WorkingMemory(BaseModel):
    """Main container for all memory components."""

    query_state: QueryState
    execution_history: "ExecutionHistory"
    information_store: InformationStore
    reasoning_state: ReasoningState
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(arbitrary_types_allowed=True)
