import os
import shutil
import logging
import colorlog
import matplotlib
import matplotlib.pyplot as plt

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


class CrossCorrelationService:
    """
    Service for computing and visualizing cross-correlation matrices of data.
    """

    def __init__(self):
        """
        Initialize the CrossCorrelationService with directories for figures and CSV files.
        """
        self.csv_file_path = './files/cross_correlation.csv'

        self.logger = logger

    def perform_cross_corr(self, df):
        self.logger.info(">> START:: perform_cross_corr")

        if df.empty:
            self.logger.error("DataFrame is empty. No cross-correlation to compute.")
            self.logger.info(">> END:: perform_cross_corr")
            return pd.DataFrame()

        # Ensure 'date' column is set as index
        if 'date' in df.columns:
            df.set_index('date', inplace=True)

        try:
            # Group columns by subject
            subjects = {}
            for col in df.columns:
                if '_' in col:
                    language, subject = col.split('_', 1)
                    if subject not in subjects:
                        subjects[subject] = []
                    subjects[subject].append(col)
                else:
                    self.logger.warning(f"Column name '{col}' does not contain an underscore and will be skipped.")

            all_results = []

            # Compute cross-correlation for each group of subjects
            for subject, columns in subjects.items():
                subject_df = df[columns].copy()
                
                # Remove leading zeros and interpolate
                subject_df = subject_df.loc[(subject_df!=0).any(axis=1)].interpolate()
                
                # Normalize the data
                subject_df = (subject_df - subject_df.mean()) / subject_df.std()
                
                results = []
                for i, col1 in enumerate(columns):
                    for col2 in columns[i+1:]:
                        lag, corr = self.cross_correlation(subject_df[col1], subject_df[col2])
                        results.append({'subject': subject, 'Page 1': col1, 'Page 2': col2, 'lag': lag, 'correlation': f"{corr:.4f}"})
                
                all_results.extend(results)

            results_df = pd.DataFrame(all_results)

            self.logger.info(">> END:: perform_cross_corr")
            self.save_dataframe_to_csv(results_df, self.csv_file_path)
            return results_df

        except Exception as e:
            self.logger.error(f"Failed to compute cross-correlation: {e}")
            self.logger.info(">> END:: perform_cross_corr")
            return pd.DataFrame()

    def moving_average(self, series, window_size):
        """
        Apply a moving average filter to the series.

        :param series: Pandas Series to be smoothed.
        :param window_size: Size of the moving window.
        :return: Smoothed Pandas Series.
        """
        if window_size < 1:
            raise ValueError("Window size must be at least 1.")
        return series.rolling(window=window_size, center=True).mean()

    def cross_correlation(self, x, y, max_lag=None):
        """
        Compute the cross-correlation between two time series.
        
        :param x: First time series as a Pandas Series.
        :param y: Second time series as a Pandas Series.
        :param max_lag: Maximum lag to consider (default is None, which uses len(x)-1)
        :return: Tuple of (lag, correlation) at maximum correlation
        """
        x = x.dropna()
        y = y.dropna()
        
        if len(x) != len(y):
            min_len = min(len(x), len(y))
            x = x[-min_len:]
            y = y[-min_len:]
        
        if max_lag is None:
            max_lag = len(x) - 1
        
        correlations = [np.correlate(x, np.roll(y, shift))[0] for shift in range(-max_lag, max_lag+1)]
        correlations = np.array(correlations) / (np.std(x) * np.std(y) * len(x))
        
        max_corr_index = np.argmax(np.abs(correlations))
        max_corr = correlations[max_corr_index]
        lag = max_corr_index - max_lag
        
        return lag, max_corr

    def run_cross_correlation(self, df):
        """
        Check if figures exist, if not, perform cross-correlation and write results to a CSV file.
        
        :param df: DataFrame to be used for cross-correlation.
        :return: Dictionary of figures or result of perform_cross_corr.
        """
        self.logger.info(">> START:: check_and_perform_cross_corr")

        # Check if csv file exists
        if os.path.exists(self.csv_file_path):
            self.logger.info(f"CSV file already exists: {self.csv_file_path}")
            self.logger.info(">> END:: check_and_perform_cross_corr")
            return pd.read_csv(self.csv_file_path, index_col=0)

        self.logger.info(">> END:: check_and_perform_cross_corr")      
        return self.perform_cross_corr(df)

    def save_dataframe_to_csv(self, df, file_path):
        """
        Save the given DataFrame to a CSV file.

        :param df: DataFrame to be saved.
        :param file_path: Path to the CSV file.
        """
        self.logger.info(">> START:: save_dataframe_to_csv")
        try:
            df.to_csv(file_path, index=True, mode='w')
            self.logger.info(f"DataFrame successfully saved to {file_path}")
        except Exception as e:
            self.logger.error(f"Failed to save DataFrame to {file_path}. Reason: {e}")
        self.logger.info(">> END:: save_dataframe_to_csv")

