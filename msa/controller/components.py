"""Component functions for the multi-step agent controller."""

import logging
from typing import Any

from langchain.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate

from msa.config import load_app_config
from msa.controller.action_handler import process_action_selection
from msa.controller.models import CompletionDecision
from msa.controller.observation_handler import process_observation
from msa.llm.client import get_llm_client
from msa.memory.manager import WorkingMemoryManager
from msa.orchestration.synthesis import SynthesisEngine
from msa.tools.base import ToolInterface, ToolResponse
from msa.tools.web_search import WebSearchTool
from msa.tools.wikipedia import WikipediaTool

log = logging.getLogger(__name__)


def initialize_llm_clients() -> dict[str, Any]:
    """Initialize LLM clients for different purposes.

    Args:
        None

    Returns:
        A dictionary mapping client names ("thinking", "action", "completion") to their respective LLMClient instances.

    Notes:
        1. Create a dictionary with keys "thinking", "action", and "completion".
        2. For each key, retrieve the corresponding LLMClient using get_llm_client with the specified model name.
        3. Return the constructed dictionary of clients.

    """
    _msg = "initialize_llm_clients starting"
    log.debug(_msg)

    clients = {
        "thinking": get_llm_client("quick-medium"),
        "action": get_llm_client("tool-big"),
        "completion": get_llm_client("quick-medium"),
    }

    _msg = "initialize_llm_clients returning"
    log.debug(_msg)
    return clients


def initialize_tools() -> dict[str, ToolInterface]:
    """Initialize available tools.

    Args:
        None

    Returns:
        A dictionary mapping tool names ("web_search", "wikipedia") to their respective ToolInterface instances.

    Notes:
        1. Create an empty dictionary to store tool instances.
        2. Add the WebSearchTool instance with key "web_search".
        3. Add the WikipediaTool instance with key "wikipedia".
        4. Return the dictionary of tools.

    """
    _msg = "initialize_tools starting"
    log.debug(_msg)

    tools: dict[str, ToolInterface] = {
        "web_search": WebSearchTool(),
        "wikipedia": WikipediaTool(),
    }

    _msg = "initialize_tools returning"
    log.debug(_msg)
    return tools


def create_prompt_templates() -> dict[str, PromptTemplate]:
    """Create prompt templates for different phases.

    Args:
        None

    Returns:
        A dictionary mapping template names ("think", "action", "completion", "final_synthesis") to their respective PromptTemplate instances.

    Notes:
        1. Create an empty dictionary to store prompt templates.
        2. Define the "think" template with a prompt that guides analysis of the question and memory state.
        3. Define the "action" template with a prompt that guides action selection based on analysis and available tools.
        4. Define the "completion" template with a prompt that determines if the question can be answered based on collected info.
        5. Define the "final_synthesis" template with a prompt that guides final answer synthesis with reasoning.
        6. Return the dictionary of templates.

    """
    _msg = "create_prompt_templates starting"
    log.debug(_msg)

    templates = {
        "think": PromptTemplate.from_template(
            "You are an AI assistant using the ReAct framework to answer questions.\n"
            "Analyze the question and current state to determine the next step.\n\n"
            "Question: {question}\n"
            "Current working memory:\n{memory_summary}\n\n"
            "Provide your analysis of what information is needed and what should be done next.",
        ),
        "action": PromptTemplate.from_template(
            "Based on the analysis, select the next action to take.\n"
            "Valid action types are: tool, plan, ask, stop\n"
            "Available tools: {tools}\n\n"
            "Analysis: {analysis}\n\n"
            "{format_instructions}\n"
            "Respond with a valid ActionSelection JSON object using only the valid action types listed above.",
        ),
        "completion": PromptTemplate.from_template(
            "Determine if we have sufficient information to answer the original question.\n\n"
            "Original question: {question}\n"
            "Collected information:\n{collected_info}\n\n"
            "{format_instructions}\n"
            "Respond with a valid CompletionDecision JSON object.",
        ),
        "final_synthesis": PromptTemplate.from_template(
            "Based on the original query and all collected information, provide a precise final answer with clear reasoning.\n\n"
            "Original Query: {query}\n\n"
            "Collected Information:\n{collected_info}\n\n"
            "Provide a comprehensive answer that:\n"
            "1. Directly addresses the original query\n"
            "2. Synthesizes information from all relevant facts\n"
            "3. Explains the reasoning process used to reach the conclusion\n"
            "4. Identifies key supporting evidence\n"
            "5. Acknowledges any uncertainties or limitations\n\n"
            "Present your response in a clear, structured format. {format_instructions}"
        ),
    }

    _msg = "create_prompt_templates returning"
    log.debug(_msg)
    return templates


