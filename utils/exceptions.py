import traceback
import logging
logger = logging.getLogger(__name__)

def handle_exception(e):
    """Handle exceptions by logging the error details."""
    tb = traceback.format_exc()
    logger.error(f"An error occurred: {e}\n{tb}")
    return "An internal error occurred. Please try again later.", 500
