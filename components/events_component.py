import json
from services.event_service import EventService

# Load default events from a JSON file
def load_default_events():
    print(">> START:: load_default_events")
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

    print("Default events loaded successfully.")
    print(">> END:: load_default_events")