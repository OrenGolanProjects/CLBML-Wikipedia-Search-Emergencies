from scipy.signal import find_peaks
import os
import logging
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Agg')

class PeaksService:
    """
    Service for detecting peaks in data and saving the results as figures and CSV files.
    """

    def __init__(self):
        """
        Initialize the PeaksService with directories for figures and CSV files.
        """
        self.figure_directory = 'static/peaks_figures'  # for images
        self.csv_file_path = './files/peaks_results.csv'  # for csv data
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)

    def peaks_check_directory_existence(self):
        """
        Ensure the figure directory exists.
        """
        self.logger.info(">> START:: peaks_check_directory_existence")
        os.makedirs(self.figure_directory, exist_ok=True)
        self.logger.info(f"Ensured directory exists: {self.figure_directory}")
        self.logger.info(">> END:: peaks_check_directory_existence")

    def load_peaks_figures(self, app):
        """
        Load and return the peaks figures.

        Parameters:
        app (Flask): The Flask application instance.

        Returns:
        set: A set of existing peaks figures filenames.
        """
        self.logger.info(">> START:: load_peaks_figures")
        peaks_figures_dir = os.path.join(app.static_folder, 'peaks_figures')
        peaks_existing_figures = set(os.listdir(peaks_figures_dir)) if os.path.exists(peaks_figures_dir) else set()
        self.logger.info(f"Loaded peaks figures from directory: {peaks_figures_dir}")
        self.logger.info(">> END:: load_peaks_figures")
        return peaks_existing_figures

    def detect_peaks(self, df, peaks_toFind=10):
        """
        Detect peaks in the dataframe and save figures.

        Parameters:
        df (pd.DataFrame): DataFrame containing the data.
        threshold (float, optional): Required threshold of peaks.
        distance (int, optional): Required minimal horizontal distance in samples between neighbouring peaks.
        prominence (float, optional): Required prominence of peaks.
        height (float, optional): Required height of peaks.
        width (float, optional): Required width of peaks.

        Returns:
        dict: Dictionary containing peaks information.
        """
        self.logger.info(">> START:: detect_peaks")
        peaks_dict = {}

        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])

        for column in df.columns:
            if column not in ['date', 'timestamp']:
                peak_filename = f'{column}_peaks.png'
                data = df[['date', column]].dropna()

                if data.empty:
                    continue

                data.set_index('date', inplace=True)
                data[column] = data[column].rolling(window=3, min_periods=1).mean()

                peaks_info = self.peaks_optimize(data[column], 2, 2, 100, 1, 1, peak_filename)
                if peaks_info:
                    peaks_dict[column] = peaks_info

        # Group images by subject
        subjects = {}
        for key, data in peaks_dict.items():
            parts = key.split('_', 1)
            if len(parts) > 1:
                subject = parts[1]
                if subject not in subjects:
                    subjects[subject] = []
                subjects[subject].append(data)

        # Write peaks to CSV
        self.write_peaks_to_csv(peaks_dict)

        self.logger.info(">> END:: detect_peaks")
        return subjects

    def peaks_optimize(self, data_column, threshold, distance, prominence, height, width, peak_filename):
        """
        Optimize peak detection by adjusting the distance and prominence parameters if the number of peaks exceeds 15.

        Parameters:
        data_column (pd.Series): The data column to detect peaks in.
        threshold (float, optional): Required threshold of peaks.
        distance (int, optional): Required minimal horizontal distance in samples between neighbouring peaks.
        prominence (float, optional): Required prominence of peaks.
        height (float, optional): Required height of peaks.
        width (float, optional): Required width of peaks.
        peak_filename (str): The filename to save the peak figure.

        Returns:
        dict: Dictionary containing peaks information.
        """
        peaks, properties = find_peaks(
            data_column,
            threshold=threshold,
            distance=distance,
            prominence=prominence,
            height=height,
            width=width
        )

        # If there are more than 15 peaks, increment the distance and prominence and run find_peaks again
        if len(peaks) > 15:
            initial_distance = distance if distance is not None else 1
            initial_prominence = prominence if prominence is not None else 0
            while len(peaks) > 15:
                initial_distance += 1
                initial_prominence += 20
                peaks, properties = find_peaks(
                    data_column,
                    threshold=threshold,
                    distance=initial_distance,
                    prominence=initial_prominence,
                    height=height,
                    width=width
                )

        # Save the figure if peaks are detected
        if len(peaks) > 0:
            plt.figure(figsize=(20, 6))
            plt.plot(data_column.index, data_column, label=peak_filename)
            plt.plot(data_column.index[peaks], data_column.iloc[peaks], 'o')

            # Annotate the peaks with their dates, alternating positions to avoid overlap
            for i, peak in enumerate(peaks):
                offset = 10 if i % 2 == 0 else -10  # Increased the offset values
                plt.annotate(data_column.index[peak].strftime('%Y-%m-%d'),
                            (data_column.index[peak], data_column.iloc[peak]),
                            textcoords="offset points",
                            xytext=(0, offset),
                            ha='center',
                            fontsize=10,  # Customize the font size here
                            color='green',  # Customize the color here
                            fontweight='bold')

            plt.title(f'Peaks in {peak_filename}')
            plt.legend()
            plt.savefig(os.path.join(self.figure_directory, peak_filename))
            plt.close()

        else:
            self.logger.warning("No peaks detected.")

        avg_distance = None
        if len(peaks) > 1:
            peak_distances = data_column.index[peaks].to_series().diff().dropna().dt.total_seconds()
            avg_distance = peak_distances.mean()

        return {
            'dates': data_column.index[peaks].strftime('%Y-%m-%d').tolist(),
            'values': data_column.iloc[peaks].tolist(),
            'filename': peak_filename,
            'avg_distance': avg_distance,
            'avg_prominence': properties['prominences'].mean() if 'prominences' in properties else None
        }

    def write_peaks_to_csv(self, peaks_dict):
        """
        Write the peaks information to a CSV file.

        Parameters:
        peaks_dict (dict): Dictionary containing peaks information.
        """
        self.logger.info(">> START:: write_peaks_to_csv")
        rows = []
        for column, peaks_info in peaks_dict.items():
            for i, date in enumerate(peaks_info['dates']):
                rows.append({
                    'name': column,
                    'date': date,
                    'traffic_value': peaks_info['values'][i]
                })

        df = pd.DataFrame(rows)
        df.to_csv(self.csv_file_path, index=False, mode='w')  # 'w' mode to overwrite the file if it exists
        self.logger.info(f"Peaks results written to CSV file: {self.csv_file_path}")
        self.logger.info(">> END:: write_peaks_to_csv")
