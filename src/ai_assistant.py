import os

import google
import pandas as pd
from dotenv import load_dotenv
from google import genai
from google.genai import types
from googleapiclient import errors

from analytics import Analytics
from data_loader import DataLoader
from data_processor import DataProcessor


class AIAssistant:
    def __init__(self):
        load_dotenv() #load file .env
        # TODO 1: Đọc biến môi trường AI_API_KEY từ file .env
        self.api_key=os.getenv("GEMINI_API_KEY")
        # TODO 2: Kiểm tra nếu không có API Key thì báo lỗi (raise ValueError)
        if not self.api_key:
            raise ValueError('Không tìm thấy API Key')
        # TODO 3: Khởi tạo client kết nối (ví dụ: genai.Client(api_key=...))
        self.client=genai.Client(api_key=self.api_key)
        self.model='gemini-2.5-flash-lite'

    def _call_api(self, system_prompt: str, user_prompt: str):
        """
        Hàm nội bộ: Dùng để gói gọn phần code gửi request lên API.
        Giúp các hàm bên dưới không phải viết lại code gọi API nhiều lần.
        """
        # TODO 1: Viết khối try-except để bắt lỗi mất mạng hoặc lỗi API.
        # TODO 2: Truyền system_prompt (định hình vai trò AI) và user_prompt (câu lệnh + dữ liệu) vào API.
        # TODO 3: Nhận kết quả văn bản trả về từ AI (response) và return.
        try:
            config=genai.types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.3
            )
            response=self.client.models.generate_content(
                model=self.model,
                contents=user_prompt,
                config=config
            )
            if response.text:
                return response.text
            else:
                return 'AI không trả lời được câu hỏi'
        except errors.HttpError as e:
            raise ValueError(f'Lỗi kết nối với máy chủ: {e}')
        except Exception as ex:
            return f'Lỗi kết nối đến API: {ex}'

    def summarize_monthly_performance(self, monthly_df: pd.DataFrame):
        """
        Tính năng: Tóm tắt báo cáo kinh doanh hàng tháng.
        """
        # TODO 1: Chuyển bảng monthly_df thành dạng chuỗi văn bản (Gợi ý dùng .to_markdown(index=False)).
        # TODO 2: Tạo `system_prompt` gán vai trò (Ví dụ: Chuyên gia phân tích dữ liệu).
        # TODO 3: Tạo `user_prompt` lồng ghép chuỗi dữ liệu ở Bước 1. Yêu cầu AI chỉ ra tháng tốt nhất, tệ nhất và tóm tắt ngắn gọn.
        # TODO 4: Gọi hàm self._call_api(...) và trả về kết quả.
        df = monthly_df.to_markdown(index=False)
        system_prompt = 'Bạn là chuyên gia Phân tích Kinh doanh (Business Analyst) của một chuỗi siêu thị lớn.'
        user_prompt=(f"""
        Dưới đây là bảng dữ liệu kinh doanh tổng hợp theo từng tháng:
        {df}
        Hãy thực hiện các yêu cầu sau bằng tiếng Việt:
        1. Tóm tắt ngắn gọn tình hình kinh doanh tổng thể.
        2. Chỉ ra tháng có hiệu suất tốt nhất và tệ nhất.
        3. Đưa ra 1-2 nhận định về xu hướng.
        Trình bày rõ ràng, súc tích bằng các gạch đầu dòng.          
        """)
        return self._call_api(system_prompt, user_prompt)

    def analyze_product_trends(self, top_best: pd.DataFrame, top_worst: pd.DataFrame) -> str | None:
        """
        Tính năng: Đưa ra đề xuất nhập hàng và cảnh báo hàng ế.
        """
        # TODO 1: Chuyển 2 bảng top_best và top_worst thành dạng chuỗi văn bản.
        # TODO 2: Tạo `system_prompt` gán vai trò (Ví dụ: Giám đốc chuỗi cung ứng).
        # TODO 3: Tạo `user_prompt` lồng ghép 2 chuỗi dữ liệu. Yêu cầu AI đưa ra cảnh báo mặt hàng nào nên xả kho, mặt hàng nào nên nhập thêm.
        # TODO 4: Gọi hàm self._call_api(...) và trả về kết quả.
        best_product=top_best.to_markdown(index=False)
        worst_product=top_worst.to_markdown(index=False)
        system_prompt='Bạn là Giám đốc Quản lý Chuỗi cung ứng (Supply Chain Manager).'
        user_prompt=f"""
        Dưới đây là bảng dữ liệu TOP 5 ngành hàng BÁN CHẠY NHẤT:
        {best_product}
        
        Dữ liệu TOP 5 ngành hàng BÁN Ế NHẤT:
        {worst_product}
        
        Dựa vào số liệu trên, hãy:
        1. Cảnh báo những mặt hàng cần giảm nhập kho hoặc lên chiến dịch xả hàng (Khuyến mãi, giảm giá).
        2. Đề xuất những mặt hàng cần tăng cường làm việc với nhà cung cấp để nhập thêm.
        Hãy giải thích ngắn gọn lý do cho mỗi đề xuất.
        """
        return self._call_api(system_prompt, user_prompt)

    def chat_with_data(self, user_question: str, context_df: pd.DataFrame) -> str | None:
        """
        Tính năng: Chatbot trả lời câu hỏi trực tiếp của người dùng.
        """
        # TODO 1: Chuyển context_df thành chuỗi văn bản.
        # TODO 2: Tạo `system_prompt` gán vai trò trợ lý hỏi đáp. (Rất quan trọng: Phải yêu cầu AI "Chỉ được trả lời dựa trên dữ liệu được cung cấp").
        # TODO 3: Tạo `user_prompt` chứa chuỗi dữ liệu và câu hỏi `user_question` của người dùng.
        # TODO 4: Gọi hàm self._call_api(...) và trả về kết quả
        data=context_df.to_markdown(index=False)
        system_prompt='Bạn là trợ lý AI thông minh hỗ trợ giám đốc siêu thị. Hãy trả lời câu hỏi một cách lịch sự, chính xác và DỰA HOÀN TOÀN VÀO DỮ LIỆU ĐƯỢC CUNG CẤP.'
        user_prompt=f"""
        Dữ liệu hiện tại của siêu thị:
        {data}
        
        Câu hỏi của giám đốc: "{user_question}"
        
        Nếu câu hỏi không thể trả lời bằng dữ liệu trên, hãy nói: "Xin lỗi, dữ liệu hiện tại không đủ để tôi trả lời câu hỏi này."
        """
        return self._call_api(system_prompt,user_prompt)

    def advise_on_predictions(self, forecast_df: pd.DataFrame) -> str:
        """
        Tính năng (Nâng cao - Làm sau cùng): Phân tích dự báo tương lai.
        """
        # TODO 1: Chuyển bảng kết quả dự đoán forecast_df thành chuỗi văn bản.
        # TODO 2: Thiết kế prompt lồng ghép số liệu dự báo, yêu cầu AI đưa ra chiến lược vốn và khuyến mãi cho tháng tới.
        # TODO 3: Gọi hàm self._call_api(...) và trả về kết quả.

        pass


# Chạy thử nghiệm ngay trong file
if __name__ == "__main__":
    dataloader= DataLoader('../data/raw/supermarket_data_sales.csv')
    df=dataloader.load_data()
    dataprocess=DataProcessor(df)
    df_cleaned=dataprocess.run_pipeline()
    analytic=Analytics(df_cleaned.head(5))
    mock_monthly_data=analytic.calculate_monthly_revenue_profit()
    # 2. Kích hoạt Trợ lý
    assistant = AIAssistant()
    # 3. Gọi thử tính năng tóm tắt
    print("--- ĐANG GỌI AI TÓM TẮT BÁO CÁO ---")
    summary = assistant.summarize_monthly_performance(mock_monthly_data)
    print(summary)