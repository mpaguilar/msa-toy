import logging
import logging.config


def setup_logging() -> None:
    """Configure logging for the application.

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
        8. This function performs no disk, network, or database access.

    """
    # Default configuration
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "INFO",
                "formatter": "standard",
                "stream": "ext://sys.stdout",
            },
        },
        "root": {"level": "INFO", "handlers": ["console"]},
    }

    logging.config.dictConfig(logging_config)


def get_logger(name: str) -> logging.Logger:
    """Get a configured logger instance.

    Retrieves or creates a logger with the specified name, ensuring it uses the configured logging setup.

    Args:
        name: The name for the logger, typically __name__ of the calling module.

    Returns:
        A configured logging.Logger instance that can be used to emit log messages.

    Notes:
        1. Use the logging.getLogger function to retrieve or create a logger with the provided name.
        2. The logger will automatically use the configuration set by setup_logging.
        3. This function performs no disk, network, or database access.

    """
    return logging.getLogger(name)
