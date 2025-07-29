"""Tool selection mechanism for the multi-step agent."""

import logging
from typing import List, Dict, Any
from msa.memory.models import WorkingMemory
from msa.tools.base import ToolInterface
from msa.orchestration.confidence import ConfidenceScorer
from msa.orchestration.conflict import ConflictResolver

log = logging.getLogger(__name__)


class ToolSelector:
    """Tool selection mechanism based on query classification and relevance scoring."""

    def __init__(self, available_tools: Dict[str, ToolInterface]) -> None:
        """Initialize tool selector with available tools.
        
        Args:
            available_tools: Dictionary of available tools by name
        """
        _msg = "ToolSelector.__init__ starting"
        log.debug(_msg)
        
        self.available_tools = available_tools
        self.confidence_scorer = ConfidenceScorer()
        self.conflict_resolver = ConflictResolver()
        
        _msg = "ToolSelector.__init__ returning"
        log.debug(_msg)

    def classify_intent(self, query: str) -> str:
        """Classify query intent to determine appropriate tool category.
        
        Args:
            query: The query to classify
            
        Returns:
            Classified intent category
        """
        _msg = f"ToolSelector.classify_intent starting with query: {query}"
        log.debug(_msg)
        
        # Simple keyword-based classification for now
        query_lower = query.lower()
        if any(word in query_lower for word in ["what is", "who is", "when", "where", "how many", "how much"]):
            result = "factual"
        elif any(word in query_lower for word in ["analyze", "compare", "explain", "why"]):
            result = "analytical"
        elif any(word in query_lower for word in ["code", "program", "function", "script"]):
            result = "coding"
        elif any(word in query_lower for word in ["write", "create", "generate", "story", "poem"]):
            result = "creative"
        else:
            result = "general"
        
        _msg = f"ToolSelector.classify_intent returning with intent: {result}"
        log.debug(_msg)
        return result

    def score_relevance(self, query: str, tool_name: str) -> float:
        """Score tool relevance based on query keywords and context.
        
        Args:
            query: The query to evaluate
            tool_name: Name of the tool to score
            
        Returns:
            Relevance score between 0.0 and 1.0
        """
        _msg = f"ToolSelector.score_relevance starting with query: {query}, tool: {tool_name}"
        log.debug(_msg)
        
        # Simple keyword matching for relevance scoring
        query_lower = query.lower()
        
        if tool_name == "web_search":
            # Web search is relevant for current events, specific facts, news
            web_keywords = ["current", "latest", "news", "today", "recent", "2024", "2025", "price", "weather"]
            score = sum(1 for keyword in web_keywords if keyword in query_lower) / len(web_keywords)
        elif tool_name == "wikipedia":
            # Wikipedia is relevant for general knowledge, historical facts, definitions
            wiki_keywords = ["what is", "who is", "history", "definition", "meaning", "origin", "invent", "discover"]
            score = sum(1 for keyword in wiki_keywords if keyword in query_lower) / len(wiki_keywords)
        else:
            score = 0.5  # Default score for unknown tools
        
        # Ensure score is between 0.0 and 1.0
        result = max(0.0, min(1.0, score))
        
        _msg = f"ToolSelector.score_relevance returning with score: {result}"
        log.debug(_msg)
        return result

    def select_tool(self, query: str, memory: WorkingMemory) -> str:
        """Select the most relevant tool for the query.
        
        Args:
            query: The query to process
            memory: Current working memory state
            
        Returns:
            Name of the selected tool
        """
        _msg = "ToolSelector.select_tool starting"
        log.debug(_msg)
        
        # Check for conflicts in the current memory
        conflicts = self.conflict_resolver.detect_conflicts(memory)
        
        # Score all available tools
        scores = {}
        for tool_name in self.available_tools:
            relevance_score = self.score_relevance(query, tool_name)
            
            # Adjust score based on confidence in existing facts
            if memory.information_store.facts:
                confidence_data = self.confidence_scorer.calculate_confidence_score(memory, query)
                confidence_score = confidence_data["overall_confidence"] / 100.0
                
                # If we already have high confidence facts, we might not need to use a tool
                if confidence_score > 0.8:
                    relevance_score *= 0.5  # Reduce relevance if we already have high confidence
            
            # If there are conflicts, prioritize tools that can help resolve them
            if conflicts:
                # Increase relevance for tools that can provide authoritative information
                if tool_name in ["web_search", "wikipedia"]:
                    relevance_score *= 1.2  # Boost relevance for fact-checking tools
            
            scores[tool_name] = relevance_score
        
        # Select the tool with the highest score
        selected_tool = max(scores, key=scores.get) if scores else ""
        
        _msg = f"ToolSelector.select_tool returning with selected tool: {selected_tool}"
        log.debug(_msg)
        return selected_tool

    def analyze_cost_benefit(self, tool_name: str, query: str, memory: WorkingMemory) -> Dict[str, Any]:
        """Analyze cost/benefit of using a tool for a specific query.
        
        Args:
            tool_name: Name of the tool to analyze
            query: The query to process
            memory: Current working memory state
            
        Returns:
            Dictionary with cost/benefit analysis
        """
        _msg = f"ToolSelector.analyze_cost_benefit starting with tool: {tool_name}, query: {query}"
        log.debug(_msg)
        
        # Simplified cost model
        tool_costs = {
            "web_search": 0.01,
            "wikipedia": 0.001
        }
        
        cost = tool_costs.get(tool_name, 0.005)
        
        # Simple value estimation based on query complexity
        query_words = len(query.split())
        expected_value = min(1.0, query_words / 20.0)  # Normalize by typical query length
        
        # Adjust value based on current confidence levels
        if memory.information_store.facts:
            confidence_data = self.confidence_scorer.calculate_confidence_score(memory, query)
            current_confidence = confidence_data["overall_confidence"] / 100.0
            
            # If we already have high confidence, the value of additional information is lower
            expected_value *= (1.0 - current_confidence)
        
        # Recommendation based on cost vs value
        recommended = expected_value > cost * 100  # Simple heuristic
        
        result = {
            "estimated_cost": cost,
            "expected_value": expected_value,
            "recommended": recommended
        }
        
        _msg = f"ToolSelector.analyze_cost_benefit returning with analysis: {result}"
        log.debug(_msg)
        return result
