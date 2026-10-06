"""
## Bike Rental Demand Prediction MLOps DAG

This Apache Airflow DAG orchestrates the automated end-to-end Machine Learning pipeline
for the Bike Rental Demand Prediction project.

### Pipeline Architecture:
1. **start_pipeline** (EmptyOperator): Initialization marker for DAG execution.
2. **run_etl_pipeline** (@task):
   - Extracts raw data from external sources/storage.
   - Cleans, transforms, and preprocesses feature columns and target variables.
   - Saves processed datasets (`input_features.csv`, `target_values.csv`) and `preprocessor.joblib`.
   - Ingests datasets and preprocessor to AWS S3.
   - Updates `bike_rental_processed_data` Asset.
3. **run_model_training_pipeline** (@task):
   - Downloads preprocessed features and targets from AWS S3.
   - Reads model configurations.
   - Runs cross-validation and candidate model training with MLflow tracking.
   - Evaluates performance metrics (R2, RMSE, MAE) and selects the best model.
   - Pushes the best model artifact to AWS S3 (`models/best_model.joblib`).
   - Updates `bike_rental_trained_model` Asset.
4. **end_pipeline** (EmptyOperator): Completion marker confirming pipeline success.

### Dependencies:
start_pipeline >> run_etl_pipeline >> run_model_training_pipeline >> end_pipeline
"""

import os
import sys
from datetime import timedelta

# Ensure project root is available in sys.path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

# Handle datetime/pendulum compatibility across environments
try:
    from pendulum import datetime
except ImportError:
    from datetime import datetime

# Handle Airflow imports (Astro Airflow SDK / Airflow 3 and Airflow 2 TaskFlow API)
try:
    from airflow.sdk import Asset, dag, task
except ImportError:
    from airflow.decorators import dag, task
    try:
        from airflow.datasets import Dataset as Asset
    except ImportError:
        Asset = None

# Empty/Dummy Operator for start/end pipeline markers
try:
    from airflow.providers.standard.operators.empty import EmptyOperator
except ImportError:
    try:
        from airflow.operators.empty import EmptyOperator
    except ImportError:
        from airflow.operators.dummy import DummyOperator as EmptyOperator


# Default task arguments
default_args = {
    "owner": "Astro",
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
}


@dag(
    dag_id="bike_rental_demand_prediction_dag",
    start_date=datetime(2025, 1, 1),
    schedule="@daily",
    catchup=False,
    default_args=default_args,
    doc_md=__doc__,
    tags=["bike-rental", "mlops", "etl", "model-training"],
)
def bike_rent_demand_prediction_dag():
    """
    Main DAG definition using Airflow TaskFlow API.
    """

    # Start marker
    start_pipeline = EmptyOperator(task_id="start_pipeline")

    # Task 1: ETL Pipeline
    @task(
        task_id="run_etl_pipeline",
        outlets=[Asset("bike_rental_processed_data")] if Asset else [],
    )
    def run_etl_pipeline(**context) -> dict:
        """
        Executes raw dataset extraction, preprocessing, and S3 ingestion.
        """
        from src.etl import ETLPipeline
        from src.logger import logging as log

        log.info("Starting Bike Rental ETL Pipeline execution via Airflow task...")
        etl = ETLPipeline()
        etl.complete_etl_pipeline()
        log.info("ETL Pipeline completed successfully.")

        return {
            "status": "success",
            "stage": "ETL",
            "message": "Data preprocessed and ingested to AWS S3",
        }

    # Task 2: Model Training, Evaluation & Pusher Pipeline
    @task(
        task_id="run_model_training_pipeline",
        outlets=[Asset("bike_rental_trained_model")] if Asset else [],
    )
    def run_model_training_pipeline(etl_result: dict, **context) -> dict:
        """
        Executes model training, evaluation with MLflow, and pushes best model to S3.
        """
        from src.full_model_train_pipeline import Model_trainer_pusher
        from src.logger import logging as log

        log.info(f"Received ETL upstream status: {etl_result.get('status')}")
        log.info("Starting Model Training and Pusher Pipeline via Airflow task...")

        trainer = Model_trainer_pusher()
        trainer.FullPipeline()
        log.info("Model training, evaluation, and S3 push completed successfully.")

        return {
            "status": "success",
            "stage": "Model_Training",
            "message": "Best model evaluated and uploaded to AWS S3",
        }

    # End marker
    end_pipeline = EmptyOperator(task_id="end_pipeline")

    # Define task dependencies
    etl_output = run_etl_pipeline()
    training_output = run_model_training_pipeline(etl_result=etl_output)

    start_pipeline >> etl_output
    training_output >> end_pipeline


# Instantiate the DAG
bike_rental_dag = bike_rent_demand_prediction_dag()
