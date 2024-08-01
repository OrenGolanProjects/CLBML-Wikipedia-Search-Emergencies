import os
import itertools
import warnings
import pandas as pd
import shutil
import matplotlib.pyplot as plt

from statsmodels.tsa.arima.model import ARIMA

class ARIMAService:

    def __init__(self):
        self.figure_directory = 'static/arima_figures'
        self.csv_file_path = './files/arima_results.csv'
        self.check_and_create_figure_directory()

    def check_and_create_figure_directory(self):
        if os.path.exists(self.figure_directory):
            shutil.rmtree(self.figure_directory) # delete current directory
            print(f"=== Deleted directory: {self.figure_directory}")
        # Check if 'arima_figures' directory exists, create if not
        os.makedirs(self.figure_directory)
        print(f"Created directory: {self.figure_directory}")

    def find_best_arima_order(self,data, column):
        p = d = q = range(0, 3)
        pdq = list(itertools.product(p, d, q))

        best_aic = float("inf")
        best_pdq = None

        warnings.filterwarnings("ignore")

        for param in pdq:
            try:
                model = ARIMA(data[column], order=param)
                results = model.fit()
                if results.aic < best_aic:
                    best_aic = results.aic
                    best_pdq = param
            except:
                continue

        return best_pdq

    def train_arima_model(self,data, column, order):
        model = ARIMA(data[column], order=order)
        results = model.fit()
        return results

    def forecast_arima_model(self,results, steps):
        forecast = results.get_forecast(steps=steps)
        forecast_df = forecast.summary_frame()
        return forecast_df

    def run_arima_model(self, df, existing_figures, steps=7):
        print(">> START:: run_arima_model")
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
        print(">> END:: run_arima_model")
        return arima_results

    def arima_forecast(self, df, column_name, existing_figures, steps=7):
        print("===  START::  arima_forecast")
        filename = f'arima_{column_name}.png'
        # Ensure the DataFrame is sorted by date
        df = df.sort_values('date')

        # Set the date as the index
        df = df.set_index('date')

        # Make sure the index is a DatetimeIndex
        if not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.to_datetime(df.index)

        order = self.find_best_arima_order(df, column_name)
        results = self.train_arima_model(df, column_name, order)
        forecast_df = self.forecast_arima_model(results, steps)

        # Make sure the forecast index is a DatetimeIndex
        if not isinstance(forecast_df.index, pd.DatetimeIndex):
            forecast_df.index = pd.to_datetime(forecast_df.index)

        # Check if the figure already exists
        if filename not in existing_figures:
            # Generate plot
            plt.figure(figsize=(10, 6))
            plt.plot(df.index, df[column_name], label='Observed')
            plt.plot(forecast_df.index, forecast_df['mean'], label='Forecast')
            plt.fill_between(forecast_df.index, 
                                forecast_df['mean_ci_lower'],
                                forecast_df['mean_ci_upper'],
                                color='k', alpha=0.1)
            plt.xlabel('Date')
            plt.ylabel('Value')
            plt.title(f'ARIMA Forecast for {column_name}')
            plt.legend()

            plt.savefig(os.path.join(self.figure_directory, filename))
            plt.close()

        print("===  END::  arima_forecast")
        return forecast_df, None, filename

    def arima_save_to_csv(self, arima_results):
        print(">> START:: arima_save_to_csv")
        # Prepare a dictionary to collect data for saving
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

        # Create a DataFrame from the collected data
        df = pd.DataFrame(rows)

        # Define file path and ensure the directory exists
        os.makedirs(os.path.dirname(self.csv_file_path), exist_ok=True)

        # Save DataFrame to CSV
        df.to_csv(self.csv_file_path, index=False)
        print(f"ARIMA results saved to {self.csv_file_path}")
        print(">> END:: arima_save_to_csv")

    def load_arima_results(self):
        print(">> START:: load_arima_results")

        arima_results = {}
        figures_dir = self.figure_directory

        # Check if CSV file exists
        if os.path.exists(self.csv_file_path):
            # Load CSV into DataFrame
            df = pd.read_csv(self.csv_file_path, parse_dates=['Date'])

            # Check each column in the DataFrame
            for column_name in df['Column'].unique():
                # Filter the DataFrame for the current column
                column_df = df[df['Column'] == column_name]

                # Check if the corresponding figure exists
                filename = f'arima_{column_name}.png'
                figure_path = os.path.join(figures_dir, filename)

                if os.path.exists(figure_path):
                    # Reconstruct the forecast DataFrame for this column
                    forecast_df = column_df.set_index('Date')

                    # Add to the arima_results dictionary
                    arima_results[column_name] = {
                        'forecast': forecast_df,
                        'error': None,  # No error information in the CSV
                        'filename': filename
                    }
                else:
                    print(f"Figure for column {column_name} does not exist.")
        else:
            print(f"CSV file {self.csv_file_path} does not exist.")
            return None

        print(">> END:: load_arima_results")
        return arima_results
