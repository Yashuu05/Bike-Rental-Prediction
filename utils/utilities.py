# general and minor helping functions
import os 
import sys 
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
import pandas as pd

class Utilities:
    @staticmethod
    def create_directory_if_not_exists(directory_path):
        """
        Create a directory if it does not exist.

        Args:
            directory_path (str): The path of the directory to create.
        """
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)

    def read_dataset(self, file_path: str) -> pd.DataFrame:
        """
        Read a dataset from a CSV file.

        Args:
            file_path (str): The path of the CSV file to read.
        Returns:
            pd.DataFrame: The dataset read from the CSV file.
        """
        try:
            df = pd.read_csv(file_path)
            return df
        except Exception as e:
            raise Exception(f"Error reading dataset from {file_path}: {e}")

    def save_dataset(self, df: pd.DataFrame, file_path: str):
        """
        Save a dataset to a CSV file.

        Args:
            df (pd.DataFrame): The dataset to save.
            file_path (str): The path of the CSV file to save the dataset to.
        """
        try:
            df.to_csv(file_path, index=False)
        except Exception as e:
            raise Exception(f"Error saving dataset to {file_path}: {e}")

    def load_ml_model(self, model_path: str):
        """
        Load a machine learning model from a file.

        Args:
            model_path (str): The path of the model file to load.
        Returns:
            The loaded machine learning model.
        """
        try:
            import joblib
            model = joblib.load(model_path)
            return model
        except Exception as e:
            raise Exception(f"Error loading ML model from {model_path}: {e}")

    def save_model_object(self, obj: object, file_path: str):
        """
        Save a Python object (model or preprocessor) to a file.

        Args:
            obj: The object to save.
            file_path (str): The path where the object will be saved.
        """
        try:
            import joblib
            joblib.dump(obj, file_path)
        except Exception as e:
            raise Exception(f"Error saving object to {file_path}: {e}")