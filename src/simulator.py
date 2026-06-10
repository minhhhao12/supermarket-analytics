import pandas as pd
import random
from datetime import datetime
import time
from database import DatabaseManager

def simulate_realtime_sales():
    db = DatabaseManager()
    try:
        df = db.load_from_db()
        if df.empty:
            print("Database rỗng. Vui lòng chạy giao diện và tải file CSV lên trước!")
            return
    except Exception as e:
        print(f"Lỗi: Không thể tải DB ({e}). Hãy tải file CSV lên giao diện trước!")
        return

    print("Đang chạy giả lập đơn hàng Real-time... (Bấm Ctrl+C để dừng)")
    try:
        while True:
            sample_row = df.sample(1).copy()
            now = datetime.now()
            sample_row['Date'] = now.strftime('%Y-%m-%d')
            sample_row['Time'] = now.strftime('%H:%M:%S')
            sample_row['Invoice ID'] = f"SIM-{random.randint(10000, 99999)}"
            
            db.append_to_db(sample_row)
            print(f"[{now.strftime('%H:%M:%S')}] Đã xuất hóa đơn mới: {sample_row['Invoice ID'].values[0]} | Doanh thu: ${sample_row['Sales'].values[0]:.2f}")
            time.sleep(random.randint(5, 10)) # Đợi 5-10 giây cho đơn tiếp theo
    except KeyboardInterrupt:
        print("\nĐã dừng giả lập.")

if __name__ == "__main__":
    simulate_realtime_sales()