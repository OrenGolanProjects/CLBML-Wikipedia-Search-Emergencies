import os
import json
from datetime import datetime
from utils.database import create_tables
from components.events_component import load_default_events
from components.wikipedia_component import load_default_wikipedia_pages
from components.wiki_traffic_component import load_wiki_traffic
from components.arima_component import load_default_arima
from components.peaks_component import reset_paeks


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


    def check_and_create_outliers_directory(self):
        # Define directory paths
        figures_dir = 'static/outliers_figures'

        # Check if 'arima_figures' directory exists, create if not
        if not os.path.exists(figures_dir):
            os.makedirs(figures_dir)
            print(f"Created directory: {figures_dir}")

def perform_updates(app):
    with app.app_context():
        create_tables(app)
        load_default_events()
        load_default_wikipedia_pages()
        load_wiki_traffic()
        reset_paeks(app)
        load_default_arima(app)
        update_log()
