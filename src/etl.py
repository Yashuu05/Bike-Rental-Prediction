import os 
import sys
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
from src.ingestion.ingestion import Ingestion
from src.extraction.extract import Extractor
from src.preprocessing.transform import TransformDataset
from src.features.feature_engg import FeatureEngineering
from src.logger import logging as log
from src.exception import CustomException
from configs.paths import Paths
from utils.utilities import Utilities
from dotenv import load_dotenv
load_dotenv()

class ETLPipeline:
    def __init__(self):
        self.ingest = Ingestion()
        self.ext = Extractor()
        self.transform = TransformDataset()
        self.feature = FeatureEngineering()
        self.paths = Paths()
        self.utils = Utilities()

    def complete_etl_pipeline(self):
        """
        complete ETL Pipeline:
        1. extract dataset from official website
        2. transform dataset into model training ready dataset
        3. ingest dataset to AWS S3 bucket

        """

        log.info("ETL PIPELINE initiated.")
        print("=========================== ETL Pipeline started ============================")
        try:
            print("Step 1: Extraction started.")
            # 1. extract
            log.info("Extracting raw dataset from website")
            X, y = self.ext.extract_dataset()

            # 2. save to loacl folder
            self.ext.extract_and_save(X=X, y=y)
            print("Step 1 completed")

            # 3. preprocessing 
            print("Step 2: preprocessing started")
            log.info("Transforming raw input features")
            prep = self.transform.preprocessing_pipeline(df=X)
            new_df, preprocessor = self.transform.preprocess_data(preprocessor=prep, df=X)

            # save preprocessed dataset to local file
            log.info(f"Saving the processed Dataset to {Paths.PROCESSED_INPUT_FILE}")
            os.makedirs(os.path.dirname(Paths.PROCESSED_INPUT_FILE), exist_ok=True)
            self.utils.save_dataset(df=new_df, file_path=Paths.PROCESSED_INPUT_FILE) 

            # save preprocessor to local file
            log.info(f"Saving the preprocessor to {Paths.PREPROCESSOR_SAVE_FILE}")
            os.makedirs(os.path.dirname(Paths.PREPROCESSOR_SAVE_FILE), exist_ok=True)
            self.utils.save_model_object(obj=preprocessor, file_path=Paths.PREPROCESSOR_SAVE_FILE)
            print("Step 2 completed")

            # ingest
            print("Step 3: Ingestion started...")
            log.info("Data Transformation Completed. Starting with ingestion")
            log.info("Ingesting Input Features")
            self.ingest.ingest_to_s3(
                file_path=self.paths.PROCESSED_INPUT_FILE,
                object_name="datasets/preprocessed/input_features.csv"   
            )
            log.info("Ingesting output labels to AWS S3")
            self.ingest.ingest_to_s3(
                file_path=self.paths.OUTPUT_TARGETS_FILE,
                object_name="datasets/raw/target_values.csv"
            )
            log.info("Saving preprocessor to AWS")
            self.ingest.ingest_to_s3(
                file_path=self.paths.PREPROCESSOR_SAVE_FILE,
                object_name="models/preprocessor.joblib"
            )
            log.info("Ingestion of input features, output labels and preprocessor complete.")
            print("Step 3 Completed")

            # END
            log.info("ETL Pipeline Terminated.")
            print("======================= ETL Completed ======================")
        
        except Exception as e:
            log.error(f"Error in ETL Pipelin: {str(e)}")
            raise CustomException(e, sys)

#########################
if __name__ == "__main__":

    etl = ETLPipeline()
    etl.complete_etl_pipeline()