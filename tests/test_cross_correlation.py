import os
import sys
import unittest
from unittest.mock import patch
import logging
from flask import Flask

# Ensure the parent directory is in sys.path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from dotenv import load_dotenv
from services.cross_corr_service import CrossCorrelationService
from services.wiki_traffic_service import WikiTrafficService
from utils.database import init_db

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TestCrossCorrelationService(unittest.TestCase):

    @patch('services.cross_corr_service.CrossCorrelationService.cross_corr_check_directory_existence')
    @patch('services.cross_corr_service.CrossCorrelationService.reset_directory')
    def test_cross_corr_service_sequence(self, mock_reset_directory, mock_check_directory):
        # Arrange

        # Load environment variables from .env file
        load_dotenv()

        # Create a Flask application
        app = Flask(__name__)
        # Use a single database URI
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URI']

        # Initialize the database
        with app.app_context():
            init_db(app)

        cross_corr_service = CrossCorrelationService()
        wiki_traffic_service = WikiTrafficService()

        with app.app_context():  # Use the application context
            logging.info("Get all traffic data as a DataFrame.")
            wiki_traffic_df = wiki_traffic_service.get_traffic_data_as_dataframe()

            logging.info("Reset the figure directory by deleting its contents.")
            cross_corr_service.reset_directory()

            logging.info("Checking directory existence.")
            cross_corr_service.cross_corr_check_directory_existence()

            logging.info("Performing cross correlation.")
            cross_corr_service.perform_cross_corr(wiki_traffic_df)

            # Assert
            logging.info("Asserting reset_directory was called once.")
            mock_reset_directory.assert_called_once()

            logging.info("Asserting cross_corr_check_directory_existence was called once.")
            mock_check_directory.assert_called_once()

if __name__ == '__main__':
    unittest.main(exit=False)
