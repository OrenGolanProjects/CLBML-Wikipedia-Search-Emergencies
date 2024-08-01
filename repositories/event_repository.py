from models.event import Event
from utils.database import db

class EventRepository:
    @staticmethod
    def add(event):
        db.session.add(event)
        db.session.commit()

    @staticmethod
    def delete(event):
        db.session.delete(event)
        db.session.commit()

    @staticmethod
    def get_by_id(event_id):
        return Event.query.get(event_id)

    @staticmethod
    def get_all():
        return Event.query.all()

    @staticmethod
    def get_by_name(name):
        return Event.query.filter_by(name=name).first()

    @staticmethod
    def get_by_event_code(event_code):
        return Event.query.filter_by(event_code=event_code).first()
