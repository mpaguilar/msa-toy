"""Component functions for the multi-step agent controller."""

import logging
from typing import Dict, Any
from langchain_core.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser

from msa.llm.client import get_llm_client
from msa.tools.base import ToolInterface, ToolResponse
from msa.tools.web_search import WebSearchTool
from msa.tools.wikipedia import WikipediaTool
from msa.controller.models import ActionSelection, CompletionDecision
from msa.config import load_app_config
from msa.memory.manager import WorkingMemoryManager
from msa.orchestration.synthesis import SynthesisEngine
from msa.controller.action_handler import process_action_selection
from msa.controller.observation_handler import process_observation

log = logging.getLogger(__name__)


def initialize_llm_clients() -> Dict[str, Any]:
    """Initialize LLM clients for different purposes.
    
    Returns:
        Dict mapping client names to LLMClient instances
    """
    _msg = "initialize_llm_clients starting"
    log.debug(_msg)
    
    clients = {
        "thinking": get_llm_client("quick-medium"),
        "action": get_llm_client("tool-big"),
        "completion": get_llm_client("quick-medium")
    }
    
    _msg = "initialize_llm_clients returning"
    log.debug(_msg)
    return clients


def initialize_tools() -> Dict[str, ToolInterface]:
    """Initialize available tools.
    
    Returns:
        Dict mapping tool names to ToolInterface instances
    """
    _msg = "initialize_tools starting"
    log.debug(_msg)
    
    tools: Dict[str, ToolInterface] = {
        "web_search": WebSearchTool(),
        "wikipedia": WikipediaTool()
    }
    
    _msg = "initialize_tools returning"
    log.debug(_msg)
    return tools


def create_prompt_templates() -> Dict[str, PromptTemplate]:
    """Create prompt templates for different phases.
    
    Returns:
        Dict mapping template names to PromptTemplate instances
    """
    _msg = "create_prompt_templates starting"
    log.debug(_msg)
    
    templates = {
        "think": PromptTemplate.from_template(
            "You are an AI assistant using the ReAct framework to answer questions.\n"
            "Analyze the question and current state to determine the next step.\n\n"
            "Question: {question}\n"
            "Current working memory:\n{memory_summary}\n\n"
            "Provide your analysis of what information is needed and what should be done next."
        ),
        "action": PromptTemplate.from_template(
            "Based on the analysis, select the next action to take.\n"
            "Available tools: {tools}\n\n"
            "Analysis: {analysis}\n\n"
            "{format_instructions}\n"
            "Respond with a valid ActionSelection JSON object."
        ),
        "completion": PromptTemplate.from_template(
            "Determine if we have sufficient information to answer the original question.\n\n"
            "Original question: {question}\n"
            "Collected information:\n{collected_info}\n\n"
            "{format_instructions}\n"
            "Respond with a valid CompletionDecision JSON object."
        )
    }
    
    _msg = "create_prompt_templates returning"
    log.debug(_msg)
    return templates


def process_thoughts(
    query: str, 
    memory_manager: Any, 
    thinking_client: Any, 
    think_prompt: PromptTemplate
) -> str:
    """Generate thoughts based on the current state and memory.
    
    Args:
        query: The original query to process
        memory_manager: The working memory manager
        thinking_client: The LLM client for thinking
        think_prompt: The prompt template for thinking
        
    Returns:
        A string containing the generated thoughts
    """
    _msg = f"process_thoughts starting with query: {query}"
    log.debug(_msg)
    
    # Get a summary of the current memory state
    memory_summary = memory_manager.serialize()
    
    # Generate thoughts using the thinking LLM
    prompt = think_prompt.format(
        question=query,
        memory_summary=memory_summary
    )
    
    response = thinking_client.call(prompt)
    
    # Handle both LLMResponse objects and dictionary responses
    if hasattr(response, 'content'):
        content = response.content
    elif isinstance(response, dict):
        content = response.get('content', str(response))
    else:
        content = str(response)
    
    _msg = "process_thoughts returning"
    log.debug(_msg)
    return content


