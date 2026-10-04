import os 
import sys

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.append(project_root)

import pandas as pd
from src.exception import CustomException
from configs.paths import Paths
from src.logger import logging as log
from utils.utilities import Utilities
from src.features import feature_engg

# 1. read model and preprocessor
# 2. read sample dataset
# 3. split dataset into x and y
# 4. predict output
# 5. save predicted output to reports

class PredictionPipeline:

    def __init__(
        self,
        model_path: str = Paths.MODEL_SAVE_PATH,
        preprocessor_path: str = Paths.PREPROCESSOR_SAVE_FILE,
        data_path: str = Paths.SAMPLE_DATASET_PATH
    ):
        self.utils = Utilities()
        self.path = Paths()
        self.model_path = model_path
        self.preprocessor_path = preprocessor_path
        self.data_path = data_path

    def read_resources(self) -> tuple:
        """
        reads resources such as saved model, saved preprocessor and sample dataset

        Args:
            none
        
        Returns:
            - model: saved and trained model
            - preprocessor: saved preprocessor during data transformation
            - df: raw sample dataset
        """

        try:
            if not os.path.exists(self.model_path):
                raise FileNotFoundError(f"Model file not found at {self.model_path}")
            if not os.path.exists(self.preprocessor_path):
                raise FileNotFoundError(f"Preprocessor file not found at {self.preprocessor_path}")
            if not os.path.exists(self.data_path):
                raise FileNotFoundError(f"Sample dataset file not found at {self.data_path}")

            log.info(f"Loading Model from {self.model_path} and Preprocessor from {self.preprocessor_path}...")
            model = self.utils.load_ml_model(model_path=self.model_path)
            preprocessor = self.utils.load_ml_model(model_path=self.preprocessor_path)
            log.info("Read Model and Preprocessor successfully.")

            log.info(f"Reading sample dataset from {self.data_path}...")
            df = self.utils.read_dataset(file_path=self.data_path)
            log.info(f"Successfully read sample data with shape {df.shape}")

            return model, preprocessor, df

        except Exception as e:
            log.error(f"Error while loading resources: {e}")
            raise CustomException(e, sys)

    def apply_preprocessing(self, preprocessor, sample_data: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series | None]:
        """
        Applies preprocessing steps to raw dataset using saved preprocessor
        Args:
            - preprocessor: saved preprocessor object 
            - sample_data: raw sample dataset 
        Returns:
            - preprocessed Input dataset
            - Target labels (or None if target not in sample_data)
        """
        try:
            df = sample_data.copy()
            y = None

            # 1. Extract target label if present in dataset
            target_cols = [c for c in df.columns if "rented" in c.lower() or "bike" in c.lower()]
            if target_cols:
                target_col = target_cols[0]
                y = df.pop(target_col)
                log.info(f"Extracted target column '{target_col}' for validation.")

            # 2. Standardize column names to match preprocessor expectation
            column_mapping = {
                "date": "date",
                "hour": "hour",
                "temperature(°c)": "temperature",
                "temperature": "temperature",
                "humidity(%)": "humidity",
                "humidity": "humidity",
                "wind speed (m/s)": "windspeed",
                "wind speed": "windspeed",
                "windspeed": "windspeed",
                "visibility (10m)": "visibility",
                "visibility": "visibility",
                "dew point temperature": "dew_point_temperature",
                "dew_point_temperature": "dew_point_temperature",
                "solar radiation (mj/m2)": "solar_radiation",
                "solar radiation": "solar_radiation",
                "solar_radiation": "solar_radiation",
                "rainfall(mm)": "rainfall",
                "rainfall": "rainfall",
                "snowfall (cm)": "snowfall",
                "snowfall": "snowfall",
                "seasons": "seasons",
                "holiday": "holiday",
                "functioning day": "functioning_day",
                "functioning_day": "functioning_day"
            }

            cleaned_cols = {}
            for col in df.columns:
                col_clean = col.strip().lower()
                cleaned_cols[col] = column_mapping.get(col_clean, col_clean)

            df.rename(columns=cleaned_cols, inplace=True)

            if "dew_point_temperature" not in df.columns:
                df["dew_point_temperature"] = 0.0

            # 3. Date conversion
            if "date" in df.columns:
                log.info("Converting 'date' column to datetime format")
                df["date"] = pd.to_datetime(df["date"])
                df["day"] = df["date"].dt.day
                df["month"] = df["date"].dt.month
                df["year"] = df["date"].dt.year
                df.drop(columns=["date"], inplace=True)

            # 4. Feature engineering
            log.info("Applying feature engineering steps")
            feature_engineer = feature_engg.FeatureEngineering()
            df = feature_engineer.create_features(df)

            # 5. Transform data using preprocessor (transform ONLY, no fit_transform)
            log.info("Transforming input features with preprocessor")
            df_preprocessed_arr = preprocessor.transform(df)

            if hasattr(df_preprocessed_arr, "toarray"):
                df_preprocessed_arr = df_preprocessed_arr.toarray()

            try:
                feature_names = preprocessor.get_feature_names_out()
            except AttributeError:
                feature_names = [f"feature_{i}" for i in range(df_preprocessed_arr.shape[1])]

            df_preprocessed = pd.DataFrame(df_preprocessed_arr, columns=feature_names)
            return df_preprocessed, y

        except Exception as e:
            log.error(f"Error during preprocessing: {e}")
            raise CustomException(e, sys)

    def predict_output(self, model, processed_input: pd.DataFrame, output_label: pd.Series = None) -> pd.DataFrame:
        """
        Performs prediction on trained model and saves predictions to reports.
        """
        try:
            log.info("Generating predictions using trained model...")
            predictions = model.predict(processed_input)

            result_dict = {"predicted_rented_bike_count": predictions}
            if output_label is not None:
                result_dict["actual_rented_bike_count"] = output_label.reset_index(drop=True)

            predicted_outputs = pd.DataFrame(result_dict)
            predicted_outputs["difference"] = predicted_outputs["actual_rented_bike_count"] - predicted_outputs["predicted_rented_bike_count"]

            # Save predicted outputs to reports directory
            reports_dir = os.path.join(project_root, "reports")
            os.makedirs(reports_dir, exist_ok=True)
            output_save_path = os.path.join(reports_dir, "predictions.csv")
            self.utils.save_dataset(df=predicted_outputs, file_path=output_save_path)
            log.info(f"Saved prediction results to {output_save_path}")

            return predicted_outputs

        except Exception as e:
            log.error(f"Error while prediction: {e}")
            raise CustomException(e, sys)

if __name__ == "__main__":
    pred = PredictionPipeline()

    # read resources
    model, preprocessor, df = pred.read_resources()
    # apply preprocessing
    new_df, y = pred.apply_preprocessing(preprocessor=preprocessor, sample_data=df)
    # predict output 
    output = pred.predict_output(model=model, processed_input=new_df, output_label=y)
    print("\n--- Model Predictions Summary (First 10 Rows) ---")
    print(output.head(10))