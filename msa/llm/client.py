import logging
import os
from typing import Any

from langchain_core.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI

from msa.config import get_endpoint_config

log = logging.getLogger(__name__)

# Global dictionary to store initialized LLM clients
_llm_clients: dict[str, "LLMClient"] = {}


class LLMClient:
    """LLM client for making calls to various LLM endpoints."""

    def __init__(self, endpoint_config: dict) -> None:
        """Initialize LLM client with endpoint configuration.

        Args:
            endpoint_config: Dictionary containing configuration for the LLM endpoint,
                including model_id, api_base, and any other relevant settings.

        Notes:
            1. Log the start of initialization with the provided endpoint configuration.
            2. Extract the model_id and api_base from the endpoint_config.
            3. Initialize the underlying LLM (ChatOpenAI) with the extracted model_id, API key,
               base URL, and default temperature of 0.7.
            4. Log the successful completion of initialization.

        """
        _msg = f"LLMClient.__init__ starting with config: {endpoint_config}"
        log.debug(_msg)

        self.endpoint_config = endpoint_config
        self.model_id = endpoint_config.get("model_id")
        self.api_base = endpoint_config.get("api_base", "https://openrouter.ai/api/v1")

        # Initialize the LLM
        self.llm = ChatOpenAI(
            model=self.model_id,
            api_key=os.getenv(
                "LLM_API_KEY",
                "EMPTY",
            ),  # Using EMPTY as default to match OpenAI API expectations
            base_url=self.api_base,
            temperature=0.7,
        )

        _msg = "LLMClient.__init__ returning"
        log.debug(_msg)

    def call(
        self,
        prompt: str,
        parser: PydanticOutputParser | None = None,
    ) -> dict[str, Any]:
        """Call LLM with prompt and optional parser.

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

        """
        _msg = f"LLMClient.call starting with prompt: {prompt[:50]}..."
        log.debug(_msg)

        try:
            if parser:
                # Include format instructions in the prompt
                formatted_prompt = f"{prompt}\n\n{parser.get_format_instructions()}"
                response = self.llm.invoke(formatted_prompt)
                parsed_response = parser.parse(response.content)
                result = {
                    "content": response.content,
                    "parsed": parsed_response.dict()
                    if hasattr(parsed_response, "dict")
                    else parsed_response,
                    "metadata": {"model": self.model_id, "api_base": self.api_base},
                }
            else:
                response = self.llm.invoke(prompt)
                result = {
                    "content": response.content,
                    "metadata": {"model": self.model_id, "api_base": self.api_base},
                }

            _msg = "LLMClient.call returning successfully"
            log.debug(_msg)
            return result

        except Exception as e:
            _msg = f"LLMClient.call failed with error: {str(e)}"
            log.exception(_msg)
            raise


def get_llm_client(name: str) -> LLMClient:
    """Get configured LLM client by name.

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

    """
    _msg = f"get_llm_client starting with name: {name}"
    log.debug(_msg)

    global _llm_clients

    # Check if client already exists
    if name in _llm_clients:
        _msg = f"get_llm_client returning existing client for: {name}"
        log.debug(_msg)
        return _llm_clients[name]

    # Get endpoint configuration
    endpoint_config = get_endpoint_config(name)

    # Create new client
    client = LLMClient(endpoint_config)
    _llm_clients[name] = client

    _msg = f"get_llm_client returning new client for: {name}"
    log.debug(_msg)
    return client
