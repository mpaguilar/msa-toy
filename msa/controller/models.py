"""Pydantic models for controller decisions in the multi-step agent."""

import logging

from pydantic import BaseModel, Field

log = logging.getLogger(__name__)


class ActionSelection(BaseModel):
    """Model for next action selection by the controller.

    Args:
        action_type: The type of action to take (e.g., "tool_call", "query_refinement")
        action_name: The specific action or tool name to use
        reasoning: The reasoning behind this action selection
        confidence: Confidence score for this action selection (0.0 to 1.0)

    Returns:
        ActionSelection: A model containing the action selection decision

    Notes:
        1. The action_type specifies the category of the next step (e.g., invoking a tool, refining the query).
        2. The action_name identifies the specific tool or function to be used.
        3. The reasoning provides a textual justification for why this particular action was chosen.
        4. The confidence value quantifies the agent's certainty in this decision, ranging from 0.0 (low confidence) to 1.0 (high confidence).
        5. This model encapsulates the controller's decision-making process for the next step in the reasoning chain.

    """

    action_type: str = Field(..., description="The type of action to take")
    action_name: str = Field(..., description="The specific action or tool name to use")
    reasoning: str = Field(
        ...,
        description="The reasoning behind this action selection",
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score for this action selection",
    )


class QueryRefinement(BaseModel):
    """Model for refined questions for tool use.

    Args:
        original_query: The original query provided by the user
        refined_query: The refined query for tool usage
        reasoning: The reasoning behind this query refinement
        context: Additional context to help with the refinement

    Returns:
        QueryRefinement: A model containing the refined query and supporting information

    Notes:
        1. The original_query is the input from the user, which may be ambiguous or too broad.
        2. The refined_query is processed to be more specific, clear, and suitable for tool execution.
        3. The reasoning explains how and why the query was modified, preserving transparency.
        4. The context provides any additional information that influenced the refinement process.
        5. This model supports iterative improvement of queries to ensure accurate tool responses.

    """

    original_query: str = Field(
        ...,
        description="The original query provided by the user",
    )
    refined_query: str = Field(..., description="The refined query for tool usage")
    reasoning: str = Field(
        ...,
        description="The reasoning behind this query refinement",
    )
    context: str | None = Field(
        None,
        description="Additional context to help with the refinement",
    )


class CompletionDecision(BaseModel):
    """Model for completion determination.

    Args:
        is_complete: Whether the task is considered complete
        answer: The final answer if complete, otherwise empty
        confidence: Confidence score for the completion decision (0.0 to 1.0)
        reasoning: The reasoning behind this completion decision
        remaining_tasks: List of remaining tasks if not complete

    Returns:
        CompletionDecision: A model containing the completion decision and supporting information

    Notes:
        1. The is_complete flag indicates whether the current reasoning process satisfies the task requirements.
        2. If complete, the answer field contains the synthesized final response for the user.
        3. The confidence value reflects the agent's certainty that the task is truly complete.
        4. The reasoning explains the justification for the completion decision.
        5. If not complete, the remaining_tasks list enumerates the next steps needed to achieve full completion.
        6. This model enables the agent to self-assess progress and plan further actions.

    """

    is_complete: bool = Field(
        ...,
        description="Whether the task is considered complete",
    )
    answer: str = Field("", description="The final answer if complete, otherwise empty")
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score for the completion decision",
    )
    reasoning: str = Field(
        ...,
        description="The reasoning behind this completion decision",
    )
    remaining_tasks: list[str] = Field(
        [],
        description="List of remaining tasks if not complete",
    )
