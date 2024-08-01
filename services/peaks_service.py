import matplotlib.pyplot as plt
from scipy.signal import find_peaks

import shutil
import os
import pandas as pd
import matplotlib
matplotlib.use('Agg')


class PeaksService:

    def __init__(self):
        self.figure_directory = 'static/peaks_figures' # for images
        self.csv_file_path = './files/peaks_results.csv' # for csv data

    def peaks_check_and_create_figure_directory(self):
        if os.path.exists(self.figure_directory):
            shutil.rmtree(self.figure_directory) # delete current directory
            print(f"=== Deleted directory: {self.figure_directory}")
        os.makedirs(self.figure_directory) # create the directory
        print(f"=== Created directory: {self.figure_directory}")

    def detect_peaks(self,df, existing_figures):

        peaks_dict = {}
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])

        for column in df.columns:
            print(f"page: {column}, {column not in ['date', 'timestamp']}")

            if column not in ['date', 'timestamp']:
                peak_filename = f'{column}_peaks.png'

                data = df[['date', column]].dropna()
                if data.empty:
                    continue

                data.set_index('date', inplace=True)

                # Optional: Smoothing the data to reduce noise
                data[column] = data[column].rolling(window=3, min_periods=1).mean()

                # Peak detection using scipy's find_peaks with adjusted parameters
                peak_indices, properties = find_peaks(
                    data[column], 
                    height=1,  # Increase to filter out smaller peaks
                    distance=2,  # Increase to ensure peaks are further apart
                    prominence=100,  # Increase to ensure peaks are more prominent
                    width=1  # Minimum width of peaks
                )

                # Check if the peak figure already exists
                if peak_filename not in existing_figures:
                    plt.figure(figsize=(20, 8))
                    plt.plot(data.index, data[column], label='Data')
                    plt.scatter(data.index[peak_indices], data[column].iloc[peak_indices], color='green', label='Peaks')
                    plt.xlabel('Date')
                    plt.ylabel(column)
                    plt.title(f'Peaks in {column}')
                    plt.legend()
                    plt.savefig(f'{self.figure_directory}/{peak_filename}')
                    plt.close()


                print(f"=== Peak length: {len(peak_indices)} for page: {column}")
                # Calculate average distance between peaks
                if len(peak_indices) > 1:
                    peak_distances = data.index[peak_indices].to_series().diff().dropna().dt.total_seconds()
                    avg_distance = peak_distances.mean()
                else:
                    avg_distance = None

                peaks_dict[column] = {
                    'dates': data.index[peak_indices].strftime('%Y-%m-%d').tolist(),
                    'values': data[column].iloc[peak_indices].tolist(),
                    'filename': peak_filename,
                    'avg_distance': avg_distance,
                    'avg_prominence': properties['prominences'].mean() if 'prominences' in properties else None
                }

        return peaks_dict
