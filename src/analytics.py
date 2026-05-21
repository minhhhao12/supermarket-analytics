# TODO 1: Viết hàm tính tổng doanh thu và lợi nhuận theo từng tháng.
# TODO 2: Viết hàm tìm top 5 mặt hàng bán chạy nhất và top 5 mặt hàng ế nhất.
# TODO 3: Viết hàm tính toán hiệu suất của từng chi nhánh siêu thị.
import pandas as pd
from pandas import DataFrame

class Analytics:
    def __init__(self,df:DataFrame):
        self.df=df
    def calculate_monthly_revenue_profit(self) -> pd.DataFrame:
        monthly_stats = self.df.groupby('Month')[['Sales', 'Profit']].sum().reset_index()
        monthly_stats = monthly_stats.sort_values(by='Month')
        return monthly_stats

    def get_top_and_bottom_products(self) -> tuple:
        product_sales = self.df.groupby('Product line')['Quantity'].sum().reset_index()
        top_bestseller = product_sales.sort_values(by='Quantity', ascending=False).head(5)
        top_worst = product_sales.sort_values(by='Quantity', ascending=True).head(5)
        return top_bestseller, top_worst #tuple

    def calculate_branch_performance(self) -> pd.DataFrame:
    # Hàm .agg() cho phép tính toán nhiều phép toán khác nhau trên các cột khác nhau cùng một lúc
        branch_stats = self.df.groupby('Branch').agg(
        Total_Sales=('Sales', 'sum'),
        Total_Profit=('Profit', 'sum'),
        Total_Orders=('Invoice ID', 'count')
     ).reset_index()
        branch_stats = branch_stats.sort_values(by='Total_Sales', ascending=False)
        return branch_stats