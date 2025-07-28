import logging
import logging.config


def setup_logging() -> None:
    """Configure logging for the application.

    Sets up a default logging configuration with console output.

    Returns:
        None
    """
    # Default configuration
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
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
        name: The name for the logger, typically __name__

    Returns:
        A configured logger instance
    """
    return logging.getLogger(name)
