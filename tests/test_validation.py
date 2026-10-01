import os 
import sys
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
from src.logger import logging as log
from utils.utilities import Utilities
from configs.paths import Paths
from src.validation.validate import DataValidation

if __name__ == "__main__":
    print("Running Data Validation test...")
    log.info("Running Data Validation test...")
    validator = DataValidation()
    utils = Utilities()
    if os.path.exists(Paths.INPUT_FEATURES_FILE):
        log.info("Raw input dataset file found. Proceeding to read...")
        df_test = utils.read_dataset(Paths.INPUT_FEATURES_FILE)
        is_valid = validator.validate_dataset(df_test)
        log.info(f"Dataset Validation Result: {is_valid}")
        print(f"Dataset Validation Result: {is_valid}")
    else:
        log.warning("Raw input dataset file not found for testing.")
        print("Raw input dataset file not found for testing.")