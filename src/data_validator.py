import pandas as pd


class DataValidator:
    # Lớp chịu trách nhiệm kiểm tra chất lượng dữ liệu siêu thị

    def __init__(self, df, tax_rate=0.1):
        # Hàm khởi tạo nhận vào trực tiếp một DataFrame và thuế suất
        self.df = df
        self.tax_rate = tax_rate

    def validate_raw_data(self):
        # Kiểm tra các lỗi vật lý cơ bản liên quan đến giá trị âm hoặc thiếu cột
        errors = []
        required_cols = ["Quantity", "Unit price", "Sales"]
        missing_cols = []

        # Kiểm tra các cột bắt buộc có tồn tại trong dữ liệu hay không
        for col in required_cols:
            if col not in self.df.columns:
                missing_cols.append(col)

        if len(missing_cols) > 0:
            errors.append(
                f"File dữ liệu bị thiếu các cột bắt buộc: {', '.join(missing_cols)}"
            )
            return errors

        # Kiểm tra lỗi số lượng (Quantity) <= 0
        invalid_quantity = self.df[self.df["Quantity"] <= 0]
        if not invalid_quantity.empty:
            errors.append(
                f"Có {len(invalid_quantity)} dòng có Quantity <= 0. Ví dụ tại dòng index: {list(invalid_quantity.index[:3])}"
            )

        # Kiểm tra lỗi đơn giá (Unit price) < 0
        invalid_price = self.df[self.df["Unit price"] < 0]
        if not invalid_price.empty:
            errors.append(
                f"Có {len(invalid_price)} dòng có Unit price < 0. Ví dụ tại dòng index: {list(invalid_price.index[:3])}"
            )

        # Kiểm tra lỗi doanh thu (Sales) < 0
        invalid_sales = self.df[self.df["Sales"] < 0]
        if not invalid_sales.empty:
            errors.append(
                f"Có {len(invalid_sales)} dòng có Sales < 0. Ví dụ tại dòng index: {list(invalid_sales.index[:3])}"
            )

        return errors

    def check_currency_logic(self):
        # Kiểm tra tính đúng đắn của logic tính toán tiền tệ dựa trên thuế suất
        errors = []

        if (
            "Quantity" not in self.df.columns
            or "Unit price" not in self.df.columns
            or "Sales" not in self.df.columns
        ):
            return errors

        # Tính toán doanh thu lý thuyết dựa trên thuộc tính tax_rate
        theoretical_sales = (
            self.df["Quantity"] * self.df["Unit price"] * (1 + self.tax_rate)
        )

        # Đo mức độ chênh lệch tiền tuyệt đối
        diff = (self.df["Sales"] - theoretical_sales).abs()
        invalid_sales = self.df[diff > 1.0]

        if not invalid_sales.empty:
            errors.append(
                f"Có {len(invalid_sales)} dòng sai logic tiền tệ. Ví dụ tại dòng index: {list(invalid_sales.index[:3])}"
            )

        return errors

    def run_all_validators(self):
        # Phương thức tổng hợp chạy toàn bộ các bước kiểm tra dữ liệu
        all_errors = []

        # Gọi các phương thức kiểm tra nội bộ thông qua từ khóa 'self'
        all_errors.extend(self.validate_raw_data())
        all_errors.extend(self.check_currency_logic())

        return {
            "is_valid": len(all_errors) == 0,
            "errors": all_errors,
        }


# KHU VỰC CHẠY CHÍNH (MAIN)
if __name__ == "__main__":
    file_path = "data/raw/supermarket_data_sales.csv"

    try:
        # Đọc file lấy DataFrame trước
        df_raw = pd.read_csv(file_path)

        # Truyền thẳng DataFrame vào class Validator để khởi tạo đối tượng
        validator = DataValidator(df=df_raw, tax_rate=0.1)

        # Tiến hành quét lỗi
        ket_qua = validator.run_all_validators()

        if ket_qua["is_valid"]:
            print("Dữ liệu sạch.")
        else:
            print("Dữ liệu có lỗi:")
            for error in ket_qua["errors"]:
                print(f" - {error}")

    except FileNotFoundError:
        print(f"Không tìm thấy file tại đường dẫn: {file_path}")
    except Exception as e:
        print(f"Đã xảy ra lỗi khi đọc file: {e}")
