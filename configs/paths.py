# paths of files and directories
import os
import sys
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

class Paths:
    # Define paths for various files and directories
    LOGS_DIR = os.path.join(project_root, "logs")
    DATA_DIR = os.path.join(project_root, "data")
    INPUT_FEATURES_FILE = os.path.join(DATA_DIR, "raw","input_features.csv")
    OUTPUT_TARGETS_FILE = os.path.join(DATA_DIR, "raw","output_targets.csv")
    PROCESSED_DATA_FILE = os.path.join(DATA_DIR, "processed")
    PROCESSED_INPUT_FILE = os.path.join(PROCESSED_DATA_FILE, "processed_inputs.csv")
    PROCESSED_OUTPUT_FILE = os.path.join(PROCESSED_DATA_FILE, "processed_output.csv")
    PREPROCESSOR_SAVE_FILE = os.path.join(project_root, "models", "preprocessor.joblib")
    MODEL_SAVE_PATH = os.path.join(project_root, "models", "model.joblib")
    DATA_SCHEMA_FILE = os.path.join(project_root, "src", "validation", "data_schema.yml")
    EVALUATION_REPORT_FILE = os.path.join(project_root, "reports", "evaluation_report.yaml")
    MODEL_CONFIG_FILE = os.path.join(project_root, "configs", "model_config.yaml")
    SAMPLE_DATASET_PATH = os.path.join(DATA_DIR, "sample", "sample_dataset.csv")
    PREDICTED_OUTPUT_PATH = os.path.join("reports","pr")