def process_completion_decision(
    query: str,
    memory_manager: Any,
    completion_client: Any,
    completion_prompt: PromptTemplate
) -> CompletionDecision:
    """Determine if we have sufficient information to answer the question.
    
    Args:
        query: The original query
        memory_manager: The working memory manager
        completion_client: The LLM client for completion checking
        completion_prompt: The prompt template for completion checking
        
    Returns:
        A CompletionDecision object indicating completion status
    """
    _msg = f"process_completion_decision starting with query: {query}"
    log.debug(_msg)
    
    # Get collected information from memory
    memory = memory_manager.get_memory()
    collected_info = str(memory.information_store)
    
    # Create output parser for CompletionDecision
    parser = PydanticOutputParser(pydantic_object=CompletionDecision)
    format_instructions = parser.get_format_instructions()
    
    # Generate completion decision using the completion LLM
    prompt = completion_prompt.format(
        question=query,
        collected_info=collected_info,
        format_instructions=format_instructions
    )
    
    try:
        response = completion_client.call(prompt)
        # Parse the response using the parser
        if isinstance(response, CompletionDecision):
            decision = response
        elif isinstance(response, dict):
            # If it's already a dict, try to create CompletionDecision directly
            try:
                decision = CompletionDecision(**response)
            except Exception as e:
                _msg = f"Failed to create CompletionDecision from dict: {e}"
                log.exception(_msg)
                # Try parsing as string representation of dict
                decision = parser.parse(str(response))
        else:
            decision = response
    except Exception as e:
        _msg = f"Error in completion check, using fallback: {e}"
        log.exception(_msg)
        # Fallback decision if LLM fails
        decision = CompletionDecision(
            is_complete=False,
            answer="",
            confidence=0.0,
            reasoning=f"Error in LLM completion check: {str(e)}",
            remaining_tasks=["Continue gathering information"]
        )
    
    # Handle CompletionDecision objects, dictionary responses, and other types
    if isinstance(decision, CompletionDecision):
        completion_decision = decision
    elif isinstance(decision, dict):
        try:
            # Check if it already has the required fields for CompletionDecision
            required_fields = ['is_complete', 'answer', 'confidence', 'reasoning']
            if all(field in decision and decision[field] is not None for field in required_fields):
                completion_decision = CompletionDecision(**decision)
            else:
                # Try to parse it through the parser
                completion_decision = parser.parse(str(decision))
        except Exception as e:
            _msg = f"Failed to parse completion response: {e}"
            log.exception(_msg)
            # Create a default completion decision for error handling
            completion_decision = CompletionDecision(
                is_complete=False,
                answer="",
                confidence=0.0,
                reasoning=f"Error parsing completion: {str(e)}",
                remaining_tasks=[]
            )
    elif hasattr(decision, 'dict'):
        # Handle Pydantic BaseModel objects
        try:
            decision_dict = decision.dict()
            
            # Check if decision_dict is actually a dictionary with the required fields
            required_fields = ['is_complete', 'answer', 'confidence', 'reasoning']
            if isinstance(decision_dict, dict) and decision_dict and all(field in decision_dict and decision_dict[field] is not None for field in required_fields):
                completion_decision = CompletionDecision(**decision_dict)
            else:
                # Try to parse it through the parser
                completion_decision = parser.parse(str(decision_dict))
        except Exception as e:
            _msg = f"Failed to convert decision object to dict: {e}"
            log.exception(_msg)
            # Create a default completion decision for error handling
            completion_decision = CompletionDecision(
                is_complete=False,
                answer="",
                confidence=0.0,
                reasoning=f"Error converting decision object: {str(e)}",
                remaining_tasks=[]
            )
    else:
        # Try to parse string responses
        try:
            completion_decision = parser.parse(str(decision))
        except Exception as e:
            _msg = f"Failed to parse completion response: {e}"
            log.exception(_msg)
            # Create a default completion decision for unexpected response types
            completion_decision = CompletionDecision(
                is_complete=False,
                answer="",
                confidence=0.0,
                reasoning=f"Unexpected response type: {type(decision)}",
                remaining_tasks=[]
            )
    
    _msg = "process_completion_decision returning"
    log.debug(_msg)
    return completion_decision


