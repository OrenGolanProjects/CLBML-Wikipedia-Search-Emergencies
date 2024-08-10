import traceback
import logging
import sys

# Ensure logger is configured
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

def handle_exception(e):
    """Handle exceptions by logging the error details."""
    logger.error("******************************************************")
    logger.error("***** An exception occurred during a request. ********")
    logger.error(f"Error: \n{e}")
    logger.error("******************************************************\n\n")
    return "An internal error occurred. Please try again later.", 500
