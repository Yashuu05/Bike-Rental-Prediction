import os 
import sys
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
from src.logger import logging

if __name__ == "__main__":
    logging.info("initial log testing message.")
    try:
        a = 1 / 0
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    
    print("Testing complete. Check the logs folder.")
