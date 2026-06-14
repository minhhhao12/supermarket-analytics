import pandas as pd
from faker import Faker
import random
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
import time
from datetime import datetime, timedelta

# Khởi tạo Faker để tạo dữ liệu giả
fake = Faker()

# ==============================================================================
# ĐỊNH NGHĨA DỮ LIỆU MẪU DỰA TRÊN FILE supermarket_data_sales.csv
# ==============================================================================
BRANCHES = {
    'A': 'TP. Hồ Chí Minh',
    'B': 'Đà Nẵng',
    'C': 'Hà Nội'
}
BRANCH_NAMES = {
    'A': 'CN Quận 1',
    'B': 'CN Hải Châu',
    'C': 'CN Cầu Giấy'
}
PRODUCT_LINES = [
    'Sức khoẻ và làm đẹp',
    'Phụ kiện điện tử',
    'Nhà cửa và đời sống',
    'Thể thao và du lịch',
    'Thực phẩm và đồ uống',
    'Phụ kiện thời trang'
]
PAYMENT_METHODS = ['Ví điện tử (Momo/Zalopay)', 'Tiền mặt', 'Thẻ ngân hàng']
CUSTOMER_TYPES = ['Thành viên', 'Khách thường']
GENDERS = ['Nam', 'Nữ']

def generate_single_order(last_invoice_id_parts):
    """Tạo ra một bản ghi đơn hàng giả."""
    branch_code = random.choice(list(BRANCHES.keys()))
    city = BRANCHES[branch_code]
    branch_name = BRANCH_NAMES[branch_code]

    unit_price = round(random.uniform(50000, 500000))
    quantity = random.randint(1, 10)

    cogs = round(unit_price * quantity)
    tax = round(cogs * 0.05)
    total = round(cogs + tax)
    gross_income = tax

    now = datetime.now()
    random_date = now - timedelta(days=random.randint(0, 90))
    random_time_obj = datetime.strptime(fake.time(), '%H:%M:%S').time()

    # Tạo Invoice ID mới dựa trên ID cuối cùng
    if last_invoice_id_parts:
        new_part1 = last_invoice_id_parts[0] + random.randint(1, 5)
        new_part2 = last_invoice_id_parts[1] + random.randint(1, 5)
        new_part3 = last_invoice_id_parts[2] + random.randint(1, 5)
    else: # Nếu không có hóa đơn nào, tạo ngẫu nhiên
        new_part1 = random.randint(100, 999)
        new_part2 = random.randint(10, 99)
        new_part3 = random.randint(1000, 9999)

    invoice_id = f"{new_part1}-{new_part2}-{new_part3}"

    return {
        'Invoice ID': invoice_id,
        'Branch': branch_name,
        'City': city,
        'Customer type': random.choice(CUSTOMER_TYPES),
        'Gender': random.choice(GENDERS),
        'Product line': random.choice(PRODUCT_LINES),
        'Unit price': float(unit_price),
        'Quantity': quantity,
        'Tax 5%': float(tax),
        'Sales': float(total),  # Đổi tên cột 'Total' thành 'Sales'
        'Date': random_date.strftime('%Y-%m-%d'),
        'Time': random_time_obj.strftime('%I:%M:%S %p'),
        'Payment': random.choice(PAYMENT_METHODS),
        'cogs': float(cogs),
        'gross margin percentage': round((gross_income / total) * 100, 9) if total > 0 else 0,
        'gross income': float(gross_income),
        'Rating': round(random.uniform(4.0, 10.0), 1)
    }

def get_last_invoice_id(engine, table_name="sales_data"):
    """Lấy ID hóa đơn cuối cùng từ database."""
    try:
        with engine.connect() as connection:
            query = text(f'SELECT "Invoice ID" FROM {table_name} ORDER BY ROWID DESC LIMIT 1')
            result = connection.execute(query).scalar_one_or_none()
            if result:
                parts = [int(p) for p in result.split('-')]
                return parts
            return None
    except Exception as e:
        print(f"Không thể lấy Invoice ID cuối cùng (có thể bảng chưa tồn tại): {e}")
        return None

def simulate_orders(db_url: str, num_orders: int = 5, table_name: str = "sales_data"):
    """
    Giả lập việc tạo ra các đơn hàng mới và thêm chúng vào database.
    """
    if not db_url:
        print("Lỗi: DATABASE_URL không được tìm thấy. Hãy chắc chắn file .env đã được cấu hình.")
        return

    try:
        engine = create_engine(db_url)
        last_invoice_id_parts = get_last_invoice_id(engine, table_name)

        new_orders = []
        for i in range(num_orders):
            order = generate_single_order(last_invoice_id_parts)
            new_orders.append(order)
            print(f"Đã tạo đơn hàng: {order['Invoice ID']} - {order['Product line']} - Tổng: {order['Sales']}")
            # Cập nhật ID cho lần lặp tiếp theo
            last_invoice_id_parts = [int(p) for p in order['Invoice ID'].split('-')]


        if new_orders:
            df_new_orders = pd.DataFrame(new_orders)
            df_new_orders.to_sql(table_name, engine, if_exists='append', index=False)
            print(f"\nThành công! Đã thêm {len(new_orders)} đơn hàng mới vào bảng '{table_name}'.")
            print("Dashboard sẽ tự động cập nhật trong lần làm mới tiếp theo.")

    except Exception as e:
        print(f"Đã xảy ra lỗi trong quá trình giả lập: {e}")

if __name__ == "__main__":
    load_dotenv()
    DATABASE_URL = os.getenv("DATABASE_URL")

    try:
        while True:
            number_of_new_orders = random.randint(1, 3)
            simulate_orders(DATABASE_URL, num_orders=number_of_new_orders)
            sleep_time = random.randint(15, 45)
            print(f"--- Sẽ tạo đơn hàng tiếp theo sau {sleep_time} giây. Nhấn Ctrl+C để dừng. ---\n")
            time.sleep(sleep_time)
            
    except KeyboardInterrupt:
        print("\nĐã dừng giả lập đơn hàng.")