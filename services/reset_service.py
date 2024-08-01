import os
import shutil

class ResetService:
    def __init__(self):
        self.files_directory = './files'
        self.static_directory = './static'
        self.instance_directory = './instance'
        self.files_to_remove = ['arima_results.csv', 'wiki_traffic_data.csv']
        self.directories_to_remove = ['arima_figures', 'peaks_figures']
        self.db_file = 'database.db'

    def reset_files_and_directories(self):
        # Remove files
        for file_name in self.files_to_remove:
            file_path = os.path.join(self.files_directory, file_name)
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"File {file_path} has been deleted.")
            else:
                print(f"No file found at {file_path}")

        # Remove directories
        for dir_name in self.directories_to_remove:
            dir_path = os.path.join(self.static_directory, dir_name)
            if os.path.exists(dir_path):
                shutil.rmtree(dir_path)
                print(f"Directory {dir_path} has been deleted.")
            else:
                print(f"No directory found at {dir_path}")

        # Remove database file
        db_file_path = os.path.join(self.instance_directory, self.db_file)
        if os.path.exists(db_file_path):
            os.remove(db_file_path)
            print(f"Database file {db_file_path} has been deleted.")
        else:
            print(f"No database file found at {db_file_path}")

# Example usage
if __name__ == "__main__":
    reset_service = ResetService()
    reset_service.reset_files_and_directories()