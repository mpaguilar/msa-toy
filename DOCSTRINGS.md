# Docstrings Reference

===
# File: `config.py`

## function: `load_app_config() -> dict`

Load application configuration from YAML file.

Args:
    None: This function does not take any arguments.

Returns:
    dict: A dictionary containing the loaded application configuration.
          Returns an empty dictionary if the file is not found or cannot be parsed.

Notes:
    1. Initialize a debug log message indicating the start of the function.
    2. Attempt to open and parse the YAML file at APP_CONFIG_PATH.
    3. If the file is not found, log a warning and return an empty dictionary.
    4. If YAML parsing fails, log an exception and return an empty dictionary.
    5. On success, return the parsed configuration dictionary (defaulting to empty if None).
    6. Log a debug message indicating the function has completed.

---

## function: `load_llm_config() -> dict`

Load LLM configuration from YAML file.

Args:
    None: This function does not take any arguments.

Returns:
    dict: A dictionary containing the loaded LLM configuration.
          Returns an empty dictionary if the file is not found or cannot be parsed.

Notes:
    1. Initialize a debug log message indicating the start of the function.
    2. Attempt to open and parse the YAML file at LLM_CONFIG_PATH.
    3. If the file is not found, log a warning and return an empty dictionary.
    4. If YAML parsing fails, log an exception and return an empty dictionary.
    5. On success, return the parsed configuration dictionary (defaulting to empty if None).
    6. Log a debug message indicating the function has completed.

---

## function: `get_endpoint_config(name: str) -> dict`

Retrieve configuration for a specific LLM endpoint by name.

Args:
    name (str): The name of the endpoint to retrieve configuration for.

Returns:
    dict: The configuration dictionary for the specified endpoint.
          Returns an empty dictionary if the endpoint is not found in the configuration.

Notes:
    1. Initialize a debug log message indicating the start of the function with the endpoint name.
    2. Load the LLM configuration using the load_llm_config function.
    3. Extract the list of endpoints from the loaded configuration.
    4. Iterate through each endpoint in the list.
    5. For each endpoint, check if its 'name' field matches the provided name argument.
    6. If a match is found, return the full configuration dictionary for that endpoint.
    7. If no match is found after iterating through all endpoints, return an empty dictionary.
    8. Log a warning if the endpoint is not found.
    9. Log a debug message indicating the function has completed.

---


===

===
# File: `__init__.py`


===

===
# File: `main.py`

## function: `main(query: str, log_level: str) -> None`

Run the Multi-Step Agent with a given query.

This function serves as the entry point for the Multi-Step Agent application.
It initializes the logging system, sets the logging level, creates the controller,
processes the user query through the agent's reasoning cycle, and outputs the final result.

Args:
    query: The input query string that the agent must process. The query should
           be a natural language request requiring multi-step reasoning and
           tool usage to answer.
    log_level: The desired logging level for the application. Valid choices are
               DEBUG, INFO, WARNING, ERROR, and CRITICAL. This controls the
               verbosity of runtime logs.

Returns:
    None. The function does not return a value. The agent's result is printed
    to stdout and logged, but no return value is provided.

Notes:
    1. Load environment variables from a .env file if the dotenv package is available.
    2. Initialize the logging system using the setup_logging function.
    3. Set the global logging level based on the provided log_level argument.
    4. Log a message indicating the start of the agent with the given query.
    5. Instantiate the Controller class to manage the agent's reasoning workflow.
    6. Call the controller's process_query method with the provided query.
    7. Print the agent's result in a formatted block.
    8. Log a success message if processing completes without exception.
    9. If an exception occurs during processing, log the error with full traceback
       and print a user-friendly error message to stdout.

---


===

===
# File: `logging_config.py`

## function: `setup_logging() -> None`

Configure logging for the application.

Sets up a default logging configuration with console output.

Args:
    None

Returns:
    None

Notes:
    1. Define a dictionary containing the logging configuration.
    2. Set the version to 1 to use the new configuration format.
    3. Disable existing loggers to prevent duplicate logging.
    4. Define a formatter named "standard" with a timestamp, logger name, log level, and message.
    5. Define a handler named "console" to output logs to stdout with the "standard" formatter.
    6. Set the root logger level to "INFO" and assign the "console" handler to it.
    7. Apply the configuration using dictConfig from the logging module.

---

## function: `get_logger(name: str) -> logging.Logger`

Get a configured logger instance.

Args:
    name: The name for the logger, typically __name__ of the calling module.

Returns:
    A configured logger instance that can be used to emit log messages.

Notes:
    1. Use the logging.getLogger function to retrieve or create a logger with the provided name.
    2. Return the logger instance, which will have already been configured by setup_logging.

---


===

===
# File: `__main__.py`


===

===
# File: `models.py`


===

===
# File: `observation_handler.py`

## function: `process_observation(action_result: ToolResponse) -> str`

Process observation from action result.

Args:
    action_result: The result from executing an action, containing the content to be observed.

Returns:
    A string representing the processed observation, formatted as "Observed: <content>".

Notes:
    1. Extract the content from the action_result object.
    2. Format the content into a string prefixed with "Observed: ".
    3. Return the formatted observation string.

---


===

===
# File: `action_handler.py`

## function: `process_action_selection(thoughts: str, action_client: Any, action_prompt: Any, tools: dict[str, ToolInterface]) -> ActionSelection`

Select the next action based on generated thoughts.

Args:
    thoughts: The thoughts generated by the think() method, representing the agent's
              analysis of the current situation and potential next steps.
    action_client: The LLM client responsible for generating the action selection.
                   This client must support the call() method with prompt and parser.
    action_prompt: The prompt template used to guide the LLM in selecting an action.
                   It should include placeholders for tools, analysis, and format instructions.
    tools: A dictionary mapping tool names to their respective ToolInterface implementations.
           This is used to list available tools in the prompt.

Returns:
    An ActionSelection object representing the chosen action. The object contains:
    - action_type: The type of action (e.g., "tool", "plan", "ask", "stop").
    - action_name: The name of the tool or action to execute.
    - reasoning: A string explaining the rationale for the selected action.
    - confidence: A float between 0 and 1 indicating the agent's confidence in the selection.

Notes:
    1. The function begins by logging the start of the process with the provided thoughts.
    2. It creates a PydanticOutputParser to ensure structured output from the LLM.
    3. It constructs a list of available tool names from the provided tools dictionary.
    4. It formats the action prompt using the available tools, generated thoughts, and format instructions.
    5. It calls the action_client with the formatted prompt and parser to generate an action.
    6. If the response contains a "parsed" field, it uses that as the action selection.
    7. Otherwise, it attempts to parse the response text using parse_json_markdown.
    8. If parsing fails, it falls back to a default web search action with a confidence of 0.5.
    9. The function logs the completion and returns the final action selection.

---


===

===
# File: `components.py`

## function: `initialize_llm_clients() -> dict[str, Any]`

Initialize LLM clients for different purposes.

Args:
    None

Returns:
    Dict mapping client names to LLMClient instances

Notes:
    1. Create a dictionary with keys "thinking", "action", and "completion".
    2. For each key, retrieve the corresponding LLMClient using get_llm_client with the specified model name.
    3. Return the constructed dictionary of clients.

---

## function: `initialize_tools() -> dict[str, ToolInterface]`

Initialize available tools.

Args:
    None

Returns:
    Dict mapping tool names to ToolInterface instances

Notes:
    1. Create an empty dictionary to store tool instances.
    2. Add the WebSearchTool instance with key "web_search".
    3. Add the WikipediaTool instance with key "wikipedia".
    4. Return the dictionary of tools.

---

## function: `create_prompt_templates() -> dict[str, PromptTemplate]`

Create prompt templates for different phases.

Args:
    None

Returns:
    Dict mapping template names to PromptTemplate instances

Notes:
    1. Create an empty dictionary to store prompt templates.
    2. Define the "think" template with a prompt that guides analysis of the question and memory state.
    3. Define the "action" template with a prompt that guides action selection based on analysis and available tools.
    4. Define the "completion" template with a prompt that determines if the question can be answered based on collected info.
    5. Return the dictionary of templates.

---

## function: `process_thoughts(query: str, memory_manager: Any, thinking_client: Any, think_prompt: PromptTemplate) -> str`

Generate thoughts based on the current state and memory.

Args:
    query: The original user query to process
    memory_manager: The working memory manager responsible for storing and retrieving memory
    thinking_client: The LLM client used for generating thoughts
    think_prompt: The prompt template used to guide the LLM's thinking process

Returns:
    A string containing the generated thoughts from the LLM

Notes:
    1. Retrieve a summary of the current memory state from the memory_manager.
    2. Format the think_prompt with the query and memory summary.
    3. Call the thinking_client with the formatted prompt.
    4. Extract the content from the response based on its structure (handling different response types).
    5. Return the generated thoughts as a string.

---

## function: `process_completion_decision(query: str, memory_manager: Any, completion_client: Any, completion_prompt: PromptTemplate) -> CompletionDecision`

Determine if we have sufficient information to answer the question.

Args:
    query: The original query to process
    memory_manager: The working memory manager responsible for retrieving collected information
    completion_client: The LLM client used for deciding completion
    completion_prompt: The prompt template used to guide the completion decision process

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

---

## function: `handle_tool_execution(tool_name: str, query: str, tools: dict[str, ToolInterface]) -> ToolResponse`

Execute a tool by name.

Args:
    tool_name: Name of the tool to execute
    query: Query/input for the tool
    tools: Dictionary of available tools mapped by name

Returns:
    ToolResponse containing the tool's response, including content and metadata

Notes:
    1. Check if the tool_name exists in the tools dictionary.
    2. If the tool exists, execute it with the provided query and return the response.
    3. If the tool does not exist, return a ToolResponse with an error message and metadata indicating the tool was not found.
    4. If an exception occurs during execution, return a ToolResponse with the error message and metadata.

---

## function: `__init__(self: UnknownType) -> None`

Initialize controller with configured LLM client and tools.

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

---

## function: `execute_tool(self: UnknownType, tool_name: str, query: str) -> ToolResponse`

Execute a tool with the given query.

Args:
    tool_name: Name of the tool to execute
    query: Query to pass to the tool

Returns:
    ToolResponse containing the tool's response with content and metadata

Notes:
    1. Check if the tool_name exists in self.tools.
    2. If the tool exists, execute it with the provided query and return the response.
    3. If the tool does not exist, return a ToolResponse with an error message and metadata indicating the tool was not found.
    4. If an exception occurs during execution, return a ToolResponse with the error message and metadata.

---

## function: `process_query(self: UnknownType, query: str) -> str`

Process user query through ReAct cycle.

Args:
    query: The original user query to process

Returns:
    The final answer generated by the agent as a string

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

---

## `Controller` class

Main controller that orchestrates the ReAct cycle for the multi-step agent.

---
## method: `Controller.__init__(self: UnknownType) -> None`

Initialize controller with configured LLM client and tools.

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

---
## method: `Controller.execute_tool(self: UnknownType, tool_name: str, query: str) -> ToolResponse`

Execute a tool with the given query.

Args:
    tool_name: Name of the tool to execute
    query: Query to pass to the tool

Returns:
    ToolResponse containing the tool's response with content and metadata

Notes:
    1. Check if the tool_name exists in self.tools.
    2. If the tool exists, execute it with the provided query and return the response.
    3. If the tool does not exist, return a ToolResponse with an error message and metadata indicating the tool was not found.
    4. If an exception occurs during execution, return a ToolResponse with the error message and metadata.

---
## method: `Controller.process_query(self: UnknownType, query: str) -> str`

Process user query through ReAct cycle.

Args:
    query: The original user query to process

Returns:
    The final answer generated by the agent as a string

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

---

===

===
# File: `main.py`


===

===
# File: `__init__.py`


===

===
# File: `manager.py`

## function: `__init__(self: UnknownType, initial_query: str) -> None`

Initialize memory manager.

Args:
    initial_query: The initial query to start with, used to initialize the query state.

Returns:
    None

Notes:
    1. Creates a new empty working memory structure with default values.
    2. Initializes the temporal reasoner to handle temporal reasoning.
    3. Sets memory management settings: maximum number of facts and confidence threshold for pruning.
    4. Logs the initialization start and completion.

---

## function: `add_observation(self: UnknownType, observation: dict[str, Any]) -> None`

Add new observation to working memory.

Args:
    observation: Dictionary containing observation data with keys:
        - content: The observed fact content
        - source: Source of the observation
        - confidence: Confidence score (0.0-1.0)
        - metadata: Additional metadata about the observation

Returns:
    None

Notes:
    1. Generates a unique fact ID based on the current number of facts.
    2. Creates a new Fact object from the observation data.
    3. Adds the fact to the information store.
    4. Adds confidence score to the confidence scores dictionary.
    5. If source is not already in sources, creates a new SourceMetadata object and adds it.
    6. Updates the last updated timestamp.
    7. Checks if the number of facts exceeds the maximum, and if so, triggers pruning.

---

## function: `get_relevant_facts(self: UnknownType, context: str) -> list[dict[str, Any]]`

Retrieve relevant facts based on context.

Args:
    context: Context string to match against facts for relevance.

