"""Base tool interface and response models for the multi-step agent."""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict

from pydantic import BaseModel

log = logging.getLogger(__name__)


from datetime import datetime

class ToolResponse(BaseModel):
    """Standardized tool response model."""

    tool_name: str = ""
    response_data: Dict[str, Any] = {}
    metadata: Dict[str, Any] = {}
    raw_response: Dict[str, Any] = {}
    content: str = ""
    timestamp: Any = None

    def __init__(self, **data: Any) -> None:
        """Initialize ToolResponse with timestamp if not provided."""
        if "timestamp" not in data or data["timestamp"] is None:
            data["timestamp"] = datetime.now()
        super().__init__(**data)


class ToolInterface(ABC):
    """Abstract base class for all tools."""

    @abstractmethod
    def execute(self, query: str) -> ToolResponse:
        """Execute tool with standardized input/output.

        Args:
            query: The query string to process

        Returns:
            ToolResponse: Standardized response from the tool
        """
        pass

    @abstractmethod
    def validate_response(self, response: dict) -> bool:
        """Check if response contains valid data.

        Args:
            response: The raw response dictionary to validate

        Returns:
            bool: True if response is valid, False otherwise
        """
        pass
