"""Main entry point for the Multi-Step Agent application."""

import click
import logging
import os
from typing import Optional

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
@click.option('--query', '-q', 
              default="Provide a list of Texas state senators", 
              help="Query to process with the multi-step agent")
@click.option('--log-level', '-l', 
              type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']),
              default='INFO', 
              help="Logging level")
def main(query: str, log_level: str) -> None:
    """Run the Multi-Step Agent with a given query.
    
    Args:
        query: The query to process
        log_level: The logging level to use
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