Returns:
    List of relevant facts as dictionaries with keys:
        - id: The fact ID
        - content: The fact content
        - source: The source of the fact
        - confidence: The confidence score of the fact
        - timestamp: The timestamp of the fact in ISO format

Notes:
    1. Converts the context to lowercase for case-insensitive matching.
    2. Iterates through all facts in the information store.
    3. Checks if the context appears in the fact content or source.
    4. If a match is found, constructs a dictionary with fact details and adds it to the result list.
    5. Returns the list of relevant facts.

---

## function: `infer_relationships(self: UnknownType) -> None`

Infer relationships between facts in working memory.

Args:
    None

Returns:
    None

Notes:
    1. Retrieves all facts from the information store.
    2. Uses the temporal reasoner to correlate temporal facts and detect causal relationships.
    3. Combines the temporal and causal relationships into a single list.
    4. Adds each relationship to the information store's relationships dictionary.
    5. Updates the temporal context in the reasoning state using the temporal reasoner.

---

## function: `update_confidence_scores(self: UnknownType) -> None`

Update confidence scores based on new evidence and source credibility.

Args:
    None

Returns:
    None

Notes:
    1. Iterates through all facts in the information store.
    2. Retrieves the source metadata for each fact's source.
    3. If source metadata exists, calculates a new confidence score as the average of the fact's current confidence and the source's credibility.
    4. Updates the confidence score in both the confidence scores dictionary and the fact object.
    5. Updates the last updated timestamp.

---

## function: `serialize(self: UnknownType) -> str`

Serialize memory to JSON string.

Args:
    None

Returns:
    JSON string representation of the working memory object.

Notes:
    1. Uses the model_dump_json method to convert the memory object to a JSON string.
    2. Returns the serialized string.

---

## function: `deserialize(self: UnknownType, data: str) -> WorkingMemory`

Deserialize memory from JSON string.

Args:
    data: JSON string representation of working memory.

Returns:
    WorkingMemory object reconstructed from the JSON string.

Notes:
    1. Parses the JSON string into a dictionary.
    2. Uses the model_validate method to create a WorkingMemory object from the dictionary.
    3. Updates the current memory object and the temporal reasoner to match the deserialized state.

---

## function: `prune_memory(self: UnknownType) -> None`

Prune memory by removing least relevant facts based on confidence and recency.

Args:
    None

Returns:
    None

Notes:
    1. Retrieves the current list of facts.
    2. If the number of facts is below the maximum, return without pruning.
    3. Scores each fact based on confidence and recency, with confidence weighted more heavily.
    4. Sorts the facts by combined score in descending order.
    5. Determines how many facts to remove based on exceeding the maximum capacity.
    6. Removes the lowest-scoring facts from the information store.
    7. Updates the last updated timestamp.

---

## function: `get_memory(self: UnknownType) -> WorkingMemory`

Get the working memory object.

Args:
    None

Returns:
    The WorkingMemory object currently managed by this instance.

Notes:
    1. Returns the internal memory object stored in the instance.
    2. This allows external access to the full memory state.

---

## function: `summarize_state(self: UnknownType) -> dict[str, Any]`

Create a summary of the current memory state for LLM context window management.

Args:
    None

Returns:
    Dictionary containing a concise summary of the working memory state with keys:
        - query_state: Dictionary with original_query and current_focus
        - reasoning_state: Dictionary with current_hypothesis, answer_draft, and information_gaps
        - top_facts: List of up to 10 most confident facts with content, confidence, and source
        - memory_stats: Dictionary with total_facts, total_relationships, created_at, and updated_at

Notes:
    1. Retrieves all facts and sorts them by confidence in descending order.
    2. Takes the top 10 most confident facts for the summary.
    3. Creates a dictionary with the current query state, reasoning state, top facts, and memory statistics.
    4. Limits the number of information gaps to 5 for brevity.
    5. Returns the constructed summary dictionary.

---

## `WorkingMemoryManager` class

Manages the working memory operations for the multi-step agent.

---
## method: `WorkingMemoryManager.__init__(self: UnknownType, initial_query: str) -> None`

Initialize memory manager.

Args:
    initial_query: The initial query to start with, used to initialize the query state.

Returns:
    None

Notes:
    1. Creates a new empty working memory structure with default values.
    2. Initializes the temporal reasoner to handle temporal reasoning.
    3. Sets memory management settings: maximum number of facts and confidence threshold for pruning.
    4. Logs the initialization start and completion.

---
## method: `WorkingMemoryManager.add_observation(self: UnknownType, observation: dict[str, Any]) -> None`

Add new observation to working memory.

Args:
    observation: Dictionary containing observation data with keys:
        - content: The observed fact content
        - source: Source of the observation
        - confidence: Confidence score (0.0-1.0)
        - metadata: Additional metadata about the observation

Returns:
    None

Notes:
    1. Generates a unique fact ID based on the current number of facts.
    2. Creates a new Fact object from the observation data.
    3. Adds the fact to the information store.
    4. Adds confidence score to the confidence scores dictionary.
    5. If source is not already in sources, creates a new SourceMetadata object and adds it.
    6. Updates the last updated timestamp.
    7. Checks if the number of facts exceeds the maximum, and if so, triggers pruning.

---
## method: `WorkingMemoryManager.get_relevant_facts(self: UnknownType, context: str) -> list[dict[str, Any]]`

Retrieve relevant facts based on context.

Args:
    context: Context string to match against facts for relevance.

Returns:
    List of relevant facts as dictionaries with keys:
        - id: The fact ID
        - content: The fact content
        - source: The source of the fact
        - confidence: The confidence score of the fact
        - timestamp: The timestamp of the fact in ISO format

Notes:
    1. Converts the context to lowercase for case-insensitive matching.
    2. Iterates through all facts in the information store.
    3. Checks if the context appears in the fact content or source.
    4. If a match is found, constructs a dictionary with fact details and adds it to the result list.
    5. Returns the list of relevant facts.

---
## method: `WorkingMemoryManager.infer_relationships(self: UnknownType) -> None`

Infer relationships between facts in working memory.

Args:
    None

Returns:
    None

Notes:
    1. Retrieves all facts from the information store.
    2. Uses the temporal reasoner to correlate temporal facts and detect causal relationships.
    3. Combines the temporal and causal relationships into a single list.
    4. Adds each relationship to the information store's relationships dictionary.
    5. Updates the temporal context in the reasoning state using the temporal reasoner.

---
## method: `WorkingMemoryManager.update_confidence_scores(self: UnknownType) -> None`

Update confidence scores based on new evidence and source credibility.

Args:
    None

Returns:
    None

Notes:
    1. Iterates through all facts in the information store.
    2. Retrieves the source metadata for each fact's source.
    3. If source metadata exists, calculates a new confidence score as the average of the fact's current confidence and the source's credibility.
    4. Updates the confidence score in both the confidence scores dictionary and the fact object.
    5. Updates the last updated timestamp.

---
## method: `WorkingMemoryManager.serialize(self: UnknownType) -> str`

Serialize memory to JSON string.

Args:
    None

Returns:
    JSON string representation of the working memory object.

Notes:
    1. Uses the model_dump_json method to convert the memory object to a JSON string.
    2. Returns the serialized string.

---
## method: `WorkingMemoryManager.deserialize(self: UnknownType, data: str) -> WorkingMemory`

Deserialize memory from JSON string.

Args:
    data: JSON string representation of working memory.

Returns:
    WorkingMemory object reconstructed from the JSON string.

Notes:
    1. Parses the JSON string into a dictionary.
    2. Uses the model_validate method to create a WorkingMemory object from the dictionary.
    3. Updates the current memory object and the temporal reasoner to match the deserialized state.

---
## method: `WorkingMemoryManager.prune_memory(self: UnknownType) -> None`

Prune memory by removing least relevant facts based on confidence and recency.

Args:
    None

Returns:
    None

Notes:
    1. Retrieves the current list of facts.
    2. If the number of facts is below the maximum, return without pruning.
    3. Scores each fact based on confidence and recency, with confidence weighted more heavily.
    4. Sorts the facts by combined score in descending order.
    5. Determines how many facts to remove based on exceeding the maximum capacity.
    6. Removes the lowest-scoring facts from the information store.
    7. Updates the last updated timestamp.

---
## method: `WorkingMemoryManager.get_memory(self: UnknownType) -> WorkingMemory`

Get the working memory object.

Args:
    None

Returns:
    The WorkingMemory object currently managed by this instance.

Notes:
    1. Returns the internal memory object stored in the instance.
    2. This allows external access to the full memory state.

---
## method: `WorkingMemoryManager.summarize_state(self: UnknownType) -> dict[str, Any]`

Create a summary of the current memory state for LLM context window management.

Args:
    None

Returns:
    Dictionary containing a concise summary of the working memory state with keys:
        - query_state: Dictionary with original_query and current_focus
        - reasoning_state: Dictionary with current_hypothesis, answer_draft, and information_gaps
        - top_facts: List of up to 10 most confident facts with content, confidence, and source
        - memory_stats: Dictionary with total_facts, total_relationships, created_at, and updated_at

Notes:
    1. Retrieves all facts and sorts them by confidence in descending order.
    2. Takes the top 10 most confident facts for the summary.
    3. Creates a dictionary with the current query state, reasoning state, top facts, and memory statistics.
    4. Limits the number of information gaps to 5 for brevity.
    5. Returns the constructed summary dictionary.

---

===

===
# File: `temporal.py`

## function: `__init__(self: UnknownType) -> None`

Initialize temporal reasoner.

Notes:
    1. Initializes the temporal reasoner with no state.
    2. No configuration or external dependencies are required.

---

## function: `correlate_temporal_facts(self: UnknownType, facts: list[Fact]) -> list[dict[str, Any]]`

Correlate facts based on temporal relationships.

Args:
    facts: List of Fact objects to analyze for temporal correlations.

Returns:
    List of dictionaries describing temporal relationships between facts.
    Each dictionary contains:
        - type: Always "temporal"
        - fact1_id: ID of the first fact
        - fact2_id: ID of the second fact
        - relationship: "before" if fact1 occurred earlier, "after" otherwise
        - confidence: Confidence score (0.8) for the temporal ordering

Notes:
    1. Iterates through all pairs of facts in the input list.
    2. Compares the timestamps of each pair of facts.
    3. If fact1's timestamp is earlier than fact2's, adds a "before" relationship.
    4. If fact1's timestamp is later than fact2's, adds an "after" relationship.
    5. The confidence score is fixed at 0.8 for all relationships.
    6. Returns the accumulated list of relationships.

---

## function: `detect_causality(self: UnknownType, facts: list[Fact], memory: WorkingMemory) -> list[dict[str, Any]]`

Detect potential causal relationships between facts.

Args:
    facts: List of Fact objects to analyze for causal relationships.
    memory: Current working memory state used for context (not directly used in this implementation).

Returns:
    List of dictionaries describing potential causal relationships.
    Each dictionary contains:
        - type: Always "causal"
        - fact1_id: ID of the first fact
        - fact2_id: ID of the second fact
        - relationship: Always "causal"
        - confidence: Confidence score (0.6) for the causal link
        - indicator: The keyword that triggered the causal detection

Notes:
    1. Iterates through all pairs of facts in the input list.
    2. Calculates the time difference between the timestamps of each pair.
    3. If the time difference is less than or equal to 86400 seconds (24 hours), proceeds to check for causal keywords.
    4. Checks if any of the defined causal indicators are present in either fact's content.
    5. If a causal indicator is found, adds a causal relationship with the detected keyword.
    6. The confidence score is fixed at 0.6 for all relationships.
    7. Returns the accumulated list of causal relationships.

---

## function: `get_temporal_context(self: UnknownType, memory: WorkingMemory) -> dict[str, Any]`

Extract temporal context from working memory.

Args:
    memory: Current working memory state containing facts to analyze.

Returns:
    Dictionary containing temporal context information with the following keys:
        - earliest_timestamp: ISO-formatted timestamp of the earliest fact, or None if no facts exist
        - latest_timestamp: ISO-formatted timestamp of the latest fact, or None if no facts exist
        - temporal_facts: List of dictionaries containing ID, timestamp, and content of each fact,
            sorted chronologically by timestamp

Notes:
    1. Extracts all facts from the working memory's information store.
    2. Converts each fact into a dictionary with ID, timestamp (as ISO string), and content.
    3. Sorts the list of fact dictionaries by timestamp in ascending order.
    4. If there are no facts, sets earliest_timestamp and latest_timestamp to None.
    5. Otherwise, sets earliest_timestamp to the first (oldest) fact's timestamp and latest_timestamp to the last (newest).
    6. Returns the constructed context dictionary.

---

## `TemporalReasoner` class

Handles temporal reasoning operations for working memory.

---
## method: `TemporalReasoner.__init__(self: UnknownType) -> None`

Initialize temporal reasoner.

Notes:
    1. Initializes the temporal reasoner with no state.
    2. No configuration or external dependencies are required.

---
## method: `TemporalReasoner.correlate_temporal_facts(self: UnknownType, facts: list[Fact]) -> list[dict[str, Any]]`

Correlate facts based on temporal relationships.

