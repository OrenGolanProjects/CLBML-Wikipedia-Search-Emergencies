import os
import warnings
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import logging
import colorlog
import numpy as np

from pmdarima import auto_arima
from statsmodels.tsa.arima.model import ARIMA
from services.wiki_traffic_service import WikiTrafficService
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error


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



class ARIMAService:
    def __init__(self):
        self.logger = logger

        self.figure_directory = 'static/arima_figures'
        self.csv_file_path = './files/arima_results.csv'
        self.wiki_traffic_service = WikiTrafficService()

    def arima_check_directory_existence(self):
        self.logger.info(">> START:: arima_check_directory_existence")
        os.makedirs(self.figure_directory, exist_ok=True)
        self.logger.info(">> END:: arima_check_directory_existence")

    def arima_save_to_csv(self, arima_results):
        self.logger.info(">> START:: arima_save_to_csv")
        rows = []
        for subject, arima_data_list in arima_results.items():
            for arima_data in arima_data_list:
                forecast = arima_data['forecast']
                date = arima_data['date']
                actual = arima_data['actual']
                error = arima_data['error']
                mae = arima_data['mae']
                rows.append({
                        'Subject': subject,
                        'Date': date,
                        'Forecast': forecast,
                        'Actual': actual,
                        'Error': error,
                        'MAE': mae
                    })

        df = pd.DataFrame(rows)
        os.makedirs(os.path.dirname(self.csv_file_path), exist_ok=True)
        df.to_csv(self.csv_file_path, index=False)
        self.logger.info(f"       ARIMA results saved to {self.csv_file_path}")
        self.logger.info(">> END:: arima_save_to_csv")

    def delete_csv_file(self):
        self.logger.info(">> START:: delete_csv_file")
        file_path = self.csv_file_path
        if os.path.exists(file_path):
            os.remove(file_path)
            self.logger.info(f"       File {file_path} has been deleted.")
        else:
            self.logger.warning(f"       No file found at {file_path}")
        self.logger.info(">> END:: delete_csv_file")

    def check_and_load_arima(self, app):
        arima_figures_dir = os.path.join(app.static_folder, 'arima_figures')
        os.makedirs(arima_figures_dir, exist_ok=True)
        
        try:
            arima_existing_figures = set(os.listdir(arima_figures_dir))
        except OSError as e:
            self.logger.error(f"Error accessing directory {arima_figures_dir}: {e}")
            arima_existing_figures = set()

        if arima_existing_figures:
            self.logger.info("       ARIMA figures already exist.")
        else:
            self.logger.info("       ARIMA figures directory is empty. Loading default ARIMA results.")
            try:
                self.load_arima_results(app,self.wiki_traffic_service.get_traffic_data_as_dataframe())
            except Exception as e:
                self.logger.error(f"Error running ARIMA model: {e}")

    def load_arima_results(self, app, merged_df):
        self.logger.info(">> START:: load_arima_results")
        
        # Store all results and figure filenames
        all_results = {}
        all_fig_filenames = []

        # Parse the date column correctly and set it as the index
        merged_df['date'] = pd.to_datetime(merged_df['date'], format='%Y-%m')  # Change 1
        merged_df.set_index('date', inplace=True)  # Change 2

        # Iterate over each column (time series) in the DataFrame
        for column_name in merged_df.columns:
            app.logger.info(f"Processing {column_name}")

            # Skip the 'date' column
            if column_name == 'date':
                continue

            # Drop rows with NaN values for the specific column
            series = merged_df[column_name].dropna()

            # Split the data into training and testing sets
            train_size = int(len(series) * 0.7)
            train_data, test_data = series.iloc[:train_size], series.iloc[train_size:]

            # Train the ARIMA model
            model = auto_arima(train_data, seasonal=False, trace=True, error_action='ignore', suppress_warnings=True)
            train_results = model.arima_res_

            # Initialize the results list
            results = []

            # Iteratively forecast and update the model

            for i in range(len(test_data)):
                # Forecast the next day
                forecast_result = model.predict(n_periods=1)
                
                # Check if the result is a Series or an array and extract the value accordingly
                if isinstance(forecast_result, pd.Series):
                    forecast = forecast_result.iloc[0]
                else:
                    forecast = forecast_result[0]

                actual = test_data.iloc[i]

                # Calculate the error
                error = abs(forecast - actual)
                mae = mean_absolute_error([actual], [forecast])

                # Store the result
                results.append({
                    'date': test_data.index[i],
                    'forecast': forecast,
                    'actual': actual,
                    'error': error,
                    'mae': mae
                })

                # Update the model with the actual value
                model.update([actual])

            # Ensure the lengths of results and test_data are the same
            if len(results) != len(test_data):
                app.logger.warning(f"Length mismatch for {column_name}: results={len(results)}, test_data={len(test_data)}")
                # Adjust the lengths if possible
                min_length = min(len(results), len(test_data))
                results = results[:min_length]
                test_data = test_data.iloc[:min_length]

            # Generate the forecast DataFrame
            forecast_df = pd.DataFrame({
                'mean': [r['forecast'] for r in results],
                'mean_ci_lower': [None] * len(results),  # Placeholder, real CI can be added if calculated
                'mean_ci_upper': [None] * len(results)   # Placeholder, real CI can be added if calculated
            }, index=[r['date'] for r in results])

            # Plotting
            fig, ax = plt.subplots(figsize=(25, 10))
            ax.plot(train_data.index, train_data, label='Training Data', color='#35424a', linestyle='-', marker='o', markersize=0)
            ax.plot(test_data.index, test_data, label='Test Data', color='#2ca02c', linestyle='--', marker='x', markersize=2)
            ax.plot(forecast_df.index, forecast_df['mean'], label='Forecast', color='#e8491d', linestyle='--', marker='s', markersize=2)
            
            # Only plot the confidence interval if it contains valid numeric data
            if forecast_df['mean_ci_lower'].notnull().any() and forecast_df['mean_ci_upper'].notnull().any():
                ax.fill_between(forecast_df.index, forecast_df['mean_ci_lower'], forecast_df['mean_ci_upper'], 
                                color='#e8491d', alpha=0.2, label='95% Confidence Interval')
            
            ax.set_xlabel('Date', fontsize=12, fontweight='bold', color='#333')
            ax.set_ylabel('Views', fontsize=12, fontweight='bold', color='#333')
            ax.set_title(f'ARIMA Forecast for {column_name}', fontsize=16, fontweight='bold', color='#35424a')
            
            # Format the x-axis to display dates correctly
            ax.xaxis.set_major_locator(mdates.MonthLocator())
            ax.xaxis.set_minor_locator(mdates.DayLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))  # Change 3
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right', color='#333')
            

            ax.grid(True, which='both', linestyle='--', linewidth=0.2, alpha=0.6, color='#ddd')
            ax.legend(loc='upper left', fontsize=12, frameon=True, framealpha=0.8, facecolor='#f4f4f4', edgecolor='#ddd')

            # Plot statistics
            aic = train_results.aic
            # RMSE calculation
            rmse = np.sqrt(mean_absolute_error(test_data, forecast_df['mean']))
            rmse_text = f'RMSE: {rmse:.4f}'
            formula_text = (
                f'ARIMA({model.order[0]},{model.order[1]},{model.order[2]}) >>>'
                f'P=({model.order[0]}, D={model.order[1]}, Q={model.order[2]})   '
                f'AIC: {aic:.2f}   '
                f'{rmse_text}'
            )
            ax.text(0.05, 0.05, formula_text, transform=ax.transAxes, fontsize=12, fontweight='bold', verticalalignment='bottom',
                    bbox=dict(facecolor='#ff4136', edgecolor='#ddd', alpha=0.8), color='#333')

            # Vertical line to separate training and forecast
            last_train_date = train_data.index[-1]
            ax.axvline(x=last_train_date, color='#ff4136', linestyle=':', linewidth=2, label='Forecast Start')
            ax.set_facecolor('#ffffff')
            fig.patch.set_facecolor('#f4f4f4')
            y_min, y_max = ax.get_ylim()
            ax.set_ylim(y_min - 0.1 * (y_max - y_min), y_max + 0.1 * (y_max - y_min))

            plt.tight_layout()

            # Save the figure
            filename = f'arima_forecast_{column_name}.png'
            plt.savefig(os.path.join(self.figure_directory, filename), dpi=300, bbox_inches='tight')
            plt.close(fig)

            app.logger.info(f"ARIMA forecast figure saved as {filename} for column: {column_name}")

            # Store results and filename
            all_results[column_name] = results
            all_fig_filenames.append(filename)

        # Save results to CSV
        self.arima_save_to_csv(all_results)

        self.logger.info(">> END:: load_arima_results")
        return all_results, all_fig_filenames
    
    def run_arima_model(self, app):
        """
        Check if figures exist, if not, perform ARIMA model.

        :param app: Application context.
        :return: Dictionary of figures or result of ARIMA model.
        """
        self.logger.info(">> START:: run_arima_model")

        # Check if CSV file exists
        csv_exists = os.path.exists(self.csv_file_path)

        # Check if figures directory exists and is not empty
        figures_exist = os.path.exists(self.figure_directory) and os.listdir(self.figure_directory)
        
        # split figures by "_"
        for figure in figures_exist:
            figure_split = figure.split("_")
            if len(figure_split) > 1:
                subject = figure_split[1].split(".")[0]

        if csv_exists and figures_exist:
            self.logger.info("CSV file and figures exist. Loading data into dictionary.")
            # Load CSV data into a DataFrame
            df = pd.read_csv(self.csv_file_path)
            arima_results = {}

            # Loop through the figures and create the dictionary
            for figure in figures_exist:

                figure_split = figure.split("_")
                if len(figure_split) > 1:
                    subject = figure_split[3].split(".")[0]


                    # initialize list that whill contain the figure data if it does not exist
                    if subject not in arima_results:
                        arima_results[subject] = []

                    # Check if the data for this subject exists in the DataFrame
                    if df[df['Subject'].str.contains(f'_{subject}')].empty:
                        self.logger.warning(f"No data found for subject: {subject}")
                        continue

                    # Extract the forecast data for this subject
                    group = df[df['Subject'].str.contains(f'_{subject}')]
                    forecast = group[['Date', 'Forecast', 'Actual','MAE']].to_dict(orient='records')

                    # append the figure filename and forecast into the list
                    arima_results[subject].append({
                        'filename': figure,
                        'forecast': forecast
                    })
            self.logger.info(">> END:: run_arima_model")

            return arima_results
        else:
            self.logger.info("CSV file or figures do not exist. Running load_arima_results.")
            # Run load_arima_results function
            merged_df = self.wiki_traffic_service.get_traffic_data_as_dataframe()
            self.load_arima_results(app, merged_df)

            self.logger.info(">> END:: run_arima_model")
            return self.run_arima_model(app)
        
