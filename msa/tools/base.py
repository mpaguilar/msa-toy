"""Base tool interface and response models for the multi-step agent."""

import logging
from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel

log = logging.getLogger(__name__)


from datetime import datetime


class ToolResponse(BaseModel):
    """Standardized tool response model."""

    tool_name: str = ""
    response_data: dict[str, Any] = {}
    metadata: dict[str, Any] = {}
    raw_response: dict[str, Any] = {}
    content: str = ""
    timestamp: Any = None

    def __init__(self, **data: Any) -> None:
        """Initialize ToolResponse with timestamp if not provided.

        Args:
            **data: Arbitrary keyword arguments to initialize the ToolResponse.

        Returns:
            None

        Notes:
            1. If the 'timestamp' key is not present in data or is None, set it to the current datetime.
            2. Call the parent class initializer with the updated data.

        """
        if "timestamp" not in data or data["timestamp"] is None:
            data["timestamp"] = datetime.now()
        super().__init__(**data)


class ToolInterface(ABC):
    """Abstract base class for all tools."""

    @abstractmethod
    def execute(self, query: str) -> ToolResponse:
        """Execute tool with standardized input/output.

        Args:
            query: The query string to process.

        Returns:
            ToolResponse: Standardized response from the tool containing tool name, response data, metadata, raw response, content, and timestamp.

        Notes:
            1. The function must process the input query using the tool's internal logic.
            2. It must return a ToolResponse object with the results of the operation.
            3. The response must include the tool's name, processed data, metadata, raw response, content, and a timestamp.

        """
        pass

    @abstractmethod
    def validate_response(self, response: dict) -> bool:
        """Check if response contains valid data.

        Args:
            response: The raw response dictionary to validate.

        Returns:
            bool: True if the response contains valid data, False otherwise.

        Notes:
            1. Analyze the provided response dictionary for structure and meaningful content.
            2. Return True if the response is valid (e.g., has required keys, non-empty data, etc.).
            3. Return False if the response is invalid (e.g., missing keys, empty, malformed, etc.).

        """
        pass
