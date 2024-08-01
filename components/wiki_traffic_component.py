from services.wiki_traffic_service import WikiTrafficService

def load_wiki_traffic():
    print(">> START:: load_wiki_traffic")
    wiki_traffic_service = WikiTrafficService()
    wiki_traffic_service.create_and_populate_wiki_traffic()

    print("Wiki traffic data update process completed")
    print(">> END:: load_wiki_traffic")
