# Supermarket Analytics: Dashboard Phân tích Dữ liệu và Trợ lý GenAI



Hệ thống Dashboard thông minh giúp các nhà quản lý chuỗi siêu thị dễ dàng theo dõi hiệu suất bán hàng, nắm bắt xu hướng thị trường và tương tác trực tiếp với dữ liệu thông qua một Trợ lý AI, hỗ trợ đưa ra các quyết định kinh doanh nhanh chóng và chính xác.



## Tính Năng Nổi Bật

### 1. Dashboard Trực Quan và Tương Tác
- **Theo dõi KPIs thời gian thực**: Cập nhật liên tục các chỉ số quan trọng như Tổng Doanh Thu, Doanh Thu Trung Bình.
- **Bộ lọc đa chiều**: Dễ dàng lọc và phân tích dữ liệu theo Thành phố, Ngành hàng, Giới tính, Loại khách hàng và Ngày.
- **Hệ thống biểu đồ đa dạng**:
  - Phân tích cơ cấu thanh toán (Biểu đồ tròn, cột).
  - Doanh thu theo ngành hàng (Biểu đồ cột ngang, cột dọc, treemap).
  - Phân bố và độ hài lòng của khách hàng (Histogram, Box Plot, Violin).
  - Hiệu suất chi nhánh, cơ cấu doanh thu theo phân khúc khách hàng.
  - Phân tích giờ mua sắm cao điểm và dự báo doanh thu.

### 2. Trợ Lý AI Thông Minh
- **Hỏi-đáp bằng ngôn ngữ tự nhiên**: Đặt câu hỏi trực tiếp cho AI về dữ liệu kinh doanh (ví dụ: *"So sánh doanh thu giữa các chi nhánh"*, *"Top 3 sản phẩm bán chạy nhất là gì?"*).
- **Tóm tắt báo cáo tự động**: Yêu cầu AI tóm tắt tình hình kinh doanh, đưa ra nhận định và đề xuất chiến lược.
- **Phân tích chuyên sâu**: AI có khả năng tự viết và thực thi các câu lệnh `pandas` để trả lời những câu hỏi phức tạp, không có sẵn trong các báo cáo.

### 3. Giả Lập Dữ Liệu và Tự Động Cập Nhật
- **Order Simulator**: Kịch bản `src/order_simulator.py` liên tục tạo ra các đơn hàng mới và ghi vào cơ sở dữ liệu, giúp dashboard luôn có dữ liệu mới để phân tích.
- **Tự động làm mới**: Dashboard tự động cập nhật dữ liệu mới mỗi 5 phút mà không cần người dùng tải lại trang, nhờ vào `APScheduler` và endpoint `/refresh`.

### 4. Quy Trình Dữ Liệu Mạnh Mẽ
- **Tải và xác thực dữ liệu**: Cho phép người dùng tải lên file CSV, hệ thống sẽ tự động kiểm tra lỗi (thiếu cột, dữ liệu không hợp lệ) và thông báo kết quả.
- **Lưu trữ và truy xuất**: Dữ liệu được xử lý và lưu trữ trong cơ sở dữ liệu SQLite, giúp truy xuất nhanh chóng và ổn định.

## Công Nghệ Sử Dụng

| Hạng mục | Công nghệ |
|---|---|
| **Ngôn ngữ** | Python 3.10+ |
| **Giao diện người dùng (UI)** | Dash, Dash Bootstrap Components |
| **Xử lý & Phân tích Dữ liệu** | Pandas, NumPy, Scikit-learn |
| **Trực quan hóa** | Plotly Express |
| **Tích hợp AI** | Google Gemini API (`google-genai`) |
| **Cơ sở dữ liệu** | SQLite |
| **Lập lịch tác vụ** | APScheduler |

##  Hướng Dẫn Cài Đặt & Chạy Ứng Dụng

### 1. Yêu cầu
- Python 3.10+
- `git`

