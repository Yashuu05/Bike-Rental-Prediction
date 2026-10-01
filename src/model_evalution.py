# performs model evaluation on the trained model using the test dataset and saves the evaluation metrics to a file
import os 
import sys
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
from src.logger import logging as log
from src.exception import CustomException
from utils.utilities import Utilities

class ModelEvaluation:

    def __init__(self):
        self.utilities = Utilities()

    def evaluate_model(self, model, X_test, y_test):
        """
        Evaluates the trained model using the test dataset and saves the evaluation metrics to a file.

        Args:
            model: Trained model object
            X_test: Test features
            y_test: Test targets

        Returns:
            dict: Evaluation metrics
        """
        from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
        try:
            y_pred = model.predict(X_test)
            mse = mean_squared_error(y_test, y_pred)
            mae = mean_absolute_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            return [mse, mae, r2]

        except Exception as e:
            log.error("Error occurred during model evaluation: %s", str(e))
            raise CustomException(e, sys)