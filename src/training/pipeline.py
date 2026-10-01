# complete training pipeline with model training and evaluation
# train_1.py + train_2.py

import os 
import sys 
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
from configs.paths import Paths
from src.logger import logging as log
from src.exception import CustomException
from utils.utilities import Utilities
from src.model_evalution import ModelEvaluation
from src.training.train_1 import ModelTrainer
from src.training.train_2 import HyperparameterTuner
from configs.models import Models

class TrainingPipeline:

    def __init__(self):
        self.utilities = Utilities()
        self.model_trainer = ModelTrainer()
        self.hyperparameter_tuner = HyperparameterTuner()
        self.model_evaluator = ModelEvaluation()
        self.models = Models()

    def run_pipeline(self, X, y, models_dict: dict):
        """
        Runs the complete training pipeline including model training, evaluation, and hyperparameter tuning.

        Args:
            X: Features
            y: Targets
            models (dict): Dictionary of model names and their corresponding objects
        Returns:

        """
        try:

            log.info("training base models....")
            best_model = self.model_trainer.TrainerEvaluationPipeline(
                X=X,
                y=y,
                models=models_dict,
            )

            log.info(f"best model: {best_model}. Training {best_model} with hyperparameters...")
            trained_best_model = self.hyperparameter_tuner.tune_hyperparameters(
                X=X,
                y=y,
                best_model_name=best_model,
                models=models_dict
            )

            # Save the best model object
            log.info(f"Saving best model {best_model} to {Paths.MODEL_SAVE_PATH}")
            os.makedirs(os.path.dirname(Paths.MODEL_SAVE_PATH), exist_ok=True)
            self.utilities.save_model_object(trained_best_model, Paths.MODEL_SAVE_PATH)
            
            log.info(f"Best tuned model saved to {Paths.MODEL_SAVE_PATH} successfully.")
            print(f"Best tuned model saved to {Paths.MODEL_SAVE_PATH} successfully.")

        except Exception as e:
            raise CustomException(e, sys)