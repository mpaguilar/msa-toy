"""Pydantic models for controller decisions in the multi-step agent."""

import logging
from typing import List, Optional
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
        This model represents the controller's decision about what action to take next
        in the reasoning process. It includes both the action to take and the reasoning
        behind that decision.
    """
    
    action_type: str = Field(..., description="The type of action to take")
    action_name: str = Field(..., description="The specific action or tool name to use")
    reasoning: str = Field(..., description="The reasoning behind this action selection")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score for this action selection")


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
        This model represents a refined version of the original query that is better
        suited for tool usage. It includes the reasoning behind the refinement to
        maintain transparency in the agent's decision-making process.
    """
    
    original_query: str = Field(..., description="The original query provided by the user")
    refined_query: str = Field(..., description="The refined query for tool usage")
    reasoning: str = Field(..., description="The reasoning behind this query refinement")
    context: Optional[str] = Field(None, description="Additional context to help with the refinement")


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
        This model represents the controller's decision about whether the task is complete.
        If complete, it includes the final answer. If not complete, it includes the remaining
        tasks that need to be addressed.
    """
    
    is_complete: bool = Field(..., description="Whether the task is considered complete")
    answer: str = Field("", description="The final answer if complete, otherwise empty")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score for the completion decision")
    reasoning: str = Field(..., description="The reasoning behind this completion decision")
    remaining_tasks: List[str] = Field([], description="List of remaining tasks if not complete")
