# transform the data to be used for training and testing ml model
import os 
import sys 
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)
from src.logger import logging as log
from src.exception import CustomException
from configs.paths import Paths
from src.features import feature_engg
import pandas as pd
from utils.utilities import Utilities
from dotenv import load_dotenv
load_dotenv()

class TransformDataset:
    def __init__(self):
        self.s3_bucket_name = os.getenv("S3_BUCKET_NAME")
        self.paths = Paths()

    def preprocessing_pipeline(self, df: pd.DataFrame):
        from sklearn.pipeline import Pipeline
        from sklearn.preprocessing import StandardScaler, OneHotEncoder
        from sklearn.compose import ColumnTransformer
        from sklearn.impute import SimpleImputer

        # Define the preprocessing steps for numerical and categorical features
        numeric_features = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
        categorical_features = df.select_dtypes(include=['object']).columns.tolist()

        if df[numeric_features].isnull().sum().sum() > 0:
            log.warning("Missing values found in numeric features. Handling before preprocessing.")
            numeric_preprocessor = Pipeline(steps=[
                ('imputer', SimpleImputer(strategy='median')),  # Impute missing values with median
                ('scaler', StandardScaler()),  # Scale numeric features
            ])
        else:
            log.info("No missing values found in numeric features. Proceeding with scaling only.")
            numeric_preprocessor = Pipeline(steps=[
                            ('scaler', StandardScaler()),  
            ])

        if df[categorical_features].isnull().sum().sum() > 0:
            log.warning("Missing values found in categorical features. Handling before preprocessing.")
            categorical_preprocessor = Pipeline(steps=[
                ('imputer', SimpleImputer(strategy='most_frequent')),  # Impute missing values with most frequent
                ('onehot', OneHotEncoder(handle_unknown='ignore'))  # One-hot encode categorical features
            ])
        else:
            log.info("No missing values found in categorical features. Proceeding with one-hot encoding only.")
            categorical_preprocessor = Pipeline(steps=[
                ('onehot', OneHotEncoder(handle_unknown='ignore'))
            ])

        preprocessor = ColumnTransformer(
            transformers=[
                ('num', numeric_preprocessor, numeric_features),
                ('cat', categorical_preprocessor, categorical_features)
        ])

        return preprocessor


    def preprocess_data(self, preprocessor, df:pd.DataFrame)-> tuple[pd.DataFrame, object]:
        """
        Preprocess the dataset for training and testing.

        Args:
            preprocessor: The preprocessing pipeline.
            df (pd.DataFrame): The input dataset.

        Returns:
            pd.DataFrame: The preprocessed dataset.
        """
        try:
            # 1. rename columns
            log.info("Renaming columns in the dataset")
            new_cols = ["date","hour","temperature","humidity","windspeed","visibility","dew_point_temperature","solar_radiation","rainfall","snowfall","seasons","holiday","functioning_day"]
            # rename columns in df
            df.columns = new_cols

            # 2. convert date column to datetime
            log.info("Converting 'date' column to datetime format")
            df["date"] = pd.to_datetime(df["date"], format="%d/%m/%Y")
            # convert date into "day", "month", "year"
            df["day"] = df["date"].dt.day
            df["month"] = df["date"].dt.month
            df["year"] = df["date"].dt.year

            # 3. drop the original date column
            log.info("Dropping the original 'date' column")
            df.drop(columns=["date"], inplace=True)

            # 4. feature engineering: create new features based on existing ones
            log.info("Creating new features based on existing ones")
            feature_engineer = feature_engg.FeatureEngineering()
            df = feature_engineer.create_features(df)

            # 5. preprocess the input features dataset using the provided preprocessor
            log.info("Preprocessing the dataset using the provided preprocessor")
            preprocessor = self.preprocessing_pipeline(df)
            df_preprocessed_arr = preprocessor.fit_transform(df)

            # Convert numpy array / sparse matrix back to pandas DataFrame
            if hasattr(df_preprocessed_arr, "toarray"):
                df_preprocessed_arr = df_preprocessed_arr.toarray()

            try:
                feature_names = preprocessor.get_feature_names_out()
            except AttributeError:
                feature_names = [f"feature_{i}" for i in range(df_preprocessed_arr.shape[1])]

            df_preprocessed = pd.DataFrame(df_preprocessed_arr, columns=feature_names)

            return df_preprocessed, preprocessor
        
        except Exception as e:
            raise CustomException(e, sys)

if __name__ == "__main__":
    # save datasets and preprocessor locally temporary
    print("DATA TRANSFORMATION INITIATED")
    # 1. read datasets
    utils = Utilities()
    log.info("reading the Input Feature dataset...")
    if os.path.exists(Paths.INPUT_FEATURES_FILE):
        X = utils.read_dataset(file_path=Paths.INPUT_FEATURES_FILE)
    log.info("reading Output Label dataset...")
    if os.path.exists(Paths.OUTPUT_TARGETS_FILE):
        y = utils.read_dataset(file_path=Paths.OUTPUT_TARGETS_FILE)

    # transform dataset
    log.info("transforming dataset initiated...")
    transformer = TransformDataset()
    preprocessor = transformer.preprocessing_pipeline(df=X)
    new_df, preprocessor = transformer.preprocess_data(preprocessor=preprocessor, df=X)

    # save dataset
    log.info(f"Saving the processed Dataset to {Paths.PROCESSED_INPUT_FILE}")
    os.makedirs(os.path.dirname(Paths.PROCESSED_INPUT_FILE), exist_ok=True)
    utils.save_dataset(df=new_df, file_path=Paths.PROCESSED_INPUT_FILE) 

    # save preprocessor
    log.info(f"Saving the preprocessor to {Paths.PREPROCESSOR_SAVE_FILE}")
    os.makedirs(os.path.dirname(Paths.PREPROCESSOR_SAVE_FILE), exist_ok=True)
    utils.save_model_object(obj=preprocessor, file_path=Paths.PREPROCESSOR_SAVE_FILE)

    print("DATA TRANSFORMATION COMMPLETED")