import os
import logging
from datetime import datetime
from functools import reduce
import pandas as pd

from repositories.wiki_traffic_repository import WikiTrafficRepository
from repositories.wikipedia_repository import WikipediaRepository
from repositories.event_repository import EventRepository

from utils.api import get_wikipedia_traffic_data


class WikiTrafficService:
    """
    Service for managing Wikipedia traffic data.
    """

    def __init__(self):
        """
        Initialize the WikiTrafficService with repositories and file paths.
        """
        self.wiki_traffic_repo = WikiTrafficRepository()
        self.wikipedia_repo = WikipediaRepository()
        self.event_repo = EventRepository()
        self.filePath = './files/wiki_traffic_data.csv'
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)

    def _get_initial_columns(self):
        """
        Get initial columns for the traffic data based on Wikipedia pages.

        Returns:
        list: List of column names.
        """
        pages = self.wikipedia_repo.get_all()
        columns = [f"{page.language}_{page.title}" for page in pages]
        self.logger.info(f"Initial columns: {columns}")
        return columns

    def get_traffic_data(self):
        """
        Collect traffic data from Wikipedia.

        Returns:
        pd.DataFrame: DataFrame containing the traffic data.
        """
        self.logger.info("Starting wiki traffic data collection...")
        today_str = datetime.now().strftime('%Y%m%d')
        data = []

        wikipedia_pages = self.wikipedia_repo.get_all()

        for page in wikipedia_pages:
            event = self.event_repo.get_by_event_code(page.event_code)
            if event is None:
                self.logger.warning(f"No event found for page: {page.title}")
                continue

            created_datetime = self._parse_datetime(event.created_datetime)
            if created_datetime is None:
                continue

            start_date = created_datetime.strftime('%Y%m%d')

            try:
                df = get_wikipedia_traffic_data(page.language, page.title, start_date, today_str, event.name)
                data.append(df)
            except Exception as e:
                self.logger.error(f"Error fetching data for {page.title}: {str(e)}")

        if not data:
            self.logger.warning("No data fetched from API")
            return pd.DataFrame()

        merged_df = reduce(lambda left, right: pd.merge(left, right, on='timestamp', how='outer', suffixes=('', '_y')), data)

        # Ensure 'timestamp' column exists and is converted to 'date'
        if 'timestamp' in merged_df.columns:
            merged_df['date'] = pd.to_datetime(merged_df['timestamp']).dt.date
            merged_df = merged_df.drop(columns=['timestamp'])  # Remove the 'timestamp' column
        else:
            merged_df['date'] = pd.to_datetime(merged_df.index).date  # Fallback to index if no 'timestamp' column

        merged_df = merged_df.reset_index(drop=True)
        # Sort the DataFrame by the 'date' column from oldest to newest
        merged_df = merged_df.sort_values(by='date')

        self.logger.info("Wiki traffic data collection completed.")
        return merged_df

    def _parse_datetime(self, datetime_str):
        """
        Parse a datetime string into a datetime object.

        Parameters:
        datetime_str (str): The datetime string to parse.

        Returns:
        datetime: The parsed datetime object, or None if parsing fails.
        """
        if isinstance(datetime_str, str):
            try:
                return datetime.strptime(datetime_str, '%d/%m/%Y')
            except ValueError as e:
                self.logger.error(f"Error parsing date '{datetime_str}': {str(e)}")
                return None
        return datetime_str

    def create_and_populate_wiki_traffic(self):
        """
        Create and populate the wiki traffic table in the database.
        """
        df = self.get_traffic_data()
        if df.empty:
            self.logger.warning("No data to insert into the database.")
            return

        columns = list(df.columns)
        if 'date' in columns:
            columns.remove('date')  # Remove 'date' if it exists

        self.logger.info(f"Columns to be created in the table: {columns}")
        self.wiki_traffic_repo.create_table(columns)

        for index, row in df.iterrows():
            date = row['date']
            row_data = {col: row[col] for col in columns if col in row.index}
            self.wiki_traffic_repo.insert_or_update(date, row_data)

        self.wiki_traffic_repo.commit()
        self.logger.info("Wiki traffic data inserted into the database.")
        self.save_to_csv(df)

    def get_all_columns(self):
        """
        Get all columns from the wiki traffic table.

        Returns:
        list: List of column names.
        """
        columns = self.wiki_traffic_repo.get_all_columns()
        self.logger.info(f"Retrieved columns: {columns}")
        return columns or []

    def get_all_traffic_data(self):
        """
        Get all traffic data from the wiki traffic table.

        Returns:
        list: List of traffic data entries.
        """
        data = self.wiki_traffic_repo.get_all()
        self.logger.info(f"Retrieved {len(data)} rows of traffic data")
        return data or []

    def get_traffic_data_as_dataframe(self):
        """
        Get all traffic data as a DataFrame.

        Returns:
        pd.DataFrame: DataFrame containing the traffic data.
        """
        all_data = self.get_all_traffic_data()
        columns = self.get_all_columns()

        data_dict = {'date': [entry.date for entry in all_data]}
        for column in columns:
            data_dict[column] = [getattr(entry, column, None) for entry in all_data]

        return pd.DataFrame(data_dict)

    def get_traffic_data_for_page(self, language, title):
        """
        Get traffic data for a specific Wikipedia page.

        Parameters:
        language (str): The language of the Wikipedia page.
        title (str): The title of the Wikipedia page.

        Returns:
        pd.DataFrame: DataFrame containing the traffic data for the specified page.
        """
        df = self.get_traffic_data_as_dataframe()
        column_name = f"{language}_{title}"
        if column_name in df.columns:
            return df[['date', column_name]].sort_values('date')
        else:
            self.logger.warning(f"No data found for page: {title} in language: {language}")
            return pd.DataFrame()

    def get_total_views_for_page(self, language, title):
        """
        Get the total views for a specific Wikipedia page.

        Parameters:
        language (str): The language of the Wikipedia page.
        title (str): The title of the Wikipedia page.

        Returns:
        int: The total number of views.
        """
        df = self.get_traffic_data_for_page(language, title)
        if not df.empty:
            column_name = f"{language}_{title}"
            return df[column_name].sum()
        return 0

    def get_average_views_for_page(self, language, title):
        """
        Get the average views for a specific Wikipedia page.

        Parameters:
        language (str): The language of the Wikipedia page.
        title (str): The title of the Wikipedia page.

        Returns:
        float: The average number of views.
        """
        df = self.get_traffic_data_for_page(language, title)
        if not df.empty:
            column_name = f"{language}_{title}"
            return df[column_name].mean()
        return 0

    def save_to_csv(self, df):
        """
        Save the traffic data to a CSV file.

        Parameters:
        df (pd.DataFrame): The DataFrame containing the traffic data.
        """
        os.makedirs(os.path.dirname(self.filePath), exist_ok=True)
        df.to_csv(self.filePath, index=True, mode='w')
        self.logger.info(f"Wiki traffic data saved to {self.filePath}")

    def read_traffic_data_from_csv(self):
        """
        Read the traffic data from a CSV file.

        Returns:
        pd.DataFrame: DataFrame containing the traffic data.
        """
        self.logger.info("===  START::   read_traffic_data_from_csv")

        if os.path.exists(self.filePath):
            df = pd.read_csv(self.filePath, index_col=1)  # Assuming the first column is the index
            self.logger.info(f"Wiki traffic data read from {self.filePath}")
            return df
        else:
            self.logger.warning(f"No CSV file found at {self.filePath}")
            return pd.DataFrame()

    def delete_csv_file(self):
        """
        Delete the CSV file containing the traffic data.
        """
        if os.path.exists(self.filePath):
            os.remove(self.filePath)
            self.logger.info(f"File {self.filePath} has been deleted.")
        else:
            self.logger.warning(f"No file found at {self.filePath}")
