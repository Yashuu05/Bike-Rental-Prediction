# test the training pipeline
import os 
import sys
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
from src.training.pipeline import TrainingPipeline
from src.logger import logging as log
from src.exception import CustomException
from configs.models import Models
from utils.utilities import Utilities
from configs.paths import Paths

class TestTrainingPipeline:

    def setup_method(self):
        self.pipeline = TrainingPipeline()

    def execute_pipeline(self, X, y, models_dict: dict):
        """
        Test the complete training pipeline.

        Args:
            X: Features
            y: Targets
            models_dict (dict): Dictionary of model names and their corresponding objects
        """
        try:
            log.info("Testing the complete training pipeline...")
            self.pipeline.run_pipeline(X, y, models_dict)
            log.info("Training pipeline test completed successfully.")
        except Exception as e:
            log.error("Error occurred during training pipeline test: %s", str(e))
            raise CustomException(e, sys)


if __name__ == "__main__":
    log.info("Starting training pipeline test...")
    print("Starting training pipeline test...")

    # 1. read configs/models.py
    log.info("Reading models dictionary...")
    models_dict = Models().models

    # 2. load dataset
    log.info("Loading dataset...")
    os.path.exists(Paths.PROCESSED_INPUT_FILE) and os.path.exists(Paths.OUTPUT_TARGETS_FILE)
    X = Utilities().read_dataset(file_path=Paths.PROCESSED_INPUT_FILE)
    y = Utilities().read_dataset(file_path=Paths.OUTPUT_TARGETS_FILE)
    log.info("Dataset loaded successfully.")

    # 3. run the training pipeline test
    test_pipeline = TestTrainingPipeline()
    test_pipeline.execute_pipeline(X, y, models_dict)
    log.info("Training pipeline test completed successfully.")