import os
import json


# A class to load a (.csv, .json) file depending on the file extension and return the data in dictionary format.
class LoadImportFile:
    def __init__(self, file_path):
        self.file_path = file_path
        self.file_type = None
        self.data = None
        self.valid_file_types = [".json"]

    def load_csv(self):
        pass

    def load_json(self):
        with open(self.file_path, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError as e:
                raise ValueError(f"Error decoding JSON: {e}")

    def load_file(self):
        """Load the file and return the data in dictionary format."""
        if not self.file_path:
            raise ValueError("File path is empty.")

        # Check if the file exists
        if not os.path.isfile(self.file_path):
            raise FileNotFoundError(f"File not found: {self.file_path}")

        # Get the file extension
        _, self.file_type = os.path.splitext(self.file_path)

        # Check if the file type is valid
        if self.file_type not in self.valid_file_types:
            raise ValueError(f"Invalid file type: {self.file_type}.")

        if self.file_type == ".json":
            self.data = self.load_json()

        return self.data