def handle_tool_execution(
    tool_name: str, 
    query: str, 
    tools: Dict[str, ToolInterface]
) -> ToolResponse:
    """Execute a tool by name.
    
    Args:
        tool_name: Name of the tool to execute
        query: Query/input for the tool
        tools: Dictionary of available tools
        
    Returns:
        Tool response from the executed tool
    """
    _msg = f"handle_tool_execution starting with tool: {tool_name}"
    log.debug(_msg)
    
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
            metadata={"error": "tool_not_found"}
        )
        _msg = "handle_tool_execution returning with error"
        log.debug(_msg)
        return response


class Controller:
    """Main controller that orchestrates the ReAct cycle for the multi-step agent."""

    def __init__(self) -> None:
        """Initialize controller with configured LLM client and tools."""
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
        
        # Initialize synthesis engine
        self.synthesis_engine = SynthesisEngine()
        
        # Initialize prompt templates
        templates = create_prompt_templates()
        self.think_prompt = templates["think"]
        self.action_prompt = templates["action"]
        self.completion_prompt = templates["completion"]
        
        _msg = "Controller.__init__ returning"
        log.debug(_msg)

    def execute_tool(self, tool_name: str, query: str) -> ToolResponse:
        """Execute a tool with the given query.
        
        Args:
            tool_name: Name of the tool to execute
            query: Query to pass to the tool
            
        Returns:
            ToolResponse containing the tool's response
        """
        _msg = f"Controller.execute_tool starting with tool: {tool_name}, query: {query}"
        log.debug(_msg)
        
        try:
            if tool_name in self.tools:
                tool = self.tools[tool_name]
                response = tool.execute(query)
                _msg = f"Controller.execute_tool returning success for tool: {tool_name}"
                log.debug(_msg)
                return response
            else:
                error_msg = f"Error: Tool '{tool_name}' not found"
                _msg = f"Controller.execute_tool returning error: {error_msg}"
                log.debug(_msg)
                return ToolResponse(
                    content=error_msg,
                    metadata={"error": "tool_not_found"}
                )
                
        except Exception as e:
            error_msg = f"Error executing tool '{tool_name}': {str(e)}"
            _msg = f"Controller.execute_tool failed with error: {error_msg}"
            log.exception(_msg)
            return ToolResponse(
                content=error_msg,
                metadata={"error": str(e)}
            )

    def process_query(self, query: str) -> str:
        """Process user query through ReAct cycle.
        
        Args:
            query: The original user query to process
            
        Returns:
            The final answer generated by the agent
        """
        _msg = f"Controller.process_query starting with query: {query}"
        log.debug(_msg)
        
        # Initialize working memory with the query
        self.memory_manager = WorkingMemoryManager(query)
        
        # Run the ReAct cycle
        for i in range(self.max_iterations):
            _msg = f"Controller.process_query iteration {i+1}"
            log.debug(_msg)
            
            # Think phase
            thought = process_thoughts(
                query=query,
                memory_manager=self.memory_manager,
                thinking_client=self.thinking_client,
                think_prompt=self.think_prompt
            )
            
            # Act phase
            action_selection = process_action_selection(
                thoughts=thought,
                action_client=self.action_client,
                action_prompt=self.action_prompt,
                tools=self.tools
            )
            
            # Check for completion
            completion = process_completion_decision(
                query=query,
                memory_manager=self.memory_manager,
                completion_client=self.completion_client,
                completion_prompt=self.completion_prompt
            )
            
            if completion.is_complete:
                # Synthesize final answer
                synthesis_result = self.synthesis_engine.synthesize_answer(self.memory_manager.memory, query)
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
                    tools=self.tools
                )
                observation = process_observation(tool_response)
                self.memory_manager.add_observation({
                    "content": observation,
                    "source": action_selection.action_name,
                    "confidence": action_selection.confidence
                })
            else:
                _msg = "Controller.process_query returning - no valid action"
                log.debug(_msg)
                return "Unable to determine next action."
        
        _msg = "Controller.process_query returning - max iterations reached"
        log.debug(_msg)
        return "Reached maximum iterations without completing the task."
