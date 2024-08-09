import os
import json

from datetime import datetime
from utils.database import create_tables

from components.events_component import load_default_events
from components.wikipedia_component import load_default_wikipedia_pages
from components.wiki_traffic_component import load_wiki_traffic
from components.arima_component import load_default_arima
from components.peaks_component import reset_paeks
from components.auto_correlation_component import load_default_auto_correlation

from services.reset_service import ResetService


UPDATE_LOG_FILE = 'update_log.json'

def has_updated_today():
    if os.path.exists(UPDATE_LOG_FILE):
        with open(UPDATE_LOG_FILE, 'r') as file:
            data = json.load(file)
            last_update = data.get('last_update')
            if last_update:
                last_update_date = datetime.strptime(last_update, '%Y-%m-%d').date()
                if last_update_date == datetime.today().date():
                    return True
    return False

def update_log():
    with open(UPDATE_LOG_FILE, 'w') as file:
        data = {'last_update': datetime.today().strftime('%Y-%m-%d')}
        json.dump(data, file)

def perform_updates(app):
    reset_service = ResetService()
    reset_service.remove_files_and_directories()
    reset_service.create_directories()

    with app.app_context():
        create_tables(app)
        load_default_events()
        load_default_wikipedia_pages()
        load_wiki_traffic()
        reset_paeks(app)
        load_default_auto_correlation(app)
        load_default_arima(app)
        update_log()
