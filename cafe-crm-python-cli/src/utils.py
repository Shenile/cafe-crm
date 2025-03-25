from sqlalchemy import Enum
from src.data_handler import DataHandler
import os
import time
from rich.console import Console
from rich.table import Table

console = Console()

helpers_map = {
        "VARCHAR": DataHandler.get_string,
        "DATE": DataHandler.get_date,
        "INTEGER": DataHandler.get_int,
        "BOOLEAN": DataHandler.get_bool,
        "ENUM": DataHandler.get_enum,
        "DECIMAL": DataHandler.get_float,
        "TIMESTAMP": DataHandler.get_timestamp,
        "DATETIME": DataHandler.get_timestamp,
        "TEXT": DataHandler.get_string,
        "TINYINT": DataHandler.get_int
}

def is_junction_table(cols):
    pk_counter = 0
    for col in cols:
        if pk_counter > 1:
            return True

        if col.primary_key:
            pk_counter += 1
    return False

def cls_decorator(func):
    def wrapper(*args, **kwargs):
        func(*args, **kwargs)
        os.system('cls')
    return wrapper

def render_as_table(title, data):
    """Renders a list of dictionaries as a formatted table using rich."""
    if not data:
        print("No data available to display.")
        return

    table = Table(title=title)

    # Add columns dynamically from dictionary keys
    for col in data[0].keys():
        table.add_column(str(col), style="bold cyan")

    # Add rows dynamically from dictionary values
    for dt in data:
        table.add_row(*[str(value) for value in dt.values()])

    # Render the table
    console = Console()
    console.print(table)

def apply_discount(total_price, discount_value, discount_type):
    try:
        if not isinstance(total_price, (int, float)) or not isinstance(discount_value, (int, float)):
            raise ValueError("total_price and discount_value must be integers or floats.")

        if not isinstance(discount_type, str):
            raise ValueError("discount_type should be a string value.")

        match discount_type:
            case "flat":
                return total_price - discount_value if discount_value <= total_price else 0
            case "percentage":
                if 0 < discount_value <= 100:  # Now supports percentage as a whole number (e.g., 10 for 10%)
                    return float(total_price - (discount_value / 100 * total_price))
                else:
                    raise ValueError("Percentage discount should be between 0 and 100.")
            case _:
                raise ValueError("Invalid discount type. Use 'flat' or 'percentage'.")
    except Exception as err:
        raise err

def add_row(cols, skip_columns=None):
    if skip_columns is None:
        skip_columns = []

    input_cols = cols
    if not is_junction_table(cols):
        input_cols = [col for col in cols if not col.primary_key and col.name not in skip_columns]

    input_data = {}

    for col in input_cols:
        if col.name in skip_columns:
            continue

        col_type = str(col.type).upper()  # Convert column type to uppercase for lookup
        prompt = f"Enter value for {col.name} ({col.type}): "

        # Handle ENUM separately
        if isinstance(col.type, Enum):
            input_data[col.name] = DataHandler.get_enum(prompt, col.type)
        else:
            # Find the corresponding helper function in helpers_map
            for key, func in helpers_map.items():
                if key in col_type:
                    input_data[col.name] = func(prompt)
                    break
            else:
                print(f"Unsupported data type: {col.type}")

    return input_data

# To convert points to cash
def points_to_cash(points, conversion_rate):
    try:
        if not isinstance(points, int):
            raise ValueError("points must be an integer.")

        if not isinstance(conversion_rate, (int, float)):
            raise ValueError("conversion_rate must be an integer or float.")

        return points * conversion_rate
    except Exception as err:
        raise err

def display_data(customer=None, order=None, order_items=None, order_bill=None, rewards=None):
    """Dynamically updates CLI to show transaction progress"""
    os.system('cls' if os.name == 'nt' else 'clear')  # Clear CLI screen

    print("\n========= TRANSACTION DETAILS =========")

    if customer:
        render_as_table("Customer Data", [customer])

    if order:
        render_as_table("Order Details", [order])

    if order_items:
        render_as_table("Item Details", order_items)

    if order_bill:
        render_as_table("Order Bill", order_bill)

    if rewards:
        print(f"Rewards : {rewards}")

    print("\n=======================================")
    time.sleep(1)