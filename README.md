# Multi-Step Agent (MSA)

A simple AI agent capable of answering complex questions through multi-step reasoning, tool usage, and information synthesis.

## Overview

The Multi-Step Agent is designed to handle complex queries that require multiple resources and reasoning steps to answer. It follows the ReAct (Reasoning + Action) pattern to iteratively analyze questions, select appropriate tools, gather information, and synthesize comprehensive answers with confidence scoring and citations.

## Key Features

### Agent Framework
- **ReAct Pattern Implementation**: Thought → Action → Observation cycle for iterative problem solving
- **LLM Controller**: Uses multiple models (strong and weak) for different purposes
- **Working Memory**: Persistent state tracking including query history, observations, and confidence scores

### Orchestration Layer
- **Step Planning**: Query decomposition and dependency mapping
- **Tool Selection**: Intent classification and relevance scoring
- **Result Synthesis**: Information extraction and cross-validation

### Knowledge Integration
- **Cross-Reference Implementation**: Entity resolution and temporal alignment
- **Confidence Scoring**: Multi-factor confidence model with source credibility weighting
- **Conflict Resolution**: Contradiction detection and investigation

### Reliability Features
- **Circuit Breaker Pattern**: Failure threshold management and automatic reset
- **Caching Strategy**: Query-based caching with time-based expiration
- **Fallback Mechanisms**: Tool substitution and degraded response quality handling
- **Timeout Management**: Per-tool and cumulative timeouts with partial results

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Controller    │◄──►│ Working Memory   │◄──►│  Synthesis      │
│ (Orchestration) │    │ (State Manager)  │    │  Engine         │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   LLM Clients   │    │  Tool Adapters   │    │  Confidence     │
│ (Thinking,      │    │ (Web Search,     │    │  Scoring        │
│  Action, etc.)  │    │  Wikipedia, etc.)│    │  & Conflict     │
└─────────────────┘    └──────────────────┘    │  Resolution     │
                                               └─────────────────┘
```

## Tool Ecosystem

The agent supports various tools for information gathering:

- **Web Search**: General web search capabilities
- **Wikipedia**: Knowledge base queries
- **(Extensible)**: Framework supports adding new tools

## Installation

```bash
# Clone the repository
git clone <repository-url>

# Install dependencies
uv sync
```

## Configuration

The agent requires configuration files:

- `msa/app_config.yml`: Application settings
- `msa/llm_config.yml`: LLM endpoint configurations

Environment variables:
- `SERPER_API_KEY`: Uses [Serper](https://serper.dev/) for Google search
- `LLM_API_KEY`: API key for OpenAI-compatible endpoint

## Usage

```bash
# Run the agent with a query
python -m msa.main -q "What is the population of Tokyo and how has it changed over the last decade?"

# Run with specific log level
python -m msa.main --log-level DEBUG -q "Explain quantum computing principles"
```

## Response Format

Agent responses include:

1. **Answer**: The synthesized response to the query
2. **Reasoning Steps**: Explanation of the thought process
3. **Confidence Report**: Numerical and qualitative confidence scoring
4. **Sources**: Citations with timestamps for all information used

## Development

### Project Structure
```
msa/
├── app_config.yml      # Application configuration
├── llm_config.yml      # LLM configuration
├── __main__.py         # Entry point
├── controller/         # Main orchestration logic
├── memory/             # Working memory management
├── orchestration/      # Planning and synthesis
├── tools/              # Tool adapters
├── monitoring/         # Performance metrics
└── evaluation/         # Accuracy and completeness evaluation
```

### Testing

```bash
# Run all tests
uv run pytest

# Run tests with verbose output
uv run pytest -v

# Run tests with coverage
uv run pytest --cov=msa
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

[MIT License](https://github.com/mpaguilar/msa-toy/blob/main/LICENCE)

## Acknowledgments

This project utilizes:
- LangChain for LLM integration
- Various LLM providers for inference capabilities
- Wikipedia and web search APIs for information retrieval
- Aider-chat as the coding agent
```
