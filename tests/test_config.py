from unittest.mock import patch, mock_open
from msa.config import load_app_config, load_llm_config, get_endpoint_config

# Sample YAML content for testing
SAMPLE_APP_CONFIG = """
app_name: "Multi-Step Agent"
version: "1.0.0"
debug: true
"""

SAMPLE_LLM_CONFIG = """
openai_endpoints:
  api_base: "https://openrouter.ai/api/v1"
  model_id: "gpt-3.5-turbo"
  endpoints:
    - name: "code-small"
      model_id: "qwen/qwen-2.5-coder-32b-instruct"
    - name: "code-big"
      model_id: "qwen/qwen-2.5-coder-32b-instruct"
    - name: "tool-big"
      model_id: "google/gemini-2.5-flash"
    - name: "quick-medium"
      model_id: "google/gemma-3-12b-it"
agents:
  - name: "planner"
    endpoint: "code-big"
    system_prompt: "You are a planning agent that breaks down tasks."
  - name: "coder"
    endpoint: "code-small"
    system_prompt: "You are a coding agent that implements solutions."
"""


def test_load_app_config_success():
    """Test successful loading of app configuration."""
    with patch("builtins.open", mock_open(read_data=SAMPLE_APP_CONFIG)):
        with patch("pathlib.Path.exists", return_value=True):
            config = load_app_config()
            assert config["app_name"] == "Multi-Step Agent"
            assert config["version"] == "1.0.0"
            assert config["debug"] is True


def test_load_app_config_file_not_found():
    """Test handling of missing app config file."""
    with patch("builtins.open", side_effect=FileNotFoundError()):
        config = load_app_config()
        assert config == {}


def test_load_app_config_yaml_error():
    """Test handling of YAML parsing errors."""
    with patch("builtins.open", mock_open(read_data="invalid: yaml: content: :")):
        with patch("pathlib.Path.exists", return_value=True):
            config = load_app_config()
            assert config == {}


def test_load_llm_config_success():
    """Test successful loading of LLM configuration."""
    with patch("builtins.open", mock_open(read_data=SAMPLE_LLM_CONFIG)):
        with patch("pathlib.Path.exists", return_value=True):
            config = load_llm_config()
            assert "openai_endpoints" in config
            assert len(config["openai_endpoints"]["endpoints"]) == 4


def test_load_llm_config_file_not_found():
    """Test handling of missing LLM config file."""
    with patch("builtins.open", side_effect=FileNotFoundError()):
        config = load_llm_config()
        assert config == {}


def test_load_llm_config_yaml_error():
    """Test handling of YAML parsing errors in LLM config."""
    with patch("builtins.open", mock_open(read_data="invalid: yaml: content: :")):
        with patch("pathlib.Path.exists", return_value=True):
            config = load_llm_config()
            assert config == {}


def test_get_endpoint_config_success():
    """Test successful retrieval of endpoint configuration."""
    with patch("builtins.open", mock_open(read_data=SAMPLE_LLM_CONFIG)):
        with patch("pathlib.Path.exists", return_value=True):
            endpoint_config = get_endpoint_config("code-small")
            assert endpoint_config["name"] == "code-small"
            assert endpoint_config["model_id"] == "qwen/qwen-2.5-coder-32b-instruct"


def test_get_endpoint_config_not_found():
    """Test handling of non-existent endpoint name."""
    with patch("builtins.open", mock_open(read_data=SAMPLE_LLM_CONFIG)):
        with patch("pathlib.Path.exists", return_value=True):
            endpoint_config = get_endpoint_config("non-existent")
            assert endpoint_config == {}


def test_get_endpoint_config_empty_config():
    """Test handling of empty LLM configuration."""
    with patch("builtins.open", mock_open(read_data="")):
        with patch("pathlib.Path.exists", return_value=True):
            endpoint_config = get_endpoint_config("code-small")
            assert endpoint_config == {}
