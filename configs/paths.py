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
    PROCESSED_DATA_FILE = os.path.join(DATA_DIR, "processed_data.csv")
    MODEL_DIR = os.path.join(project_root, "models")
