import pandas as pd
from sqlalchemy import create_engine
import os

def setup_sqlite_db(csv_file_path: str, db_file_path: str, table_name: str = "sales_data"):
    """
    Reads a CSV file and loads its content into a SQLite database table.
    """
    if not os.path.exists(csv_file_path):
        print(f"Error: CSV file not found at {csv_file_path}")
        return

    try:
        df = pd.read_csv(csv_file_path)
        print(f"Successfully read {len(df)} rows from {csv_file_path}")

        # Create a SQLite engine
        # The triple slash /// indicates a relative path to the database file
        # For an absolute path, it would be sqlite:////absolute/path/to/your.db
        engine = create_engine(f'sqlite:///{db_file_path}')

        # Write the DataFrame to the SQLite table
        # if_exists='replace' will overwrite the table if it already exists
        # if_exists='append' will add new rows to the table
        # if_exists='fail' will raise an error if the table exists
        df.to_sql(table_name, engine, if_exists='replace', index=False)
        print(f"Successfully loaded data into SQLite table '{table_name}' in '{db_file_path}'")

    except Exception as e:
        print(f"Error setting up SQLite database: {e}")

if __name__ == "__main__":
    # Define your CSV file path and desired SQLite database file path
    # Make sure 'your_sales_data.csv' exists in your project root or specify the full path
    csv_source_path = "../data/raw/supermarket_data_sales.csv" # Replace with your actual CSV file name/path
    sqlite_db_path = "../data/supermarket_data.db"  # Name of your SQLite database file
    table_name = "sales_data" # Name of the table inside the database

    setup_sqlite_db(csv_source_path, sqlite_db_path, table_name)