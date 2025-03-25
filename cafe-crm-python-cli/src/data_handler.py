from datetime import datetime
from sqlalchemy.types import Enum


class DataHandler:

    def __init__(self):
        pass

    @staticmethod
    def get_int(prompt):
        """Prompt user for an integer input and validate."""
        while True:
            try:
                return int(input(prompt))
            except ValueError:
                print("Invalid input. Please enter a valid integer.")

    @staticmethod
    def get_float(prompt):
        """Prompt user for a float input and validate."""
        while True:
            try:
                return float(input(prompt))
            except ValueError:
                print("Invalid input. Please enter a valid float.")

    @staticmethod
    def get_bool(prompt):
        """Prompt user for a boolean input and validate."""
        while True:
            val = input(prompt).strip().lower()
            if val in ["true", "1", "yes", "y"]:
                return True
            elif val in ["false", "0", "no", "n"]:
                return False
            else:
                print("Invalid input. Enter 'yes' or 'no'.")

    @staticmethod
    def sql_date_validator(date_str):
        """Validate an SQL DATE format (YYYY-MM-DD)."""
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    @staticmethod
    def get_date(prompt):
        """Prompt user for a valid date input."""
        while True:
            date_str = input(prompt)
            if DataHandler.sql_date_validator(date_str):
                return date_str
            print("Invalid date format. Please enter in YYYY-MM-DD format.")

    @staticmethod
    def is_enum(val, enum_type):
        """Check if a value is a valid ENUM choice."""
        return isinstance(enum_type, Enum) and val in enum_type.enums

    @staticmethod
    def get_enum(prompt, enum_type):
        """Prompt user for an ENUM input, automatically displaying available options."""
        if not isinstance(enum_type, Enum):
            raise ValueError("Provided type is not a valid SQLAlchemy Enum.")

        enum_values = enum_type.enums  # Extract ENUM options

        while True:
            print(f"Available options: {', '.join(enum_values)}")
            val = input(f"{prompt} (Choose one from above): ").strip()
            if val in enum_values:
                return val
            print(f"Invalid choice. Please choose from: {', '.join(enum_values)}")

    @staticmethod
    def get_string(prompt, max_length=None):
        """Prompt user for a string input and validate its length."""
        while True:
            val = input(prompt).strip()
            if max_length and len(val) > max_length:
                print(f"Input too long. Maximum length is {max_length} characters.")
            else:
                return val


    @staticmethod
    def get_timestamp(prompt):
        """Prompt user for a valid timestamp input or use the current time."""
        while True:
            val = input(f"{prompt} (Press Enter for current time): ").strip()
            if not val:  # Use current timestamp if input is empty
                return datetime.now()
            try:
                return datetime.strptime(val, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                print("Invalid timestamp format. Use YYYY-MM-DD HH:MM:SS.")

