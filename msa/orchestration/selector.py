"""Tool selection mechanism for the multi-step agent."""

import logging
from typing import Any

from msa.memory.models import WorkingMemory
from msa.orchestration.confidence import ConfidenceScorer
from msa.orchestration.conflict import ConflictResolver
from msa.tools.base import ToolInterface

log = logging.getLogger(__name__)


class ToolSelector:
    """Tool selection mechanism based on query classification and relevance scoring."""

    def __init__(self, available_tools: dict[str, ToolInterface]) -> None:
        """Initialize tool selector with available tools.

        Args:
            available_tools: A dictionary mapping tool names (str) to their respective ToolInterface instances.
                            This defines the set of tools the selector can choose from.

        Notes:
            1. Stores the provided available_tools dictionary for later use.
            2. Instantiates a ConfidenceScorer to evaluate the confidence of facts in memory.
            3. Instantiates a ConflictResolver to detect contradictions in the current memory state.

        """
        _msg = "ToolSelector.__init__ starting"
        log.debug(_msg)

        self.available_tools = available_tools
        self.confidence_scorer = ConfidenceScorer()
        self.conflict_resolver = ConflictResolver()

        _msg = "ToolSelector.__init__ returning"
        log.debug(_msg)

    def classify_intent(self, query: str) -> str:
        """Classify the user's query intent to determine which category of tools is most appropriate.

        Args:
            query: The natural language query to be classified. This is the input text from the user.

        Returns:
            A string representing the classified intent category. Possible values are:
                - "factual": queries asking for specific facts (e.g., "who is the president?")
                - "analytical": queries requiring analysis, comparison, or explanation (e.g., "why did the stock drop?")
                - "coding": queries related to code generation or programming (e.g., "write a Python function")
                - "creative": queries for creative content (e.g., "write a poem")
                - "general": queries that do not match any of the above categories.

        Notes:
            1. Converts the query to lowercase for consistent keyword matching.
            2. Checks for keywords related to factual queries and returns "factual" if any are found.
            3. Checks for keywords related to analytical queries and returns "analytical" if any are found.
            4. Checks for keywords related to coding queries and returns "coding" if any are found.
            5. Checks for keywords related to creative queries and returns "creative" if any are found.
            6. If no keywords match, defaults to "general".

        """
        _msg = f"ToolSelector.classify_intent starting with query: {query}"
        log.debug(_msg)

        # Simple keyword-based classification for now
        query_lower = query.lower()
        if any(
            word in query_lower
            for word in ["what is", "who is", "when", "where", "how many", "how much"]
        ):
            result = "factual"
        elif any(
            word in query_lower for word in ["analyze", "compare", "explain", "why"]
        ):
            result = "analytical"
        elif any(
            word in query_lower for word in ["code", "program", "function", "script"]
        ):
            result = "coding"
        elif any(
            word in query_lower
            for word in ["write", "create", "generate", "story", "poem"]
        ):
            result = "creative"
        else:
            result = "general"

        _msg = f"ToolSelector.classify_intent returning with intent: {result}"
        log.debug(_msg)
        return result

    def score_relevance(self, query: str, tool_name: str) -> float:
        """Calculate a relevance score between 0.0 and 1.0 for a specific tool given a query.

        Args:
            query: The natural language query to be evaluated.
            tool_name: The name of the tool (e.g., "web_search", "wikipedia") whose relevance is being scored.

        Returns:
            A float score between 0.0 and 1.0 indicating how relevant the specified tool is to the query.
            Higher scores indicate higher relevance.

        Notes:
            1. Converts the query to lowercase for consistent keyword matching.
            2. For "web_search", checks for keywords associated with current events, specific facts, or news.
               The score is calculated as the proportion of relevant keywords found.
            3. For "wikipedia", checks for keywords associated with general knowledge, historical facts, or definitions.
               The score is calculated as the proportion of relevant keywords found.
            4. For any other tool, assigns a default score of 0.5.
            5. Ensures the final score is clamped between 0.0 and 1.0.

        """
        _msg = f"ToolSelector.score_relevance starting with query: {query}, tool: {tool_name}"
        log.debug(_msg)

        # Simple keyword matching for relevance scoring
        query_lower = query.lower()

        if tool_name == "web_search":
            # Web search is relevant for current events, specific facts, news
            web_keywords = [
                "current",
                "latest",
                "news",
                "today",
                "recent",
                "2024",
                "2025",
                "price",
                "weather",
            ]
            score = sum(1 for keyword in web_keywords if keyword in query_lower) / len(
                web_keywords,
            )
        elif tool_name == "wikipedia":
            # Wikipedia is relevant for general knowledge, historical facts, definitions
            wiki_keywords = [
                "what is",
                "who is",
                "history",
                "definition",
                "meaning",
                "origin",
                "invent",
                "discover",
            ]
            score = sum(1 for keyword in wiki_keywords if keyword in query_lower) / len(
                wiki_keywords,
            )
        else:
            score = 0.5  # Default score for unknown tools

        # Ensure score is between 0.0 and 1.0
        result = max(0.0, min(1.0, score))

        _msg = f"ToolSelector.score_relevance returning with score: {result}"
        log.debug(_msg)
        return result

    def select_tool(self, query: str, memory: WorkingMemory) -> str:
        """Select the most appropriate tool from the available tools based on query relevance and memory state.

        Args:
            query: The natural language query to be processed.
            memory: The current state of the working memory, containing previously gathered facts and metadata.

        Returns:
            The name of the selected tool as a string, or an empty string if no tools are available.

        Notes:
            1. Detects any conflicts in the current memory state using the conflict resolver.
            2. Iterates over all available tools and calculates a relevance score using the score_relevance method.
            3. Adjusts the relevance score based on the confidence in existing facts in memory.
               If the overall confidence is already high (>80%), the relevance score is reduced by half.
            4. If conflicts are detected in the memory, boosts the relevance score of fact-checking tools
               (web_search and wikipedia) by a factor of 1.2 to prioritize resolving conflicts.
            5. Selects the tool with the highest adjusted relevance score.
            6. Returns the name of the selected tool, or an empty string if the available tools list is empty.

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
                confidence_data = self.confidence_scorer.calculate_confidence_score(
                    memory,
                    query,
                )
                confidence_score = confidence_data["overall_confidence"] / 100.0

                # If we already have high confidence facts, we might not need to use a tool
                if confidence_score > 0.8:
                    relevance_score *= (
                        0.5  # Reduce relevance if we already have high confidence
                    )

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

    def analyze_cost_benefit(
        self,
        tool_name: str,
        query: str,
        memory: WorkingMemory,
    ) -> dict[str, Any]:
        """Analyze the cost and benefit of using a specific tool for a given query and memory state.

        Args:
            tool_name: The name of the tool to analyze (e.g., "web_search", "wikipedia").
            query: The natural language query to be processed.
            memory: The current state of the working memory, containing previously gathered facts and metadata.

        Returns:
            A dictionary with the following keys:
                - "estimated_cost": A float representing the estimated cost of using the tool.
                - "expected_value": A float between 0.0 and 1.0 representing the expected informational value.
                - "recommended": A boolean indicating whether the tool should be used based on a simple heuristic.

        Notes:
            1. Defines a cost model for different tools (e.g., web_search costs more than wikipedia).
            2. Estimates the expected value based on the number of words in the query, normalized to a maximum of 1.0.
            3. Adjusts the expected value based on the current confidence level in the memory.
               If confidence is already high, the expected value is reduced proportionally.
            4. Determines the recommendation by comparing the expected value to the cost scaled by a factor of 100.
               If expected_value > cost * 100, the tool is recommended.
            5. Returns a dictionary containing the cost, value, and recommendation.

        """
        _msg = f"ToolSelector.analyze_cost_benefit starting with tool: {tool_name}, query: {query}"
        log.debug(_msg)

        # Simplified cost model
        tool_costs = {"web_search": 0.01, "wikipedia": 0.001}

        cost = tool_costs.get(tool_name, 0.005)

        # Simple value estimation based on query complexity
        query_words = len(query.split())
        expected_value = min(
            1.0,
            query_words / 20.0,
        )  # Normalize by typical query length

        # Adjust value based on current confidence levels
        if memory.information_store.facts:
            confidence_data = self.confidence_scorer.calculate_confidence_score(
                memory,
                query,
            )
            current_confidence = confidence_data["overall_confidence"] / 100.0

            # If we already have high confidence, the value of additional information is lower
            expected_value *= 1.0 - current_confidence

        # Recommendation based on cost vs value
        recommended = expected_value > cost * 100  # Simple heuristic

        result = {
            "estimated_cost": cost,
            "expected_value": expected_value,
            "recommended": recommended,
        }

        _msg = f"ToolSelector.analyze_cost_benefit returning with analysis: {result}"
        log.debug(_msg)
        return result
