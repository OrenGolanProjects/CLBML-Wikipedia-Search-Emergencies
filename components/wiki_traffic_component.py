from services.wiki_traffic_service import WikiTrafficService

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

def load_wiki_traffic():
    logger.info(">> START:: load_wiki_traffic")
    wiki_traffic_service = WikiTrafficService()
    wiki_traffic_service.delete_csv_file()
    wiki_traffic_service.create_and_populate_wiki_traffic()

    logger.info("Wiki traffic data update process completed")
    logger.info(">> END:: load_wiki_traffic")