def process_thoughts(
    query: str,
    memory_manager: Any,
    thinking_client: Any,
    think_prompt: PromptTemplate,
) -> str:
    """Generate thoughts based on the current state and memory.

    Args:
        query: The original user query to process.
        memory_manager: The working memory manager responsible for storing and retrieving memory.
        thinking_client: The LLM client used for generating thoughts.
        think_prompt: The prompt template used to guide the LLM's thinking process.

    Returns:
        A string containing the generated thoughts from the LLM.

    Notes:
        1. Retrieve a summary of the current memory state from the memory_manager.
        2. Format the think_prompt with the query and memory summary.
        3. Call the thinking_client with the formatted prompt.
        4. Extract the content from the response based on its structure (handling different response types).
        5. Return the generated thoughts as a string.

    """
    _msg = f"process_thoughts starting with query: {query}"
    log.debug(_msg)

    # Get a summary of the current memory state
    memory_summary = memory_manager.summarize_state()

    # Generate thoughts using the thinking LLM
    prompt = think_prompt.format(question=query, memory_summary=str(memory_summary))

    response = thinking_client.call(prompt)

    # Handle both LLMResponse objects and dictionary responses
    if hasattr(response, "content"):
        content = response.content
    elif isinstance(response, dict):
        content = response.get("content", str(response))
    else:
        content = str(response)

    _msg = "process_thoughts returning"
    log.debug(_msg)
    return content


def process_completion_decision(
    query: str,
    memory_manager: Any,
    completion_client: Any,
    completion_prompt: PromptTemplate,
) -> CompletionDecision:
    """Determine if we have sufficient information to answer the question.

    Args:
        query: The original query to process.
        memory_manager: The working memory manager responsible for retrieving collected information.
        completion_client: The LLM client used for deciding completion.
        completion_prompt: The prompt template used to guide the completion decision process.

    Returns:
        A CompletionDecision object indicating whether the question can be answered, with details on confidence, reasoning, and remaining tasks.

    Notes:
        1. Retrieve the current working memory and extract the collected information.
        2. Create a PydanticOutputParser for CompletionDecision to format the LLM's response.
        3. Format the completion_prompt with the query, collected info, and format instructions.
        4. Call the completion_client with the formatted prompt.
        5. Parse the response into a CompletionDecision object, handling various response formats.
        6. If parsing fails, fall back to a default decision with an error message.
        7. Return the completion decision.

    """
    _msg = f"process_completion_decision starting with query: {query}"
    log.debug(_msg)

    # Get collected information from memory
    memory = memory_manager.get_memory()
    collected_info = []
        
    # Extract collected information from memory
    for fact_id, fact in memory.information_store.facts.items():
        collected_info.append({
            "id": fact_id,
            "content": fact.content,
            "source": fact.source,
            "confidence": memory.information_store.confidence_scores.get(fact_id, 0.0)
        })

    # Create output parser for CompletionDecision
    parser = PydanticOutputParser(pydantic_object=CompletionDecision)
    format_instructions = parser.get_format_instructions()

    # Generate completion decision using the completion LLM
    prompt = completion_prompt.format(
        question=query,
        collected_info=str(collected_info),
        format_instructions=format_instructions,
    )

    try:
        response = completion_client.call(prompt, parser)

        # Handle LLM response format which may contain 'content', 'parsed', 'metadata' fields
        if isinstance(response, dict):
            # If response has a 'parsed' field, use that directly
            if "parsed" in response and response["parsed"] is not None:
                if isinstance(response["parsed"], CompletionDecision):
                    decision = response["parsed"]
                else:
                    decision = CompletionDecision(**response["parsed"])
            # If response has a 'content' field, parse that
            elif "content" in response:
                decision = parser.parse(response["content"])
            # Otherwise try to create CompletionDecision directly from the dict
            else:
                decision = CompletionDecision(**response)
        elif hasattr(response, "parsed") and response.parsed is not None:
            decision = response.parsed
        elif hasattr(response, "content"):
            decision = parser.parse(response.content)
        elif isinstance(response, CompletionDecision):
            decision = response
        else:
            # Try to parse as string
            decision = parser.parse(str(response))

    except Exception as e:
        _msg = f"Error in completion check, using fallback: {e}"
        log.exception(_msg)
        # Fallback decision if LLM fails
        decision = CompletionDecision(
            is_complete=False,
            answer="",
            confidence=0.0,
            reasoning=f"Error in LLM completion check: {str(e)}",
            remaining_tasks=["Continue gathering information"],
        )

    _msg = "process_completion_decision returning"
    log.debug(_msg)
    return decision


