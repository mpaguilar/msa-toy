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

    Args:
        name: The name for the logger, typically __name__ of the calling module.

    Returns:
        A configured logger instance that can be used to emit log messages.

    Notes:
        1. Use the logging.getLogger function to retrieve or create a logger with the provided name.
        2. Return the logger instance, which will have already been configured by setup_logging.

    """
    return logging.getLogger(name)
