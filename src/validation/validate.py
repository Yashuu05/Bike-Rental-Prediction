# data validation script to validate the input and output datasets before ingestion to S3 bucket
import os
import sys
import pandas as pd
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)
from src.logger import logging as log
from src.exception import CustomException
from configs.paths import Paths
from utils.utilities import Utilities

class DataValidation:

    def __init__(self):
        self.utilities = Utilities()

    def validate_dataset(self, df: pd.DataFrame, schema_file: str = None) -> bool:
        """
        Validates the dataset against schema rules.
        Checks if dataset is not empty, all required columns exist, and data types are valid.

        Args:
            df (pd.DataFrame): dataset to validate
            schema_file (str, optional): path to schema YAML file

        Returns:
            bool: True if dataset is valid, False otherwise.
        """
        try:
            log.info("Starting dataset validation...")

            if df is None or df.empty:
                log.error("Dataset is empty or None.")
                raise ValueError("Dataset is empty or None.")

            if schema_file is None:
                schema_file = getattr(Paths, "DATA_SCHEMA_FILE", None)
                if not schema_file or not os.path.exists(schema_file):
                    possible_paths = [
                        os.path.join(project_root, "src", "validation", "data_schema.yml"),
                        os.path.join(project_root, "src", "validation", "data_schema.yaml"),
                        os.path.join(project_root, "configs", "schema.yaml")
                    ]
                    for path in possible_paths:
                        if os.path.exists(path):
                            schema_file = path
                            break

            if not schema_file or not os.path.exists(schema_file):
                log.warning("Data schema file not found. Skipping schema validation.")
                return True

            log.info(f"Data schema file found at {schema_file}. Reading schema...")
            schema = self.utilities.read_yaml_file(file_path=schema_file)

            columns_schema = schema.get("columns_data_types", {})
            input_features = schema.get("input_features", [])

            # Check missing columns
            df_cols_lower = {str(col).strip().lower(): col for col in df.columns}
            missing_columns = []
            type_mismatches = []

            for exp_col, exp_type in columns_schema.items():
                exp_col_cleaned = str(exp_col).strip()
                col_name_found = None
                
                if exp_col_cleaned in df.columns:
                    col_name_found = exp_col_cleaned
                elif exp_col_cleaned.lower() in df_cols_lower:
                    col_name_found = df_cols_lower[exp_col_cleaned.lower()]

                if col_name_found is None:
                    missing_columns.append(exp_col_cleaned)
                    continue

                # Check data type
                actual_dtype = df[col_name_found].dtype
                exp_type_str = str(exp_type).strip().lower()

                if "int" in exp_type_str or "float" in exp_type_str or "number" in exp_type_str:
                    if not pd.api.types.is_numeric_dtype(actual_dtype):
                        type_mismatches.append(f"Column '{col_name_found}': expected numeric ({exp_type}), got {actual_dtype}")
                elif "str" in exp_type_str or "object" in exp_type_str:
                    if not (pd.api.types.is_string_dtype(actual_dtype) or actual_dtype == 'object'):
                        type_mismatches.append(f"Column '{col_name_found}': expected string ({exp_type}), got {actual_dtype}")

            if missing_columns:
                log.error(f"Missing required columns: {missing_columns}")
                raise ValueError(f"Missing required columns: {missing_columns}")

            if type_mismatches:
                log.error(f"Data type mismatches found: {type_mismatches}")
                raise ValueError(f"Data type mismatches: {type_mismatches}")

            log.info("Dataset validation successful. All columns and types match schema.")
            return True

        except Exception as e:
            log.error("Error occurred during dataset validation: %s", str(e))
            raise CustomException(e, sys)

    def validate_datasets(self, df: pd.DataFrame, schema_file: str = None) -> bool:
        """Alias for validate_dataset."""
        return self.validate_dataset(df, schema_file)
