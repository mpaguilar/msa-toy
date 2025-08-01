"""Unit tests for the tool selector."""

from msa.orchestration.selector import ToolSelector
from msa.tools.base import ToolInterface
from msa.memory.models import (
    WorkingMemory,
    QueryState,
    ExecutionHistory,
    InformationStore,
    ReasoningState,
    Fact,
    SourceMetadata,
)


class MockTool(ToolInterface):
    """Mock tool implementation for testing."""

    def execute(self, query: str):
        """Execute mock tool."""
        pass

    def validate_response(self, response: dict) -> bool:
        """Validate mock response."""
        return True


class TestToolSelector:
    """Test cases for ToolSelector class."""

    def test_init(self) -> None:
        """Test ToolSelector initialization."""
        tools = {"web_search": MockTool(), "wikipedia": MockTool()}
        selector = ToolSelector(tools)
        assert isinstance(selector, ToolSelector)
        assert selector.available_tools == tools

    def test_classify_intent_factual(self) -> None:
        """Test factual intent classification."""
        tools = {"mock": MockTool()}
        selector = ToolSelector(tools)
        query = "What is the capital of France?"
        result = selector.classify_intent(query)
        assert isinstance(result, str)
        assert result == "factual"

    def test_classify_intent_analytical(self) -> None:
        """Test analytical intent classification."""
        tools = {"mock": MockTool()}
        selector = ToolSelector(tools)
        query = "Why did the Roman Empire fall?"
        result = selector.classify_intent(query)
        assert isinstance(result, str)
        assert result == "analytical"

    def test_classify_intent_coding(self) -> None:
        """Test coding intent classification."""
        tools = {"mock": MockTool()}
        selector = ToolSelector(tools)
        query = "Write a Python function to sort a list"
        result = selector.classify_intent(query)
        assert isinstance(result, str)
        assert result == "coding"

    def test_classify_intent_creative(self) -> None:
        """Test creative intent classification."""
        tools = {"mock": MockTool()}
        selector = ToolSelector(tools)
        query = "Write a poem about spring"
        result = selector.classify_intent(query)
        assert isinstance(result, str)
        assert result == "creative"

    def test_classify_intent_general(self) -> None:
        """Test general intent classification."""
        tools = {"mock": MockTool()}
        selector = ToolSelector(tools)
        query = "Hello, how are you?"
        result = selector.classify_intent(query)
        assert isinstance(result, str)
        assert result == "general"

    def test_score_relevance_web_search(self) -> None:
        """Test web search relevance scoring."""
        tools = {"web_search": MockTool()}
        selector = ToolSelector(tools)
        query = "What is the current price of Bitcoin?"
        result = selector.score_relevance(query, "web_search")
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    def test_score_relevance_wikipedia(self) -> None:
        """Test Wikipedia relevance scoring."""
        tools = {"wikipedia": MockTool()}
        selector = ToolSelector(tools)
        query = "What is photosynthesis?"
        result = selector.score_relevance(query, "wikipedia")
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    def test_score_relevance_unknown_tool(self) -> None:
        """Test relevance scoring for unknown tool."""
        tools = {"mock": MockTool()}
        selector = ToolSelector(tools)
        query = "What is the capital of France?"
        result = selector.score_relevance(query, "unknown_tool")
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0
        assert result == 0.5  # Default score

    def test_select_tool(self) -> None:
        """Test tool selection."""
        tools = {"web_search": MockTool(), "wikipedia": MockTool()}
        # Create a minimal working memory instance
        memory = WorkingMemory(
            query_state=QueryState(
                original_query="Test query",
                refined_queries=[],
                query_history=[],
                current_focus="",
            ),
            execution_history=ExecutionHistory(
                actions_taken=[],
                timestamps={},
                tool_call_sequence=[],
                intermediate_results=[],
            ),
            information_store=InformationStore(
                facts={},
                relationships={},
                sources={},
                confidence_scores={},
            ),
            reasoning_state=ReasoningState(
                current_hypothesis="",
                answer_draft="",
                information_gaps=[],
                next_steps=[],
                termination_criteria_met=False,
            ),
            created_at="2023-01-01T00:00:00Z",
            updated_at="2023-01-01T00:00:00Z",
        )
        selector = ToolSelector(tools)
        query = "What is the capital of France?"
        result = selector.select_tool(query, memory)
        assert isinstance(result, str)
        assert result in tools.keys()

    def test_analyze_cost_benefit_web_search(self) -> None:
        """Test cost/benefit analysis for web search."""
        tools = {"web_search": MockTool()}
        # Create a minimal working memory instance
        memory = WorkingMemory(
            query_state=QueryState(
                original_query="Test query",
                refined_queries=[],
                query_history=[],
                current_focus="",
            ),
            execution_history=ExecutionHistory(
                actions_taken=[],
                timestamps={},
                tool_call_sequence=[],
                intermediate_results=[],
            ),
            information_store=InformationStore(
                facts={},
                relationships={},
                sources={},
                confidence_scores={},
            ),
            reasoning_state=ReasoningState(
                current_hypothesis="",
                answer_draft="",
                information_gaps=[],
                next_steps=[],
                termination_criteria_met=False,
            ),
            created_at="2023-01-01T00:00:00Z",
            updated_at="2023-01-01T00:00:00Z",
        )
        selector = ToolSelector(tools)
        tool_name = "web_search"
        query = "What is the capital of France?"
        result = selector.analyze_cost_benefit(tool_name, query, memory)
        assert isinstance(result, dict)
        assert "estimated_cost" in result
        assert "expected_value" in result
        assert "recommended" in result
        assert result["estimated_cost"] == 0.01

    def test_analyze_cost_benefit_wikipedia(self) -> None:
        """Test cost/benefit analysis for Wikipedia."""
        tools = {"wikipedia": MockTool()}
        # Create a minimal working memory instance
        memory = WorkingMemory(
            query_state=QueryState(
                original_query="Test query",
                refined_queries=[],
                query_history=[],
                current_focus="",
            ),
            execution_history=ExecutionHistory(
                actions_taken=[],
                timestamps={},
                tool_call_sequence=[],
                intermediate_results=[],
            ),
            information_store=InformationStore(
                facts={},
                relationships={},
                sources={},
                confidence_scores={},
            ),
            reasoning_state=ReasoningState(
                current_hypothesis="",
                answer_draft="",
                information_gaps=[],
                next_steps=[],
                termination_criteria_met=False,
            ),
            created_at="2023-01-01T00:00:00Z",
            updated_at="2023-01-01T00:00:00Z",
        )
        selector = ToolSelector(tools)
        tool_name = "wikipedia"
        query = "What is photosynthesis?"
        result = selector.analyze_cost_benefit(tool_name, query, memory)
        assert isinstance(result, dict)
        assert "estimated_cost" in result
        assert "expected_value" in result
        assert "recommended" in result
        assert result["estimated_cost"] == 0.001

    def test_select_tool_with_high_confidence_facts(self) -> None:
        """Test tool selection when high confidence facts already exist."""
        tools = {"web_search": MockTool(), "wikipedia": MockTool()}
        # Create a working memory with high confidence facts
        facts = {
            "1": Fact(
                id="1",
                content="High confidence fact",
                confidence=0.95,
                source="source1",
                timestamp="2023-01-01T00:00:00Z",
            ),
        }
        information_store = InformationStore(
            facts=facts,
            relationships={},
            sources={
                "source1": SourceMetadata(
                    id="source1",
                    name="Test",
                    url="https://example.com",
                    credibility=0.8,
                    retrieval_date="2023-01-01T00:00:00Z",
                ),
            },
            confidence_scores={"1": 0.95},
        )
        memory = WorkingMemory(
            query_state=QueryState(
                original_query="Test query",
                refined_queries=[],
                query_history=[],
                current_focus="",
            ),
            execution_history=ExecutionHistory(
                actions_taken=[],
                timestamps={},
                tool_call_sequence=[],
                intermediate_results=[],
            ),
            information_store=information_store,
            reasoning_state=ReasoningState(
                current_hypothesis="",
                answer_draft="",
                information_gaps=[],
                next_steps=[],
                termination_criteria_met=False,
            ),
            created_at="2023-01-01T00:00:00Z",
            updated_at="2023-01-01T00:00:00Z",
        )
        selector = ToolSelector(tools)
        query = "What is the capital of France?"
        result = selector.select_tool(query, memory)
        assert isinstance(result, str)
        # Should still return a tool, but the selection logic may be adjusted
        assert result in tools.keys()

    def test_select_tool_with_conflicts(self) -> None:
        """Test tool selection when conflicts exist in memory."""
        tools = {"web_search": MockTool(), "wikipedia": MockTool()}
        # Create a working memory with conflicting facts
        facts = {
            "1": Fact(
                id="1",
                content="The Earth is round",
                confidence=0.9,
                source="source1",
                timestamp="2023-01-01T00:00:00Z",
            ),
            "2": Fact(
                id="2",
                content="The Earth is flat",
                confidence=0.3,
                source="source2",
                timestamp="2023-01-01T00:00:00Z",
            ),
        }
        information_store = InformationStore(
            facts=facts,
            relationships={},
            sources={
                "source1": SourceMetadata(
                    id="source1",
                    name="Wikipedia",
                    url="https://example.com",
                    credibility=0.85,
                    retrieval_date="2023-01-01T00:00:00Z",
                ),
                "source2": SourceMetadata(
                    id="source2",
                    name="Blog",
                    url="https://example.com",
                    credibility=0.3,
                    retrieval_date="2023-01-01T00:00:00Z",
                ),
            },
            confidence_scores={"1": 0.9, "2": 0.3},
        )
        memory = WorkingMemory(
            query_state=QueryState(
                original_query="Test query",
                refined_queries=[],
                query_history=[],
                current_focus="",
            ),
            execution_history=ExecutionHistory(
                actions_taken=[],
                timestamps={},
                tool_call_sequence=[],
                intermediate_results=[],
            ),
            information_store=information_store,
            reasoning_state=ReasoningState(
                current_hypothesis="",
                answer_draft="",
                information_gaps=[],
                next_steps=[],
                termination_criteria_met=False,
            ),
            created_at="2023-01-01T00:00:00Z",
            updated_at="2023-01-01T00:00:00Z",
        )
        selector = ToolSelector(tools)
        query = "What is the shape of the Earth?"
        result = selector.select_tool(query, memory)
        assert isinstance(result, str)
        # Should prioritize fact-checking tools when conflicts exist
        assert result in tools.keys()
