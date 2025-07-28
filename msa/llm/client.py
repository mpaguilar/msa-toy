import logging
from typing import Dict, Any, Optional
import os
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import PydanticOutputParser
from msa.config import get_endpoint_config
from msa.llm.models import LLMResponse

log = logging.getLogger(__name__)

# Global dictionary to store initialized LLM clients
_llm_clients: Dict[str, "LLMClient"] = {}


class LLMClient:
    """LLM client for making calls to various LLM endpoints."""
    
    def __init__(self, endpoint_config: dict) -> None:
        """Initialize LLM client with endpoint configuration.
        
        Args:
            endpoint_config: Dictionary containing endpoint configuration
        """
        _msg = f"LLMClient.__init__ starting with config: {endpoint_config}"
        log.debug(_msg)
        
        self.endpoint_config = endpoint_config
        self.model_id = endpoint_config.get("model_id")
        self.api_base = endpoint_config.get("api_base", "https://openrouter.ai/api/v1")
        
        # Initialize the LLM
        self.llm = ChatOpenAI(
            model=self.model_id,
            api_key=os.getenv("LLM_API_KEY", "EMPTY"),  # Using EMPTY as default to match OpenAI API expectations
            base_url=self.api_base,
            temperature=0.7
        )
        
        _msg = "LLMClient.__init__ returning"
        log.debug(_msg)

    def call(self, prompt: str, parser: Optional[PydanticOutputParser] = None) -> Dict[str, Any]:
        """Call LLM with prompt and optional parser.
        
        Args:
            prompt: The prompt to send to the LLM
            parser: Optional PydanticOutputParser for structured output
            
        Returns:
            Dictionary containing the LLM response
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
                    "parsed": parsed_response.dict() if hasattr(parsed_response, 'dict') else parsed_response,
                    "metadata": {
                        "model": self.model_id,
                        "api_base": self.api_base
                    }
                }
            else:
                response = self.llm.invoke(prompt)
                result = {
                    "content": response.content,
                    "metadata": {
                        "model": self.model_id,
                        "api_base": self.api_base
                    }
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
        name: Name of the LLM client to retrieve
        
    Returns:
        LLMClient instance
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