Args:
    facts: List of Fact objects to analyze for temporal correlations.

Returns:
    List of dictionaries describing temporal relationships between facts.
    Each dictionary contains:
        - type: Always "temporal"
        - fact1_id: ID of the first fact
        - fact2_id: ID of the second fact
        - relationship: "before" if fact1 occurred earlier, "after" otherwise
        - confidence: Confidence score (0.8) for the temporal ordering

Notes:
    1. Iterates through all pairs of facts in the input list.
    2. Compares the timestamps of each pair of facts.
    3. If fact1's timestamp is earlier than fact2's, adds a "before" relationship.
    4. If fact1's timestamp is later than fact2's, adds an "after" relationship.
    5. The confidence score is fixed at 0.8 for all relationships.
    6. Returns the accumulated list of relationships.

---
## method: `TemporalReasoner.detect_causality(self: UnknownType, facts: list[Fact], memory: WorkingMemory) -> list[dict[str, Any]]`

Detect potential causal relationships between facts.

Args:
    facts: List of Fact objects to analyze for causal relationships.
    memory: Current working memory state used for context (not directly used in this implementation).

Returns:
    List of dictionaries describing potential causal relationships.
    Each dictionary contains:
        - type: Always "causal"
        - fact1_id: ID of the first fact
        - fact2_id: ID of the second fact
        - relationship: Always "causal"
        - confidence: Confidence score (0.6) for the causal link
        - indicator: The keyword that triggered the causal detection

Notes:
    1. Iterates through all pairs of facts in the input list.
    2. Calculates the time difference between the timestamps of each pair.
    3. If the time difference is less than or equal to 86400 seconds (24 hours), proceeds to check for causal keywords.
    4. Checks if any of the defined causal indicators are present in either fact's content.
    5. If a causal indicator is found, adds a causal relationship with the detected keyword.
    6. The confidence score is fixed at 0.6 for all relationships.
    7. Returns the accumulated list of causal relationships.

---
## method: `TemporalReasoner.get_temporal_context(self: UnknownType, memory: WorkingMemory) -> dict[str, Any]`

Extract temporal context from working memory.

Args:
    memory: Current working memory state containing facts to analyze.

Returns:
    Dictionary containing temporal context information with the following keys:
        - earliest_timestamp: ISO-formatted timestamp of the earliest fact, or None if no facts exist
        - latest_timestamp: ISO-formatted timestamp of the latest fact, or None if no facts exist
        - temporal_facts: List of dictionaries containing ID, timestamp, and content of each fact,
            sorted chronologically by timestamp

Notes:
    1. Extracts all facts from the working memory's information store.
    2. Converts each fact into a dictionary with ID, timestamp (as ISO string), and content.
    3. Sorts the list of fact dictionaries by timestamp in ascending order.
    4. If there are no facts, sets earliest_timestamp and latest_timestamp to None.
    5. Otherwise, sets earliest_timestamp to the first (oldest) fact's timestamp and latest_timestamp to the last (newest).
    6. Returns the constructed context dictionary.

---

===

===
# File: `models.py`


===

===
# File: `conflict.py`

## function: `__init__(self: UnknownType) -> None`

Initialize the conflict resolver.

Notes:
    1. Initialize the conflict resolver instance.
    2. Log the start of initialization.
    3. Log the completion of initialization.

---

## function: `detect_conflicts(self: UnknownType, memory: WorkingMemory) -> list[dict[str, Any]]`

Identify contradictory claims in the working memory.

Args:
    memory: The working memory containing facts to check for conflicts

Returns:
    A list of detected conflicts with details about contradictory facts.
    Each conflict is a dictionary with keys:
        - fact1: The first conflicting fact (Fact)
        - fact2: The second conflicting fact (Fact)
        - type: The type of conflict (str)
        - description: A human-readable description of the contradiction (str)

Notes:
    1. Retrieve all facts from the working memory's information store.
    2. Compare each fact with every other fact in the list.
    3. For each pair of facts, check if they are contradictory using _are_contradictory.
    4. If a contradiction is found, create a conflict dictionary and add it to the list.
    5. Return the list of detected conflicts.

---

## function: `investigate_conflicts(self: UnknownType, conflicts: list[dict[str, Any]], memory: WorkingMemory) -> list[dict[str, Any]]`

Gather additional context to investigate detected conflicts.

Args:
    conflicts: List of detected conflicts to investigate
    memory: The working memory containing facts

Returns:
    A list of investigation results with additional context.
    Each result is a dictionary with keys:
        - conflict: The original conflict dictionary
        - investigation: A description of the investigation performed (str)
        - sources: List of source identifiers for the conflicting facts (List[str])

Notes:
    1. Iterate over each conflict in the provided list.
    2. For each conflict, create an investigation result dictionary.
    3. In this implementation, the investigation is simulated.
    4. The sources are taken directly from the conflicting facts.
    5. Return the list of investigation results.

---

## function: `resolve_conflicts(self: UnknownType, investigations: list[dict[str, Any]], memory: WorkingMemory) -> list[dict[str, Any]]`

Weight and resolve contradictory information based on source reliability.

Args:
    investigations: List of conflict investigations with additional context
    memory: The working memory containing facts

Returns:
    A list of resolved conflicts with weighted decisions.
    Each resolution is a dictionary with keys:
        - preferred_fact: The fact selected as correct (Fact)
        - rejected_fact: The fact selected as incorrect (Fact)
        - reasoning: Explanation for the selection (str)

Notes:
    1. Iterate over each investigation result.
    2. Extract the conflicting facts from the investigation.
    3. Compare the confidence scores of the two facts.
    4. If one fact has higher confidence, select it as preferred.
    5. If confidence scores are equal, prefer the first encountered fact.
    6. Generate a reasoning string explaining the decision.
    7. Create a resolution dictionary and add it to the list.
    8. Return the list of resolutions.

---

## function: `synthesize_with_uncertainty(self: UnknownType, facts: list[Fact], conflicts: list[dict[str, Any]]) -> str`

Create nuanced answers that acknowledge uncertainties.

Args:
    facts: List of facts to synthesize
    conflicts: List of unresolved conflicts

Returns:
    A synthesized answer that acknowledges uncertainties.
    The string contains a bullet list of facts with confidence scores,
    followed by a note about conflicting claims if conflicts exist.

Notes:
    1. If no facts are provided, return a default message.
    2. Start with a header line.
    3. Add each fact as a bullet point with confidence score.
    4. If conflicts exist, append a note about uncertainty and verification recommendation.
    5. Return the synthesized string.

---

## function: `_are_contradictory(self: UnknownType, fact1: Fact, fact2: Fact) -> bool`

Check if two facts are contradictory.

Args:
    fact1: First fact to compare
    fact2: Second fact to compare

Returns:
    True if facts are contradictory, False otherwise

Notes:
    1. Convert both fact contents to lowercase for case-insensitive comparison.
    2. Check for predefined contradictory keyword pairs.
    3. If a matching pair is found, return True.
    4. Check for direct opposite concepts (e.g., "round" vs "flat").
    5. If no contradiction is found, return False.

---

## `ConflictResolver` class

Handles detection and resolution of contradictory information.

---
## method: `ConflictResolver.__init__(self: UnknownType) -> None`

Initialize the conflict resolver.

Notes:
    1. Initialize the conflict resolver instance.
    2. Log the start of initialization.
    3. Log the completion of initialization.

---
## method: `ConflictResolver.detect_conflicts(self: UnknownType, memory: WorkingMemory) -> list[dict[str, Any]]`

Identify contradictory claims in the working memory.

Args:
    memory: The working memory containing facts to check for conflicts

Returns:
    A list of detected conflicts with details about contradictory facts.
    Each conflict is a dictionary with keys:
        - fact1: The first conflicting fact (Fact)
        - fact2: The second conflicting fact (Fact)
        - type: The type of conflict (str)
        - description: A human-readable description of the contradiction (str)

Notes:
    1. Retrieve all facts from the working memory's information store.
    2. Compare each fact with every other fact in the list.
    3. For each pair of facts, check if they are contradictory using _are_contradictory.
    4. If a contradiction is found, create a conflict dictionary and add it to the list.
    5. Return the list of detected conflicts.

---
## method: `ConflictResolver.investigate_conflicts(self: UnknownType, conflicts: list[dict[str, Any]], memory: WorkingMemory) -> list[dict[str, Any]]`

Gather additional context to investigate detected conflicts.

Args:
    conflicts: List of detected conflicts to investigate
    memory: The working memory containing facts

Returns:
    A list of investigation results with additional context.
    Each result is a dictionary with keys:
        - conflict: The original conflict dictionary
        - investigation: A description of the investigation performed (str)
        - sources: List of source identifiers for the conflicting facts (List[str])

Notes:
    1. Iterate over each conflict in the provided list.
    2. For each conflict, create an investigation result dictionary.
    3. In this implementation, the investigation is simulated.
    4. The sources are taken directly from the conflicting facts.
    5. Return the list of investigation results.

---
## method: `ConflictResolver.resolve_conflicts(self: UnknownType, investigations: list[dict[str, Any]], memory: WorkingMemory) -> list[dict[str, Any]]`

Weight and resolve contradictory information based on source reliability.

Args:
    investigations: List of conflict investigations with additional context
    memory: The working memory containing facts

Returns:
    A list of resolved conflicts with weighted decisions.
    Each resolution is a dictionary with keys:
        - preferred_fact: The fact selected as correct (Fact)
        - rejected_fact: The fact selected as incorrect (Fact)
        - reasoning: Explanation for the selection (str)

Notes:
    1. Iterate over each investigation result.
    2. Extract the conflicting facts from the investigation.
    3. Compare the confidence scores of the two facts.
    4. If one fact has higher confidence, select it as preferred.
    5. If confidence scores are equal, prefer the first encountered fact.
    6. Generate a reasoning string explaining the decision.
    7. Create a resolution dictionary and add it to the list.
    8. Return the list of resolutions.

---
## method: `ConflictResolver.synthesize_with_uncertainty(self: UnknownType, facts: list[Fact], conflicts: list[dict[str, Any]]) -> str`

Create nuanced answers that acknowledge uncertainties.

Args:
    facts: List of facts to synthesize
    conflicts: List of unresolved conflicts

Returns:
    A synthesized answer that acknowledges uncertainties.
    The string contains a bullet list of facts with confidence scores,
    followed by a note about conflicting claims if conflicts exist.

Notes:
    1. If no facts are provided, return a default message.
    2. Start with a header line.
    3. Add each fact as a bullet point with confidence score.
    4. If conflicts exist, append a note about uncertainty and verification recommendation.
    5. Return the synthesized string.

---
## method: `ConflictResolver._are_contradictory(self: UnknownType, fact1: Fact, fact2: Fact) -> bool`

Check if two facts are contradictory.

Args:
    fact1: First fact to compare
    fact2: Second fact to compare

Returns:
    True if facts are contradictory, False otherwise

Notes:
    1. Convert both fact contents to lowercase for case-insensitive comparison.
    2. Check for predefined contradictory keyword pairs.
    3. If a matching pair is found, return True.
    4. Check for direct opposite concepts (e.g., "round" vs "flat").
    5. If no contradiction is found, return False.

---

===

===
# File: `synthesis.py`

## function: `__init__(self: UnknownType) -> None`

Initialize the synthesis engine.

Notes:
    1. Logs a debug message indicating initialization has started.
    2. Initializes the ConfidenceScorer instance for use in confidence calculations.
    3. Logs a debug message indicating initialization has completed.

---

## function: `synthesize_answer(self: UnknownType, memory: WorkingMemory, query: str) -> str`

Generate an answer from collected facts.

Args:
    memory: The working memory containing collected facts
    query: The original query to answer

Returns:
    A synthesized answer string with confidence scoring and citations.
    If no facts are available, returns a default message indicating no information was gathered.

Notes:
    1. Logs a debug message indicating the synthesis process has started.
    2. Retrieves all facts from the memory's information store.
    3. If no facts are found, returns a default message and exits.
    4. Eliminates duplicate facts using the eliminate_redundancy method.
    5. Constructs a narrative from the unique facts using the construct_narrative method.
    6. Generates citations for the facts using the generate_citations method.
    7. Calculates confidence scores for the answer using the confidence scorer.
    8. Generates a confidence report based on the calculated scores.
    9. Combines the narrative, confidence report, and citations into a single answer string.
    10. Logs a debug message indicating the synthesis process has completed.
    11. Returns the final synthesized answer.

---

## function: `eliminate_redundancy(self: UnknownType, facts: list[Fact]) -> list[Fact]`

Remove duplicate information from collected facts.

Args:
    facts: List of facts to process

Returns:
    List of unique facts with redundancy removed.

Notes:
    1. Currently returns all input facts without any deduplication.
    2. Intended to be extended with logic to identify and eliminate duplicate facts.

---

## function: `construct_narrative(self: UnknownType, facts: list[Fact], query: str) -> str`

Build a coherent response from discrete facts.

Args:
    facts: List of facts to construct narrative from
    query: The original query to answer

Returns:
    A coherent narrative string summarizing the facts.
    If no facts are provided, returns a default message indicating no information was found.

