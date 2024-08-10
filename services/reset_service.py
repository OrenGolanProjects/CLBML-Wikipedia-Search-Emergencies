import os
import shutil
import logging
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


class ResetService:
    """
    Service for resetting the application state by removing specific files and directories.
    """

    def __init__(self):
        """
        Initialize the ResetService with directories and files to manage.
        """
        self.root_directory = 'CLBML-Wikipedia-Search-Emergencies'
        self.files_directory = './files'
        self.static_directory = './static'
        self.instance_directory = './instance'
        self.files_to_remove = ['arima_results.csv', 'wiki_traffic_data.csv']
        self.directories_to_remove = ['arima_figures', 'peaks_figures', 'auto_corr_figures']
        self.db_file = 'CLBML.db'
        self.logger = logger
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

    # def print_files_and_directories(self):
    #     """
    #     Print the files that exists in the directories.
    #     """
    #     self.logger.info(">> START:: print_files_and_directories")

    #     # Loop through the directory files and print them
    #     for file_name in self.files_to_remove:
    #         file_path = os.path.join(self.files_directory, file_name)
    #         if os.path.exists(file_path):
    #             self.logger.info(f"EXISTS:: File {file_path}.")
    #         else:
    #             self.logger.warning(f"NOT EXISTS:: No file found at {file_path}")
        
    #     # Loop through the directory static files and print them
    #     for dir_name in self.directories_to_remove:
    #         dir_path = os.path.join(self.static_directory, dir_name)
    #         if os.path.exists(dir_path):
    #             self.logger.info(f"EXISTS:: Directory {dir_path}.")
    #         else:
    #             self.logger.warning(f"NOT EXISTS:: No directory found at {dir_path}")
        
    #     # Print the database file
    #     db_file_path = os.path.join(self.instance_directory, self.db_file)
    #     if os.path.exists(db_file_path):
    #         self.logger.info(f"EXISTS:: Database file {db_file_path}.")
    #     else:
    #         self.logger.warning(f"NOT EXISTS:: No database file found at {db_file_path}")

    #     self.logger.info(">> END:: print_files_and_directories")

    def print_files_and_directories(self):
        """
        Print all the files that exist in the root directory and its subdirectories.
        """
        self.logger.info(">> START:: print_files_and_directories")
        root_directory = os.path.dirname(os.path.dirname(__file__))
        directories = ["instance", "templates", "tests", "static", "models", "repositories", "services", "utils", "components", "files"]

        # Check if the root directory exists
        if not os.path.exists(root_directory):
            self.logger.error(f"Root directory {root_directory} does not exist.")
            return

        # Walk through the root directory and print all files in specified directories
        for root, dirs, files in os.walk(root_directory):
            relative_path = os.path.relpath(root, root_directory)
            if any(relative_path.startswith(directory) for directory in directories):
                for file_name in files:
                    file_path = os.path.join(root, file_name)
                    if os.path.exists(file_path):
                        self.logger.info(f"EXISTS:: File {file_path}.")
                    else:
                        self.logger.warning(f"NOT EXISTS:: No file found at {file_path}")

        self.logger.info(">> END:: print_files_and_directories")



# Example usage
if __name__ == "__main__":
    reset_service = ResetService()
    reset_service.remove_files_and_directories()
    reset_service.create_directories()