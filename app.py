
import os
import logging
import matplotlib.pyplot as plt

from flask import Flask,render_template, request, redirect, url_for
from dotenv import load_dotenv
from utils.database import init_db
from utils.exceptions import handle_exception

from services.event_service import EventService
from services.wikipedia_service import WikipediaService
from services.wiki_traffic_service import WikiTrafficService
from services.peaks_service import PeaksService
from services.arima_service import ARIMAService

from components.update_check_component import has_updated_today, perform_updates

# Load environment variables from .env file
load_dotenv()

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Use a single database URI
try:
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URI']
except KeyError:
    logger.error("DATABASE_URI environment variable not set")
    raise

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.environ.get('SQLALCHEMY_TRACK_MODIFICATIONS', 'False').lower() == 'true'

# Initialize the database
try:
    init_db(app)
except Exception as e:
    logger.error(f"Failed to initialize the database: {e}")
    raise


# Check for updates and perform if necessary
try:
    if not has_updated_today():
        perform_updates(app)
except Exception as e:
    logger.error(f"Failed to perform updates: {e}")

app.register_error_handler(Exception, handle_exception)
obj_peaksService = PeaksService()


@app.teardown_appcontext
def cleanup_matplotlib(exception=None):
    plt.close('all')

@app.route('/')
def welcome():
    return render_template('welcome.html')

@app.route('/events', methods=['GET', 'POST'])
def manage_events():
    if request.method == 'POST':
        event_name = request.form.get('name')
        event_language = request.form.get('language')
        created_datetime = request.form.get('created_datetime')
        event_code = request.form.get('event_code')
        EventService.create_event(event_name, event_language, created_datetime, event_code)
        return redirect(url_for('manage_events'))
    events = EventService.get_all_events()
    return render_template('events.html', events=events)

@app.route('/wikipedia', methods=['GET', 'POST'])
def manage_wikipedia_pages():
    if request.method == 'POST':
        page_title = request.form.get('page_title')
        page_language = request.form.get('language')
        page_views = request.form.get('views')
        event_code = request.form.get('event_code')
        WikipediaService.create_page(page_title, page_language, page_views, event_code)
        return redirect(url_for('manage_wikipedia_pages'))
    pages = WikipediaService.get_all_pages()
    return render_template('wikipedia.html', pages=pages)

@app.route('/research', methods=['GET', 'POST'])
def research():
    print(">> START::/research route done.")

    wiki_traffic_service = WikiTrafficService()
    merged_df = wiki_traffic_service.get_traffic_data_as_dataframe()
    print("===  created merged_df.")

    obj_peaksService.peaks_check_and_create_figure_directory()

    # Extract settings from form
    if request.method == 'POST':
        threshold = request.form.get('threshold', type=int)
        distance = request.form.get('distance', type=int)
        prominence = request.form.get('prominence', type=int)
        height = request.form.get('height', type=int)
        width = request.form.get('width', type=int)
    else:
        threshold = 2
        distance = 2
        prominence = 100
        height = 1
        width = 1


    # Detect peaks, using existing figures if available
    peaks_results = obj_peaksService.detect_peaks(
        merged_df, 
        threshold=threshold, 
        distance=distance, 
        prominence=prominence, 
        height=height, 
        width=width
    )

    # Read traffic data from CSV
    merged_df = wiki_traffic_service.read_traffic_data_from_csv()

    # Create an instance of ARIMAService
    arima_service = ARIMAService()
    # Run ARIMA model analysis for all events
    arima_results = arima_service.load_arima_results()

    print("=== arima model done.")
    print(">> END::/research rout")
    return render_template('research.html', peaks_results=peaks_results, arima_results=arima_results)


if __name__ == '__main__':
    app.run(debug=False)
