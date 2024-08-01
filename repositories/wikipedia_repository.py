from models.wikipedia_page import WikipediaPage
from utils.database import db

class WikipediaRepository:
    @staticmethod
    def add(page):
        db.session.add(page)
        db.session.commit()

    @staticmethod
    def delete(page):
        db.session.delete(page)
        db.session.commit()

    @staticmethod
    def get_by_id(page_id):
        return WikipediaPage.query.get(page_id)

    @staticmethod
    def get_all():
        return WikipediaPage.query.all()

    @staticmethod
    def get_by_title(title):
        return WikipediaPage.query.filter_by(title=title).first()

    @staticmethod
    def get_by_event_code(event_code):
        return WikipediaPage.query.filter_by(event_code=event_code).first()