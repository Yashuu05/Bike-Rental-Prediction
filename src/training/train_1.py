# train the base models (without hyperparameter tuning) and save the trained models to the models directory

import os
import sys 
import pandas as pd

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

from configs.paths import Paths
from src.logger import logging as log
from src.exception import CustomException
from utils.utilities import Utilities
from src.model_evalution import ModelEvaluation
from configs.models import Models
import mlflow

class ModelTrainer:
    
    def __init__(self):
        self.utilities = Utilities()
        self.model_evaluator = ModelEvaluation()
    
    def train_base_models(self, X_train, y_train, model):
        """
        Trains base models (without hyperparameter tuning) and saves the trained models.

        Args:
            X_train: Training features
            y_train: Training targets

        Returns:
            Trained model instance
        """
        try:
            
            #log.info(f"Training model: {type(model).__name__}...")
            model.fit(X_train, y_train)
            log.info(f"Model {type(model).__name__} trained successfully.")
            return model

        except Exception as e:
            log.error("Error occurred during model training: %s", str(e))
            raise CustomException(e, sys)   

    def TrainerEvaluationPipeline(self, X, y, models: dict) -> str:
        """
        Full pipeline to train base models and evaluate them.

        Args:
            X: Features
            y: Targets
            models (dict): Dictionary of model names and their corresponding objects
        Returns:
            str: Name of the best model based on R2 score
        """
        try:
            # split dataset into train and test sets
            log.info("Splitting dataset into training and testing sets...")
            X_train, X_test, y_train, y_test = self.utilities.split_dataset(X, y)
            log.info("Dataset split completed successfully.")
            print("Dataset split completed successfully.")

            try:
                import mlflow
                mlflow.set_experiment("Bike_Rental_Prediction_Experiment")
            except Exception:
                pass
            
            # start training and evaluation pipeline
            log.info("Starting full model training and evaluation pipeline...")
            
            mlflow.sklearn.autolog()  # Enable automatic logging of scikit-learn models and metrics
            evaluation_results = {}
            for model_name, model in models.items():
                log.info(f"Training model: {model_name}")
                print(f"Training model: {model_name}")
                trained_model = self.train_base_models(X_train, y_train, model)
                log.info(f"Evaluating model: {model_name}")
                metrics = self.model_evaluator.evaluate_model(trained_model, X_test, y_test)
                evaluation_results[model_name] = metrics
                log.info(f"Model: {model_name}, Evaluation Metrics: {metrics}")
                print(f"Model: {model_name}, Evaluation Metrics: {metrics}")

            log.info("Model training and evaluation pipeline completed successfully.")

            # save evaluation results to a file as csv
            log.info(f"Saving evaluation results to {Paths.EVALUATION_REPORT_FILE}...")
            os.makedirs(os.path.dirname(Paths.EVALUATION_REPORT_FILE), exist_ok=True)
            evaluation_df = pd.DataFrame(evaluation_results, index=["MSE", "MAE", "R2_Score"]).T
            self.utilities.save_dataset(df=evaluation_df, file_path=Paths.EVALUATION_REPORT_FILE)
            log.info(f"Evaluation results saved to {Paths.EVALUATION_REPORT_FILE} successfully.")
            print(f"Evaluation results saved to {Paths.EVALUATION_REPORT_FILE} successfully.")
            print("Full model training and evaluation pipeline completed successfully.")

            # find best model based on R2 score (R2 score is at index 2)
            best_model_name = max(evaluation_results, key=lambda x: evaluation_results[x][2])
            best_model_metrics = evaluation_results[best_model_name]
            log.info(f"Best model: {best_model_name}, Metrics: {best_model_metrics}")
            print(f"Best model: {best_model_name}, Metrics (MSE, MAE, R2): {best_model_metrics}")

            return best_model_name

        except Exception as e:
            log.error("Error occurred during full model training and evaluation pipeline: %s", str(e))
            raise CustomException(e, sys)

if __name__ == "__main__":
    print("Starting Model Training Pipeline (Base Models)...")
    trainer = ModelTrainer()
    utils = Utilities()
    target_file = Paths.PROCESSED_OUTPUT_FILE if os.path.exists(Paths.PROCESSED_OUTPUT_FILE) else Paths.OUTPUT_TARGETS_FILE
    if os.path.exists(Paths.PROCESSED_INPUT_FILE) and os.path.exists(target_file):
        X = utils.read_dataset(Paths.PROCESSED_INPUT_FILE)
        y = utils.read_dataset(target_file)
        if hasattr(y, 'squeeze'):
            y = y.squeeze()
        best_model = trainer.TrainerEvaluationPipeline(X, y, Models.models)
        print(f"Pipeline finished. Selected best base model: {best_model}")
    else:
        print("Dataset files not found. Run preprocessing first.")