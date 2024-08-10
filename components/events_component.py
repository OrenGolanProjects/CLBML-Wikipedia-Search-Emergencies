import json
from services.event_service import EventService

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



# Load default events from a JSON file
def load_default_events():
    logger.info(">> START:: load_default_events")

    event_filePath = 'files/events_default.json'
    with open(event_filePath, 'r', encoding='utf-8') as file:
        events_data = json.load(file)

    for event_data in events_data:
        existing_event = EventService.get_event_by_name(event_data['name'])
        if not existing_event:
            EventService.create_event(
                event_data['name'],
                event_data['language'],
                event_data['created_datetime'],
                event_data['event_code']
            )

    logger.info("Default events loaded successfully.")
    logger.info(">> END:: load_default_events")
