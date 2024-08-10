from services.arima_service import ARIMAService
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


def load_default_arima(app):
    logger.info(">> START:: load_default_arima")
    arima_service = ARIMAService()
    wiki_traffic_service = WikiTrafficService()

    # Check for existing arima figures
    arima_service.arima_check_directory_existence()

    # arima_service.run_arima_model(wiki_traffic_service.get_traffic_data_as_dataframe(),arima_existing_figures,7)

    logger.info("Default arima results loaded successfully.")
    logger.info(">> END:: load_default_arima")
