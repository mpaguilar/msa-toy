"""Main entry point for the Multi-Step Agent application."""

import logging

import click

try:
    from dotenv import load_dotenv

    HAS_DOTENV = True
except ImportError:
    HAS_DOTENV = False

from msa.controller.main import Controller
from msa.logging_config import setup_logging

# Load environment variables from .env file
if HAS_DOTENV:
    load_dotenv()

# Set up logging
setup_logging()
log = logging.getLogger(__name__)


@click.command()
@click.option(
    "--query",
    "-q",
    default="Provide a list of Texas state senators",
    help="Query to process with the multi-step agent",
)
@click.option(
    "--log-level",
    "-l",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]),
    default="INFO",
    help="Logging level",
)
def main(query: str, log_level: str) -> None:
    """Run the Multi-Step Agent with a given query.

    This function serves as the entry point for the Multi-Step Agent application.
    It initializes the logging system, sets the logging level, creates the controller,
    processes the user query through the agent's reasoning cycle, and outputs the final result.

    Args:
        query: The input query string that the agent must process. The query should
               be a natural language request requiring multi-step reasoning and
               tool usage to answer.
        log_level: The desired logging level for the application. Valid choices are
                   DEBUG, INFO, WARNING, ERROR, and CRITICAL. This controls the
                   verbosity of runtime logs.

    Returns:
        None. The function does not return a value. The agent's result is printed
        to stdout and logged, but no return value is provided.

    Notes:
        1. Load environment variables from a .env file if the dotenv package is available.
        2. Initialize the logging system using the setup_logging function.
        3. Set the global logging level based on the provided log_level argument.
        4. Log a message indicating the start of the agent with the given query.
        5. Instantiate the Controller class to manage the agent's reasoning workflow.
        6. Call the controller's process_query method with the provided query.
        7. Print the agent's result in a formatted block.
        8. Log a success message if processing completes without exception.
        9. If an exception occurs during processing, log the error with full traceback
           and print a user-friendly error message to stdout.

    """
    # Set the logging level
    logging.getLogger().setLevel(getattr(logging, log_level))

    _msg = f"Starting Multi-Step Agent with query: {query}"
    log.info(_msg)

    try:
        # Initialize the controller
        controller = Controller()

        # Process the query
        result = controller.process_query(query)

        # Output the result
        print("\n=== Multi-Step Agent Response ===")
        print(result)
        print("==================================\n")

        _msg = "Multi-Step Agent completed successfully"
        log.info(_msg)

    except Exception as e:
        _msg = f"Error running Multi-Step Agent: {str(e)}"
        log.exception(_msg)
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
