import os 
import sys 
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
from src.logger import logging
from src.exception import CustomException

def test_custom_exception():
    try:
        try:
            a = 10
            b = 0
            print("Attempting to divide by zero...")
            c = a / b  # This will raise a ZeroDivisionError
        except Exception as e:
            # We catch the base exception and raise our CustomException
            exc_type, exc_value, exc_tb = sys.exc_info()
            filename = os.path.basename(exc_tb.tb_frame.f_code.co_filename)
            lineno = exc_tb.tb_lineno
            raise CustomException("Zero division error", filename, lineno)

    except CustomException as e:
        logging.error(str(e))
        print(f"CustomException caught: {e}")
        assert "Zero division error" in str(e)

if __name__ == "__main__":
    test_custom_exception()
    print("Test completed. Check the logs folder for details.")