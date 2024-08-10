from scipy.signal import find_peaks
import os
import logging
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Agg')


import colorlog

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
        self.logger = logger
        logging.basicConfig(level=logging.INFO)

    def peaks_check_directory_existence(self):
        self.logger.info(">> START:: peaks_check_directory_existence")
        os.makedirs(self.figure_directory, exist_ok=True)
        self.logger.info(f"Ensured directory exists: {self.figure_directory}")
        self.logger.info(">> END:: peaks_check_directory_existence")

    def load_peaks_figures(self, app):
        self.logger.info(">> START:: load_peaks_figures")
        peaks_figures_dir = os.path.join(app.static_folder, 'peaks_figures')
        peaks_existing_figures = set(os.listdir(peaks_figures_dir)) if os.path.exists(peaks_figures_dir) else set()
        self.logger.info(f"Loaded peaks figures from directory: {peaks_figures_dir}")
        self.logger.info(">> END:: load_peaks_figures")
        return peaks_existing_figures

    def detect_peaks(self, df, peaks_toFind=10):
        self.logger.info(">> START:: detect_peaks")
        peaks_dict = {}

        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)

        for column in df.columns:
            if column != 'date':
                event_name, language = self.parse_column_name(column)
                peak_filename = f'peaks_{language}_{event_name}.png'
                data = df[column].dropna()

                if data.empty:
                    continue

                data = data.rolling(window=3, min_periods=1).mean()
                normalized_data = self.oneP(data)

                peaks_info = self.peaks_optimize(normalized_data, event_name, language, peak_filename, peaks_toFind)
                if peaks_info:
                    peaks_dict[column] = peaks_info

        # Group images by event
        events = {}
        for key, data in peaks_dict.items():
            event_name, _ = self.parse_column_name(key)
            if event_name not in events:
                events[event_name] = []
            events[event_name].append(data)

        # Write peaks to CSV
        self.write_peaks_to_csv(peaks_dict)

        self.logger.info(">> END:: detect_peaks")
        return events

    def parse_column_name(self, column_name):
        parts = column_name.split('_', 1)
        return parts[1], parts[0] if len(parts) > 1 else (column_name, 'unknown')

    # Modified oneP method
    def oneP(self, data):
        return (data - data.mean()) / data.std()  # Changed to z-score normalization

    def peaks_optimize(self, data_column, event_name, language, peak_filename, peaks_toFind=10):
        self.logger.info(f">> START:: peaks_optimize for {event_name} ({language})")
        
        initial_distance = max(len(data_column) // 20, 1)  # Start with 5% of data length, minimum 1
        initial_prominence = 0.5  # Increased initial prominence
        
        while True:
            peaks, properties = find_peaks(
                data_column,
                distance=initial_distance,
                prominence=initial_prominence,
            )
            
            if len(peaks) <= peaks_toFind:  # Added upper limit for prominence
                break
            
            initial_distance = int(initial_distance * 1.01)
            initial_prominence *= 1.02 

        # Save the figure if peaks are detected
        if len(peaks) > 0:
            plt.figure(figsize=(20, 6))
            plt.plot(data_column.index, data_column, label=f'{event_name} ({language})', linewidth=0.2)  # Set linewidth to 0.2
            plt.plot(data_column.index[peaks], data_column.iloc[peaks], 'o', markersize=4)  # Optionally, adjust marker size

            for i, peak in enumerate(peaks):
                offset = 10 if i % 2 == 0 else -10
                plt.annotate(data_column.index[peak].strftime('%Y-%m-%d'),
                            (data_column.index[peak], data_column.iloc[peak]),
                            textcoords="offset points",
                            xytext=(0, offset),
                            ha='center',
                            fontsize=10,
                            color='green',
                            fontweight='bold')

            plt.title(f'Peaks in {event_name} ({language})')
            plt.legend()
            plt.savefig(os.path.join(self.figure_directory, peak_filename))
            plt.close()

        else:
            self.logger.warning(f"No peaks detected for {event_name} ({language}).")

        avg_distance = None
        if len(peaks) > 1:
            peak_distances = data_column.index[peaks].to_series().diff().dropna().dt.total_seconds()
            avg_distance = peak_distances.mean()

        return {
            'dates': data_column.index[peaks].strftime('%Y-%m-%d').tolist(),
            'values': data_column.iloc[peaks].tolist(),
            'filename': peak_filename,
            'avg_distance': avg_distance,
            'avg_prominence': properties['prominences'].mean() if 'prominences' in properties else None,
            'language': language,
            'event_name': event_name
        }

    def write_peaks_to_csv(self, peaks_dict):
        self.logger.info(">> START:: write_peaks_to_csv")
        rows = []
        for column, peaks_info in peaks_dict.items():
            for i, date in enumerate(peaks_info['dates']):
                rows.append({
                    'event_name': peaks_info['event_name'],
                    'language': peaks_info['language'],
                    'date': date,
                    'traffic_value': peaks_info['values'][i]
                })

        df = pd.DataFrame(rows)
        df.to_csv(self.csv_file_path, index=False, mode='w')
        self.logger.info(f"Peaks results written to CSV file: {self.csv_file_path}")
        self.logger.info(">> END:: write_peaks_to_csv")

    def run_peak_detection(self, df, peaks_toFind=5):
        """
        Check if figures exist, if not, perform peak detection.
        
        :param df: DataFrame to be used for peak detection.
        :param peaks_toFind: Number of peaks to find.
        :return: Dictionary of figures or result of detect_peaks.
        """
        self.logger.info(">> START:: run_peak_detection")
        
        # Check if the figure directory exists and contains files
        if os.path.exists(self.figure_directory):
            figures = {}
            for f in os.listdir(self.figure_directory):
                if f.endswith('.png'):
                    event_name, language = self.parse_column_name(f.replace('peaks_', '').replace('.png', ''))
                    if event_name not in figures:
                        figures[event_name] = []
                    figures[event_name].append({
                        'filename': f,
                        'event_name': event_name,
                        'language': language
                    })
            if figures:
                for event, imgs in figures.items():
                    for img in imgs:
                        self.logger.info(f"Loaded existing figure: {img['filename']}")
                self.logger.info("Figures already exist. Returning existing figures.")
                self.logger.info(">> END:: run_peak_detection")
                return figures
        
        # If figures do not exist, perform peak detection
        self.logger.info("Figures do not exist. Performing peak detection.")
        result = self.detect_peaks(df, peaks_toFind)
        self.logger.info(">> END:: run_peak_detection")
        return result    

