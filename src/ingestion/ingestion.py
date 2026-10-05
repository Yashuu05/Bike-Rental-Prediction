# ingest the preprocessed / transformed dataset to s3 bucket
import os 
import sys 
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)
from src.logger import logging as log
from src.exception import CustomException
from utils.utilities import Utilities
from src.aws.s3 import AwsS3
from configs.paths import Paths

class Ingestion:

    def __init__(self):
        self.aws_s3 = AwsS3()

    def ingest_to_s3(self, file_path:str, object_name:None|str=None):
        """
        Ingests the preprocessed/transformed dataset to S3 bucket.

        Args:
            :param file_path: Path to the local CSV file (e.g., 'data/dataset.csv')
            :param object_name: S3 object key. If not specified, file_path's filename is used.
        Returns:
            :return: True if upload is successful, else raises an exception.
        """
        try:
            log.info("Starting ingestion to S3 bucket...")
            bucket_name = self.aws_s3.read_bucket_name()
            upload_success = self.aws_s3.upload_to_s3(file_path, bucket_name, object_name)
            if upload_success:
                log.info("Ingestion to S3 bucket completed successfully.")
                return True
    
        except Exception as e:
            log.error("Error occurred during ingestion to S3: %s", str(e))
            raise CustomException(e, sys)

    def read_from_s3(self, object_name: str, download_path: None | str = None):
        """
        Reads or downloads a specific dataset/file from S3 bucket.

        Args:
            :param object_name: S3 object key (e.g., 'datasets/preprocessed/input_features.csv')
            :param download_path: Optional local destination file path.
        Returns:
            :return: Path to downloaded file if download_path is provided, or raw bytes content if download_path is None.
        """
        try:
            log.info("Starting file retrieval from S3 bucket...")
            return self.aws_s3.read_bucket_files(object_name=object_name, download_path=download_path)
        except Exception as e:
            log.error("Error occurred during reading from S3: %s", str(e))
            raise CustomException(e, sys)



if __name__ == "__main__":
    print("Starting ingestion process...")

    ingest = Ingestion()
    utils = Utilities()
    # read dataset 
    log.info("Reading datasets from local files...")
    if os.path.exists(Paths.PROCESSED_INPUT_FILE) and os.path.exists(Paths.OUTPUT_TARGETS_FILE):
        log.info("Datasets found. Proceeding to read...")
        X = utils.read_dataset(file_path=Paths.PROCESSED_INPUT_FILE)
        y = utils.read_dataset(file_path=Paths.OUTPUT_TARGETS_FILE)
    else:
        log.error("Processed datasets not found. Please ensure the preprocessing step is completed.")
        print("Processed datasets not found. Please ensure the preprocessing step is completed.")
        X, y = None, None

    if X is not None and y is not None:
        log.info("Datasets read successfully. Proceeding to ingest to S3 bucket...")
        # ingest the input dataset to s3 bucket
        ingest.ingest_to_s3(file_path=Paths.PROCESSED_INPUT_FILE, object_name="preprocessed_datasets/input_features.csv")
        # ingest the output dataset to s3 bucket
        ingest.ingest_to_s3(file_path=Paths.OUTPUT_TARGETS_FILE, object_name="preprocessed_datasets/target_values.csv")
        log.info("Ingestion process completed successfully.")
        print("Ingestion process completed successfully.")

    else:
        log.error("Failed to read datasets. Ingestion process aborted.")
        print("Ingestion process failed. Check the logs for more details.")