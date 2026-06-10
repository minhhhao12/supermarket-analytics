import sqlite3
import pandas as pd
import os

class DatabaseManager:
    def __init__(self, db_name='supermarket.db'):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(base_dir, 'data')
        os.makedirs(data_dir, exist_ok=True)
        self.db_path = os.path.join(data_dir, db_name)

    def save_to_db(self, df: pd.DataFrame, table_name='sales_data'):
        with sqlite3.connect(self.db_path) as conn:
            df.to_sql(table_name, conn, if_exists='replace', index=False)

    def append_to_db(self, df: pd.DataFrame, table_name='sales_data'):
        with sqlite3.connect(self.db_path) as conn:
            df.to_sql(table_name, conn, if_exists='append', index=False)

    def load_from_db(self, table_name='sales_data') -> pd.DataFrame:
        with sqlite3.connect(self.db_path) as conn:
            df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
        return df