Notes:
    1. Checks if the list of facts is empty and returns a default message if so.
    2. Creates a list of formatted fact strings using a bullet point format.
    3. Combines the bullet points into a single narrative string.
    4. Returns the narrative string.

---

## function: `generate_citations(self: UnknownType, facts: list[Fact]) -> str`

Create source attributions for claims with timestamp tracking.

Args:
    facts: List of facts to generate citations for

Returns:
    Formatted citations string including source names and retrieval timestamps.
    Returns an empty string if no facts are provided.

Notes:
    1. Checks if the list of facts is empty and returns an empty string if so.
    2. Initializes a list with the header "## Sources:".
    3. For each fact, appends a citation entry with source name and timestamp (if available).
    4. Joins all citation entries into a single string, skipping the header if no citations were added.
    5. Returns the formatted citations string.

---

## `SynthesisEngine` class

Synthesizes answers from collected facts with confidence scoring and conflict resolution.

---
## method: `SynthesisEngine.__init__(self: UnknownType) -> None`

Initialize the synthesis engine.

Notes:
    1. Logs a debug message indicating initialization has started.
    2. Initializes the ConfidenceScorer instance for use in confidence calculations.
    3. Logs a debug message indicating initialization has completed.

---
## method: `SynthesisEngine.synthesize_answer(self: UnknownType, memory: WorkingMemory, query: str) -> str`

Generate an answer from collected facts.

Args:
    memory: The working memory containing collected facts
    query: The original query to answer

Returns:
    A synthesized answer string with confidence scoring and citations.
    If no facts are available, returns a default message indicating no information was gathered.

Notes:
    1. Logs a debug message indicating the synthesis process has started.
    2. Retrieves all facts from the memory's information store.
    3. If no facts are found, returns a default message and exits.
    4. Eliminates duplicate facts using the eliminate_redundancy method.
    5. Constructs a narrative from the unique facts using the construct_narrative method.
    6. Generates citations for the facts using the generate_citations method.
    7. Calculates confidence scores for the answer using the confidence scorer.
    8. Generates a confidence report based on the calculated scores.
    9. Combines the narrative, confidence report, and citations into a single answer string.
    10. Logs a debug message indicating the synthesis process has completed.
    11. Returns the final synthesized answer.

---
## method: `SynthesisEngine.eliminate_redundancy(self: UnknownType, facts: list[Fact]) -> list[Fact]`

Remove duplicate information from collected facts.

Args:
    facts: List of facts to process

Returns:
    List of unique facts with redundancy removed.

Notes:
    1. Currently returns all input facts without any deduplication.
    2. Intended to be extended with logic to identify and eliminate duplicate facts.

---
## method: `SynthesisEngine.construct_narrative(self: UnknownType, facts: list[Fact], query: str) -> str`

Build a coherent response from discrete facts.

Args:
    facts: List of facts to construct narrative from
    query: The original query to answer

Returns:
    A coherent narrative string summarizing the facts.
    If no facts are provided, returns a default message indicating no information was found.

Notes:
    1. Checks if the list of facts is empty and returns a default message if so.
    2. Creates a list of formatted fact strings using a bullet point format.
    3. Combines the bullet points into a single narrative string.
    4. Returns the narrative string.

---
## method: `SynthesisEngine.generate_citations(self: UnknownType, facts: list[Fact]) -> str`

Create source attributions for claims with timestamp tracking.

Args:
    facts: List of facts to generate citations for

Returns:
    Formatted citations string including source names and retrieval timestamps.
    Returns an empty string if no facts are provided.

Notes:
    1. Checks if the list of facts is empty and returns an empty string if so.
    2. Initializes a list with the header "## Sources:".
    3. For each fact, appends a citation entry with source name and timestamp (if available).
    4. Joins all citation entries into a single string, skipping the header if no citations were added.
    5. Returns the formatted citations string.

---

===

===
# File: `selector.py`

## function: `__init__(self: UnknownType, available_tools: dict[str, ToolInterface]) -> None`

Initialize tool selector with available tools.

Args:
    available_tools: A dictionary mapping tool names (str) to their respective ToolInterface instances.
                    This defines the set of tools the selector can choose from.

Notes:
    1. Stores the provided available_tools dictionary for later use.
    2. Instantiates a ConfidenceScorer to evaluate the confidence of facts in memory.
    3. Instantiates a ConflictResolver to detect contradictions in the current memory state.

---

## function: `classify_intent(self: UnknownType, query: str) -> str`

Classify the user's query intent to determine which category of tools is most appropriate.

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

---

## function: `score_relevance(self: UnknownType, query: str, tool_name: str) -> float`

Calculate a relevance score between 0.0 and 1.0 for a specific tool given a query.

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

---

## function: `select_tool(self: UnknownType, query: str, memory: WorkingMemory) -> str`

Select the most appropriate tool from the available tools based on query relevance and memory state.

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

---

## function: `analyze_cost_benefit(self: UnknownType, tool_name: str, query: str, memory: WorkingMemory) -> dict[str, Any]`

Analyze the cost and benefit of using a specific tool for a given query and memory state.

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

---

## `ToolSelector` class

Tool selection mechanism based on query classification and relevance scoring.

---
## method: `ToolSelector.__init__(self: UnknownType, available_tools: dict[str, ToolInterface]) -> None`

Initialize tool selector with available tools.

Args:
    available_tools: A dictionary mapping tool names (str) to their respective ToolInterface instances.
                    This defines the set of tools the selector can choose from.

Notes:
    1. Stores the provided available_tools dictionary for later use.
    2. Instantiates a ConfidenceScorer to evaluate the confidence of facts in memory.
    3. Instantiates a ConflictResolver to detect contradictions in the current memory state.

---
## method: `ToolSelector.classify_intent(self: UnknownType, query: str) -> str`

Classify the user's query intent to determine which category of tools is most appropriate.

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

---
## method: `ToolSelector.score_relevance(self: UnknownType, query: str, tool_name: str) -> float`

Calculate a relevance score between 0.0 and 1.0 for a specific tool given a query.

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

---
## method: `ToolSelector.select_tool(self: UnknownType, query: str, memory: WorkingMemory) -> str`

Select the most appropriate tool from the available tools based on query relevance and memory state.

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

---
## method: `ToolSelector.analyze_cost_benefit(self: UnknownType, tool_name: str, query: str, memory: WorkingMemory) -> dict[str, Any]`

Analyze the cost and benefit of using a specific tool for a given query and memory state.

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

---

===

===
# File: `__init__.py`


===

===
# File: `confidence.py`

## function: `__init__(self: UnknownType) -> None`

Initialize the confidence scorer with default weights and source categories.

Notes:
    1. Initializes the source credibility weights for different source types.
    2. Sets up keyword-based categorization for source names.
    3. Logs initialization start and completion.

---

## function: `calculate_source_credibility(self: UnknownType, source_name: str) -> float`

Rate source reliability based on source type.

Args:
    source_name: The name or identifier of the source (str)

Returns:
    A float between 0.0 and 1.0 representing the credibility score of the source.

Notes:
    1. Converts the source name to lowercase for case-insensitive matching.
    2. Uses keyword matching to categorize the source into one of the predefined categories.
    3. Retrieves the credibility weight for the matched category or defaults to "unknown".
    4. Returns the credibility score.

---

## function: `calculate_temporal_consistency(self: UnknownType, facts: list[Fact]) -> float`

Handle time-sensitive information consistency.

Args:
    facts: List of Fact objects to evaluate for temporal consistency.

Returns:
    A float between 0.0 and 1.0 representing the temporal consistency score.

Notes:
    1. Initializes the consistency score to a default value of 0.9.
    2. In a real implementation, this would check timestamps and temporal relationships between facts.
    3. Returns the default consistency score for now.

---

## function: `calculate_consistency_score(self: UnknownType, facts: list[Fact]) -> float`

Evaluate consistency across multiple sources.

Args:
    facts: List of Fact objects to evaluate for consistency between sources.

Returns:
    A float between 0.0 and 1.0 representing the cross-source consistency score.

Notes:
    1. If fewer than two facts are present, returns 1.0 (perfect consistency by default).
    2. In a real implementation, this would compare the content of facts for similarity.
    3. Returns a default score of 0.85 for now.

---

## function: `calculate_completeness_score(self: UnknownType, facts: list[Fact], query: str) -> float`

Assess answer coverage and completeness.

Args:
    facts: List of Fact objects related to the query.
    query: The original user query (str) used to assess completeness.

Returns:
    A float between 0.0 and 1.0 representing the completeness score.

Notes:
    1. Uses the number of facts as a proxy for completeness.
    2. Assumes that up to 5 facts represent full completeness.
    3. Returns the ratio of facts to 5, capped at 1.0.

---

## function: `calculate_confidence_score(self: UnknownType, memory: WorkingMemory, query: str) -> dict[str, Any]`

Calculate overall confidence score for the current state.

Args:
    memory: The current working memory state containing facts and sources.
    query: The original query (str) to assess confidence against.

Returns:
    A dictionary containing:
        - overall_confidence: float (0-100) representing the final confidence score.
        - source_credibility: float (0-100) representing the average source credibility.
        - temporal_consistency: float (0-100) representing temporal consistency.
        - cross_source_consistency: float (0-100) representing consistency between sources.
        - completeness: float (0-100) representing completeness of answer.

Notes:
    1. Extracts all facts from the working memory.
    2. If no facts exist, returns a result with all scores set to 0.0.
    3. For each fact, retrieves its source and calculates credibility.
    4. Computes average source credibility from all facts.
    5. Calculates temporal consistency, cross-source consistency, and completeness.
    6. Combines scores using weighted averaging (source: 40%, temporal: 20%, cross-source: 20%, completeness: 20%).
    7. Scales the overall confidence to 0-100 scale and returns all metrics.

---

## function: `generate_confidence_report(self: UnknownType, confidence_data: dict[str, Any]) -> str`

Generate a detailed explanation of confidence scores.

Args:
    confidence_data: Dictionary containing confidence metrics from calculate_confidence_score.

Returns:
    A formatted string report showing all confidence metrics with percentages.

Notes:
    1. Constructs a multi-line string with each metric on a separate line.
    2. Formats all values to one decimal place for readability.
    3. Returns the completed report string.

---

## `ConfidenceScorer` class

Calculates confidence scores for facts and answers based on multiple factors.

---
## method: `ConfidenceScorer.__init__(self: UnknownType) -> None`

Initialize the confidence scorer with default weights and source categories.

Notes:
    1. Initializes the source credibility weights for different source types.
    2. Sets up keyword-based categorization for source names.
    3. Logs initialization start and completion.

---
## method: `ConfidenceScorer.calculate_source_credibility(self: UnknownType, source_name: str) -> float`

Rate source reliability based on source type.

Args:
    source_name: The name or identifier of the source (str)

Returns:
    A float between 0.0 and 1.0 representing the credibility score of the source.

Notes:
    1. Converts the source name to lowercase for case-insensitive matching.
    2. Uses keyword matching to categorize the source into one of the predefined categories.
    3. Retrieves the credibility weight for the matched category or defaults to "unknown".
    4. Returns the credibility score.

---
## method: `ConfidenceScorer.calculate_temporal_consistency(self: UnknownType, facts: list[Fact]) -> float`

Handle time-sensitive information consistency.

Args:
    facts: List of Fact objects to evaluate for temporal consistency.

Returns:
    A float between 0.0 and 1.0 representing the temporal consistency score.

Notes:
    1. Initializes the consistency score to a default value of 0.9.
    2. In a real implementation, this would check timestamps and temporal relationships between facts.
    3. Returns the default consistency score for now.

---
## method: `ConfidenceScorer.calculate_consistency_score(self: UnknownType, facts: list[Fact]) -> float`

Evaluate consistency across multiple sources.

Args:
    facts: List of Fact objects to evaluate for consistency between sources.

Returns:
    A float between 0.0 and 1.0 representing the cross-source consistency score.

Notes:
    1. If fewer than two facts are present, returns 1.0 (perfect consistency by default).
    2. In a real implementation, this would compare the content of facts for similarity.
    3. Returns a default score of 0.85 for now.

---
## method: `ConfidenceScorer.calculate_completeness_score(self: UnknownType, facts: list[Fact], query: str) -> float`

Assess answer coverage and completeness.

Args:
    facts: List of Fact objects related to the query.
    query: The original user query (str) used to assess completeness.

Returns:
    A float between 0.0 and 1.0 representing the completeness score.

Notes:
    1. Uses the number of facts as a proxy for completeness.
    2. Assumes that up to 5 facts represent full completeness.
    3. Returns the ratio of facts to 5, capped at 1.0.

---
## method: `ConfidenceScorer.calculate_confidence_score(self: UnknownType, memory: WorkingMemory, query: str) -> dict[str, Any]`

Calculate overall confidence score for the current state.

Args:
    memory: The current working memory state containing facts and sources.
    query: The original query (str) to assess confidence against.

Returns:
    A dictionary containing:
        - overall_confidence: float (0-100) representing the final confidence score.
        - source_credibility: float (0-100) representing the average source credibility.
        - temporal_consistency: float (0-100) representing temporal consistency.
        - cross_source_consistency: float (0-100) representing consistency between sources.
        - completeness: float (0-100) representing completeness of answer.

