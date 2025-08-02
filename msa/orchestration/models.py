import logging
from typing import List
from pydantic import BaseModel

log = logging.getLogger(__name__)


class SynthesizedAnswer(BaseModel):
    """Model for the final synthesized answer with reasoning."""
    answer: str
    reasoning_steps: List[str]
    confidence: float
