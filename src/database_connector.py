import os
from dotenv import load_dotenv
import pandas as pd
from sqlalchemy import create_engine, text

class DatabaseConnector:
    def __init__(self):
        load_dotenv()
        self.db_url = os.getenv("DATABASE_URL")
        if not self.db_url:
            raise ValueError("DATABASE_URL not found in .env file")

        if self.db_url.startswith("sqlite:///"):
            db_file = self.db_url[len("sqlite:///"):]
            os.makedirs(os.path.dirname(db_file) or '.', exist_ok=True)

        self.engine = create_engine(self.db_url)



    def fetch_data_to_dataframe(self, table_name: str = "sales_data") -> pd.DataFrame:

        try:
            query = text(f"SELECT * FROM {table_name}")
            with self.engine.connect() as connection:
                df = pd.read_sql(query, connection)
            print(f"Successfully fetched {len(df)} rows from {table_name}")
            return df
        except Exception as e:
            print(f"Error fetching data from database: {e}")
            return pd.DataFrame()

