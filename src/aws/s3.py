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