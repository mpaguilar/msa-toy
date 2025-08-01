"""Observation handler for the multi-step agent controller."""

import logging

from msa.tools.base import ToolResponse

log = logging.getLogger(__name__)


def process_observation(action_result: ToolResponse) -> str:
    """Process observation from action result.

    Args:
        action_result: The result from executing an action, containing the content to be observed.

    Returns:
        A string representing the processed observation, formatted as "Observed: <content>".

    Notes:
        1. Extract the content from the action_result object.
        2. Format the content into a string prefixed with "Observed: ".
        3. Return the formatted observation string.

    """
    _msg = "process_observation starting"
    log.debug(_msg)

    # Process the tool response into an observation
    observation = f"Observed: {action_result.content}"

    _msg = "process_observation returning"
    log.debug(_msg)
    return observation
