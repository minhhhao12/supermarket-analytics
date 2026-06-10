from ai_assistant import AIAssistant
from analytics import Analytics
from data_loader import DataLoader
from data_processor import DataProcessor
import pandas as pd

from data_validator import DataValidator

# dataloader=DataLoader('data/raw/supermarket_data_sales.csv')
# df=dataloader.load_data()
# processor=DataProcessor(df)
# df_cleaned=processor.run_pipeline()
# processor.save_processed_data()
# analytic=Analytics(df_cleaned)
#
dataloader = DataLoader('data/raw/supermarket_data_sales.csv')
df = dataloader.load_data()
dataprocess = DataProcessor(df)
df_cleaned = dataprocess.run_pipeline()

# Khởi tạo đối tượng Analytics
analytic_instance = Analytics(df_cleaned.head(100))
# top_best_top_worst=analytic_instance.get_top_and_bottom_products()
assistant = AIAssistant(analytics_instance=analytic_instance)
# print(assistant.analyze_product_trends(top_best_top_worst))
# print("\n--- THỬ NGHIỆM CHATBOT FUNCTION CALLING ---")
#
# cau_hoi_1 = "Chi nhánh nào đang có doanh thu và số lượng đơn hàng tốt nhất vậy?"
# print(f"\nGiám đốc hỏi: {cau_hoi_1}")
# tra_loi_1 = assistant.chat_with_data(cau_hoi_1)
# print(f"AI trả lời:\n{tra_loi_1}")
print('Câu hỏi của bạn là:')
cau_hoi_2 = str(input())
print(f"\nGiám đốc hỏi: {cau_hoi_2}")
tra_loi_2 = assistant.chat_with_data(cau_hoi_2)
print(f"AI trả lời:\n{tra_loi_2}")


