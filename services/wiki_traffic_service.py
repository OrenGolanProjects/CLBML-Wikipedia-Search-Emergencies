import os
from datetime import datetime
from functools import reduce
import pandas as pd

from repositories.wiki_traffic_repository import WikiTrafficRepository
from repositories.wikipedia_repository import WikipediaRepository
from repositories.event_repository import EventRepository

from utils.api import get_wikipedia_traffic_data


class WikiTrafficService:

    def __init__(self):
        self.wiki_traffic_repo = WikiTrafficRepository()
        self.wikipedia_repo = WikipediaRepository()
        self.event_repo = EventRepository()

    def _get_initial_columns(self):
        pages = self.wikipedia_repo.get_all()
        columns = [f"{page.language}_{page.title}" for page in pages]
        print(f"Initial columns: {columns}")
        return columns

    # def get_traffic_data(self):
    #     print("Starting wiki traffic data collection...")
    #     today_str = datetime.now().strftime('%Y%m%d')
    #     data = []

    #     wikipedia_pages = self.wikipedia_repo.get_all()

    #     for page in wikipedia_pages:
    #         event = self.event_repo.get_by_event_code(page.event_code)
    #         if event is None:
    #             print(f"No event found for page: {page.title}")
    #             continue

    #         created_datetime = self._parse_datetime(event.created_datetime)
    #         if created_datetime is None:
    #             continue

    #         start_date = created_datetime.strftime('%Y%m%d')

    #         try:
    #             df = get_wikipedia_traffic_data(page.language, page.title, start_date, today_str, event.name)
    #             data.append(df)
    #         except Exception as e:
    #             print(f"Error fetching data for {page.title}: {str(e)}")

    #     if not data:
    #         print("No data fetched from API")
    #         return pd.DataFrame()

    #     merged_df = reduce(lambda left, right: pd.merge(left, right, on='timestamp', how='outer', suffixes=('', '_y')), data)

    #     # Ensure 'timestamp' column exists and is converted to 'date'
    #     if 'timestamp' in merged_df.columns:
    #         merged_df['date'] = pd.to_datetime(merged_df['timestamp']).dt.date
    #         merged_df = merged_df.drop(columns=['timestamp'])  # Remove the 'timestamp' column
    #     else:
    #         merged_df['date'] = pd.to_datetime(merged_df.index).date  # Fallback to index if no 'timestamp' column

    #     merged_df = merged_df.reset_index(drop=True)
    #     print("Wiki traffic data collection completed.")
    #     return merged_df


    def get_traffic_data(self):
        print("Starting wiki traffic data collection...")
        today_str = datetime.now().strftime('%Y%m%d')
        data = []

        wikipedia_pages = self.wikipedia_repo.get_all()

        for page in wikipedia_pages:
            event = self.event_repo.get_by_event_code(page.event_code)
            if event is None:
                print(f"No event found for page: {page.title}")
                continue

            created_datetime = self._parse_datetime(event.created_datetime)
            if created_datetime is None:
                continue

            start_date = created_datetime.strftime('%Y%m%d')

            try:
                df = get_wikipedia_traffic_data(page.language, page.title, start_date, today_str, event.name)
                data.append(df)
            except Exception as e:
                print(f"Error fetching data for {page.title}: {str(e)}")

        if not data:
            print("No data fetched from API")
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

        print("Wiki traffic data collection completed.")
        return merged_df

    def _parse_datetime(self, datetime_str):
        if isinstance(datetime_str, str):
            try:
                return datetime.strptime(datetime_str, '%d/%m/%Y')
            except ValueError as e:
                print(f"Error parsing date '{datetime_str}': {str(e)}")
                return None
        return datetime_str

    def create_and_populate_wiki_traffic(self):
        df = self.get_traffic_data()
        if df.empty:
            print("No data to insert into the database.")
            return

        columns = list(df.columns)
        if 'date' in columns:
            columns.remove('date')  # Remove 'date' if it exists

        print(f"Columns to be created in the table: {columns}")
        self.wiki_traffic_repo.create_table(columns)

        for index, row in df.iterrows():
            date = row['date']
            row_data = {col: row[col] for col in columns if col in row.index}
            self.wiki_traffic_repo.insert_or_update(date, row_data)

        self.wiki_traffic_repo.commit()
        print("Wiki traffic data inserted into the database.")
        self.save_to_csv(df)

    def get_all_columns(self):
        columns = self.wiki_traffic_repo.get_all_columns()
        print(f"Retrieved columns: {columns}")
        return columns or []

    def get_all_traffic_data(self):
        data = self.wiki_traffic_repo.get_all()
        print(f"Retrieved {len(data)} rows of traffic data")
        return data or []

    def get_traffic_data_as_dataframe(self):
        all_data = self.get_all_traffic_data()
        columns = self.get_all_columns()

        data_dict = {'date': [entry.date for entry in all_data]}
        for column in columns:
            data_dict[column] = [getattr(entry, column, None) for entry in all_data]

        return pd.DataFrame(data_dict)

    def get_traffic_data_for_page(self, language, title):
        df = self.get_traffic_data_as_dataframe()
        column_name = f"{language}_{title}"
        if column_name in df.columns:
            return df[['date', column_name]].sort_values('date')
        else:
            print(f"No data found for page: {title} in language: {language}")
            return pd.DataFrame()

    def get_total_views_for_page(self, language, title):
        df = self.get_traffic_data_for_page(language, title)
        if not df.empty:
            column_name = f"{language}_{title}"
            return df[column_name].sum()
        return 0

    def get_average_views_for_page(self, language, title):
        df = self.get_traffic_data_for_page(language, title)
        if not df.empty:
            column_name = f"{language}_{title}"
            return df[column_name].mean()
        return 0

    def save_to_csv(self, df):
        file_path = './files/wiki_traffic_data.csv'
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        df.to_csv(file_path, index=True, mode='w')
        print(f"Wiki traffic data saved to {file_path}")

    def read_traffic_data_from_csv(self):
        print("===  START::   read_traffic_data_from_csv")

        file_path = './files/wiki_traffic_data.csv'
        if os.path.exists(file_path):
            df = pd.read_csv(file_path, index_col=1)  # Assuming the first column is the index
            print(f"     Wiki traffic data read from {file_path}")
            return df
        else:
            print(f"No CSV file found at {file_path}")
            return pd.DataFrame()
