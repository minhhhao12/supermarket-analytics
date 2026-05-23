import os
import pandas as pd
from pandas import DataFrame

class DataLoader:
    def __init__(self, pathname: str):
        self.pathname = pathname

    def load_data(self) -> DataFrame:
        if self.pathname.lower().endswith('.csv'):
            read_file = pd.read_csv
            file_type = 'csv'
        elif self.pathname.lower().endswith(('.xlsx', '.xls')):
            read_file = pd.read_excel
            file_type = 'excel'
        else:
            raise ValueError('Lỗi định dạng file')
        if os.path.getsize(self.pathname) == 0:
            raise ValueError(f'File {self.pathname} có kích thước bằng 0')
        try:
            df = read_file(self.pathname)
            if df.empty:
                raise ValueError(f'File {file_type} rỗng')
            return df
        except FileNotFoundError:
            raise ValueError(f'Không tìm thấy file ở {self.pathname}')
        except Exception as ex:
            raise ValueError(f'Lỗi khi đọc file {file_type} ở {self.pathname}')
