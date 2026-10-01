# training best model from train_1.py with hyperparameter tuning and saving the best model to a file
import os 
import sys 

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

from configs.paths import Paths
from src.logger import logging as log
from src.exception import CustomException
from utils.utilities import Utilities
from src.model_evalution import ModelEvaluation
from src.training.train_1 import ModelTrainer
from configs.models import Models

class HyperparameterTuner:

    def __init__(self):
        self.utilities = Utilities()
        self.model_evaluator = ModelEvaluation()
        self.model_trainer = ModelTrainer()

    def tune_hyperparameters(self, X, y, best_model_name: str, models: dict):
        """
        Tunes hyperparameters of the given model using GridSearchCV and saves the best model.

        Args:
            X: Training features
            y: Training targets
            best_model_name (str): Name of the model to tune
            models (dict): Dictionary of model names and their corresponding objects

        Returns:
            best_model: Model with the best hyperparameters found
        """
        from sklearn.model_selection import GridSearchCV
        try:
            if not os.path.exists(Paths.MODEL_CONFIG_FILE):
                log.error(f"Model configuration file not found at {Paths.MODEL_CONFIG_FILE}")
                raise FileNotFoundError(f"Model configuration file not found at {Paths.MODEL_CONFIG_FILE}")

            log.info(f"Reading model configuration from {Paths.MODEL_CONFIG_FILE}...")
            model_config = self.utilities.read_yaml_file(file_path=Paths.MODEL_CONFIG_FILE)

            if best_model_name not in models:
                log.error(f"Model '{best_model_name}' not found in the provided models dictionary.")
                raise ValueError(f"Model '{best_model_name}' not found in the provided models dictionary.")
            model = models[best_model_name]

            # Flexible hyperparameter extraction logic
            model_entry = model_config.get(best_model_name)
            if not model_entry:
                for sec_name, sec_val in model_config.items():
                    if isinstance(sec_val, dict) and sec_val.get("algorithm") == best_model_name:
                        model_entry = sec_val
                        break

            if not model_entry:
                log.error(f"Hyperparameter grid for model '{best_model_name}' not found in configuration.")
                raise ValueError(f"Hyperparameter grid for model '{best_model_name}' not found in configuration.")

            if isinstance(model_entry, dict) and "hyperparameters" in model_entry:
                raw_params = model_entry["hyperparameters"]
            elif isinstance(model_entry, dict):
                raw_params = model_entry
            else:
                raw_params = {}

            # Convert parameters into dictionary with list of values for GridSearchCV
            params = {}
            for key, value in raw_params.items():
                if key == "algorithm":
                    continue
                if isinstance(value, list):
                    params[key] = value
                else:
                    params[key] = [value]
            
            log.info(f"Hyperparameter grid for model '{best_model_name}': {params}")

            # split dataset into train and test sets
            log.info("Splitting dataset into training and testing sets...")
            X_train, X_test, y_train, y_test = self.utilities.split_dataset(X, y)
            log.info("Dataset split completed successfully.")

            # start hyperparameter tuning using GridSearchCV
            log.info("Starting hyperparameter tuning...")
            grid_search = GridSearchCV(estimator=model, param_grid=params, cv=5, scoring='r2', n_jobs=-1)
            grid_search.fit(X_train, y_train)
            best_model = grid_search.best_estimator_
            best_params = grid_search.best_params_
            log.info(f"Hyperparameter tuning completed. Best parameters: {best_params}")
            print(f"Hyperparameter tuning completed. Best parameters for {best_model_name}: {best_params}")

            # Evaluate tuned model
            metrics = self.model_evaluator.evaluate_model(best_model, X_test, y_test)
            log.info(f"Tuned model evaluation metrics (MSE, MAE, R2): {metrics}")
            print(f"Tuned model evaluation metrics (MSE, MAE, R2): {metrics}")
            
            return best_model

        except Exception as e:
            log.error("Error occurred during hyperparameter tuning: %s", str(e))
            raise CustomException(e, sys)

if __name__ == "__main__":
    print("Starting Hyperparameter Tuning Pipeline...")
    tuner = HyperparameterTuner()
    trainer = ModelTrainer()
    utils = Utilities()
    target_file = Paths.PROCESSED_OUTPUT_FILE if os.path.exists(Paths.PROCESSED_OUTPUT_FILE) else Paths.OUTPUT_TARGETS_FILE
    if os.path.exists(Paths.PROCESSED_INPUT_FILE) and os.path.exists(target_file):
        X = utils.read_dataset(Paths.PROCESSED_INPUT_FILE)
        y = utils.read_dataset(target_file)
        if hasattr(y, 'squeeze'):
            y = y.squeeze()
        print("1. Running base model selection pipeline...")
        best_model_name = trainer.TrainerEvaluationPipeline(X, y, Models.models)
        print(f"2. Tuning hyperparameters for selected best model: {best_model_name}...")
        best_tuned_model = tuner.tune_hyperparameters(X, y, best_model_name, Models.models)
        print("Hyperparameter tuning pipeline completed successfully.")
    else:
        print("Dataset files not found. Run preprocessing first.")

