import os
import shutil
import logging
import colorlog
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns

import numpy as np
from scipy import signal
import pandas as pd

matplotlib.use('Agg')


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

class AutoCorrelationService:
    """
    Service for computing and visualizing auto-correlation of data.
    """

    def __init__(self):
        """
        Initialize the AutoCorrelationService with directories for figures.
        """
        self.figure_directory = 'static/auto_corr_figures'
        self.logger = logger

    def reset_directory(self):
        """
        Reset the figure directory by deleting its contents.
        """
        self.logger.info(">> START:: reset_directory")
        self.logger.info(f"Resetting directory: {self.figure_directory}")
        if os.path.exists(self.figure_directory):
            for filename in os.listdir(self.figure_directory):
                file_path = os.path.join(self.figure_directory, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    self.logger.error(f"Failed to delete {file_path}. Reason: {e}")
        self.logger.info(f"Directory reset: {self.figure_directory}")
        self.logger.info(">> END:: reset_directory")

    def auto_corr_check_directory_existence(self):
        """
        Ensure the auto-correlation directory exists.
        """
        self.logger.info(">> START:: auto_corr_check_directory_existence")
        os.makedirs(self.figure_directory, exist_ok=True)
        self.logger.info(f"Ensured directory exists: {self.figure_directory}")
        self.logger.info(">> END:: auto_corr_check_directory_existence")

    def perform_auto_corr(self, df, days_to_autocorrelate=30):
        self.logger.info(">> START:: perform_auto_corr")

        if df.empty:
            self.logger.error("DataFrame is empty. No auto-correlation to compute.")
            self.logger.info(">> END:: perform_auto_corr")
            return {}

        # Ensure 'date' column is set as index
        if 'date' in df.columns:
            df.set_index('date', inplace=True)

        result_file_paths = {}

        try:
            for col in df.columns:
                series = df[col]

                # Handle NaN values by filling them with 0 or interpolating
                series = series.fillna(0)  # or use series.interpolate() for interpolation

                # Calculate auto-correlation
                autocorr = self.auto_correlation(series, days_to_autocorrelate=days_to_autocorrelate)

                # Plot the auto-correlation
                plt.figure(figsize=(12, 6))
                plt.acorr(series, maxlags=days_to_autocorrelate, color='blue', alpha=1)
                plt.title(f"Auto-correlation for {col} (Last \u00B1{days_to_autocorrelate} Days)")
                plt.xlabel("Lag")
                plt.ylabel("Auto-correlation")
                plt.tight_layout()

                filepath = f'auto_corr_{col}.png'
                plt.savefig(os.path.join(self.figure_directory, filepath))
                plt.close()
                result_file_paths[col] = {
                    'auto_corr_plot': filepath,
                    'auto_correlation': autocorr
                }

                self.logger.info(f"Auto-correlation analysis for {col} completed. Plot saved to {os.path.join(self.figure_directory, filepath)}")

            # Group images by subject
            subjects = {}
            for key, data in result_file_paths.items():
                parts = key.split('_', 1)
                if len(parts) > 1:
                    subject = parts[1]
                    if subject not in subjects:
                        subjects[subject] = []
                    subjects[subject].append(data)

            self.logger.info(">> END:: perform_auto_corr")
            return subjects

        except Exception as e:
            self.logger.error(f"Failed to compute auto-correlation: {e}")
            self.logger.info(">> END:: perform_auto_corr")
            return result_file_paths

    def auto_correlation(self, series, days_to_autocorrelate=30):
        # Remove NaN values
        series = series.dropna()

        # Adjust series to consider only the last 40 days
        if days_to_autocorrelate < len(series):
            series = series[-days_to_autocorrelate:]

        # Calculate auto-correlation
        autocorr = np.correlate(series, series, mode='full')
        return autocorr[autocorr.size // 2:] / (np.std(series) * len(series))

    def run_auto_cross_correlation(self, df):
        """
        Check if figures exist, if not, perform auto-correlation.
        
        :param df: DataFrame to be used for auto-correlation.
        :param days_to_autocorrelate: Number of days to auto-correlate.
        :return: Dictionary of figures or result of perform_auto_corr.
        """
        self.logger.info(">> START:: run_auto_cross_correlation")
        
        # Check if the figure directory exists and contains files
        if os.path.exists(self.figure_directory) and os.listdir(self.figure_directory):
            self.logger.info("Figures already exist. Returning existing figures.")
            figures = {}
            for f in os.listdir(self.figure_directory):
                if f.endswith('.png'):
                    subject = f.split('_')[3].split('.')[0]  # Assuming the filename format is 'auto_corr_{col}.png'
                    if subject not in figures:
                        figures[subject] = []
                    figures[subject].append({
                        'auto_corr_plot': f
                    })
            self.logger.info(">> END:: run_auto_cross_correlation")
            return figures
        
        # If figures do not exist, perform auto-correlation
        self.logger.info("Figures do not exist. Performing auto-correlation.")
        result = self.perform_auto_corr(df, 30)
        self.logger.info(">> END:: run_auto_cross_correlation")
        return result