Notes:
    1. Extracts all facts from the working memory.
    2. If no facts exist, returns a result with all scores set to 0.0.
    3. For each fact, retrieves its source and calculates credibility.
    4. Computes average source credibility from all facts.
    5. Calculates temporal consistency, cross-source consistency, and completeness.
    6. Combines scores using weighted averaging (source: 40%, temporal: 20%, cross-source: 20%, completeness: 20%).
    7. Scales the overall confidence to 0-100 scale and returns all metrics.

---
## method: `ConfidenceScorer.generate_confidence_report(self: UnknownType, confidence_data: dict[str, Any]) -> str`

Generate a detailed explanation of confidence scores.

Args:
    confidence_data: Dictionary containing confidence metrics from calculate_confidence_score.

Returns:
    A formatted string report showing all confidence metrics with percentages.

Notes:
    1. Constructs a multi-line string with each metric on a separate line.
    2. Formats all values to one decimal place for readability.
    3. Returns the completed report string.

---

===

===
# File: `client.py`

## function: `get_llm_client(name: str) -> LLMClient`

Get configured LLM client by name.

Args:
    name: The name of the LLM client to retrieve from configuration.

Returns:
    An LLMClient instance configured with settings from the specified endpoint.

Notes:
    1. Log the start of the retrieval process with the provided name.
    2. Check if a client with the given name already exists in the global _llm_clients dictionary.
    3. If it exists, return the existing client.
    4. If it does not exist, retrieve the endpoint configuration using the name.
    5. Create a new LLMClient instance with the retrieved configuration.
    6. Store the new client in the _llm_clients dictionary under the given name.
    7. Return the newly created (or existing) client.

---

## function: `__init__(self: UnknownType, endpoint_config: dict) -> None`

Initialize LLM client with endpoint configuration.

Args:
    endpoint_config: Dictionary containing configuration for the LLM endpoint,
        including model_id, api_base, and any other relevant settings.

Notes:
    1. Log the start of initialization with the provided endpoint configuration.
    2. Extract the model_id and api_base from the endpoint_config.
    3. Initialize the underlying LLM (ChatOpenAI) with the extracted model_id, API key,
       base URL, and default temperature of 0.7.
    4. Log the successful completion of initialization.

---

## function: `call(self: UnknownType, prompt: str, parser: PydanticOutputParser | None) -> dict[str, Any]`

Call LLM with prompt and optional parser.

Args:
    prompt: The input text prompt to send to the LLM.
    parser: Optional PydanticOutputParser to parse the LLM's response into a structured format.

Returns:
    A dictionary containing:
        - "content": The raw content returned by the LLM (string).
        - "parsed": The parsed output (if a parser was provided), in dictionary form or as-is.
        - "metadata": A dictionary with "model" and "api_base" identifying the LLM used.

Notes:
    1. Log the start of the call with the first 50 characters of the prompt.
    2. If a parser is provided, append the parser's format instructions to the prompt.
    3. Invoke the LLM with the (possibly modified) prompt.
    4. If a parser is used, parse the response content and store the parsed result.
    5. Construct and return the result dictionary with content, parsed output (if any),
       and metadata about the model and API base.
    6. If an exception occurs during the call, log it and re-raise the exception.

---

## `LLMClient` class

LLM client for making calls to various LLM endpoints.

---
## method: `LLMClient.__init__(self: UnknownType, endpoint_config: dict) -> None`

Initialize LLM client with endpoint configuration.

Args:
    endpoint_config: Dictionary containing configuration for the LLM endpoint,
        including model_id, api_base, and any other relevant settings.

Notes:
    1. Log the start of initialization with the provided endpoint configuration.
    2. Extract the model_id and api_base from the endpoint_config.
    3. Initialize the underlying LLM (ChatOpenAI) with the extracted model_id, API key,
       base URL, and default temperature of 0.7.
    4. Log the successful completion of initialization.

---
## method: `LLMClient.call(self: UnknownType, prompt: str, parser: PydanticOutputParser | None) -> dict[str, Any]`

Call LLM with prompt and optional parser.

Args:
    prompt: The input text prompt to send to the LLM.
    parser: Optional PydanticOutputParser to parse the LLM's response into a structured format.

Returns:
    A dictionary containing:
        - "content": The raw content returned by the LLM (string).
        - "parsed": The parsed output (if a parser was provided), in dictionary form or as-is.
        - "metadata": A dictionary with "model" and "api_base" identifying the LLM used.

Notes:
    1. Log the start of the call with the first 50 characters of the prompt.
    2. If a parser is provided, append the parser's format instructions to the prompt.
    3. Invoke the LLM with the (possibly modified) prompt.
    4. If a parser is used, parse the response content and store the parsed result.
    5. Construct and return the result dictionary with content, parsed output (if any),
       and metadata about the model and API base.
    6. If an exception occurs during the call, log it and re-raise the exception.

---

===

===
# File: `base.py`

## function: `__init__(self: UnknownType) -> None`

Initialize ToolResponse with timestamp if not provided.

Args:
    **data: Arbitrary keyword arguments to initialize the ToolResponse.

Returns:
    None

Notes:
    1. If the 'timestamp' key is not present in data or is None, set it to the current datetime.
    2. Call the parent class initializer with the updated data.

---

## function: `execute(self: UnknownType, query: str) -> ToolResponse`

Execute tool with standardized input/output.

Args:
    query: The query string to process.

Returns:
    ToolResponse: Standardized response from the tool containing tool name, response data, metadata, raw response, content, and timestamp.

Notes:
    1. The function must process the input query using the tool's internal logic.
    2. It must return a ToolResponse object with the results of the operation.
    3. The response must include the tool's name, processed data, metadata, raw response, content, and a timestamp.

---

## function: `validate_response(self: UnknownType, response: dict) -> bool`

Check if response contains valid data.

Args:
    response: The raw response dictionary to validate.

Returns:
    bool: True if the response contains valid data, False otherwise.

Notes:
    1. Analyze the provided response dictionary for structure and meaningful content.
    2. Return True if the response is valid (e.g., has required keys, non-empty data, etc.).
    3. Return False if the response is invalid (e.g., missing keys, empty, malformed, etc.).

---

## `ToolResponse` class

Standardized tool response model.

---
## method: `ToolResponse.__init__(self: UnknownType) -> None`

Initialize ToolResponse with timestamp if not provided.

Args:
    **data: Arbitrary keyword arguments to initialize the ToolResponse.

Returns:
    None

Notes:
    1. If the 'timestamp' key is not present in data or is None, set it to the current datetime.
    2. Call the parent class initializer with the updated data.

---
## `ToolInterface` class

Abstract base class for all tools.

---
## method: `ToolInterface.execute(self: UnknownType, query: str) -> ToolResponse`

Execute tool with standardized input/output.

Args:
    query: The query string to process.

Returns:
    ToolResponse: Standardized response from the tool containing tool name, response data, metadata, raw response, content, and timestamp.

Notes:
    1. The function must process the input query using the tool's internal logic.
    2. It must return a ToolResponse object with the results of the operation.
    3. The response must include the tool's name, processed data, metadata, raw response, content, and a timestamp.

---
## method: `ToolInterface.validate_response(self: UnknownType, response: dict) -> bool`

Check if response contains valid data.

Args:
    response: The raw response dictionary to validate.

Returns:
    bool: True if the response contains valid data, False otherwise.

Notes:
    1. Analyze the provided response dictionary for structure and meaningful content.
    2. Return True if the response is valid (e.g., has required keys, non-empty data, etc.).
    3. Return False if the response is invalid (e.g., missing keys, empty, malformed, etc.).

---

===

===
# File: `rate_limiter.py`

## function: `__init__(self: UnknownType, config: RateLimitConfig) -> None`

Initialize the rate limiter with configuration.

Args:
    config: RateLimitConfig with rate limiting parameters

Notes:
    1. Initialize internal state variables: tokens, last_refill, and usage_stats.
    2. Set the provided configuration as an instance attribute.
    3. Log the initialization start and completion.

---

## function: `_refill_tokens(self: UnknownType, endpoint: str) -> None`

Refill tokens based on time elapsed since last refill.

Args:
    endpoint: The endpoint identifier

Notes:
    1. Get the current time.
    2. If this is the first time using this endpoint, initialize its refill time and tokens.
    3. Calculate the time elapsed since the last refill.
    4. Compute the number of new tokens to add based on the elapsed time and requests_per_second.
    5. Add new tokens to the bucket, but do not exceed bucket_capacity.
    6. Update the last_refill time to the current time.

---

## function: `_consume_token(self: UnknownType, endpoint: str) -> bool`

Consume a token if available.

Args:
    endpoint: The endpoint identifier

Returns:
    bool: True if token was consumed, False if rate limited

Notes:
    1. Initialize usage statistics for the endpoint if not already present.
    2. Initialize token and refill state for the endpoint if not already present.
    3. Refill tokens based on elapsed time since the last refill.
    4. If the bucket has at least one token, consume it and update request count.
    5. Otherwise, increment the throttled request count and return False.

---

## function: `queue_request(self: UnknownType, endpoint: str, func: Callable) -> Any`

Queue a request and execute when rate limit allows.

Args:
    endpoint: The endpoint identifier
    func: The function to execute
    *args: Positional arguments for the function
    **kwargs: Keyword arguments for the function

Returns:
    Any: The result of the function execution

Notes:
    1. Wait in a loop until a token can be consumed from the rate limiter.
    2. When a token is available, calculate the sleep time based on the rate limit.
    3. Sleep for the calculated duration to respect the rate limit.
    4. Execute the function with the provided arguments.
    5. Return the result of the function.

---

## function: `get_usage_stats(self: UnknownType, endpoint: str | None) -> dict[str, Any]`

Get usage statistics for endpoints.

Args:
    endpoint: Specific endpoint to get stats for, or None for all

Returns:
    Dict[str, Any]: Usage statistics

Notes:
    1. If a specific endpoint is requested, return its stats or default stats if not found.
    2. Otherwise, return a copy of all usage statistics.

---

## function: `reset_usage_stats(self: UnknownType) -> None`

Reset all usage statistics.

Notes:
    1. Iterate through all usage statistics and reset request and throttled counts to zero.

---

## `RateLimiter` class

Implements rate limiting using token bucket algorithm with adaptive throttling.

---
## method: `RateLimiter.__init__(self: UnknownType, config: RateLimitConfig) -> None`

Initialize the rate limiter with configuration.

Args:
    config: RateLimitConfig with rate limiting parameters

Notes:
    1. Initialize internal state variables: tokens, last_refill, and usage_stats.
    2. Set the provided configuration as an instance attribute.
    3. Log the initialization start and completion.

---
## method: `RateLimiter._refill_tokens(self: UnknownType, endpoint: str) -> None`

Refill tokens based on time elapsed since last refill.

Args:
    endpoint: The endpoint identifier

Notes:
    1. Get the current time.
    2. If this is the first time using this endpoint, initialize its refill time and tokens.
    3. Calculate the time elapsed since the last refill.
    4. Compute the number of new tokens to add based on the elapsed time and requests_per_second.
    5. Add new tokens to the bucket, but do not exceed bucket_capacity.
    6. Update the last_refill time to the current time.

---
## method: `RateLimiter._consume_token(self: UnknownType, endpoint: str) -> bool`

Consume a token if available.

Args:
    endpoint: The endpoint identifier

Returns:
    bool: True if token was consumed, False if rate limited

Notes:
    1. Initialize usage statistics for the endpoint if not already present.
    2. Initialize token and refill state for the endpoint if not already present.
    3. Refill tokens based on elapsed time since the last refill.
    4. If the bucket has at least one token, consume it and update request count.
    5. Otherwise, increment the throttled request count and return False.

---
## method: `RateLimiter.queue_request(self: UnknownType, endpoint: str, func: Callable) -> Any`

Queue a request and execute when rate limit allows.

Args:
    endpoint: The endpoint identifier
    func: The function to execute
    *args: Positional arguments for the function
    **kwargs: Keyword arguments for the function

Returns:
    Any: The result of the function execution

Notes:
    1. Wait in a loop until a token can be consumed from the rate limiter.
    2. When a token is available, calculate the sleep time based on the rate limit.
    3. Sleep for the calculated duration to respect the rate limit.
    4. Execute the function with the provided arguments.
    5. Return the result of the function.

---
## method: `RateLimiter.get_usage_stats(self: UnknownType, endpoint: str | None) -> dict[str, Any]`

Get usage statistics for endpoints.

Args:
    endpoint: Specific endpoint to get stats for, or None for all

Returns:
    Dict[str, Any]: Usage statistics

Notes:
    1. If a specific endpoint is requested, return its stats or default stats if not found.
    2. Otherwise, return a copy of all usage statistics.

---
## method: `RateLimiter.reset_usage_stats(self: UnknownType) -> None`

Reset all usage statistics.

Notes:
    1. Iterate through all usage statistics and reset request and throttled counts to zero.

---

===

===
# File: `wikipedia.py`

## function: `__init__(self: UnknownType, cache_manager: CacheManager, rate_limiter: RateLimiter) -> None`

