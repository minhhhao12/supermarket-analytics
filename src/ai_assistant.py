import os
import io
import contextlib
import json
import pandas as pd
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.types import GenerateContentResponse
from googleapiclient import errors

from analytics import Analytics


class AIAssistant:
    def __init__(self,analytics_instance:Analytics=None):
        load_dotenv() #load file .env
        #Đọc biến môi trường AI_API_KEY từ file .env
        self.api_key=os.getenv("GEMINI_API_KEY")

        if not self.api_key:
            raise ValueError('Không tìm thấy API Key')
        #Khởi tạo client kết nối (ví dụ: genai.Client(api_key=...))
        self.client=genai.Client(api_key=self.api_key)
        self.model='gemma-4-26b-a4b-it'
        self.analytics=analytics_instance
        self.chat_session=None

    def _call_api(self, system_prompt: str, user_prompt: str,tools:list=None)-> GenerateContentResponse | None:
        """
        Hàm nội bộ: Gửi request lên Gemini API và trả về đối tượng Response gốc.
        """
        try:
            config = genai.types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.3,
                tools=tools
            )
            response = self.client.models.generate_content(
                model=self.model,
                contents=user_prompt,
                config=config
            )
            return response

        except errors.HttpError as e:
            raise ValueError(f'Lỗi kết nối với máy chủ: {e}')
        except Exception as ex:
            print(f'Lỗi kết nối đến API: {ex}')
            return None

    def get_branch_performance(self)->str:
        """
            Lấy bảng thống kê hiệu suất của các chi nhánh siêu thị, bao gồm doanh thu và số lượng đơn hàng.
            Hàm này được gọi khi người dùng hỏi về doanh thu, so sánh hoặc tình hình kinh doanh của các chi nhánh.
        """
        if self.analytics: #kiểm tra xem thuộc tính self.analytics đã được khởi tạo (khác None) hay chưa.
            df_branch=self.analytics.calculate_branch_performance()
            return df_branch.to_markdown(index=False)
        return 'Không có dữ liệu phân tích chi nhánh'
    def get_products_trend(self)->str:
        """
        Lấy bảng dữ liệu về xu hướng ngành hàng bao gồm TOP ngành hàng bán chạy nhất và bán ế nhất.
        Returns: Chuỗi văn bản chứa thông tin sản phẩm.
        """
        if self.analytics:
            df_products_trend=self.analytics.get_top_and_bottom_products()
            if isinstance(df_products_trend,tuple):
                return f"TOP BÁN CHẠY:\n{df_products_trend[0].to_markdown()}\n\nTOP BÁN Ế:\n{df_products_trend[1].to_markdown()}"
        return 'Không có dữ liệu phân tích sản phẩm.'
    def get_branch_rating(self)->str:
        """
        Lấy bảng thống kế số điểm đánh giá trung bình ở các chi nhánh
        Hàm này được gọi khi người dùng hỏi về điểm đánh giá ở các chi nhánh
        return: Chuỗi văn bản chứa điểm đánh giá trung bình ở các chi nhánh
        """
        if self.analytics:
            df_branch_rating=self.analytics.calculate_avg_rating_branches()
            df_branch_rating=df_branch_rating.to_markdown(index=False)
            return df_branch_rating
        return 'Không có dữ liệu để phân tích'

    def get_monthly_revenue_profit(self) -> str:
        """
        Lấy bảng thống kê tổng doanh thu và lợi nhuận theo từng tháng.
        Hàm này được gọi khi người dùng hỏi về doanh thu theo tháng, lợi nhuận các tháng, hoặc so sánh doanh thu giữa các tháng.
        """
        if self.analytics:
            df = self.analytics.calculate_monthly_revenue_profit()
            return df.to_markdown(index=False)
        return 'Không có dữ liệu phân tích theo tháng.'

    def get_payment_method_stats(self) -> str:
        """
        Lấy bảng phân tích doanh thu và số lượng đơn hàng theo phương thức thanh toán (Tiền mặt, Thẻ, E-wallet...).
        Hàm này được gọi khi người dùng hỏi về thói quen thanh toán, phương thức nào được dùng nhiều nhất.
        """
        if self.analytics:
            df = self.analytics.calculate_revenue_and_number_of_orders_by_payment_method()
            return df.to_markdown(index=False)
        return 'Không có dữ liệu phân tích phương thức thanh toán.'

    def get_customer_demographics_revenue(self) -> str:
        """
        Lấy bảng phân tích doanh thu dựa trên loại khách hàng (Customer type: Member, Normal) và Giới tính (Gender: Male, Female).
        Hàm này được gọi khi người dùng hỏi khách nam hay nữ mua nhiều hơn, hoặc thành viên hay khách vãng lai chi tiêu nhiều hơn.
        """
        if self.analytics:
            df = self.analytics.get_revenue_by_customer_type_and_gender()
            return df.to_markdown(index=False)
        return 'Không có dữ liệu phân tích tệp khách hàng.'

    def get_shopping_hours_analysis(self) -> str:
        """
        Lấy bảng phân tích khung giờ mua sắm cao điểm. Bao gồm số đơn hàng, doanh thu và đánh giá theo từng khung giờ trong ngày.
        Hàm này được gọi khi người dùng hỏi về giờ cao điểm, giờ nào đông khách nhất, giờ nào bán được nhiều nhất.
        """
        if self.analytics:
            df = self.analytics.analyze_shopping_hours()
            return df.to_markdown(index=False)
        return 'Không có dữ liệu phân tích khung giờ mua sắm.'

    def get_product_line_revenue(self) -> str:
        """
        Lấy bảng thống kê doanh thu và lợi nhuận theo từng ngành hàng (Product line).
        Hàm này được gọi khi người dùng hỏi ngành hàng nào mang lại lợi nhuận cao nhất, ngành nào doanh thu tốt nhất.
        """
        if self.analytics:
            stats, top_profit, worst_profit = self.analytics.calculate_revenue_by_product_line()
            return f"Bảng tổng hợp:\n{stats.to_markdown(index=False)}\n\nNgành lợi nhuận cao nhất:\n{top_profit.to_markdown(index=False)}\n\nNgành lợi nhuận thấp nhất:\n{worst_profit.to_markdown(index=False)}"
        return 'Không có dữ liệu phân tích doanh thu ngành hàng.'

    def get_product_line_rating(self) -> str:
        """
        Lấy bảng thống kê điểm đánh giá trung bình của khách hàng cho từng ngành hàng.
        Hàm này được gọi khi người dùng hỏi về điểm đánh giá, mức độ hài lòng của các ngành hàng.
        """
        if self.analytics:
            df = self.analytics.get_avg_rating_by_product_line()
            return df.to_markdown(index=False)
        return 'Không có dữ liệu đánh giá ngành hàng.'

    def get_customer_loyalty_value(self) -> str:
        """
        Lấy tỷ lệ phần trăm (%) đóng góp lợi nhuận của khách hàng là Thành viên (Member) so với khách Vãng lai (Normal).
        Hàm này được gọi khi người dùng hỏi về mức độ trung thành, giá trị của khách hàng thành viên, hoặc so sánh lợi nhuận giữa member và normal.
        """
        if self.analytics:
            df = self.analytics.calculate_loyalty_value()
            return df.to_markdown(index=False)
        return 'Không có dữ liệu phân tích mức độ trung thành.'

    def get_average_order_value_info(self) -> str:
        """
        Lấy thông tin giá trị đơn hàng trung bình phân theo từng Chi nhánh và Loại khách hàng.
        Hàm này được gọi khi người dùng muốn biết nhóm khách hàng nào đang mua giỏ hàng "giá trị cao" để tìm cơ hội upsell, hoặc hỏi về giá trị trung bình của mỗi đơn hàng.
        """
        if self.analytics:
            df_aov = self.analytics.calculate_average_order_value()
            # Reset index để hiển thị rõ cột Branch và Customer type trong markdown
            return df_aov.reset_index().to_markdown(index=False)
        return 'Không có dữ liệu phân tích giá trị đơn hàng trung bình.'

    def get_basket_size_analysis(self) -> str:
        """
        Phân tích số lượng sản phẩm trung bình trên một đơn hàng theo từng Ngành hàng.
        Hàm này được gọi khi người dùng hỏi về quy mô giỏ hàng, xu hướng mua nhiều/ít sản phẩm trong một lần mua, hoặc số lượng mua trung bình của các loại sản phẩm/ngành hàng.
        """
        if self.analytics:
            df_basket = self.analytics.analyze_basket_size()
            return df_basket.to_markdown(index=False)
        return 'Không có dữ liệu phân tích quy mô giỏ hàng.'

    def get_rating_vs_sales_correlation(self) -> str:
        """
        Tính hệ số tương quan (Correlation) giữa điểm đánh giá (Rating) và doanh số (Sales).
        Hàm này được gọi khi người dùng thắc mắc liệu khách hàng mua đơn hàng lớn có khó tính hơn (cho điểm thấp hơn) không, hoặc muốn biết mối liên hệ giữa doanh thu và mức độ hài lòng.
        """
        if self.analytics:
            correlation = self.analytics.analyze_rating_vs_sales_correlation()
            return f"Hệ số tương quan giữa Rating và Sales là: {correlation}"
        return 'Không có dữ liệu để tính toán hệ số tương quan.'

    def get_executive_summary_kpi(self) -> str:
        """
        Lấy bảng tổng hợp các chỉ số sức khỏe tài chính cốt lõi của siêu thị (KPIs) bao gồm: tổng doanh thu, tổng lợi nhuận, số lượng đơn, biên lợi nhuận, AOV và điểm đánh giá trung bình.
        Hàm này được gọi khi người dùng muốn có cái nhìn tổng quan về tình hình kinh doanh, sức khỏe tài chính, hoặc xem báo cáo tóm tắt.
        """
        if self.analytics:
            summary_dict = self.analytics.get_executive_summary()
            # Chuyển đổi dictionary thành JSON string định dạng đẹp để AI dễ đọc
            return json.dumps(summary_dict, indent=4, ensure_ascii=False)
        return 'Không có dữ liệu báo cáo tổng quan.'

    def get_revenue_forecast(self) -> str:
        """
        Dự báo doanh thu trong 30 ngày tiếp theo dựa trên dữ liệu lịch sử.
        Hàm này được gọi khi người dùng yêu cầu dự đoán doanh thu, xu hướng bán hàng trong tháng tới, hoặc ước tính doanh số tương lai.
        """
        if self.analytics:
            forecast_df = self.analytics.forecast_next_month_revenue()
            return forecast_df.to_markdown(index=False)
        return 'Không thể thực hiện dự báo doanh thu lúc này.'

    def get_low_rating_bottlenecks(self) -> str:
        """
        Phân tích các yếu tố (điểm nghẽn) gây ra điểm đánh giá thấp (dưới 5 sao) phân theo Chi nhánh và Ngành hàng.
        Hàm này được gọi khi người dùng muốn tìm hiểu nguyên nhân khiến khách hàng không hài lòng, những chi nhánh hay ngành hàng nào đang bị phàn nàn nhiều nhất.
        """
        if self.analytics:
            result = self.analytics.analyze_low_rating_bottlenecks()
            if not result:
                return "Không có dữ liệu đánh giá thấp nào (tất cả đều từ 5 sao trở lên)."

            by_branch, by_product = result
            report = "### Phân tích đánh giá thấp theo Chi nhánh:\n"
            report += by_branch.to_markdown(index=False)
            report += "\n\n### Phân tích đánh giá thấp theo Ngành hàng:\n"
            report += by_product.to_markdown(index=False)
            return report
        return 'Không có dữ liệu phân tích các đánh giá thấp.'

    def get_high_profit_low_cogs_info(self) -> str:
        """
        Lấy danh sách các ngành hàng có tỷ lệ lợi nhuận trên giá vốn (Profit per COGS) cao.
        Hàm này được gọi khi người dùng muốn xác định ngành hàng nào mang lại lợi nhuận biên tốt nhất để tập trung kinh doanh, hoặc so sánh hiệu quả chi phí của các ngành hàng.
        """
        if self.analytics:
            df_profit = self.analytics.calculate_high_profit_low_cogs()
            return df_profit.to_markdown(index=False)
        return 'Không có dữ liệu phân tích lợi nhuận trên giá vốn.'


    def summarize_monthly_performance(self, monthly_df: pd.DataFrame):
        """
        Tính năng: Tóm tắt báo cáo kinh doanh hàng tháng.
        """
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

    def analyze_product_trends(self, top_best_top_worst:tuple) -> str | None:
        """
        Tính năng: Đưa ra đề xuất nhập hàng và cảnh báo hàng ế.
        """
        best_product=top_best_top_worst[0].to_markdown(index=False)
        worst_product=top_best_top_worst[1].to_markdown(index=False)
        system_prompt='Bạn là Giám đốc Quản lý Chuỗi cung ứng (Supply Chain Manager).'
        user_prompt=f"""
        Dưới đây là bảng dữ liệu TOP 3 ngành hàng BÁN CHẠY NHẤT:
        {best_product}
        
        Dữ liệu TOP 3 ngành hàng BÁN Ế NHẤT:
        {worst_product}
        
        Dựa vào số liệu trên, hãy:
        1. Cảnh báo những mặt hàng cần giảm nhập kho hoặc lên chiến dịch xả hàng (Khuyến mãi, giảm giá).
        2. Đề xuất những mặt hàng cần tăng cường làm việc với nhà cung cấp để nhập thêm.
        Hãy giải thích ngắn gọn lý do cho mỗi đề xuất.
        """
        response=self._call_api(system_prompt,user_prompt)
        return response.text

    def analyze_branch_performance(self,branch_stats:pd.DataFrame)->str|None:
        system_prompt='Bạn là chuyên gia Phân tích Kinh doanh (Business Analyst) của một chuỗi siêu thị lớn.'
        df_stats=branch_stats.to_markdown(index=False)
        user_prompt = f"""
                    Dưới đây là bảng dữ liệu doanh thu của các chi nhánh siêu thị:
                    {df_stats}
                    
                    Dựa vào số liệu trên, hãy:
                    1. Cho biết chi nhánh nào đang dẫn đầu doanh thu hiện tại và chi nhánh có doanh thu thấp nhất
                    2. Cho biết chi nhánh nào đang có số lượng đơn hàng nhiều nhất và chi nhánh có số lượng đơn hàng thấp nhất
                    3. Đề xuất 2-3 phương pháp để thu hút khách hàng hiệu quả
                """
        response=self._call_api(system_prompt,user_prompt)
        return response.text

    def chat_with_data(self, user_question: str) -> str | None:
        """
        Tính năng: Chatbot thông minh tự động chọn hàm và phân tích dữ liệu
        """
        system_prompt = (
            "Bạn là trợ lý AI thông minh hỗ trợ giám đốc chuỗi siêu thị. "
            "Nhiệm vụ của bạn là sử dụng các công cụ (tools) được cung cấp để trích xuất dữ liệu chính xác trước khi trả lời. "
            "Nếu dữ liệu trả về dạng bảng, hãy phân tích sơ bộ và trình bày câu trả lời một cách rõ ràng, súc tích bằng tiếng Việt."
        )
        tools_list = [self.get_products_trend,
            self.get_branch_performance,
            self.get_branch_rating,
            self.get_monthly_revenue_profit,
            self.get_payment_method_stats,
            self.get_customer_demographics_revenue,
            self.get_shopping_hours_analysis,
            self.get_product_line_revenue,
            self.get_product_line_rating,
            self.get_customer_loyalty_value,self.get_average_order_value_info,
            self.get_basket_size_analysis,
            self.get_rating_vs_sales_correlation,
            self.get_executive_summary_kpi,
            self.get_revenue_forecast,
            self.get_low_rating_bottlenecks,
            self.get_high_profit_low_cogs_info,
            self.execute_dynamic_pandas_query]

        try:
            if self.chat_session is None:
                self.chat_session=self.client.chats.create(
                    model=self.model,
                    config=genai.types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=0.1,
                    tools=tools_list
                )
            )
            response=self.chat_session.send_message(user_question)
            return response.text

        except Exception as ex:
            print(f"Lỗi khi chat với dữ liệu: {ex}")
            return "Xin lỗi, hệ thống gặp sự cố khi xử lý dữ liệu câu hỏi."

    def clear_chat_history(self):
        self.chat_session = None
        return "Đã xóa lịch sử trò chuyện. Bạn có muốn hỏi về chủ đề mới không?"

    def execute_dynamic_pandas_query(self, generated_code: str) -> str:
        """
        Thực thi mã Python/Pandas động tự động để phân tích dữ liệu tùy biến trên DataFrame 'df'.
        Hàm này BẮT BUỘC ĐƯỢC GỌI khi các hàm báo cáo cụ thể có sẵn KHÔNG đáp ứng được câu hỏi chi tiết, phức tạp của người dùng.

        Args:
            generated_code: Đoạn code Python sử dụng thư viện pandas để tính toán trên biến 'df'.
                            BẮT BUỘC phải sử dụng hàm print() để in kết quả ra màn hình (ví dụ: print(df['Sales'].max())).
        """
        if not self.analytics:
            return "Lỗi: Không thể truy cập dữ liệu DataFrame từ class Analytics."
        df_source = self.analytics.df
        local_vars = {'df': df_source, 'pd': pd}
        stdout_capture = io.StringIO()
        try:
            with contextlib.redirect_stdout(stdout_capture):
                exec(generated_code, {}, local_vars)
            result = stdout_capture.getvalue()
            return result
        except Exception as e:
            return f"Lỗi code: {str(e)}. Hãy kiểm tra lại tên cột hoặc cú pháp Pandas và tự sửa lại nhé."

    def advise_on_predictions(self, forecast_df: pd.DataFrame) -> str:
        """
        Tính năng (Nâng cao - Làm sau cùng): Phân tích dự báo tương lai.
        """
        # TODO 1: Chuyển bảng kết quả dự đoán forecast_df thành chuỗi văn bản.
        # TODO 2: Thiết kế prompt lồng ghép số liệu dự báo, yêu cầu AI đưa ra chiến lược vốn và khuyến mãi cho tháng tới.
        # TODO 3: Gọi hàm self._call_api(...) và trả về kết quả.

        pass
