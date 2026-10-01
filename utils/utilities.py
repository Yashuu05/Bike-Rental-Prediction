# general and minor helping functions
import os 
import sys 
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
from src.logger import logging as log
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

    def read_yaml_file(self, file_path: str) -> dict:
        """
        Read a YAML file and return its contents as a dictionary.

        Args:
            file_path (str): The path of the YAML file to read.
        Returns:
            dict: The contents of the YAML file as a dictionary.
        """
        import yaml
        try:
            with open(file_path, 'r') as file:
                data = yaml.safe_load(file)
            return data
        except Exception as e:
            raise Exception(f"Error reading YAML file from {file_path}: {e}")

    def split_features_and_target(self, X_df: pd.DataFrame, y_df: pd.DataFrame, test_size: float = 0.2, random_state: int = 42):
        """
        Split the DataFrame into features and target.

        Args:
            X_df (pd.DataFrame): The input DataFrame containing features.
            y_df (pd.DataFrame): The input DataFrame containing the target.
            test_size (float): The proportion of the dataset to include in the test split.
            random_state (int): Random seed for reproducibility.
        Returns:
            X_train, X_test, y_train, y_test: Split datasets.
        """
        from sklearn.model_selection import train_test_split
        try:
            log.info(f"Splitting dataset into train and test sets with test size {test_size} and random state {random_state}...")  
            X_train, X_test, y_train, y_test = train_test_split(X_df, y_df, test_size=test_size, random_state=random_state, shuffle=True)
            return X_train, X_test, y_train, y_test
        
        except Exception as e:
            raise Exception(f"Error splitting features and target: {e}")

    def split_dataset(self, X_df: pd.DataFrame, y_df: pd.DataFrame, test_size: float = 0.2, random_state: int = 42):
        """Alias for split_features_and_target."""
        return self.split_features_and_target(X_df, y_df, test_size=test_size, random_state=random_state)