import logging
from pathlib import Path

import yaml

log = logging.getLogger(__name__)

APP_CONFIG_PATH = Path("msa/app_config.yml")
LLM_CONFIG_PATH = Path("msa/llm_config.yml")


def load_app_config() -> dict:
    """Load application configuration from YAML.

    Returns:
        dict: The application configuration dictionary.
    """
    _msg = "load_app_config starting"
    log.debug(_msg)

    try:
        with open(APP_CONFIG_PATH, "r") as file:
            config = yaml.safe_load(file) or {}
    except FileNotFoundError:
        _msg = f"App config file not found at {APP_CONFIG_PATH}, returning empty dict"
        log.warning(_msg)
        config = {}
    except yaml.YAMLError as e:
        _msg = f"Error parsing app config YAML: {e}"
        log.exception(_msg)
        config = {}

    _msg = "load_app_config returning"
    log.debug(_msg)
    return config


def load_llm_config() -> dict:
    """Load LLM configuration from YAML.

    Returns:
        dict: The LLM configuration dictionary.
    """
    _msg = "load_llm_config starting"
    log.debug(_msg)

    try:
        with open(LLM_CONFIG_PATH, "r") as file:
            config = yaml.safe_load(file) or {}
    except FileNotFoundError:
        _msg = f"LLM config file not found at {LLM_CONFIG_PATH}, returning empty dict"
        log.warning(_msg)
        config = {}
    except yaml.YAMLError as e:
        _msg = f"Error parsing LLM config YAML: {e}"
        log.exception(_msg)
        config = {}

    _msg = "load_llm_config returning"
    log.debug(_msg)
    return config


def get_endpoint_config(name: str) -> dict:
    """Get specific endpoint configuration by name.

    Args:
        name: The name of the endpoint to retrieve configuration for.

    Returns:
        dict: The endpoint configuration dictionary.
    """
    _msg = f"get_endpoint_config starting for endpoint {name}"
    log.debug(_msg)

    llm_config = load_llm_config()
    endpoints = llm_config.get("openai_endpoints", {}).get("endpoints", [])

    for endpoint in endpoints:
        if endpoint.get("name") == name:
            _msg = f"get_endpoint_config returning config for {name}"
            log.debug(_msg)
            return endpoint

    _msg = f"Endpoint {name} not found, returning empty dict"
    log.warning(_msg)
    return {}