Initialize Wikipedia tool.

Args:
    cache_manager: Optional cache manager for caching results
    rate_limiter: Optional rate limiter for API compliance

Returns:
    None

Notes:
    1. Initializes the Wikipedia retriever using the LangChain WikipediaRetriever.
    2. Sets the cache manager to the provided instance or defaults to a new CacheManager if not provided.
    3. Sets the rate limiter to the provided instance or defaults to a new RateLimiter with 5 requests per second and a bucket capacity of 10 if not provided.

---

## function: `_create_default_rate_limiter(self: UnknownType) -> RateLimiter`

Create a default rate limiter for Wikipedia searches.

Args:
    None

Returns:
    RateLimiter: Configured rate limiter instance with 5 requests per second and bucket capacity of 10

Notes:
    1. Creates a RateLimitConfig with 5 requests per second and a bucket capacity of 10.
    2. Instantiates a RateLimiter with the created configuration.
    3. Returns the configured RateLimiter instance.

---

## function: `execute(self: UnknownType, query: str) -> ToolResponse`

Execute Wikipedia search with rate limiting.

Args:
    query: The query string to search for on Wikipedia

Returns:
    ToolResponse: Standardized response containing Wikipedia search results.
        - If successful: content contains formatted results, metadata includes count and sources, raw_response contains documents and query.
        - If no results found: content is "No results found on Wikipedia.", metadata includes results_count=0.
        - If error: content contains error message, metadata includes error=True and results_count=0, raw_response contains error string.

Notes:
    1. Constructs a cache key using the normalized query from the cache manager.
    2. Checks if a cached result exists for the cache key.
    3. If cached result exists, returns it immediately.
    4. If no cache hit, performs the Wikipedia search using the retriever.
    5. Processes search results into a formatted content string in Markdown with section headers for each result.
    6. Constructs metadata with results count and source titles.
    7. Creates a raw_response dictionary containing the original documents and query.
    8. Creates a ToolResponse with content, metadata, and raw_response.
    9. Caches the response using the cache manager.
    10. Returns the final response.
    11. If an exception occurs during search, returns an error ToolResponse with the exception message.

---

## function: `validate_response(self: UnknownType, response: dict) -> bool`

Validate Wikipedia response.

Args:
    response: The raw response dictionary to validate

Returns:
    bool: True if response is valid (contains documents with page_content or content as string), False otherwise

Notes:
    1. Checks if response is a dictionary; returns False if not.
    2. Checks if response contains an "error" key; returns False if present.
    3. Checks if response contains "documents" key and if it's a list.
    4. Verifies that each document in the list is a dictionary and contains "page_content".
    5. If documents are valid, returns True.
    6. If no documents, checks if response contains "content" and if it's a string.
    7. If content is valid, returns True.
    8. Otherwise, returns False.

---

## function: `_perform_search() -> ToolResponse`



---

## `WikipediaTool` class

Wikipedia search tool implementation.

---
## method: `WikipediaTool.__init__(self: UnknownType, cache_manager: CacheManager, rate_limiter: RateLimiter) -> None`

Initialize Wikipedia tool.

Args:
    cache_manager: Optional cache manager for caching results
    rate_limiter: Optional rate limiter for API compliance

Returns:
    None

Notes:
    1. Initializes the Wikipedia retriever using the LangChain WikipediaRetriever.
    2. Sets the cache manager to the provided instance or defaults to a new CacheManager if not provided.
    3. Sets the rate limiter to the provided instance or defaults to a new RateLimiter with 5 requests per second and a bucket capacity of 10 if not provided.

---
## method: `WikipediaTool._create_default_rate_limiter(self: UnknownType) -> RateLimiter`

Create a default rate limiter for Wikipedia searches.

Args:
    None

Returns:
    RateLimiter: Configured rate limiter instance with 5 requests per second and bucket capacity of 10

Notes:
    1. Creates a RateLimitConfig with 5 requests per second and a bucket capacity of 10.
    2. Instantiates a RateLimiter with the created configuration.
    3. Returns the configured RateLimiter instance.

---
## method: `WikipediaTool.execute(self: UnknownType, query: str) -> ToolResponse`

Execute Wikipedia search with rate limiting.

Args:
    query: The query string to search for on Wikipedia

Returns:
    ToolResponse: Standardized response containing Wikipedia search results.
        - If successful: content contains formatted results, metadata includes count and sources, raw_response contains documents and query.
        - If no results found: content is "No results found on Wikipedia.", metadata includes results_count=0.
        - If error: content contains error message, metadata includes error=True and results_count=0, raw_response contains error string.

Notes:
    1. Constructs a cache key using the normalized query from the cache manager.
    2. Checks if a cached result exists for the cache key.
    3. If cached result exists, returns it immediately.
    4. If no cache hit, performs the Wikipedia search using the retriever.
    5. Processes search results into a formatted content string in Markdown with section headers for each result.
    6. Constructs metadata with results count and source titles.
    7. Creates a raw_response dictionary containing the original documents and query.
    8. Creates a ToolResponse with content, metadata, and raw_response.
    9. Caches the response using the cache manager.
    10. Returns the final response.
    11. If an exception occurs during search, returns an error ToolResponse with the exception message.

---
## method: `WikipediaTool.validate_response(self: UnknownType, response: dict) -> bool`

Validate Wikipedia response.

Args:
    response: The raw response dictionary to validate

Returns:
    bool: True if response is valid (contains documents with page_content or content as string), False otherwise

Notes:
    1. Checks if response is a dictionary; returns False if not.
    2. Checks if response contains an "error" key; returns False if present.
    3. Checks if response contains "documents" key and if it's a list.
    4. Verifies that each document in the list is a dictionary and contains "page_content".
    5. If documents are valid, returns True.
    6. If no documents, checks if response contains "content" and if it's a string.
    7. If content is valid, returns True.
    8. Otherwise, returns False.

---
## method: `WikipediaTool._perform_search() -> ToolResponse`



---

===

===
# File: `cache.py`

## function: `__init__(self: UnknownType, cache_dir: str | None, default_ttl: int) -> UnknownType`

Initialize the cache manager.

Args:
    cache_dir: Directory for persistent cache storage. If not provided, defaults to "msa/cache".
    default_ttl: Default time-to-live in seconds for cached entries. If not provided, defaults to 3600 seconds (1 hour).

Returns:
    None

Notes:
    1. Initializes the cache manager with the provided cache directory or defaults to "msa/cache".
    2. Creates the cache directory if it does not exist.
    3. Attempts to load application configuration from msa.config.load_app_config().
    4. If configuration is loaded, updates default_ttl with the value from the config under "cache.default_ttl".
    5. Logs initialization start and completion messages.

---

## function: `_get_cache_file_path(self: UnknownType, key: str) -> Path`

Get the file path for a cache entry.

Args:
    key: Cache key used to generate the file path.

Returns:
    Path object pointing to the file where the cache entry is stored.

Notes:
    1. Takes the provided cache key and appends ".json" to form the file name.
    2. Constructs a Path object using the cache directory and the generated file name.
    3. Returns the constructed Path.

---

## function: `_is_expired(self: UnknownType, timestamp: float, ttl: int | None) -> bool`

Check if a cache entry is expired.

Args:
    timestamp: The timestamp when the cache entry was created.
    ttl: Time-to-live in seconds for this entry. If None, uses the default_ttl.

Returns:
    True if the entry has expired, False otherwise.

Notes:
    1. If ttl is None, uses the instance's default_ttl.
    2. Calculates the difference between the current time and the timestamp.
    3. Returns True if the difference exceeds the ttl, otherwise False.

---

## function: `normalize_query(self: UnknownType, query: str) -> str`

Normalize a query string for consistent cache keys.

Args:
    query: The query string to normalize.

Returns:
    A normalized string suitable for use as a cache key, created by converting to lowercase, stripping whitespace, and hashing.

Notes:
    1. Converts the input query to lowercase.
    2. Strips leading and trailing whitespace.
    3. Removes extra internal whitespace by splitting and rejoining with single spaces.
    4. Creates a hash of the normalized query using MD5.
    5. Returns the hexadecimal digest of the hash.

---

## function: `get(self: UnknownType, key: str, ttl: int | None) -> dict[str, Any] | None`

Retrieve an item from the cache.

Args:
    key: Cache key used to locate the entry.
    ttl: Optional override for the time-to-live of this entry. If None, uses the default_ttl.

Returns:
    The cached data (dict) if the entry exists and is not expired; otherwise, returns None.

Notes:
    1. Constructs the file path for the cache entry using _get_cache_file_path.
    2. If the file does not exist, returns None.
    3. Tries to read the file and load the JSON content.
    4. Checks if the entry has expired using _is_expired.
    5. If expired, the file is deleted and None is returned.
    6. If not expired, the content from the cache entry is returned.

---

## function: `set(self: UnknownType, key: str, value: dict[str, Any], ttl: int | None) -> None`

Store an item in the cache.

Args:
    key: Cache key under which to store the data.
    value: Data to be cached, must be a dictionary.
    ttl: Time-to-live in seconds for this entry. If None, uses the default_ttl.

Returns:
    None

Notes:
    1. If ttl is None, uses the instance's default_ttl.
    2. Constructs the file path using _get_cache_file_path.
    3. Creates a cache data dictionary containing the key, value, timestamp, and ttl.
    4. Writes the cache data to the file in JSON format.
    5. If an error occurs during writing, logs the exception.

---

## function: `invalidate(self: UnknownType, key: str) -> bool`

Remove an item from the cache.

Args:
    key: Cache key of the entry to remove.

Returns:
    True if the entry was found and removed; otherwise, False.

Notes:
    1. Constructs the file path using _get_cache_file_path.
    2. Checks if the file exists.
    3. If the file exists, attempts to delete it.
    4. If deletion succeeds, returns True.
    5. If the file does not exist or deletion fails, returns False.

---

## function: `warm_cache(self: UnknownType, key: str, value: dict[str, Any], ttl: int | None) -> None`

Pre-populate the cache with frequently accessed data.

Args:
    key: Cache key under which to store the data.
    value: Data to be cached, must be a dictionary.
    ttl: Time-to-live in seconds for this entry. If None, uses the default_ttl.

Returns:
    None

Notes:
    1. Uses the set method to store the provided key-value pair in the cache.
    2. Logs the successful addition of the warm cache entry.

---

## `CacheManager` class

Manages caching operations for tool responses.

---
## method: `CacheManager.__init__(self: UnknownType, cache_dir: str | None, default_ttl: int) -> UnknownType`

Initialize the cache manager.

Args:
    cache_dir: Directory for persistent cache storage. If not provided, defaults to "msa/cache".
    default_ttl: Default time-to-live in seconds for cached entries. If not provided, defaults to 3600 seconds (1 hour).

Returns:
    None

Notes:
    1. Initializes the cache manager with the provided cache directory or defaults to "msa/cache".
    2. Creates the cache directory if it does not exist.
    3. Attempts to load application configuration from msa.config.load_app_config().
    4. If configuration is loaded, updates default_ttl with the value from the config under "cache.default_ttl".
    5. Logs initialization start and completion messages.

---
## method: `CacheManager._get_cache_file_path(self: UnknownType, key: str) -> Path`

Get the file path for a cache entry.

Args:
    key: Cache key used to generate the file path.

Returns:
    Path object pointing to the file where the cache entry is stored.

Notes:
    1. Takes the provided cache key and appends ".json" to form the file name.
    2. Constructs a Path object using the cache directory and the generated file name.
    3. Returns the constructed Path.

---
## method: `CacheManager._is_expired(self: UnknownType, timestamp: float, ttl: int | None) -> bool`

Check if a cache entry is expired.

Args:
    timestamp: The timestamp when the cache entry was created.
    ttl: Time-to-live in seconds for this entry. If None, uses the default_ttl.

Returns:
    True if the entry has expired, False otherwise.

Notes:
    1. If ttl is None, uses the instance's default_ttl.
    2. Calculates the difference between the current time and the timestamp.
    3. Returns True if the difference exceeds the ttl, otherwise False.

---
## method: `CacheManager.normalize_query(self: UnknownType, query: str) -> str`

Normalize a query string for consistent cache keys.

Args:
    query: The query string to normalize.

Returns:
    A normalized string suitable for use as a cache key, created by converting to lowercase, stripping whitespace, and hashing.

Notes:
    1. Converts the input query to lowercase.
    2. Strips leading and trailing whitespace.
    3. Removes extra internal whitespace by splitting and rejoining with single spaces.
    4. Creates a hash of the normalized query using MD5.
    5. Returns the hexadecimal digest of the hash.

---
## method: `CacheManager.get(self: UnknownType, key: str, ttl: int | None) -> dict[str, Any] | None`

Retrieve an item from the cache.

Args:
    key: Cache key used to locate the entry.
    ttl: Optional override for the time-to-live of this entry. If None, uses the default_ttl.

Returns:
    The cached data (dict) if the entry exists and is not expired; otherwise, returns None.

Notes:
    1. Constructs the file path for the cache entry using _get_cache_file_path.
    2. If the file does not exist, returns None.
    3. Tries to read the file and load the JSON content.
    4. Checks if the entry has expired using _is_expired.
    5. If expired, the file is deleted and None is returned.
    6. If not expired, the content from the cache entry is returned.

