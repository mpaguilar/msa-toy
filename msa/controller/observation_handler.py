"""Observation handler for the multi-step agent controller."""

import logging
from msa.tools.base import ToolResponse

log = logging.getLogger(__name__)


def process_observation(action_result: ToolResponse) -> str:
    """Process observation from action result.
    
    Args:
        action_result: The result from executing an action
        
    Returns:
        Processed observation as a string
    """
    _msg = "process_observation starting"
    log.debug(_msg)
    
    # Process the tool response into an observation
    observation = f"Observed: {action_result.content}"
    
    _msg = "process_observation returning"
    log.debug(_msg)
    return observation