### 2. Clone Kho Lưu Trữ
Mở Terminal (hoặc Command Prompt) và chạy lệnh sau:
```bash
git clone https://github.com/minhhhao12/supermarket-analytics.git
cd supermarket-analytics
```

### 3. Thiết Lập Môi Trường Ảo
Khuyến khích sử dụng môi trường ảo để quản lý các thư viện một cách độc lập.
```bash
# Tạo môi trường ảo
python -m venv venv

# Kích hoạt môi trường ảo
# Trên Windows:
venv\Scripts\activate
# Trên macOS/Linux:
source venv/bin/activate
```

### 4. Cài Đặt Thư Viện
Cài đặt tất cả các thư viện cần thiết từ file `requirements.txt`.
```bash
pip install -r requirements.txt
```

### 5. Cấu Hình Biến Môi Trường
1.  Tạo một file mới tên là `.env` trong thư mục gốc của dự án bằng cách sao chép từ file `.env.example`.
2.  Mở file `.env` và điền các giá trị của bạn:
    ```text
    GEMINI_API_KEY="your_actual_gemini_api_key_here"
    DATABASE_URL="sqlite:///data/supermarket_data.db"
    ```
    -   `GEMINI_API_KEY`: API Key của bạn từ Google AI Studio.
    -   `DATABASE_URL`: Đường dẫn đến file cơ sở dữ liệu SQLite. Bạn có thể giữ nguyên giá trị mặc định.

### 6. Khởi Tạo Dữ Liệu (Tùy chọn)
Ứng dụng có thể bắt đầu với một cơ sở dữ liệu trống và bạn có thể tải dữ liệu lên qua giao diện. Tuy nhiên, nếu bạn muốn có sẵn dữ liệu mẫu để trải nghiệm, hãy chạy script sau:
```bash
python src/init_database.py
```
Script này sẽ đọc dữ liệu từ `data/raw/supermarket_data_sales.csv` và tạo file `supermarket_data.db` trong thư mục `data/`.

### 7. Chạy Ứng Dụng
1.  **Chạy Dashboard chính**:
    ```bash
    python main.py
    ```
    Mở trình duyệt và truy cập vào http://127.0.0.1:8050.

2.  **(Tùy chọn) Chạy trình giả lập đơn hàng**:
    Để xem tính năng cập nhật dữ liệu thời gian thực, hãy mở một Terminal khác và chạy:
    ```bash
    python src/order_simulator.py
    ```
    Script này sẽ tự động thêm các đơn hàng mới vào cơ sở dữ liệu và dashboard sẽ tự động cập nhật sau mỗi khoảng thời gian ngắn.

##  Cấu Trúc Thư Mục

```
supermarket-analytics/
├── data/
│   ├── raw/                    # Dữ liệu gốc (CSV/Excel)
│   └── supermarket_data.db     # Cơ sở dữ liệu SQLite
├── notebooks/
│   └── 01_exploratory_data_analysis.ipynb
├── src/
│   ├── ai_assistant.py         # Logic Trợ lý AI (Gemini API)
│   ├── analytics.py            # Các hàm tính toán, phân tích
│   ├── data_loader.py          # Logic nạp/đọc dữ liệu
│   ├── data_processor.py       # Logic tiền xử lý, làm sạch
│   ├── data_validator.py       # Logic xác thực dữ liệu
│   ├── database_connector.py   # Logic kết nối và thao tác CSDL
│   ├── order_simulator.py      # Kịch bản giả lập đơn hàng mới
│   ├── test.py                 # Kịch bản khởi tạo CSDL từ CSV
│   ├── ui.py                   # Xây dựng giao diện người dùng (Dash)
│   └── visualization.py        # Logic vẽ biểu đồ (Plotly)
├── .env.example                # File mẫu biến môi trường
├── .gitignore                  # Các file/thư mục được Git bỏ qua
├── main.py                     # File entry-point để chạy ứng dụng
├── requirements.txt            # Danh sách thư viện Python
└── README.md                   # Tài liệu dự án