---
## method: `CacheManager.set(self: UnknownType, key: str, value: dict[str, Any], ttl: int | None) -> None`

Store an item in the cache.

Args:
    key: Cache key under which to store the data.
    value: Data to be cached, must be a dictionary.
    ttl: Time-to-live in seconds for this entry. If None, uses the default_ttl.

Returns:
    None

Notes:
    1. If ttl is None, uses the instance's default_ttl.
    2. Constructs the file path using _get_cache_file_path.
    3. Creates a cache data dictionary containing the key, value, timestamp, and ttl.
    4. Writes the cache data to the file in JSON format.
    5. If an error occurs during writing, logs the exception.

---
## method: `CacheManager.invalidate(self: UnknownType, key: str) -> bool`

Remove an item from the cache.

Args:
    key: Cache key of the entry to remove.

Returns:
    True if the entry was found and removed; otherwise, False.

Notes:
    1. Constructs the file path using _get_cache_file_path.
    2. Checks if the file exists.
    3. If the file exists, attempts to delete it.
    4. If deletion succeeds, returns True.
    5. If the file does not exist or deletion fails, returns False.

---
## method: `CacheManager.warm_cache(self: UnknownType, key: str, value: dict[str, Any], ttl: int | None) -> None`

Pre-populate the cache with frequently accessed data.

Args:
    key: Cache key under which to store the data.
    value: Data to be cached, must be a dictionary.
    ttl: Time-to-live in seconds for this entry. If None, uses the default_ttl.

Returns:
    None

Notes:
    1. Uses the set method to store the provided key-value pair in the cache.
    2. Logs the successful addition of the warm cache entry.

---

===

===
# File: `web_search.py`

## function: `__init__(self: UnknownType, cache_manager: CacheManager, rate_limiter: RateLimiter) -> None`

Initialize web search tool.

Args:
    cache_manager: Optional cache manager for caching results
    rate_limiter: Optional rate limiter for API compliance

---

## function: `_create_default_rate_limiter(self: UnknownType) -> RateLimiter`

Create a default rate limiter for web searches.

Returns:
    RateLimiter: Configured rate limiter instance

Notes:
    1. Creates a RateLimitConfig with 10 requests per second and a bucket capacity of 20.
    2. Instantiates a RateLimiter using the created config.
    3. Returns the configured RateLimiter instance.

---

## function: `execute(self: UnknownType, query: str) -> ToolResponse`

Execute web search with rate limiting.

Args:
    query: The query string to search for on the web

Returns:
    ToolResponse: Standardized response containing web search results.
        - If successful: content contains formatted results, metadata includes count and sources.
        - If API key missing: content contains error message, metadata indicates error.
        - If an exception occurs: content contains error message, metadata indicates error.

Notes:
    1. Checks for the presence of the SERPAPI_API_KEY environment variable.
    2. If API key is missing, returns an error ToolResponse.
    3. Uses the cache manager to check if a result exists for the normalized query.
    4. If cached result exists, returns it directly.
    5. Otherwise, performs the web search using the SERPAPI client.
    6. Processes the search results into a formatted content string.
    7. Limits results to the top 5 and formats each result with title, link, and snippet.
    8. Constructs a ToolResponse with content, metadata (results count, sources), and raw response.
    9. Caches the response using the cache manager.
    10. Returns the constructed ToolResponse.

---

## function: `validate_response(self: UnknownType, response: dict) -> bool`

Validate web search response.

Args:
    response: The raw response dictionary to validate

Returns:
    bool: True if response is valid, False otherwise

Notes:
    1. Checks if response is a dictionary.
    2. If response contains an "error" key, returns False.
    3. If response contains "organic_results" key, checks if it's a list; returns True if valid.
    4. If response contains "content" key and it's a string, returns True.
    5. Otherwise, returns False.

---

## function: `_perform_search() -> ToolResponse`



---

## `WebSearchTool` class

Web search tool implementation.

---
## method: `WebSearchTool.__init__(self: UnknownType, cache_manager: CacheManager, rate_limiter: RateLimiter) -> None`

Initialize web search tool.

Args:
    cache_manager: Optional cache manager for caching results
    rate_limiter: Optional rate limiter for API compliance

---
## method: `WebSearchTool._create_default_rate_limiter(self: UnknownType) -> RateLimiter`

Create a default rate limiter for web searches.

Returns:
    RateLimiter: Configured rate limiter instance

Notes:
    1. Creates a RateLimitConfig with 10 requests per second and a bucket capacity of 20.
    2. Instantiates a RateLimiter using the created config.
    3. Returns the configured RateLimiter instance.

---
## method: `WebSearchTool.execute(self: UnknownType, query: str) -> ToolResponse`

Execute web search with rate limiting.

Args:
    query: The query string to search for on the web

Returns:
    ToolResponse: Standardized response containing web search results.
        - If successful: content contains formatted results, metadata includes count and sources.
        - If API key missing: content contains error message, metadata indicates error.
        - If an exception occurs: content contains error message, metadata indicates error.

Notes:
    1. Checks for the presence of the SERPAPI_API_KEY environment variable.
    2. If API key is missing, returns an error ToolResponse.
    3. Uses the cache manager to check if a result exists for the normalized query.
    4. If cached result exists, returns it directly.
    5. Otherwise, performs the web search using the SERPAPI client.
    6. Processes the search results into a formatted content string.
    7. Limits results to the top 5 and formats each result with title, link, and snippet.
    8. Constructs a ToolResponse with content, metadata (results count, sources), and raw response.
    9. Caches the response using the cache manager.
    10. Returns the constructed ToolResponse.

---
## method: `WebSearchTool.validate_response(self: UnknownType, response: dict) -> bool`

Validate web search response.

Args:
    response: The raw response dictionary to validate

Returns:
    bool: True if response is valid, False otherwise

Notes:
    1. Checks if response is a dictionary.
    2. If response contains an "error" key, returns False.
    3. If response contains "organic_results" key, checks if it's a list; returns True if valid.
    4. If response contains "content" key and it's a string, returns True.
    5. Otherwise, returns False.

---
## method: `WebSearchTool._perform_search() -> ToolResponse`



---

===

===
# File: `circuit_breaker.py`

## function: `__init__(self: UnknownType, name: str, config: CircuitBreakerConfig) -> None`

Initialize the circuit breaker.

Args:
    name: The name of the circuit breaker for logging and identification.
    config: Configuration for circuit breaker behavior, including failure threshold,
            timeout duration, and number of half-open attempts.

Notes:
    1. Initializes the circuit breaker with the given name and configuration.
    2. Sets the initial state to CLOSED.
    3. Initializes failure count to zero and last failure time to None.
    4. Initializes half-open success count to zero.

---

## function: `execute_with_circuit_breaker(self: UnknownType, func: Callable) -> Any`

Execute a function with circuit breaker protection.

Args:
    func: The function to execute. Must be callable and can accept variable arguments.
    *args: Positional arguments passed to the function.
    **kwargs: Keyword arguments passed to the function.

Returns:
    The result of the function execution if successful.

Raises:
    Exception: If the circuit breaker is in OPEN state and reset conditions are not met,
               or if the function raises an exception during execution.

Notes:
    1. Determines the function name for logging purposes.
    2. Checks if the circuit breaker is in OPEN state.
    3. If OPEN, attempts to transition to HALF_OPEN if sufficient time has passed.
    4. If unable to transition (too soon), raises an exception.
    5. Executes the function within a try block.
    6. On success, calls _on_success to handle the success state.
    7. On failure, calls _on_failure to handle the failure state and re-raises the exception.

---

## function: `_should_attempt_reset(self: UnknownType) -> bool`

Check if enough time has passed to attempt reset.

Returns:
    True if the timeout has expired since the last failure, False otherwise.

Notes:
    1. Returns False if there is no recorded last failure time.
    2. Calculates the elapsed time since the last failure.
    3. Compares elapsed time to the configured timeout.
    4. Returns True if elapsed time exceeds timeout.

---

## function: `_transition_to_half_open(self: UnknownType) -> None`

Transition the circuit breaker to half-open state.

Notes:
    1. Sets the state to HALF_OPEN.
    2. Resets the success counter for half-open attempts to zero.

---

## function: `_on_success(self: UnknownType) -> None`

Handle successful execution.

Notes:
    1. Checks if the current state is HALF_OPEN.
    2. If HALF_OPEN, increments the success counter.
    3. If the success counter reaches the half-open threshold, resets the circuit.
    4. Otherwise, resets the circuit regardless of state.

---

## function: `_on_failure(self: UnknownType) -> None`

Handle failed execution.

Notes:
    1. Increments the failure count.
    2. Records the current time as the last failure time.
    3. If in HALF_OPEN state, trips the circuit.
    4. If the failure count reaches the threshold, trips the circuit.

---

## function: `_trip(self: UnknownType) -> None`

Trip the circuit breaker to open state.

Notes:
    1. Sets the state to OPEN.
    2. Logs a warning message indicating the circuit has been tripped.

---

## function: `_reset(self: UnknownType) -> None`

Reset the circuit breaker to closed state.

Notes:
    1. Sets the state to CLOSED.
    2. Resets the failure count to zero.
    3. Clears the last failure time.
    4. Resets the half-open success count to zero.
    5. Logs an informational message indicating the reset.

---

## function: `get_state_info(self: UnknownType) -> dict[str, Any]`

Get current state information for monitoring.

Returns:
    A dictionary containing the circuit breaker's name, current state, failure count,
    last failure time, and half-open success count.

Notes:
    1. Constructs a dictionary with the current state information.
    2. Includes the name, state, failure count, last failure time, and half-open success count.
    3. Returns the constructed dictionary.

---

## `CircuitBreaker` class

Implements the circuit breaker pattern for tool reliability.

---
## method: `CircuitBreaker.__init__(self: UnknownType, name: str, config: CircuitBreakerConfig) -> None`

Initialize the circuit breaker.

Args:
    name: The name of the circuit breaker for logging and identification.
    config: Configuration for circuit breaker behavior, including failure threshold,
            timeout duration, and number of half-open attempts.

Notes:
    1. Initializes the circuit breaker with the given name and configuration.
    2. Sets the initial state to CLOSED.
    3. Initializes failure count to zero and last failure time to None.
    4. Initializes half-open success count to zero.

---
## method: `CircuitBreaker.execute_with_circuit_breaker(self: UnknownType, func: Callable) -> Any`

Execute a function with circuit breaker protection.

Args:
    func: The function to execute. Must be callable and can accept variable arguments.
    *args: Positional arguments passed to the function.
    **kwargs: Keyword arguments passed to the function.

Returns:
    The result of the function execution if successful.

Raises:
    Exception: If the circuit breaker is in OPEN state and reset conditions are not met,
               or if the function raises an exception during execution.

Notes:
    1. Determines the function name for logging purposes.
    2. Checks if the circuit breaker is in OPEN state.
    3. If OPEN, attempts to transition to HALF_OPEN if sufficient time has passed.
    4. If unable to transition (too soon), raises an exception.
    5. Executes the function within a try block.
    6. On success, calls _on_success to handle the success state.
    7. On failure, calls _on_failure to handle the failure state and re-raises the exception.

---
## method: `CircuitBreaker._should_attempt_reset(self: UnknownType) -> bool`

Check if enough time has passed to attempt reset.

Returns:
    True if the timeout has expired since the last failure, False otherwise.

Notes:
    1. Returns False if there is no recorded last failure time.
    2. Calculates the elapsed time since the last failure.
    3. Compares elapsed time to the configured timeout.
    4. Returns True if elapsed time exceeds timeout.

---
## method: `CircuitBreaker._transition_to_half_open(self: UnknownType) -> None`

Transition the circuit breaker to half-open state.

Notes:
    1. Sets the state to HALF_OPEN.
    2. Resets the success counter for half-open attempts to zero.

---
## method: `CircuitBreaker._on_success(self: UnknownType) -> None`

Handle successful execution.

Notes:
    1. Checks if the current state is HALF_OPEN.
    2. If HALF_OPEN, increments the success counter.
    3. If the success counter reaches the half-open threshold, resets the circuit.
    4. Otherwise, resets the circuit regardless of state.

---
## method: `CircuitBreaker._on_failure(self: UnknownType) -> None`

Handle failed execution.

Notes:
    1. Increments the failure count.
    2. Records the current time as the last failure time.
    3. If in HALF_OPEN state, trips the circuit.
    4. If the failure count reaches the threshold, trips the circuit.

---
## method: `CircuitBreaker._trip(self: UnknownType) -> None`

Trip the circuit breaker to open state.

Notes:
    1. Sets the state to OPEN.
    2. Logs a warning message indicating the circuit has been tripped.

---
## method: `CircuitBreaker._reset(self: UnknownType) -> None`

Reset the circuit breaker to closed state.

Notes:
    1. Sets the state to CLOSED.
    2. Resets the failure count to zero.
    3. Clears the last failure time.
    4. Resets the half-open success count to zero.
    5. Logs an informational message indicating the reset.

