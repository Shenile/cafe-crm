import logging
import os
from colorama import init, Fore

# Initialize colorama for Windows compatibility
init(autoreset=True)

# Define log file path (ensuring it's in the project directory)
log_file = os.path.join(os.path.dirname(__file__), "app.log")

# Custom log formatter with color support (not needed for file logs)
class ColoredFormatter(logging.Formatter):
    COLORS = {
        logging.DEBUG: Fore.CYAN,  # Cyan for debug
        logging.INFO: Fore.GREEN,  # Green for info (success)
        logging.WARNING: Fore.YELLOW,  # Yellow for warnings
        logging.ERROR: Fore.RED,  # Red for errors
        logging.CRITICAL: Fore.MAGENTA,  # Magenta for critical errors
    }

    def format(self, record):
        log_message = super().format(record)
        return log_message  # No colors for file logging

# Configure logging (Only logs to file)
log_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

file_handler = logging.FileHandler(log_file)
file_handler.setFormatter(log_formatter)

logging.basicConfig(level=logging.INFO, handlers=[file_handler])  # No StreamHandler

# Create logger
logger = logging.getLogger(__name__)
