from models.event import Event
from repositories.event_repository import EventRepository

class EventService:
    """Service layer for Event model operations."""

    @staticmethod
    def create_event(name, language, created_datetime,event_code):
        event = Event(name=name, language=language, created_datetime=created_datetime,event_code=event_code)
        EventRepository.add(event)

    @staticmethod
    def delete_event(event_id):
        event = EventRepository.get_by_id(event_id)
        if event:
            EventRepository.delete(event)

    @staticmethod
    def get_all_events():
        return EventRepository.get_all()

    @staticmethod
    def get_event_by_name(name):
        return EventRepository.get_by_name(name)