def handle_tool_execution(
    tool_name: str,
    query: str,
    tools: dict[str, ToolInterface],
) -> ToolResponse:
    """Execute a tool by name.

    Args:
        tool_name: Name of the tool to execute.
        query: Query/input for the tool.
        tools: Dictionary of available tools mapped by name.

    Returns:
        ToolResponse containing the tool's response, including content and metadata.

    Notes:
        1. Check if the tool_name exists in the tools dictionary.
        2. If the tool exists, execute it with the provided query and return the response.
        3. If the tool does not exist, return a ToolResponse with an error message and metadata indicating the tool was not found.
        4. If an exception occurs during execution, return a ToolResponse with the error message and metadata.

    """
    _msg = f"handle_tool_execution starting with tool: {tool_name}"
    log.debug(_msg)

    try:
        # Execute the tool if it exists
        if tool_name in tools:
            response = tools[tool_name].execute(query)
            _msg = "handle_tool_execution returning"
            log.debug(_msg)
            return response
        else:
            # Return an error response if tool not found
            response = ToolResponse(
                content=f"Error: Tool '{tool_name}' not found",
                metadata={"error": "tool_not_found"},
            )
            _msg = "handle_tool_execution returning with error"
            log.debug(_msg)
            return response
    except Exception as e:
        error_msg = f"Error executing tool '{tool_name}': {str(e)}"
        _msg = f"handle_tool_execution failed with error: {error_msg}"
        log.exception(_msg)
        return ToolResponse(content=error_msg, metadata={"error": str(e)})


