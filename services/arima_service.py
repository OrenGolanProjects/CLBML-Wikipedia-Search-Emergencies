import os
import warnings
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import logging
import numpy as np

from pmdarima import auto_arima
from statsmodels.tsa.arima.model import ARIMA
from services.wiki_traffic_service import WikiTrafficService


class ARIMAService:
    """
    Service class for ARIMA model operations including training, forecasting, and saving results.
    """

    def __init__(self):
        """
        Initialize the ARIMAService with default directories and logger.
        """
        self.logger = logging.getLogger(__name__)
        self.figure_directory = 'static/arima_figures'
        self.csv_file_path = './files/arima_results.csv'
        self.wiki_traffic_service = WikiTrafficService()

    def arima_check_directory_existence(self):
        """
        Check if the figure directory exists, delete it if it does, and create a new one.
        """
        self.logger.info(">> START:: arima_check_directory_existence")
        os.makedirs(self.figure_directory, exist_ok=True)
        self.logger.info(">> END:: arima_check_directory_existence")

    def find_best_arima_order(self, data, column):
        """
        Find the best ARIMA order for the given data column using auto_arima.

        :param data: DataFrame containing the data.
        :param column: Column name to find the ARIMA order for.
        :return: Best ARIMA order.
        """
        self.logger.info(">> START:: find_best_arima_order")
        warnings.filterwarnings("ignore")

        # Check for NaN values and handle them
        if data[column].isna().any():
            self.logger.warning(f"       Column {column} contains NaN values. Removing leading NaNs.")
            # Remove leading NaNs
            data = data.loc[data[column].first_valid_index():]
            # Forward and backward fill remaining NaNs
            data[column] = data[column].fillna(method='ffill')
            data[column] = data[column].fillna(method='bfill')

        self.logger.info(f"       Finding best ARIMA order for column {column}")
        model = auto_arima(data[column], seasonal=False, stepwise=True, suppress_warnings=True)
        self.logger.info(">> END:: find_best_arima_order")
        return model.order

    def train_arima_model(self, data, column, order):
        """
        Train the ARIMA model with the given order on the specified data column.

        :param data: DataFrame containing the data.
        :param column: Column name to train the ARIMA model on.
        :param order: ARIMA order.
        :return: Trained ARIMA model results.
        """
        self.logger.info(">> START:: train_arima_model")
        model = ARIMA(data[column], order=order)
        results = model.fit()
        self.logger.info(">> END:: train_arima_model")
        return results

    def forecast_arima_model(self, results, steps):
        """
        Forecast future values using the trained ARIMA model.

        :param results: Trained ARIMA model results.
        :param steps: Number of steps to forecast.
        :return: DataFrame containing the forecasted values.
        """
        self.logger.info(">> START:: forecast_arima_model")
        forecast = results.get_forecast(steps=steps)
        forecast_df = forecast.summary_frame()
        self.logger.info(">> END:: forecast_arima_model")
        return forecast_df

    def run_arima_model(self, df, existing_figures, steps=7):
        """
        Run the ARIMA model on the given DataFrame and save the results.

        :param df: DataFrame containing the data.
        :param existing_figures: List of existing figure filenames.
        :param steps: Number of steps to forecast.
        :return: Dictionary containing the ARIMA results.
        """
        self.logger.info(">> START:: run_arima_model")
        arima_results = {}
        for column_name in df.columns:
            if column_name != 'date':
                forecast_df, error_message, filename = self.arima_forecast(
                    df=df,
                    column_name=column_name,
                    existing_figures=existing_figures,
                    steps=steps
                )
                arima_results[column_name] = {
                    'forecast': forecast_df,
                    'error': error_message,
                    'filename': filename
                }
        self.arima_save_to_csv(arima_results)
        self.logger.info(">> END:: run_arima_model")
        return arima_results

    def arima_forecast(self, df, column_name, existing_figures, steps=7):
        """
        Perform ARIMA forecasting for a specific column in the DataFrame.

        :param df: DataFrame containing the data.
        :param column_name: Column name to forecast.
        :param existing_figures: List of existing figure filenames.
        :param steps: Number of steps to forecast.
        :return: Tuple containing the forecast DataFrame, error message, and filename.
        """
        self.logger.info(f">> START:: arima_forecast for page: {column_name}")
        filename = f'arima_{column_name}.png'
        df = df.sort_values('date')
        df = df.set_index('date')

        if not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.to_datetime(df.index)

        order = self.find_best_arima_order(df, column_name)
        results = self.train_arima_model(df, column_name, order)
        forecast_df = self.forecast_arima_model(results, steps)

        if not isinstance(forecast_df.index, pd.DatetimeIndex):
            forecast_df.index = pd.to_datetime(forecast_df.index)

        # Plot the forecasted data
        if filename not in existing_figures:
            fig, ax = plt.subplots(figsize=(25, 10))

            # Plot observed data
            ax.plot(df.index, df[column_name], label='Observed', color='#35424a', linestyle='-', marker='o', markersize=0)

            # Plot forecasted data
            ax.plot(forecast_df.index, forecast_df['mean'], label='Forecast', color='#e8491d', linestyle='--', marker='s', markersize=2)

            # Fill between the confidence intervals
            ax.fill_between(forecast_df.index,forecast_df['mean_ci_lower'],forecast_df['mean_ci_upper'],color='#e8491d', alpha=0.2, label='95% Confidence Interval')

            # Customize the plot
            ax.set_xlabel('Date', fontsize=12, fontweight='bold', color='#333')
            ax.set_ylabel('Value', fontsize=12, fontweight='bold', color='#333')
            ax.set_title(f'ARIMA Forecast for {column_name} (Forcast {steps} Days)', fontsize=16, fontweight='bold', color='#35424a')

            # Improve x-axis
            ax.xaxis.set_major_locator(mdates.AutoDateLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right', color='#333')

            # Add grid lines
            ax.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.6, color='#ddd')

            # Customize legend
            ax.legend(loc='upper left', fontsize=12, frameon=True, framealpha=0.8, facecolor='#f4f4f4', edgecolor='#ddd')

            # Extract important details from the results
            aic = results.aic
            bic = results.bic
            log_likelihood = results.llf
            residual_std_error = np.sqrt(results.scale)

            # Add ARIMA formula text
            formula_text = (
                f'ARIMA({order[0]},{order[1]},{order[2]})   '
                f'Formula: $y_t = c + \\phi_1 y_{{t-1}} + \\theta_1 \\epsilon_{{t-1}}$   '
                f'AIC: {aic:.2f}, BIC: {bic:.2f}   '
                f'Log-Likelihood: {log_likelihood:.2f}   '
                f'Residual Std Error: {residual_std_error:.4f}'
            )
            ax.text(0.05, 0.05, formula_text, transform=ax.transAxes, fontsize=20, fontweight='bold', verticalalignment='bottom', bbox=dict(facecolor='#ff4136', edgecolor='#ddd', alpha=0.8), color='#333')

            # Add a vertical line to separate observed and forecasted data
            last_observed_date = df.index[-1]
            ax.axvline(x=last_observed_date, color='#ff4136', linestyle=':', linewidth=2, label='Forecast Start')

            # Set background color
            ax.set_facecolor('#ffffff')
            fig.patch.set_facecolor('#f4f4f4')

            # Adjust y-axis to show all data points
            y_min, y_max = ax.get_ylim()
            ax.set_ylim(y_min - 0.1 * (y_max - y_min), y_max + 0.1 * (y_max - y_min))

            # Adjust layout and save
            plt.tight_layout()
            plt.savefig(os.path.join(self.figure_directory, filename), dpi=300, bbox_inches='tight')
            plt.close(fig)

        self.logger.info(f">> END:: arima_forecast for page: {column_name}")
        return forecast_df, None, filename

    def arima_save_to_csv(self, arima_results):
        """
        Save the ARIMA results to a CSV file.

        :param arima_results: Dictionary containing the ARIMA results.
        """
        self.logger.info(">> START:: arima_save_to_csv")
        rows = []
        for column, result in arima_results.items():
            forecast = result['forecast']
            for index, row in forecast.iterrows():
                rows.append({
                    'Column': column,
                    'Date': index,
                    'Mean': row['mean'],
                    'Mean_CI_Lower': row['mean_ci_lower'],
                    'Mean_CI_Upper': row['mean_ci_upper']
                })

        df = pd.DataFrame(rows)
        os.makedirs(os.path.dirname(self.csv_file_path), exist_ok=True)
        df.to_csv(self.csv_file_path, index=False)
        self.logger.info(f"       ARIMA results saved to {self.csv_file_path}")
        self.logger.info(">> END:: arima_save_to_csv")

    def load_arima_results(self, app,arima_daysToForcast=1):
        """
        Load the ARIMA results from the CSV file.

        :return: Dictionary containing the ARIMA results.
        """
        self.logger.info(">> START:: load_arima_results")
        self.check_and_load_arima(app=app,arima_daysToForcast=arima_daysToForcast)

        arima_results = {}

        df = pd.read_csv(self.csv_file_path, parse_dates=['Date'])

        for column_name in df['Column'].unique():
            column_df = df[df['Column'] == column_name]
            filename = f'arima_{column_name}.png'
            figure_path = os.path.join(self.figure_directory, filename)

            if os.path.exists(figure_path):
                forecast_df = column_df.set_index('Date')
                arima_results[column_name] = {
                    'forecast': forecast_df,
                    'error': None,
                    'filename': filename
                }
            else:
                self.logger.warning(f"       Figure for column {filename} does not exist.")


        if arima_results:
            # Group images by subject
            subjects = {}
            for key, data in arima_results.items():
                parts = key.split('_', 1)
                if len(parts) > 1:
                    subject = parts[1]
                    if subject not in subjects:
                        subjects[subject] = []
                    subjects[subject].append(data)

        self.logger.info(">> END:: load_arima_results")
        return subjects

    def delete_csv_file(self):
        """
        Delete the CSV file containing the ARIMA results.
        """
        self.logger.info(">> START:: delete_csv_file")
        file_path = self.csv_file_path
        if os.path.exists(file_path):
            os.remove(file_path)
            self.logger.info(f"       File {file_path} has been deleted.")
        else:
            self.logger.warning(f"       No file found at {file_path}")
        self.logger.info(">> END:: delete_csv_file")

    def check_and_load_arima(self, app,arima_daysToForcast=1):
        """
        Check if there are files in the arima_figures directory.
        If the directory is empty, activate the load_default_arima function.
        
        :param app: Flask app instance
        """
        arima_figures_dir = os.path.join(app.static_folder, 'arima_figures')
        arima_existing_figures = set(os.listdir(arima_figures_dir)) if os.path.exists(arima_figures_dir) else set()

        if os.path.exists(arima_figures_dir) and os.listdir(arima_figures_dir):
            self.logger.info("       ARIMA figures already exist.")
        else:
            self.logger.info("       ARIMA figures directory is empty. Loading default ARIMA results.")
            self.run_arima_model(self.wiki_traffic_service.get_traffic_data_as_dataframe(), arima_existing_figures, arima_daysToForcast)
