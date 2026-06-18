import os
from dotenv import load_dotenv
import pandas as pd
from sqlalchemy import create_engine, text

class DatabaseConnector:
    def __init__(self):
        load_dotenv()
        self.db_url = os.getenv("DATABASE_URL")
        if not self.db_url:
            raise ValueError("Không tìm thấy file .env")

        if self.db_url.startswith("sqlite:///"):
            db_file = self.db_url[len("sqlite:///"):]
            os.makedirs(os.path.dirname(db_file) or '.', exist_ok=True)

        self.engine = create_engine(self.db_url)



    def fetch_data_to_dataframe(self, table_name: str = "sales_data") -> pd.DataFrame:

        try:
            query = text(f"SELECT * FROM {table_name}")
            with self.engine.connect() as connection:
                df = pd.read_sql(query, connection)
            print(f"Đọc thành công {len(df)} dòng từ database {table_name}")
            return df
        except Exception as e:
            print(f"Lỗi khi đọc dữ liệu: {e}")
            return pd.DataFrame()

    def write_dataframe_to_table(self, df: pd.DataFrame, table_name: str):
        try:
            with self.engine.connect() as connection:
                df.to_sql(table_name, connection, if_exists='replace', index=False)
            print(f"Ghi thành công {len(df)} dòng vào bảng '{table_name}'.")
            return True
        except Exception as e:
            print(f"Lỗi khi ghi dữ liệu vào bảng '{table_name}': {e}")
            return False