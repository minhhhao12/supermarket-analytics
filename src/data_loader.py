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
            raise ValueError('Lỗi định dạng file: Chỉ hỗ trợ định dạng .csv hoặc .xlsx/.xls')
        if not os.path.exists(self.pathname):
            raise FileNotFoundError(f'Không tìm thấy file tại đường dẫn: {self.pathname}')
        if os.path.getsize(self.pathname) == 0:
            raise ValueError(f'File {self.pathname} lỗi: Kích thước bằng 0 (File trống)')

        try:
            df = read_file(self.pathname)
        except Exception as ex:
            raise ValueError(f'Lỗi hệ thống khi đọc file {file_type} ở {self.pathname}. Chi tiết lỗi: {ex}')
        if df.empty:
            raise ValueError(f'File {file_type} rỗng: Không tìm thấy hàng dữ liệu nào.')


        from data_validator import DataValidator
        data_valid = DataValidator(df)
        error = data_valid.run_all_validators()
        if error:
            raise ValueError(f'Lỗi:{error}')
        return df