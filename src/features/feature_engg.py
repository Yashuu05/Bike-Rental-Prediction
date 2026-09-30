import os 
import sys 
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

class FeatureEngineering:
    def __init__(self):
        pass

    def create_features(self, df):
        """
        Create new features for the dataset.

        Args:
            df (pd.DataFrame): The input dataset.
        Returns:
            pd.DataFrame: The dataset with new features added.
        """
        try:
            # Example feature engineering steps (replace with actual logic)
            df["temp_humidity_interaction"] = df["temperature"] * df["humidity"]
            df["temp_windspeed_interaction"] = df["temperature"] * df["windspeed"]
            return df
        
        except Exception as e:
            raise Exception(f"Error creating features: {e}")