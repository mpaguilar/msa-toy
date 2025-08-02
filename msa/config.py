import logging
from pathlib import Path

import yaml

log = logging.getLogger(__name__)

APP_CONFIG_PATH = Path("msa/app_config.yml")
LLM_CONFIG_PATH = Path("msa/llm_config.yml")


def load_app_config() -> dict:
    """Load application configuration from YAML file.

    Args:
        None: This function does not take any arguments.

    Returns:
        dict: A dictionary containing the loaded application configuration.
              Returns an empty dictionary if the file is not found or cannot be parsed.

    Notes:
        1. Read the YAML file located at APP_CONFIG_PATH from disk.
        2. Parse the YAML content into a Python dictionary.
        3. If the file is not found, return an empty dictionary.
        4. If the file exists but contains invalid YAML, return an empty dictionary.
        5. If parsing succeeds, return the parsed configuration dictionary (defaulting to empty if None).

    """
    _msg = "load_app_config starting"
    log.debug(_msg)

    try:
        with open(APP_CONFIG_PATH) as file:
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
    """Load LLM configuration from YAML file.

    Args:
        None: This function does not take any arguments.

    Returns:
        dict: A dictionary containing the loaded LLM configuration.
              Returns an empty dictionary if the file is not found or cannot be parsed.

    Notes:
        1. Read the YAML file located at LLM_CONFIG_PATH from disk.
        2. Parse the YAML content into a Python dictionary.
        3. If the file is not found, return an empty dictionary.
        4. If the file exists but contains invalid YAML, return an empty dictionary.
        5. If parsing succeeds, return the parsed configuration dictionary (defaulting to empty if None).

    """
    _msg = "load_llm_config starting"
    log.debug(_msg)

    try:
        with open(LLM_CONFIG_PATH) as file:
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
    """Retrieve configuration for a specific LLM endpoint by name.

    Args:
        name (str): The name of the endpoint to retrieve configuration for.

    Returns:
        dict: The configuration dictionary for the specified endpoint.
              Returns an empty dictionary if the endpoint is not found in the configuration.

    Notes:
        1. Load the LLM configuration from the YAML file at LLM_CONFIG_PATH.
        2. Extract the list of endpoints from the loaded configuration.
        3. Iterate through each endpoint in the list.
        4. For each endpoint, compare its 'name' field with the provided name argument.
        5. If a match is found, return the full configuration dictionary for that endpoint.
        6. If no match is found after iterating through all endpoints, return an empty dictionary.

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
