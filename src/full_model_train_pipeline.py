# trains, evaluates and push model

import os 
import sys 
import io
import pandas as pd 
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from src.exception import CustomException
from src.logger import logging as log
from src.training import pipeline
from configs import paths, models
from utils.utilities import Utilities
from src.aws.s3 import AwsS3

class Model_trainer_pusher():
    """
    train multiple models, select best one, retrains best model and saves to AWS S3
    """

    def __init__(self):
        self.utils = Utilities()
        self.trainer = pipeline.TrainingPipeline()
        self.paths = paths.Paths()
        self.model_config = models.Models()
        self.aws = AwsS3()

    def FullPipeline(self):
        try:
            print("============================== MODEL TRAINER ====================================")
            log.info("Initiated Model Trainer Pipeline")
            print("Step 1: read the model config file")
            models_dict = self.model_config.models
            print(models_dict)

            print("\nStep 2: reading preprocessed inputs from S3")
            log.info('Step 2: reading preprocessed input features from S3 bucket')
            content = self.aws.read_bucket_files(object_name="datasets/preprocessed/input_features.csv")
            X = pd.read_csv(io.BytesIO(content))
            print(f"\n{X.head(3)}")
            print()
            print("Step 3: reading preprocessed target values from S3")
            log.info('Step 3: reading preprocessed target values from S3 bucket')
            content = self.aws.read_bucket_files(object_name="datasets/raw/target_values.csv")
            y = pd.read_csv(io.BytesIO(content))
            print(f"{y.head(10)}")
            print()
            
            # to load preprocessor.joblib
            """
            log.info("reading preprocessot from S3 bucket")
            file_bytes = self.aws.read_bucket_files(object_name="models/preprocessor.joblib")
            buffer = io.BytesIO(file_bytes)
            preprocessor = joblib.load(buffer) 
            """

            print("Step 4: Training model")
            log.info("Training Pipeline initiated")
            self.trainer.run_pipeline(X=X, y=y, models_dict=models_dict)

            print("Step 5: uploading model to S3")
            bucket_name = self.aws.read_bucket_name()
            log.info("saving best model to S3 bucket")
            self.aws.upload_to_s3(
                file_path=self.paths.MODEL_SAVE_PATH,
                bucket_name=bucket_name,
                object_name="models/best_model.joblib"
            )

            print("============================== MODEL TRAINER COMPLETED ==========================")
            log.info("Model trainer terminated")


        except Exception as e:
            log.error(f"Error during model training: {e}")
            raise CustomException(e, sys)

#########################
if __name__ == "__main__":

    trainer = Model_trainer_pusher()
    trainer.FullPipeline()