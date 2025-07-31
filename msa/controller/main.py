"""Main controller implementation for the multi-step agent."""

# Import the refactored controller
from msa.controller.components import Controller
from msa.llm.client import LLMClient
from msa.tools.web_search import WebSearchTool
from msa.tools.wikipedia import WikipediaTool

# For backward compatibility, we can still expose the same interface
__all__ = ['Controller', 'LLMClient', 'WebSearchTool', 'WikipediaTool']
