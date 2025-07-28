# Multi-Step Agent System

## Overview

The Multi-Step Agent (MSA) is a sophisticated question-answering system that implements the ReAct (Reasoning and Acting) pattern to decompose complex queries into manageable steps. The system leverages multiple Large Language Models (LLMs) and external tools to gather, validate, and synthesize information from various sources.

## Core Architecture

### Controller System (`msa/controller/models.py`, `msa/controller/main.py`)

The controller orchestrates the entire ReAct cycle through a structured decision-making process:

**Key Models:**
- `ActionSelection`: Represents decisions about what action to take next, including action type, specific tool/action name, reasoning, and confidence scores
- `QueryRefinement`: Models refined queries optimized for tool usage, maintaining the original query alongside the refined version
- `CompletionDecision`: Determines when the task is complete, including the final answer and remaining tasks if incomplete

**Controller Class:**
The `Controller` class manages the ReAct cycle with:
- Multiple LLM clients for different purposes (thinking, action selection, completion checking)
- Tool management (web search, Wikipedia)
- Working memory integration
- Iterative processing with configurable maximum iterations

**Core Methods:**
- `process_query()`: Main entry point that runs the ReAct cycle
- `think()`: Generates thoughts based on current state and memory
- `act()`: Selects the next action based on generated thoughts
- `observe()`: Processes tool responses into observations
- `check_completion()`: Determines if sufficient information has been gathered
- `execute_tool()`: Executes selected tools with error handling

### Memory Management System (`msa/memory/models.py`, `msa/memory/manager.py`)

The working memory system provides persistent state tracking throughout the reasoning process:

**Memory Components:**
- `QueryState`: Tracks original query, refinements, and current focus
- `ExecutionHistory`: Records all actions, timestamps, and tool calls
- `InformationStore`: Manages facts, relationships, sources, and confidence scores
- `ReasoningState`: Maintains current hypothesis, answer drafts, and information gaps

**WorkingMemoryManager:**
- Initializes empty memory structure with the original query
- Provides methods to add observations with metadata
- Retrieves relevant facts based on context (currently using keyword matching)
- Updates confidence scores based on source credibility
- Supports full serialization/deserialization to JSON for persistence

### Tool System (`msa/tools/base.py`, `msa/tools/web_search.py`, `msa/tools/wikipedia.py`)

**Base Infrastructure:**
- `ToolInterface`: Abstract base class defining the tool contract
- `ToolResponse`: Standardized response model with content, metadata, and raw response

**Web Search Tool:**
- Uses SerpAPI (Google Search) for web queries
- Requires `SERPAPI_API_KEY` environment variable
- Returns top 5 search results with titles, links, and snippets
- Formats results in a structured, readable format

**Wikipedia Tool:**
- Uses LangChain's WikipediaRetriever
- Returns multiple relevant Wikipedia pages
- Formats results in Markdown with section headers
- Includes source attribution in metadata

### LLM Integration (`msa/llm/client.py`)

**LLMClient:**
- Wraps LangChain's ChatOpenAI for OpenRouter compatibility
- Supports multiple model endpoints configured in `llm_config.yml`
- Handles structured output parsing with PydanticOutputParser
- Manages API keys through environment variables (`LLM_API_KEY`)
- Implements singleton pattern for client reuse

### Configuration System (`msa/config.py`)

**Configuration Loading:**
- `load_app_config()`: Loads application settings from `app_config.yml`
- `load_llm_config()`: Loads LLM endpoint configurations
- `get_endpoint_config()`: Retrieves specific endpoint settings by name
- Graceful error handling for missing or malformed configuration files

## Configuration Files

**app_config.yml:**
- Application metadata (name, version)
- Debug settings
- Logging configuration

**llm_config.yml:**
- OpenRouter API base URL
- Multiple model endpoints for different purposes:
  - `code-small`: Qwen 2.5 Coder for code tasks
  - `code-big`: Qwen 2.5 Coder for complex code tasks
  - `tool-big`: Google Gemini 2.5 Flash for tool usage
  - `quick-medium`: Google Gemma 3 12b it for general reasoning
- Agent configurations with system prompts

## Logging System (`msa/logging_config.py`)

- Standardized logging setup across all modules
- Console output with timestamp, module name, level, and message
- Configurable log levels through app configuration
- Consistent debug logging at function entry/exit points

## Orchestration Layer

### Step Planning (`msa/orchestration/planner.py`)

The StepPlanner handles query decomposition and execution strategy:

**StepPlanner Class:**
- `decompose_query()`: Breaks complex questions into sub-questions
- `map_dependencies()`: Identifies which steps must happen before others
- `determine_strategy()`: Determines optimal order of tool usage
- `track_progress()`: Monitors which information gaps remain

## Tool Selection Mechanism (`msa/orchestration/selector.py`)

**ToolSelector Class:**
- `classify_intent()`: Categorizes query type using keyword-based classification into categories: factual, analytical, creative, coding, general
- `score_relevance()`: Scores tools based on query keywords and context with specific scoring for web_search (current events, specific facts, news) and wikipedia (general knowledge, historical facts, definitions)
- `select_tool()`: Selects the most relevant tool for a query based on relevance scores
- `analyze_cost_benefit()`: Analyzes API costs vs. information value using simplified cost model and query complexity estimation

The ToolSelector implements a practical keyword-based approach for intent classification and tool relevance scoring. The `classify_intent()` method analyzes query text to determine the most appropriate category, while `score_relevance()` evaluates how well each tool matches the query context. The `analyze_cost_benefit()` method provides a basic cost/value analysis to optimize resource usage.

## Implementation Status

All core components have been implemented:
- Configuration management system
- Logging infrastructure
- Working memory models and manager
- Tool interface and implementations (Web Search, Wikipedia)
- LLM client infrastructure with multiple endpoints
- Controller models and main orchestration logic
- Orchestration layer (Step Planning, Tool Selection)

## Notes:
- The system currently uses placeholder implementations for some LLM interactions (e.g., action selection returns hardcoded values)
- The memory relevance matching is basic (keyword-based) and could be enhanced with embeddings
- Error handling is comprehensive throughout the system
- Tool selection mechanisms currently use default implementations and need enhancement for production use
