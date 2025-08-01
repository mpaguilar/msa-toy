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
        1. Initialize a debug log message indicating the start of the function.
        2. Attempt to open and parse the YAML file at APP_CONFIG_PATH.
        3. If the file is not found, log a warning and return an empty dictionary.
        4. If YAML parsing fails, log an exception and return an empty dictionary.
        5. On success, return the parsed configuration dictionary (defaulting to empty if None).
        6. Log a debug message indicating the function has completed.

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
        1. Initialize a debug log message indicating the start of the function.
        2. Attempt to open and parse the YAML file at LLM_CONFIG_PATH.
        3. If the file is not found, log a warning and return an empty dictionary.
        4. If YAML parsing fails, log an exception and return an empty dictionary.
        5. On success, return the parsed configuration dictionary (defaulting to empty if None).
        6. Log a debug message indicating the function has completed.

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
        1. Initialize a debug log message indicating the start of the function with the endpoint name.
        2. Load the LLM configuration using the load_llm_config function.
        3. Extract the list of endpoints from the loaded configuration.
        4. Iterate through each endpoint in the list.
        5. For each endpoint, check if its 'name' field matches the provided name argument.
        6. If a match is found, return the full configuration dictionary for that endpoint.
        7. If no match is found after iterating through all endpoints, return an empty dictionary.
        8. Log a warning if the endpoint is not found.
        9. Log a debug message indicating the function has completed.

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
