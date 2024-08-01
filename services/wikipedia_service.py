from models.wikipedia_page import WikipediaPage
from repositories.wikipedia_repository import WikipediaRepository

class WikipediaService:
    """Service layer for WikipediaPage model operations."""

    @staticmethod
    def create_page(title, language, views,event_code):
        page = WikipediaPage(title=title, language=language, views=views,event_code=event_code)
        WikipediaRepository.add(page)

    @staticmethod
    def delete_page(page_id):
        page = WikipediaRepository.get_by_id(page_id)
        if page:
            WikipediaRepository.delete(page)

    @staticmethod
    def get_all_pages():
        return WikipediaRepository.get_all()

    @staticmethod
    def get_page_by_title(title):
        return WikipediaRepository.get_by_title(title)