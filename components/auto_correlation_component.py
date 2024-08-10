from services.auto_correlation_service import AutoCorrelationService
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

def load_default_auto_correlation(app):
    logger.info(">> START:: load_default_auto_correlation")
    auto_correlation_service = AutoCorrelationService()
    wiki_traffic_service = WikiTrafficService()

    wiki_traffic_df = wiki_traffic_service.get_traffic_data_as_dataframe()
    auto_correlation_service.reset_directory()
    auto_correlation_service.auto_corr_check_directory_existence()
    auto_correlation_service.perform_auto_corr(wiki_traffic_df)

    logger.info("Default auto correlation results loaded successfully.")
    logger.info(">> END:: load_default_auto_correlation")
