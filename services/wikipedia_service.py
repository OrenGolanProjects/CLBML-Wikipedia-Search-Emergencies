import logging
from models.wikipedia_page import WikipediaPage
from repositories.wikipedia_repository import WikipediaRepository

import logging
import colorlog

# Initialize logging with colorlog
log_colors = {
    'DEBUG': 'cyan',
    'INFO': 'green',
    'WARNING': 'yellow',
    'ERROR': 'red',
    'CRITICAL': 'bold_red',
}

formatter = colorlog.ColoredFormatter(
    "%(log_color)s%(levelname)s:%(name)s:%(message)s (%(filename)s:%(lineno)d)",
    log_colors=log_colors
)

handler = logging.StreamHandler()
handler.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Set the logging level
logger.addHandler(handler)
logger.propagate = False  # Disable propagation to avoid duplicate log messages



class WikipediaService:
    """
    Service layer for WikipediaPage model operations.
    """
    logger = logger
    logging.basicConfig(level=logging.INFO)

    @staticmethod
    def create_page(title, language, views, event_code):
        """
        Create a new Wikipedia page entry.

        Parameters:
        title (str): The title of the Wikipedia page.
        language (str): The language of the Wikipedia page.
        views (int): The number of views for the Wikipedia page.
        event_code (str): The event code associated with the Wikipedia page.
        """
        page = WikipediaPage(title=title, language=language, views=views, event_code=event_code)
        WikipediaRepository.add(page)
        WikipediaService.logger.info(f"Created page: {title} in language: {language}")

    @staticmethod
    def delete_page(page_id):
        """
        Delete a Wikipedia page entry by its ID.

        Parameters:
        page_id (int): The ID of the Wikipedia page to delete.
        """
        page = WikipediaRepository.get_by_id(page_id)
        if page:
            WikipediaRepository.delete(page)
            WikipediaService.logger.info(f"Deleted page with ID: {page_id}")
        else:
            WikipediaService.logger.warning(f"Page with ID: {page_id} not found")

    @staticmethod
    def get_all_pages():
        """
        Get all Wikipedia page entries.

        Returns:
        list: List of all Wikipedia pages.
        """
        pages = WikipediaRepository.get_all()
        WikipediaService.logger.info(f"Retrieved {len(pages)} pages")
        return pages

    @staticmethod
    def get_page_by_title(title):
        """
        Get a Wikipedia page entry by its title.

        Parameters:
        title (str): The title of the Wikipedia page to retrieve.

        Returns:
        WikipediaPage: The Wikipedia page with the specified title.
        """
        page = WikipediaRepository.get_by_title(title)
        if page:
            WikipediaService.logger.info(f"Retrieved page: {title}")
        else:
            WikipediaService.logger.warning(f"Page with title: {title} not found")
        return page