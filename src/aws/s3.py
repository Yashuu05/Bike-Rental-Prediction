# file to interact with AWS S3 bucket such as uploading and downloading files

import os 
import sys 
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)
from src.logger import logging as log
from src.exception import CustomException
from dotenv import load_dotenv
import boto3

class AwsS3:

    def read_bucket_name(self):
        """
        reads aws bucket name from .env
        Args: 
            None
        Returns: 
            bucket_name: valid s3 bucket name 
        """
        try:
            log.info("reading S3 Bucket name...")
            load_dotenv()
            bucket_name = os.getenv("S3_BUCKET_NAME")
            if bucket_name:
                # Sanitize bucket name by stripping s3:// prefix and any path components
                bucket_name = bucket_name.replace("s3://", "").strip("/").split("/")[0]
                log.info("Bucket Name found.")
                return bucket_name
            
        except Exception as e:
            log.error("Error occurred while reading bucket name: %s", str(e))
            raise CustomException(e, sys)

    def upload_to_s3(self,file_path:str, bucket_name:str,object_name:None|str=None):
        """
        uploads local csv dataset to given s3 bucket 

        Args:
            :param file_path: Path to the local CSV file (e.g., 'data/dataset.csv')
            :param bucket_name: Name of the target S3 bucket
            :param object_name: S3 object key. If not specified, file_path's filename is used.
        
        Returns:
        """
        try:
            if object_name is None:
                object_name = os.path.basename(file_path)            
            s3_client = boto3.client('s3')
            print(f"Uploading {file_path} to s3://{bucket_name}/{object_name}...")

            # upload to s3 bucket with content type as text/csv
            s3_client.upload_file(
                Filename=file_path,
                Bucket=bucket_name,
                Key=object_name,
                ExtraArgs={'ContentType': 'text/csv'}
            )
            print("Upload successful!")
            return True

        except Exception as e:
            log.error(f"Error occured while uploading to s3: {str(e)}")
            raise CustomException(e, sys)

    def read_bucket_files(self, object_name: str, bucket_name: None | str = None, download_path: None | str = None):
        """
        Reads or downloads a specific file from an AWS S3 bucket.

        Args:
            :param object_name: S3 object key (e.g., 'datasets/preprocessed/input_features.csv')
            :param bucket_name: Name of the target S3 bucket. If None, reads from environment variables.
            :param download_path: Optional local file path to save the downloaded file.

        Returns:
            :return: If download_path is provided, returns the download_path string.
                     If download_path is None, returns raw bytes of the file content.
        """
        try:
            if bucket_name is None:
                bucket_name = self.read_bucket_name()

            s3_client = boto3.client('s3')
            log.info(f"Reading object '{object_name}' from s3://{bucket_name}...")

            if download_path:
                os.makedirs(os.path.dirname(download_path), exist_ok=True)
                s3_client.download_file(Bucket=bucket_name, Key=object_name, Filename=download_path)
                log.info(f"File successfully downloaded from s3://{bucket_name}/{object_name} to {download_path}")
                return download_path
            else:
                response = s3_client.get_object(Bucket=bucket_name, Key=object_name)
                log.info(f"File successfully read from s3://{bucket_name}/{object_name}")
                return response['Body'].read()

        except Exception as e:
            log.error(f"Error occurred while reading file from S3: {str(e)}")
            raise CustomException(e, sys)