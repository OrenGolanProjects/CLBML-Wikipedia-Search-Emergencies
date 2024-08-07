import os
import shutil
import logging

class ResetService:
    """
    Service for resetting the application state by removing specific files and directories.
    """

    def __init__(self):
        """
        Initialize the ResetService with directories and files to manage.
        """
        self.files_directory = './files'
        self.static_directory = './static'
        self.instance_directory = './instance'
        self.files_to_remove = ['arima_results.csv', 'wiki_traffic_data.csv']
        self.directories_to_remove = ['arima_figures', 'peaks_figures', 'cross_corr_figures']
        self.db_file = 'CLBML.db'
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)

    def remove_files_and_directories(self):
        """
        Remove specified files and directories.
        """
        self.logger.info(">> START:: remove_files_and_directories")

        # Remove files
        for file_name in self.files_to_remove:
            file_path = os.path.join(self.files_directory, file_name)
            if os.path.exists(file_path):
                os.remove(file_path)
                self.logger.info(f"File {file_path} has been deleted.")
            else:
                self.logger.warning(f"No file found at {file_path}")

        # Remove directories
        for dir_name in self.directories_to_remove:
            dir_path = os.path.join(self.static_directory, dir_name)
            if os.path.exists(dir_path):
                shutil.rmtree(dir_path)
                self.logger.info(f"Directory {dir_path} has been deleted.")
            else:
                self.logger.warning(f"No directory found at {dir_path}")

        # Remove database file
        db_file_path = os.path.join(self.instance_directory, self.db_file)
        if os.path.exists(db_file_path):
            os.remove(db_file_path)
            self.logger.info(f"Database file {db_file_path} has been deleted.")
        else:
            self.logger.warning(f"No database file found at {db_file_path}")

        self.logger.info(">> END:: remove_files_and_directories")

    def create_directories(self):
        """
        Create specified directories if they do not exist.
        """
        self.logger.info(">> START:: create_directories")

        for dir_name in self.directories_to_remove:
            dir_path = os.path.join(self.static_directory, dir_name)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
                self.logger.info(f"Directory {dir_path} has been created.")
            else:
                self.logger.info(f"Directory {dir_path} already exists.")

        self.logger.info(">> END:: create_directories")

# Example usage
if __name__ == "__main__":
    reset_service = ResetService()
    reset_service.remove_files_and_directories()
    reset_service.create_directories()