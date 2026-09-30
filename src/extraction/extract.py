# extract or import dataset from offiical dataset source
import os 
import sys 
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)
from src.logger import logging
from src.exception import CustomException
from configs.paths import Paths

class Extractor:
    def __init__(self):
        pass

    def extract(self) -> tuple:
        # Implement the logic to extract or import the dataset from the official source
        from ucimlrepo import fetch_ucirepo 
        try:
            # fetch dataset 
            logging.info("Fetching the Seoul Bike Sharing Demand dataset from UCI Machine Learning Repository...")
            seoul_bike_sharing_demand = fetch_ucirepo(id=560) 
  
            # data (as pandas dataframes) 
            X = seoul_bike_sharing_demand.data.features 
            y = seoul_bike_sharing_demand.data.targets 
            # metadata 
            print("\nSouel Bike Sharing Demand Dataset Metadata:")
            print(seoul_bike_sharing_demand.metadata) 
              
            # variable information 
            print("\nSouel Bike Sharing Demand Dataset Variable Information:")
            print(seoul_bike_sharing_demand.variables) 

            return X, y
        
        except Exception as e:
            logging.error("Error occurred while fetching dataset: %s", str(e))
            raise CustomException(e, sys)
  

    def extract_and_save(self):
        try:
            X, y = self.extract()
            # Save the extracted data to CSV files
            logging.info("Saving extracted data to CSV files...")
            os.makedirs(Paths.DATA_DIR, exist_ok=True)
            X.to_csv(Paths.INPUT_FEATURES_FILE, index=False)
            y.to_csv(Paths.OUTPUT_TARGETS_FILE, index=False)
            logging.info("Data extraction and saving completed successfully.")
        except Exception as e:
            logging.error("Error occurred while extracting and saving data: %s", str(e))
            raise CustomException(e, sys)


if __name__ == "__main__":
    extractor = Extractor()
    extractor.extract_and_save()
    print("extraction and saving completed successfully.")