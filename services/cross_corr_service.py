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
        self.figure_directory = 'static/cross_corr_figures'
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


    def cross_corr_check_directory_existence(self):
        """
        Ensure the cross-correlation directory exists.
        """
        self.logger.info(">> START:: cross_corr_check_directory_existence")
        os.makedirs(self.figure_directory, exist_ok=True)
        self.logger.info(f"Ensured directory exists: {self.figure_directory}")
        self.logger.info(">> END:: cross_corr_check_directory_existence")

    def perform_cross_corr(self, df):
        self.logger.info(">> START:: perform_cross_corr")

        if df.empty:
            self.logger.error("DataFrame is empty. No cross-correlation to compute.")
            self.logger.info(">> END:: perform_cross_corr")
            return {}

        # Ensure 'date' column is set as index
        if 'date' in df.columns:
            df.set_index('date', inplace=True)

        result_file_paths = {}

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

            # Compute cross-correlation for each group of subjects
            for subject, columns in subjects.items():
                # Extract columns for the subject
                subject_df = df[columns]
                
                # Handle NaN values by filling them with 0 or interpolating
                subject_df = subject_df.fillna(0)  # or use subject_df.interpolate() for interpolation

                # Calculate cross-correlation for each pair of columns
                results = []
                for i, col1 in enumerate(columns):
                    for col2 in columns[i+1:]:
                        corr = self.cross_correlation(subject_df[col1], subject_df[col2])
                        results.append({'column1': col1, 'column2': col2, 'correlation': corr})

                results_df = pd.DataFrame(results)

                # Find the highest cross-correlation
                highest_corr = results_df.loc[results_df['correlation'].idxmax()]

                # Plot all language variants for this subject
                fig, (ax, text_ax) = plt.subplots(2, 1, figsize=(12, 8), gridspec_kw={'height_ratios': [6, 1]})

                for col in columns:
                    ax.plot(subject_df.index, subject_df[col], label=col)

                ax.set_title(f"Cross-Correlation Analysis for {subject}")
                ax.set_xlabel("Date")
                ax.set_ylabel("Value")
                ax.legend()
                plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')

                # Remove axes from the text subplot
                text_ax.axis('off')

                # Add correlation result text under the figure
                result_text = (f"Highest Correlation:\n"
                            f"{highest_corr['column1']} and {highest_corr['column2']}\n"
                            f"Correlation: {highest_corr['correlation']:.2f}")
                text_ax.text(0.5, 0.5, result_text, fontsize=14, fontweight='bold', ha='center', va='center', bbox=dict(facecolor='#ff4136', edgecolor='#ddd', alpha=0.8))
                plt.tight_layout()

                filepath = f'cross_corr_{subject}.png'
                plt.savefig(os.path.join(self.figure_directory, filepath))
                plt.close()

                result_file_paths[subject] = {
                    'line_plot': filepath,
                    'correlations': results_df.to_dict('records'),
                    'highest_corr': {
                        'column1': highest_corr['column1'],
                        'column2': highest_corr['column2'],
                        'correlation': highest_corr['correlation']
                    }
                }

                self.logger.info(f"Cross-correlation analysis for {subject} completed. Line plot saved to {os.path.join(self.figure_directory, filepath)}")

            self.logger.info(">> END:: perform_cross_corr")
            return result_file_paths

        except Exception as e:
            self.logger.error(f"Failed to compute cross-correlation: {e}")
            self.logger.info(">> END:: perform_cross_corr")
            return result_file_paths

    def cross_correlation(self, x, y):
        # Remove NaN values
        x = x.dropna()
        y = y.dropna()

        # Ensure both series have the same length
        min_length = min(len(x), len(y))
        x = x[:min_length]
        y = y[:min_length]

        # Calculate cross-correlation
        corr = signal.correlate(x, y, mode='full', method='direct')
        return np.max(corr) / (np.std(x) * np.std(y) * len(x))
