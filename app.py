"""This is the main file for the Flask application. It contains the routes for the application and the main function to run the application."""

import os
import logging
import colorlog
import matplotlib.pyplot as plt

from flask import Flask, render_template, request, redirect, url_for
from dotenv import load_dotenv
from utils.database import init_db
from utils.exceptions import handle_exception

from services.event_service import EventService
from services.wikipedia_service import WikipediaService
from services.wiki_traffic_service import WikiTrafficService
from services.peaks_service import PeaksService
from services.arima_service import ARIMAService
from services.cross_corr_service import CrossCorrelationService
from services.auto_correlation_service import AutoCorrelationService

from components.update_check_component import has_updated_today, perform_updates

# Initialize logging with colorlog
log_colors = {
    'DEBUG': 'cyan',
    'INFO': 'green',
    'WARNING': 'yellow',
    'ERROR': 'red',
    'CRITICAL': 'bold_red',
}

formatter = colorlog.ColoredFormatter(
    "%(log_color)s%(levelname)s:%(name)s:%(message)s (%(filename)s:%(lineno)d)",
    log_colors=log_colors
)

handler = logging.StreamHandler()
handler.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Set the logging level
logger.addHandler(handler)
logger.propagate = False  # Disable propagation to avoid duplicate log messages

# Load environment variables from .env file
load_dotenv()

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

@app.teardown_appcontext
def cleanup_matplotlib(exception=None):
    """Close all Matplotlib figures at the end of each request."""
    plt.close('all')

@app.route('/')
def welcome():
    """Route for the welcome page."""
    return render_template('welcome.html')

@app.route('/events', methods=['GET', 'POST'])
def manage_events():
    """Route for managing events."""
    logger.info(">> START:: /events")
    if request.method == 'POST':
        event_name = request.form.get('name')
        event_language = request.form.get('language')
        created_datetime = request.form.get('created_datetime')
        event_code = request.form.get('event_code')
        EventService.create_event(event_name, event_language, created_datetime, event_code)
        logger.info(">> END:: /events")
        return redirect(url_for('manage_events'))
    events = EventService.get_all_events()
    logger.info(">> END:: /events")
    return render_template('events.html', events=events)

@app.route('/wikipedia', methods=['GET', 'POST'])
def manage_wikipedia_pages():
    logger.info(">> START:: /wikipedia")
    if request.method == 'POST':
        page_title = request.form.get('page_title')
        page_language = request.form.get('language')
        page_views = request.form.get('views')
        event_code = request.form.get('event_code')
        WikipediaService.create_page(page_title, page_language, page_views, event_code)
        logger.info(">> END:: /wikipedia")
        return redirect(url_for('manage_wikipedia_pages'))
    pages = WikipediaService.get_all_pages()
    logger.info(">> END:: /wikipedia")
    return render_template('wikipedia.html', pages=pages)

@app.route('/research', methods=['GET', 'POST'])
def research():
    logger.info(">> START:: /research")

    # Initialize instances of services
    wiki_traffic_service = WikiTrafficService()
    arima_service = ARIMAService()
    cross_corr_service = CrossCorrelationService()
    peaks_service = PeaksService()
    auto_corr_service = AutoCorrelationService()

    # Check if directories exist
    peaks_service.peaks_check_directory_existence()
    cross_corr_service.cross_corr_check_directory_existence()
    arima_service.arima_check_directory_existence()
    auto_corr_service.auto_corr_check_directory_existence()

    # Get traffic data from Wikipedia API
    merged_df = wiki_traffic_service.get_traffic_data_as_dataframe()
    logger.info("=== created merged_df.")

    # Extract settings from form if available
    if request.method == 'POST':
        peaks_toFind = request.form.get('peaks_toFind', type=int)
        days_to_autocorrelate = request.form.get('days_to_autocorrelate', type=int)
        arima_daysToForcast = request.form.get('days_to_forecast', type=int)

    # ========================================================
    # ================ PEAKS DETECTION =======================
    # ========================================================

    # Detect peaks, using existing figures if available
    peaks_results = peaks_service.detect_peaks(
        merged_df,
        peaks_toFind=peaks_toFind
    )



    # ========================================================
    # ================ AUTO-CORRELATION ======================
    # ========================================================
    auto_corr_results = auto_corr_service.perform_auto_corr(merged_df,days_to_autocorrelate=days_to_autocorrelate)

    # ========================================================
    # ================ CROSS-CORRELATION =====================
    # ========================================================
    cross_corr_results = cross_corr_service.perform_cross_corr(merged_df)

    # ========================================================
    # ================ ARIMA MODEL ===========================
    # ========================================================
    arima_results = arima_service.load_arima_results(app=app,arima_daysToForcast=arima_daysToForcast)

    logger.info("=== arima model done.")

    logger.info(">> END:: /research")
    return render_template('research.html', 
                        peaks_results=peaks_results, 
                        arima_results=arima_results, 
                        cross_corr_results=cross_corr_results,
                        auto_corr_results=auto_corr_results)

if __name__ == '__main__':
    app.run(debug=True)
