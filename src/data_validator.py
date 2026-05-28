import pandas as pd

# Kiểm tra lỗi vật lý
    # Số lượng (Quantity) phải > 0
    # Đơn giá (Unit price) phải >= 0
    # Doanh thu (Sales) phải >= 0
def validate_raw_data(df):
    errors = []

    # Định nghĩa danh sách các tên cột
    required_cols = ["Quantity", "Unit price", "Sales"]
    missing_cols = []

    for col in required_cols:
        if col not in df.columns:
            missing_cols.append(col)

    # Nếu thiếu cột thì báo lỗi và dừng hàm
    if len(missing_cols) > 0:
        errors.append(f"File dữ liệu bị thiếu các cột bắt buộc: {', '.join(missing_cols)}")
        return errors
    
    # Kiểm tra lỗi Số lượng (Quantity) <= 0
    invalid_quantity = df[df["Quantity"] <= 0]
    if not invalid_quantity.empty:
        errors.append(f"Có {len(invalid_quantity)} dòng có Quantity <= 0. Ví dụ tại dòng index: {list(invalid_quantity.index[:3])}")
    
    # Kiểm tra lỗi Đơn giá (Unit price) < 0
    invalid_price = df[df["Unit price"] < 0]
    if not invalid_price.empty:
        errors.append(f"Có {len(invalid_price)} dòng có Unit price < 0. Ví dụ tại dòng index: {list(invalid_price.index[:3])}")

    # Kiểm tra lỗi Doanh thu (Sales) < 0
    invalid_sales = df[df["Sales"] < 0]
    if not invalid_sales.empty:
        errors.append(f"Có {len(invalid_sales)} dòng có Sales < 0. Ví dụ tại dòng index: {list(invalid_sales.index[:3])}")
    return errors


# Kiểm tra logic tiền tệ (Thuế mặc định là 10%)
def check_currency_logic(df, tax_rate=0.1):
    errors = []

    # Kiểm tra file có đủ 3 cột trước khi tính toán
    if "Quantity" not in df.columns or "Unit price" not in df.columns or "Sales" not in df.columns:
        return errors

    # Doanh thu lý thuyết: Số lượng * Đơn giá * (1 + tax_rate)
    theoretical_sales = df["Quantity"] * df["Unit price"] * (1 + tax_rate)

    # kiểm tra mức chênh lệch giữa doanh thu thực tế và doanh thu lý thuyết 
    diff = (df["Sales"] - theoretical_sales).abs()

    # Lọc các dòng dữ liệu có mức chênh lệch lớn hơn 1
    invalid_sales = df[diff > 1.0]

    if not invalid_sales.empty:
        errors.append(f"Có {len(invalid_sales)} dòng sai logic tiền tệ. Ví dụ tại dòng index: {list(invalid_sales.index[:3])}")
    return errors

# Hàm tổng hợp các validator và trả về kết quả cuối cùng
def run_all_validators(df, tax_rate=0.1):
    all_errors = []

    # Gom tất cả các lỗi vật lý và logic tiền tệ 
    all_errors.extend(validate_raw_data(df))
    all_errors.extend(check_currency_logic(df, tax_rate))

    # Trả về kết quả dạng dictionary
    return {
        "is_valid": len(all_errors) == 0, # True: không có lỗi nào, False: có ít nhất 1 lỗi
        "errors": all_errors
    }

if __name__ == "__main__":
    file_path = "data/raw/supermarket_data_sales.csv"

    # Đọc file CSV và chạy validator
    try:
        df = pd.read_csv(file_path)
        ket_qua = run_all_validators(df, tax_rate=0.1)
        if ket_qua["is_valid"]:
            print("Dữ liệu sạch.")
        else:
            print("Dữ liệu có lỗi:")
            for error in ket_qua["errors"]:
                print(f" {error}")
    except FileNotFoundError:
        print(f"Không tìm thấy file tại đường dẫn: {file_path}")
    except Exception as e:
        print(f"Đã xảy ra lỗi khi đọc file: {e}")

    