import pandas as pd
from pandas import DataFrame

class Analytics:
    def __init__(self,df:DataFrame):
        self.df=df

    #: tính tổng doanh thu và lợi nhuận theo từng tháng.
    def calculate_monthly_revenue_profit(self) -> pd.DataFrame:
        monthly_stats = self.df.groupby('Month')[['Sales', 'gross income']].sum().reset_index()
        monthly_stats = monthly_stats.sort_values(by='Month')
        return monthly_stats


    #tìm top 3 mặt hàng bán chạy nhất và top 3 mặt hàng ế nhất.
    def get_top_and_bottom_products(self) -> tuple:
        product_sales = self.df.groupby('Product line')['Quantity'].sum().reset_index()
        top_bestseller = product_sales.sort_values(by='Quantity', ascending=False).head(3)
        top_worst = product_sales.sort_values(by='Quantity', ascending=True).head(3)
        return top_bestseller, top_worst #tuple


    #tính toán hiệu suất của từng chi nhánh siêu thị.
    def calculate_branch_performance(self) -> pd.DataFrame:
    # Hàm .agg() cho phép tính toán nhiều phép toán khác nhau trên các cột khác nhau cùng một lúc
        branch_stats = self.df.groupby('Branch').agg(
        Total_Sales=('Sales', 'sum'),
        Total_Profit=('gross income', 'sum'),
        Total_Orders=('Invoice ID', 'count')
     ).reset_index()
        branch_stats = branch_stats.sort_values(by='Total_Sales', ascending=False)
        return branch_stats

    # Phân tích doanh thu và số lượng đơn hàng theo phương thức thanh toán
    def calculate_revenue_and_number_of_orders_by_payment_method(self)->pd.DataFrame:
        df=self.df.groupby('Payment').agg(
            Total_Orders=('Invoice ID','count'),
            Total_Sales=('Sales', 'sum'),
            Total_Profit=('gross income', 'sum'),
        )
        df=df.sort_values(by='Total_Sales',ascending=False)
        return df

    # Phân tích doanh thu theo loại khách hàng (Customer type) và Giới tính (Gender)
    def get_revenue_by_customer_type_and_gender(self)->pd.DataFrame:
        df_revenue_by_gender_customer_type=self.df.groupby(['Gender','Customer type'])[['Sales','gross income']].sum().reset_index()
        df_revenue_by_gender_customer_type=df_revenue_by_gender_customer_type.sort_values(by='Sales',ascending=False)
        return df_revenue_by_gender_customer_type

    # Phân tích khung giờ mua sắm cao điểm (Ví dụ: Sáng, Trưa, Chiều, Tối)
    def analyze_shopping_hours(self)->pd.DataFrame:
        df_shopping_hours=self.df.groupby('Hour').agg(
            Total_Orders=('Invoice ID','count'),
            Total_Sales=('Sales', 'sum'),
            Total_Profit=('gross income', 'sum'),
            avg_rating=('Rating','mean')
        ).reset_index()
        df_shopping_hours['invoice per mins']=(df_shopping_hours['Total_Orders']/60).round(1)
        df_shopping_hours['avg_rating']=df_shopping_hours['avg_rating'].round(2)
        df_shopping_hours=df_shopping_hours.sort_values(by='Total_Orders',ascending=False)
        return df_shopping_hours

    #: Doanh thu theo từng ngành, ngành nào đang gánh lợi nhuận cho siêu thị
    def calculate_revenue_by_product_line(self)->tuple:
        revenue_product_line_stats=self.df.groupby('Product line')[['gross income','Sales']].sum().reset_index()
        revenue_product_line_stats=revenue_product_line_stats.sort_values(by='gross income',ascending=False)

        top_profit_revenue_product_line=revenue_product_line_stats.sort_values(by='gross income',ascending=False).head(1)
        worst_profit_revenue_product_line=revenue_product_line_stats.sort_values(by='gross income',ascending=True).head(1)
        return revenue_product_line_stats,top_profit_revenue_product_line,worst_profit_revenue_product_line

    #Điểm đánh giá trung bình ở các chi nhánh
    def calculate_avg_rating_branches(self)->pd.DataFrame:
        df_rating_branch=self.df.groupby('Branch')['Rating'].mean().reset_index()
        df_rating_branch['Rating']=df_rating_branch['Rating'].round(2)
        df_rating_branch=df_rating_branch.sort_values(by='Rating',ascending=False)
        return df_rating_branch

    #: Điểm đánh giá theo từng ngành hàng
    def get_avg_rating_by_product_line(self)->pd.DataFrame:
        df_rating_product_line=self.df.groupby('Product line')['Rating'].mean().reset_index()
        df_rating_product_line=df_rating_product_line.sort_values(by='Rating',ascending=False)
        return df_rating_product_line

    # Tỷ suất lợi nhuận gộp (Gross Profit Margin): Ngành lợi nhuận cao mà cogs thấp
    def calculate_high_profit_low_cogs(self):
        df_tmp=self.df.groupby('Product line')[['cogs','gross income']].sum().reset_index()
        df_tmp['Profit per cogs']=df_tmp['gross income']/df_tmp['cogs']
        sorted_df=df_tmp.sort_values(by='Profit per cogs',ascending=False)
        return sorted_df
    # Biến động điểm số đánh giá (Rating Volatility): Tìm hiểu xem các điểm số thấp (1-3 sao) thường rơi vào chi nhánh nào, ngành hàng nào, hoặc phương thức thanh toán nào để tìm ra "vấn đề hệ thống" (Bottleneck).
    # Mức độ trung thành (Loyalty Value): Nhóm khách hàng Member đóng góp bao nhiêu % vào tổng lợi nhuận so với nhóm khách vãng lai Normal?
    def calculate_loyalty_value(self)->pd.DataFrame:
        df_revenue_customer_type=self.df.groupby('Customer type')[['Sales','gross income']].sum().reset_index()
        df_revenue=self.df['gross income'].sum()
        df_revenue_customer_type['percentage of total profit']=((df_revenue_customer_type['gross income']/df_revenue)*100).round(2)
        return df_revenue_customer_type


    #TODO:  calculate_average_order_value(self) -> pd.DataFrame: Cách tính: Tính giá trị đơn hàng trung bình (Tổng Sales / Tổng số Invoice ID) phân theo từng Chi nhánh, Loại khách hàng hoặc Khung giờ. Giá trị: Biết được nhóm nào đang mua giỏ hàng "giá trị cao" để tập trung upsell.
    def analyze_low_rating_bottlenecks(self) -> dict:
        low_rating_df = self.df[self.df['Rating'] < 5]
        if low_rating_df.empty:
            return {}

        by_branch = low_rating_df.groupby('Branch')['Invoice ID'].count().reset_index().rename(
            columns={'Invoice ID': 'Low_Rating_Count'})
        by_product = low_rating_df.groupby('Product line')['Invoice ID'].count().reset_index().rename(
            columns={'Invoice ID': 'Low_Rating_Count'})

        return {
            "by_branch": by_branch.sort_values(by='Low_Rating_Count', ascending=False),
            "by_product": by_product.sort_values(by='Low_Rating_Count', ascending=False)
        }