class Controller:
    """Main controller that orchestrates the ReAct cycle for the multi-step agent."""

    def __init__(self) -> None:
        """Initialize controller with configured LLM client and tools.

        Args:
            None

        Returns:
            None

        Notes:
            1. Load application configuration using load_app_config.
            2. Set max_iterations from configuration (default 10).
            3. Initialize LLM clients using initialize_llm_clients.
            4. Initialize tools using initialize_tools.
            5. Initialize synthesis engine.
            6. Initialize prompt templates using create_prompt_templates.
            7. Assign all components to class attributes.

        """
        _msg = "Controller.__init__ starting"
        log.debug(_msg)

        # Load configuration
        app_config = load_app_config()
        self.max_iterations = app_config.get("max_iterations", 10)

        # Initialize LLM clients for different purposes
        clients = initialize_llm_clients()
        self.thinking_client = clients["thinking"]
        self.action_client = clients["action"]
        self.completion_client = clients["completion"]

        # Initialize tools
        self.tools = initialize_tools()

        # Initialize prompt templates
        templates = create_prompt_templates()
        self.think_prompt = templates["think"]
        self.action_prompt = templates["action"]
        self.completion_prompt = templates["completion"]
        self.final_synthesis_prompt = templates["final_synthesis"]

        # Initialize synthesis engine with completion client and final synthesis prompt
        self.synthesis_engine = SynthesisEngine(
            completion_client=self.completion_client,
            final_synthesis_prompt=self.final_synthesis_prompt
        )

        _msg = "Controller.__init__ returning"
        log.debug(_msg)

    def execute_tool(self, tool_name: str, query: str) -> ToolResponse:
        """Execute a tool with the given query.

        Args:
            tool_name: Name of the tool to execute.
            query: Query to pass to the tool.

        Returns:
            ToolResponse containing the tool's response with content and metadata.

        Notes:
            1. Check if the tool_name exists in self.tools.
            2. If the tool exists, execute it with the provided query and return the response.
            3. If the tool does not exist, return a ToolResponse with an error message and metadata indicating the tool was not found.
            4. If an exception occurs during execution, return a ToolResponse with the error message and metadata.

        """
        _msg = (
            f"Controller.execute_tool starting with tool: {tool_name}, query: {query}"
        )
        log.debug(_msg)

        try:
            if tool_name in self.tools:
                tool = self.tools[tool_name]
                response = tool.execute(query)
                _msg = (
                    f"Controller.execute_tool returning success for tool: {tool_name}"
                )
                log.debug(_msg)
                return response
            else:
                error_msg = f"Error: Tool '{tool_name}' not found"
                _msg = f"Controller.execute_tool returning error: {error_msg}"
                log.debug(_msg)
                return ToolResponse(
                    content=error_msg,
                    metadata={"error": "tool_not_found"},
                )

        except Exception as e:
            error_msg = f"Error executing tool '{tool_name}': {str(e)}"
            _msg = f"Controller.execute_tool failed with error: {error_msg}"
            log.exception(_msg)
            return ToolResponse(content=error_msg, metadata={"error": str(e)})

    def process_query(self, query: str) -> str:
        """Process user query through ReAct cycle.

        Args:
            query: The original user query to process.

        Returns:
            The final answer generated by the agent as a string.

        Notes:
            1. Initialize a WorkingMemoryManager with the query.
            2. Loop up to max_iterations times to perform the ReAct cycle.
            3. In each iteration:
                a. Call process_thoughts to generate analysis based on query and memory.
                b. Call process_action_selection to determine the next action based on thoughts.
                c. Call process_completion_decision to check if the question can be answered.
                d. If the question is complete, use synthesis_engine to generate the final answer and return it.
                e. If the action is a tool call, execute it and add the observation to memory.
                f. If no valid action is selected, return a failure message.
                g. Track consecutive tool failures to prevent infinite loops.
            4. If max_iterations are reached without completing, return a timeout message.

        """
        _msg = f"Controller.process_query starting with query: {query}"
        log.debug(_msg)

        # Initialize working memory with the query
        self.memory_manager = WorkingMemoryManager(query)

        # Track consecutive tool failures to prevent infinite loops
        consecutive_tool_failures = 0
        max_consecutive_tool_failures = 3

        # Run the ReAct cycle
        for i in range(self.max_iterations):
            _msg = f"Controller.process_query iteration {i + 1}"
            log.debug(_msg)

            # Think phase
            thought = process_thoughts(
                query=query,
                memory_manager=self.memory_manager,
                thinking_client=self.thinking_client,
                think_prompt=self.think_prompt,
            )

            # Act phase
            action_selection = process_action_selection(
                thoughts=thought,
                action_client=self.action_client,
                action_prompt=self.action_prompt,
                tools=self.tools,
            )

            # Check for completion
            completion = process_completion_decision(
                query=query,
                memory_manager=self.memory_manager,
                completion_client=self.completion_client,
                completion_prompt=self.completion_prompt,
            )

            if completion.is_complete:
                # Synthesize final answer
                synthesis_result = self.synthesis_engine.synthesize_answer(
                    self.memory_manager.memory,
                    query,
                )
                # Handle both string and dict return types
                if isinstance(synthesis_result, dict):
                    final_answer = synthesis_result["answer"]
                else:
                    final_answer = str(synthesis_result)

                _msg = "Controller.process_query returning completed answer"
                log.debug(_msg)
                return final_answer

            # Observe phase
            if action_selection.action_type == "tool":
                tool_response = handle_tool_execution(
                    tool_name=action_selection.action_name,
                    query=query,
                    tools=self.tools,
                )
                observation = process_observation(tool_response)
                self.memory_manager.add_observation(
                    {
                        "content": observation,
                        "source": action_selection.action_name,
                        "confidence": action_selection.confidence,
                    },
                )
                
                # Track tool execution success/failure
                if tool_response.metadata.get("error"):
                    consecutive_tool_failures += 1
                    _msg = f"Tool execution failed, consecutive failures: {consecutive_tool_failures}"
                    log.debug(_msg)
                    
                    # If too many consecutive failures, stop processing
                    if consecutive_tool_failures >= max_consecutive_tool_failures:
                        _msg = "Controller.process_query returning - too many consecutive tool failures"
                        log.debug(_msg)
                        return "Unable to complete task due to repeated tool failures."
                else:
                    # Reset failure counter on success
                    consecutive_tool_failures = 0
            elif action_selection.action_type == "stop":
                # Handle stop action - check if we have meaningful information
                memory = self.memory_manager.get_memory()
                facts = memory.information_store.facts
                
                # If we have no facts or only error facts, return appropriate message
                if not facts:
                    _msg = "Controller.process_query returning - stop action with no information"
                    log.debug(_msg)
                    return "Unable to determine next action."
                
                # Check if all facts are errors
                only_errors = True
                for fact in facts.values():
                    if "Error executing tool" not in fact.content:
                        only_errors = False
                        break
                
                if only_errors:
                    _msg = "Controller.process_query returning - stop action with only errors"
                    log.debug(_msg)
                    return "Unable to complete task due to tool failures."
                
                # Synthesize answer with current information
                synthesis_result = self.synthesis_engine.synthesize_answer(
                    self.memory_manager.memory,
                    query,
                )
                # Handle both string and dict return types
                if isinstance(synthesis_result, dict):
                    final_answer = synthesis_result["answer"]
                else:
                    final_answer = str(synthesis_result)

                _msg = "Controller.process_query returning - stop action received"
                log.debug(_msg)
                return final_answer
            else:
                _msg = "Controller.process_query returning - no valid action"
                log.debug(_msg)
                return "Unable to determine next action."

        _msg = "Controller.process_query returning - max iterations reached"
        log.debug(_msg)
        return "Reached maximum iterations without completing the task."
