import os
import sys
import unittest
from unittest.mock import patch, MagicMock
import logging
from flask import Flask

# Ensure the parent directory is in sys.path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from dotenv import load_dotenv
from services.auto_correlation_service import AutoCorrelationService
from services.wiki_traffic_service import WikiTrafficService
from utils.database import init_db

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TestAutoCorrelationService(unittest.TestCase):

    @patch('services.auto_correlation_service.AutoCorrelationService.auto_corr_check_directory_existence')
    @patch('services.auto_correlation_service.AutoCorrelationService.reset_directory')
    @patch('services.auto_correlation_service.AutoCorrelationService.perform_auto_corr')
    @patch('services.wiki_traffic_service.WikiTrafficService.get_traffic_data_as_dataframe')
    def test_auto_corr_service_sequence(self, mock_get_traffic_data, mock_perform_auto_corr, mock_reset_directory, mock_check_directory):
        # Arrange
        load_dotenv()

        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI', 'sqlite:///test.db')

        with app.app_context():
            init_db(app)

            auto_corr_service = AutoCorrelationService()
            wiki_traffic_service = WikiTrafficService()

            # Mock the DataFrame return
            mock_df = MagicMock()
            mock_get_traffic_data.return_value = mock_df

            # Act
            logging.info("Get all traffic data as a DataFrame.")
            wiki_traffic_df = wiki_traffic_service.get_traffic_data_as_dataframe()

            logging.info("Reset the figure directory by deleting its contents.")
            auto_corr_service.reset_directory()

            logging.info("Checking directory existence.")
            auto_corr_service.auto_corr_check_directory_existence()

            logging.info("Performing auto correlation.")
            auto_corr_service.perform_auto_corr(wiki_traffic_df)

            # Assert
            logging.info("Asserting get_traffic_data_as_dataframe was called once.")
            mock_get_traffic_data.assert_called_once()

            logging.info("Asserting reset_directory was called once.")
            mock_reset_directory.assert_called_once()

            logging.info("Asserting auto_corr_check_directory_existence was called once.")
            mock_check_directory.assert_called_once()

            logging.info("Asserting perform_auto_corr was called once with the mock DataFrame.")
            mock_perform_auto_corr.assert_called_once_with(mock_df)

if __name__ == '__main__':
    unittest.main()