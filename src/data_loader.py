import pandas as pd
import os
from pandas import DataFrame

class DataLoader:
    def __init__(self,pathname:str):
        self.pathname=pathname

    def load_csv(self)->DataFrame:
        if not self.pathname.lower().endswith('.csv'):
            raise ValueError(f'Lỗi định dạng file')
        if os.path.getsize(self.pathname)==0:
            raise ValueError(f'File {self.pathname} có kích thước bằng 0')
        try:
            df=pd.read_csv(self.pathname)
            if df.empty:
                raise ValueError('File csv rỗng')
            return df
        except FileNotFoundError:
            raise ValueError(f"Không tìm thấy file ở {self.pathname}")
        except Exception as ex:
            raise ValueError(f"Lỗi khi đọc file csv ở {self.pathname}")

    def load_excel(self)->DataFrame:
        if not self.pathname.lower().endswith(('.xlsx','.xls')):
            raise ValueError(f'Lỗi định dạng file')
        if os.path.getsize(self.pathname) == 0:
            raise ValueError(f'File {self.pathname} có kích thước bằng 0')
        try:
            df=pd.read_excel(self.pathname)
            if df.empty:
                raise ValueError('File excel rỗng')
            return df
        except FileNotFoundError:
            raise ValueError(f"Không tìm thấy file ở {self.pathname}")
        except Exception as ex:
            raise ValueError(f"Lỗi khi đọc file excel ở {self.pathname}")
