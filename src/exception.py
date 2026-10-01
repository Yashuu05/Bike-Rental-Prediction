import sys
import os

class CustomException(Exception):
    def __init__(self, message, filename=None, lineno=None):
        if hasattr(filename, 'exc_info'):
            # Second argument is sys module (e.g. CustomException(e, sys))
            _, _, exc_tb = filename.exc_info()
            if exc_tb is not None:
                self.filename = os.path.basename(exc_tb.tb_frame.f_code.co_filename)
                self.lineno = exc_tb.tb_lineno
            else:
                self.filename = "unknown"
                self.lineno = 0
            self.message = str(message)
        elif filename is not None and lineno is not None:
            # Explicit parameters (message, filename, lineno)
            self.message = str(message)
            self.filename = filename
            self.lineno = lineno
        else:
            # Fallback to sys.exc_info()
            _, _, exc_tb = sys.exc_info()
            if exc_tb is not None:
                self.filename = os.path.basename(exc_tb.tb_frame.f_code.co_filename)
                self.lineno = exc_tb.tb_lineno
            else:
                self.filename = str(filename or "unknown")
                self.lineno = lineno or 0
            self.message = str(message)

        super().__init__(self.message)

    def __str__(self):
        return f"{self.message} in {self.filename} at line {self.lineno}"