---
## method: `CircuitBreaker.get_state_info(self: UnknownType) -> dict[str, Any]`

Get current state information for monitoring.

Returns:
    A dictionary containing the circuit breaker's name, current state, failure count,
    last failure time, and half-open success count.

Notes:
    1. Constructs a dictionary with the current state information.
    2. Includes the name, state, failure count, last failure time, and half-open success count.
    3. Returns the constructed dictionary.

---

===

===
# File: `components.py`

## function: `initialize_llm_clients() -> dict[str, Any]`

Initialize LLM clients for different purposes.

Args:
    None

Returns:
    A dictionary mapping client names ("thinking", "action", "completion") to their respective LLMClient instances.

Notes:
    1. Create a dictionary with keys "thinking", "action", and "completion".
    2. For each key, retrieve the corresponding LLMClient using get_llm_client with the specified model name.
    3. Return the constructed dictionary of clients.

---

## function: `initialize_tools() -> dict[str, ToolInterface]`

Initialize available tools.

Args:
    None

Returns:
    A dictionary mapping tool names ("web_search", "wikipedia") to their respective ToolInterface instances.

Notes:
    1. Create an empty dictionary to store tool instances.
    2. Add the WebSearchTool instance with key "web_search".
    3. Add the WikipediaTool instance with key "wikipedia".
    4. Return the dictionary of tools.

---

## function: `create_prompt_templates() -> dict[str, PromptTemplate]`

Create prompt templates for different phases.

Args:
    None

Returns:
    A dictionary mapping template names ("think", "action", "completion") to their respective PromptTemplate instances.

Notes:
    1. Create an empty dictionary to store prompt templates.
    2. Define the "think" template with a prompt that guides analysis of the question and memory state.
    3. Define the "action" template with a prompt that guides action selection based on analysis and available tools.
    4. Define the "completion" template with a prompt that determines if the question can be answered based on collected info.
    5. Return the dictionary of templates.

---

## function: `process_thoughts(query: str, memory_manager: Any, thinking_client: Any, think_prompt: PromptTemplate) -> str`

Generate thoughts based on the current state and memory.

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

---

## function: `process_completion_decision(query: str, memory_manager: Any, completion_client: Any, completion_prompt: PromptTemplate) -> CompletionDecision`

Determine if we have sufficient information to answer the question.

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

---

## function: `handle_tool_execution(tool_name: str, query: str, tools: dict[str, ToolInterface]) -> ToolResponse`

Execute a tool by name.

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

---

## function: `__init__(self: UnknownType) -> None`

Initialize controller with configured LLM client and tools.

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

---

## function: `execute_tool(self: UnknownType, tool_name: str, query: str) -> ToolResponse`

Execute a tool with the given query.

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

---

## function: `process_query(self: UnknownType, query: str) -> str`

Process user query through ReAct cycle.

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

---

## `Controller` class

Main controller that orchestrates the ReAct cycle for the multi-step agent.

---
## method: `Controller.__init__(self: UnknownType) -> None`

Initialize controller with configured LLM client and tools.

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

---
## method: `Controller.execute_tool(self: UnknownType, tool_name: str, query: str) -> ToolResponse`

Execute a tool with the given query.

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

---
## method: `Controller.process_query(self: UnknownType, query: str) -> str`

Process user query through ReAct cycle.

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

---

===

===
# File: `metrics.py`

## function: `timing_decorator(metric_name: str) -> UnknownType`

Decorator to time function execution and record metrics.

Args:
    metric_name: Name to use for the metric (defaults to function name).

Returns:
    Decorated function that records timing metrics.

Notes:
    1. Extract the metrics instance from the first argument if it's a method.
    2. Determine the operation name based on the provided metric_name or function name.
    3. Start the timer for the operation.
    4. Record the start time.
    5. Execute the function and capture the result.
    6. Calculate the duration and stop the timer.
    7. Return the result of the function.

---

## function: `__init__(self: UnknownType) -> UnknownType`

Initialize performance metrics collector.

Notes:
    1. Initialize an empty dictionary for storing metrics.
    2. Initialize an empty dictionary for tracking start times of operations.
    3. Log the initialization.

---

## function: `start_timer(self: UnknownType, operation_name: str) -> None`

Start timing an operation.

Args:
    operation_name: The name of the operation to time.

Returns:
    None

Notes:
    1. Store the current time in the start_times dictionary using operation_name as the key.
    2. Log the start of the timer.

---

## function: `stop_timer(self: UnknownType, operation_name: str) -> float`

Stop timing an operation and record the duration.

Args:
    operation_name: The name of the operation to stop timing.

Returns:
    The duration of the operation in seconds. Returns 0.0 if no start time is found.

Notes:
    1. Check if the operation_name exists in start_times.
    2. If it exists, calculate the duration by subtracting the start time from the current time.
    3. Append the duration to the list of timings for operation_name.
    4. Remove the operation_name from start_times.
    5. Log the duration and return it.
    6. If operation_name is not found, log a warning and return 0.0.

---

## function: `record_api_call(self: UnknownType, endpoint: str, duration: float, cost: float) -> None`

Record an API call with timing and cost.

Args:
    endpoint: The API endpoint that was called.
    duration: The duration of the API call in seconds.
    cost: The cost of the API call in USD (default: 0.0).

Returns:
    None

Notes:
    1. If the endpoint is not in the api_calls dictionary, initialize its metrics.
    2. Increment the count of API calls for the endpoint.
    3. Add the duration and cost to the total for the endpoint.
    4. Calculate and store the average duration and cost.

---

## function: `record_controller_iteration(self: UnknownType, iteration: int, thoughts_duration: float, action_duration: float, completion_duration: float) -> None`

Record metrics for a controller iteration.

Args:
    iteration: The iteration number.
    thoughts_duration: Time taken for the thinking phase.
    action_duration: Time taken for the action phase.
    completion_duration: Time taken for the completion phase.

Returns:
    None

Notes:
    1. Create a dictionary to store the metrics for the given iteration.
    2. Include the durations for each phase and the total duration.
    3. Store the dictionary in the controller_iterations dictionary using the iteration number as the key.

---

## function: `record_memory_operation(self: UnknownType, operation: str, duration: float) -> None`

Record a memory operation with timing.

Args:
    operation: The name of the memory operation (e.g., "add_observation", "serialize").
    duration: The duration of the operation in seconds.

Returns:
    None

Notes:
    1. If the operation is not in the memory_operations dictionary, initialize an empty list.
    2. Append the duration to the list of timings for the operation.

---

## function: `record_tool_execution(self: UnknownType, tool_name: str, duration: float, success: bool) -> None`

Record a tool execution with timing and success status.

Args:
    tool_name: The name of the tool executed.
    duration: The duration of the tool execution in seconds.
    success: Whether the tool execution was successful (default: True).

Returns:
    None

Notes:
    1. If the tool_name is not in the tool_executions dictionary, initialize its metrics.
    2. Increment the count of tool executions for the tool.
    3. If the execution was successful, increment the success count.
    4. Add the duration to the total duration for the tool.
    5. Calculate and store the average duration and success rate.

---

## function: `get_metrics_summary(self: UnknownType) -> Dict[str, Any]`

Get a summary of all collected metrics.

Returns:
    A dictionary containing summary statistics for all metrics, including:
    - operation_timings: Counts, totals, averages, mins, and maxes for each operation.
    - api_calls: Count, total and average duration and cost for each endpoint.
    - controller_iterations: Durations for each phase of each iteration.
    - memory_operations: Lists of durations for each operation.
    - tool_executions: Counts, success rates, and average durations for each tool.

Notes:
    1. Initialize an empty dictionary for the summary.
    2. Summarize operation timings by calculating counts, totals, averages, mins, and maxes.
    3. Include other metrics directly from the metrics dictionary.

---

## function: `reset_metrics(self: UnknownType) -> None`

Reset all collected metrics.

Returns:
    None

Notes:
    1. Reinitialize the metrics dictionary to empty.
    2. Reinitialize the start_times dictionary to empty.

---

## function: `save_metrics(self: UnknownType, filepath: str) -> None`

Save metrics to a JSON file.

Args:
    filepath: The path to save the metrics file.

Returns:
    None

Notes:
    1. Create a copy of the metrics dictionary to avoid serialization issues.
    2. Write the metrics dictionary to the file in JSON format with indentation.

---

## function: `decorator(func: Callable) -> Callable`



---

## function: `wrapper() -> UnknownType`



---

## `PerformanceMetrics` class

Collects and manages performance metrics for the agent.

---
## method: `PerformanceMetrics.__init__(self: UnknownType) -> UnknownType`

Initialize performance metrics collector.

Notes:
    1. Initialize an empty dictionary for storing metrics.
    2. Initialize an empty dictionary for tracking start times of operations.
    3. Log the initialization.

---
## method: `PerformanceMetrics.start_timer(self: UnknownType, operation_name: str) -> None`

Start timing an operation.

Args:
    operation_name: The name of the operation to time.

Returns:
    None

Notes:
    1. Store the current time in the start_times dictionary using operation_name as the key.
    2. Log the start of the timer.

---
## method: `PerformanceMetrics.stop_timer(self: UnknownType, operation_name: str) -> float`

Stop timing an operation and record the duration.

Args:
    operation_name: The name of the operation to stop timing.

Returns:
    The duration of the operation in seconds. Returns 0.0 if no start time is found.

Notes:
    1. Check if the operation_name exists in start_times.
    2. If it exists, calculate the duration by subtracting the start time from the current time.
    3. Append the duration to the list of timings for operation_name.
    4. Remove the operation_name from start_times.
    5. Log the duration and return it.
    6. If operation_name is not found, log a warning and return 0.0.

---
## method: `PerformanceMetrics.record_api_call(self: UnknownType, endpoint: str, duration: float, cost: float) -> None`

Record an API call with timing and cost.

Args:
    endpoint: The API endpoint that was called.
    duration: The duration of the API call in seconds.
    cost: The cost of the API call in USD (default: 0.0).

Returns:
    None

Notes:
    1. If the endpoint is not in the api_calls dictionary, initialize its metrics.
    2. Increment the count of API calls for the endpoint.
    3. Add the duration and cost to the total for the endpoint.
    4. Calculate and store the average duration and cost.

---
## method: `PerformanceMetrics.record_controller_iteration(self: UnknownType, iteration: int, thoughts_duration: float, action_duration: float, completion_duration: float) -> None`

Record metrics for a controller iteration.

Args:
    iteration: The iteration number.
    thoughts_duration: Time taken for the thinking phase.
    action_duration: Time taken for the action phase.
    completion_duration: Time taken for the completion phase.

Returns:
    None

Notes:
    1. Create a dictionary to store the metrics for the given iteration.
    2. Include the durations for each phase and the total duration.
    3. Store the dictionary in the controller_iterations dictionary using the iteration number as the key.

---
## method: `PerformanceMetrics.record_memory_operation(self: UnknownType, operation: str, duration: float) -> None`

Record a memory operation with timing.

Args:
    operation: The name of the memory operation (e.g., "add_observation", "serialize").
    duration: The duration of the operation in seconds.

Returns:
    None

Notes:
    1. If the operation is not in the memory_operations dictionary, initialize an empty list.
    2. Append the duration to the list of timings for the operation.

---
## method: `PerformanceMetrics.record_tool_execution(self: UnknownType, tool_name: str, duration: float, success: bool) -> None`

Record a tool execution with timing and success status.

Args:
    tool_name: The name of the tool executed.
    duration: The duration of the tool execution in seconds.
    success: Whether the tool execution was successful (default: True).

Returns:
    None

Notes:
    1. If the tool_name is not in the tool_executions dictionary, initialize its metrics.
    2. Increment the count of tool executions for the tool.
    3. If the execution was successful, increment the success count.
    4. Add the duration to the total duration for the tool.
    5. Calculate and store the average duration and success rate.

---
## method: `PerformanceMetrics.get_metrics_summary(self: UnknownType) -> Dict[str, Any]`

Get a summary of all collected metrics.

Returns:
    A dictionary containing summary statistics for all metrics, including:
    - operation_timings: Counts, totals, averages, mins, and maxes for each operation.
    - api_calls: Count, total and average duration and cost for each endpoint.
    - controller_iterations: Durations for each phase of each iteration.
    - memory_operations: Lists of durations for each operation.
    - tool_executions: Counts, success rates, and average durations for each tool.

Notes:
    1. Initialize an empty dictionary for the summary.
    2. Summarize operation timings by calculating counts, totals, averages, mins, and maxes.
    3. Include other metrics directly from the metrics dictionary.

---
## method: `PerformanceMetrics.reset_metrics(self: UnknownType) -> None`

Reset all collected metrics.

Returns:
    None

Notes:
    1. Reinitialize the metrics dictionary to empty.
    2. Reinitialize the start_times dictionary to empty.

---
## method: `PerformanceMetrics.save_metrics(self: UnknownType, filepath: str) -> None`

Save metrics to a JSON file.

Args:
    filepath: The path to save the metrics file.

Returns:
    None

Notes:
    1. Create a copy of the metrics dictionary to avoid serialization issues.
    2. Write the metrics dictionary to the file in JSON format with indentation.

---

===

