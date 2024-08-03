import logging
from models.event import Event
from repositories.event_repository import EventRepository

class EventService:
    """Service layer for Event model operations."""

    logger = logging.getLogger(__name__)

    @staticmethod
    def create_event(name, language, created_datetime, event_code):
        """
        Create a new event and add it to the repository.

        :param name: Name of the event.
        :param language: Language of the event.
        :param created_datetime: Datetime when the event was created.
        :param event_code: Unique code for the event.
        """
        EventService.logger.info(">> START:: create_event")
        event = Event(name=name, language=language, created_datetime=created_datetime, event_code=event_code)
        EventRepository.add(event)
        EventService.logger.info(">> END:: create_event")

    @staticmethod
    def delete_event(event_id):
        """
        Delete an event from the repository by its ID.

        :param event_id: ID of the event to be deleted.
        """
        EventService.logger.info(">> START:: delete_event")
        event = EventRepository.get_by_id(event_id)
        if event:
            EventRepository.delete(event)
            EventService.logger.info(f"       Event with ID {event_id} deleted.")
        else:
            EventService.logger.warning(f"       Event with ID {event_id} not found.")
        EventService.logger.info(">> END:: delete_event")

    @staticmethod
    def get_all_events():
        """
        Retrieve all events from the repository.

        :return: List of all events.
        """
        EventService.logger.info(">> START:: get_all_events")
        events = EventRepository.get_all()
        EventService.logger.info(">> END:: get_all_events")
        return events

    @staticmethod
    def get_event_by_name(name):
        """
        Retrieve an event from the repository by its name.

        :param name: Name of the event to retrieve.
        :return: Event object if found, else None.
        """
        EventService.logger.info(">> START:: get_event_by_name")
        event = EventRepository.get_by_name(name)
        if event:
            EventService.logger.info(f"       Event with name {name} found.")
        else:
            EventService.logger.warning(f"       Event with name {name} not found.")
        EventService.logger.info(">> END:: get_event_by_name")
        return event
