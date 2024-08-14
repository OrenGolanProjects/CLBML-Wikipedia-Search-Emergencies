import json
from services.wikipedia_service import WikipediaService

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

def load_default_wikipedia_pages():
    logger.info(">> START:: load_default_wikipedia_pages")
    with open('files/wikipedia_pages_default.json', 'r', encoding='utf-8') as file:
        pages_data = json.load(file)

    for page_data in pages_data:
        existing_page = WikipediaService.get_page_by_title(page_data['page_title'])
        if not existing_page:
            WikipediaService.create_page(
                page_data['page_title'],
                page_data['language'],
                page_data['views'],
                page_data['event_code'],
                page_data['url']
            )

    logger.info("Default Wikipedia pages loaded successfully.")
    logger.info(">> END:: load_default_wikipedia_pages")