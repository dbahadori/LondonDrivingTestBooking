import os
import json
import glob
import logging
from src.utils.app_utils import get_project_root

class FileManager:
    def __init__(self, directory):
        # Get the current working directory
        self.base_dir = get_project_root()
        logging.info(f'base directory:{self.base_dir}')

        # Remove any leading slashes from the directory
        directory = directory.lstrip('/')
        # Construct the path to the Data directory
        self.directory = os.path.join(self.base_dir, "Data", directory)

        # Ensure the directory exists; create it if it doesn't
        os.makedirs(self.directory, exist_ok=True)

    def save_data(self, file_name, data):
        """
        Writes data to a JSON file. Overwrites if the file exists.
        """
        output_path = os.path.join(self.directory, f"{file_name}.json")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return output_path

    def append_data(self, file_name, data):
        """
        Appends data to an existing JSON file, or creates the file if it doesn't exist.
        """
        output_path = os.path.join(self.directory, f"{file_name}.json")

        # Check if the file exists
        if os.path.exists(output_path):
            with open(output_path, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
        else:
            existing_data = []  # Initialize empty list if file doesn't exist

        # Append the new data
        existing_data.append(data)

        # Write the updated data back to the file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=4)
        return output_path

    def read_data(self, file_name):
        """
        Reads data from a JSON file. Returns an empty list if the file doesn't exist.
        """
        output_path = os.path.join(self.directory, f"{file_name}.json")

        if os.path.exists(output_path):
            with open(output_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            logging.warning(f"File {file_name}.json does not exist.")
            return []  # Return empty list for consistency

    def read_all_json_files(self):
        """
        Reads all JSON files from the directory and returns their contents as a list.
        """
        json_files = glob.glob(os.path.join(self.directory, '*.json'))
        all_data = []

        for file_path in json_files:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                all_data.append(data)

        return all_data

    def list_files(self):
        """
        Lists all files in the directory.
        """
        return os.listdir(self.directory)

    def ensure_data_directory(self, base_dir):
        """
        Ensures that the Data directory exists and creates it if not present.
        """
        # Define the data path
        data_path = os.path.join(base_dir, "Data", self.directory)

        # Create the directory if it does not exist
        os.makedirs(data_path, exist_ok=True)

        return data_path


# Example usage:
base_dir = os.getcwd()  # This can be passed from a different part of app if needed
if __name__ == "__main__":
    print(get_project_root())
    fm = FileManager("ddd")
    fm.save_data("aa", "{sdsa}")
