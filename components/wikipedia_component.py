import json
from services.wikipedia_service import WikipediaService

def load_default_wikipedia_pages():
    print(">> START:: load_default_wikipedia_pages")
    with open('files/wikipedia_pages_default.json', 'r', encoding='utf-8') as file:
        pages_data = json.load(file)

    for page_data in pages_data:
        existing_page = WikipediaService.get_page_by_title(page_data['page_title'])
        if not existing_page:
            WikipediaService.create_page(
                page_data['page_title'],
                page_data['language'],
                page_data['views'],
                page_data['event_code']
            )

    print("Default Wikipedia pages loaded successfully.")
    print(">> END:: load_default_wikipedia_pages")