# TODO 1: Viết hàm load_csv() và load_excel() sử dụng thư viện pandas để đọc file từ thư mục data/raw/.
# TODO 2: Thêm logic try...except để báo lỗi nếu đường dẫn file không tồn tại.
# TODO 3: Viết hàm kiểm tra xem dữ liệu nạp vào có bị trống không (trả về lỗi nếu file rỗng).
import pandas as pd
import os
from pandas import DataFrame


def load_csv(path:str)->DataFrame:
    if not path.lower().endswith('.csv'):
        raise ValueError(f'Lỗi định dạng file')
    if os.path.getsize(path)==0:
        raise ValueError(f'File {path} có kích thước bằng 0')
    try:
        df=pd.read_csv(path)
        if df.empty:
            raise ValueError('File csv rỗng')
        return df
    except FileNotFoundError:
        raise ValueError(f"Không tìm thấy file ở {path}")
    except Exception as ex:
        raise ValueError(f"Lỗi khi đọc file csv ở {path}")

def load_excel(path:str)->DataFrame:
    if not path.lower().endswith(('.xlsx','.xls')):
        raise ValueError(f'Lỗi định dạng file')
    if os.path.getsize(path) == 0:
        raise ValueError(f'File {path} có kích thước bằng 0')
    try:
        df=pd.read_excel(path)
        if df.empty:
            raise ValueError('File excel rỗng')
        return df
    except FileNotFoundError:
        raise ValueError(f"Không tìm thấy file ở {path}")
    except Exception as ex:
        raise ValueError(f"Lỗi khi đọc file excel ở {path}")
