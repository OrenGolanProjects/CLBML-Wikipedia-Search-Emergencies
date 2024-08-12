import os
import logging
import colorlog
import matplotlib
import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import ccf
import numpy as np
from itertools import combinations
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

    # def perform_cross_corr(self, df):
    #     self.logger.info(">> START:: perform_cross_corr")

    #     if df.empty:
    #         self.logger.error("DataFrame is empty. No cross-correlation to compute.")
    #         self.logger.info(">> END:: perform_cross_corr")
    #         return pd.DataFrame()

    #     # Ensure 'date' column is set as index
    #     if 'date' in df.columns:
    #         df.set_index('date', inplace=True)

    #     try:
    #         # Group columns by subject
    #         subjects = {}
    #         for col in df.columns:
    #             if '_' in col:
    #                 language, subject = col.split('_', 1)
    #                 if subject not in subjects:
    #                     subjects[subject] = []
    #                 subjects[subject].append(col)
    #             else:
    #                 self.logger.warning(f"Column name '{col}' does not contain an underscore and will be skipped.")

    #         all_results = []

    #         # Compute cross-correlation for each group of subjects
    #         for subject, columns in subjects.items():
    #             subject_df = df[columns].copy()
                
    #             # Remove leading zeros and interpolate
    #             subject_df = subject_df.loc[(subject_df!=0).any(axis=1)].interpolate()
                
    #             # Normalize the data
    #             subject_df = (subject_df - subject_df.mean()) / subject_df.std()
                
    #             results = []
    #             for i, col1 in enumerate(columns):
    #                 for col2 in columns[i+1:]:
    #                     lag, corr = self.cross_correlation(subject_df[col1], subject_df[col2])
    #                     results.append({'subject': subject, 'Page 1': col1, 'Page 2': col2, 'lag': lag, 'correlation': f"{corr:.4f}"})
                
    #             all_results.extend(results)

    #         results_df = pd.DataFrame(all_results)

    #         self.logger.info(">> END:: perform_cross_corr")
    #         self.save_dataframe_to_csv(results_df, self.csv_file_path)
    #         return results_df

    #     except Exception as e:
    #         self.logger.error(f"Failed to compute cross-correlation: {e}")
    #         self.logger.info(">> END:: perform_cross_corr")
    #         return pd.DataFrame()


    # def run_cross_correlation(self, df):
    #     """
    #     Check if figures exist, if not, perform cross-correlation and write results to a CSV file.
        
    #     :param df: DataFrame to be used for cross-correlation.
    #     :return: Dictionary of figures or result of perform_cross_corr.
    #     """
    #     self.logger.info(">> START:: check_and_perform_cross_corr")

    #     # Check if csv file exists
    #     if os.path.exists(self.csv_file_path):
    #         self.logger.info(f"CSV file already exists: {self.csv_file_path}")
    #         self.logger.info(">> END:: check_and_perform_cross_corr")
    #         return pd.read_csv(self.csv_file_path, index_col=0)

    #     self.logger.info(">> END:: check_and_perform_cross_corr")  

    #     self.compute_cross_correlation(df)    # Return the result of perform_cross_corr
    #     return pd.dataFrame()   

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

    def cross_correlation_test(self, df, max_lag=10):
        cross_corr_results = pd.DataFrame(columns=["subject", "Page 1", "Page 2", "Best Lag", "Max Correlation"])

        for col1, col2 in combinations(df.columns, 2):
            # if first column is date then skip
            if col1 == 'date':
                continue
            # Calculate cross-correlation for all lags using ccf
            corr_values = ccf(df[col1].fillna(0), df[col2].fillna(0), adjusted=False)
            lags = np.arange(-max_lag, max_lag + 1)

            # Find the lag with the maximum absolute correlation
            max_corr_index = np.argmax(np.abs(corr_values[:2*max_lag+1]))
            max_corr = corr_values[max_corr_index]
            best_lag = lags[max_corr_index]

            # Assuming 'subject' is derived from the column names
            subject = f"{col1}-{col2}"

            # If max correlation is lower then 0.5 then skip
            if max_corr < 0.5:
                continue

            # Round max_corr to 2 decimal places
            max_corr = round(max_corr, 2)
             
            result_df = pd.DataFrame({
                "subject": [subject],
                "Page 1": [col1],
                "Page 2": [col2],
                "Best Lag": [best_lag],
                "Max Correlation": [max_corr]
            })

            cross_corr_results = pd.concat([cross_corr_results, result_df], ignore_index=True)

        return cross_corr_results.sort_values(by="Max Correlation", ascending=False).reset_index(drop=True)