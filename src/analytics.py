import pandas as pd
from pandas import DataFrame

class Analytics:
    def __init__(self,df:DataFrame):
        self.df=df

    #: tính tổng doanh thu và lợi nhuận theo từng tháng.

    def calculate_monthly_revenue_profit(self) -> pd.DataFrame:
        monthly_stats = self.df.groupby('Month')[['Sales', 'Profit']].sum().reset_index()
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
        Total_Profit=('Profit', 'sum'),
        Total_Orders=('Invoice ID', 'count')
     ).reset_index()
        branch_stats = branch_stats.sort_values(by='Total_Sales', ascending=False)
        return branch_stats

    # Phân tích doanh thu và số lượng đơn hàng theo phương thức thanh toán
    def calculate_revenue_and_number_of_orders_by_payment_method(self)->pd.DataFrame:
        df=self.df.groupby('Payment').agg(
            Total_Orders=('Invoice ID','count'),
            Total_Sales=('Sales', 'sum'),
            Total_Profit=('Profit', 'sum'),
        )
        df=df.sort_values(by='Total_Sales')
        return df



    # Phân tích doanh thu theo loại khách hàng (Customer type) và Giới tính (Gender)


    # Phân tích khung giờ mua sắm cao điểm (Ví dụ: Sáng, Trưa, Chiều, Tối)
    def analyze_shopping_hours(self)->pd.DataFrame:
        df_shopping_hours=self.df.groupby('Hour').agg(
            Total_Orders=('Invoice ID','count'),
            Total_Sales=('Sales', 'sum'),
            Total_Profit=('Profit', 'sum'),
            avg_rating=('Rating','mean')
        ).reset_index()
        df_shopping_hours['avg_rating']=df_shopping_hours['avg_rating'].round(2)
        df_shopping_hours=df_shopping_hours.sort_values(by='Total_Orders')
        return df_shopping_hours

    #: Doanh thu theo từng ngành
    def calculate_revenue_by_product_line(self)->pd.DataFrame:
        revenue_product_line_stats=self.df.groupby('Product line')[['Profit','Sales']].sum().reset_index()
        return revenue_product_line_stats

    #Điểm đánh giá trung bình ở các chi nhánh
    def calculate_avg_rating_branches(self)->pd.DataFrame:
        df_rating_branch=self.df.groupby('Branch')['Rating'].mean().reset_index()
        df_rating_branch=df_rating_branch.sort_values(by='Rating')
        return df_rating_branch

    #: Điểm đánh giá theo từng ngành hàng
    def get_rating_by_product_line(self)->pd.DataFrame:
        df_rating_product_line=self.df.groupby('Product line')['Rating'].mean().reset_index()
        df_rating_product_line=df_rating_product_line.sort_values(by='Rating')
        return df_rating_product_line

    # TODO: Sức mua trên mỗi đơn hàng (Quantity per Ticket): Trung bình một hóa đơn khách mua bao nhiêu sản phẩm? Mặt hàng đó là gì?
    # Tương quan giữa các Ngành hàng (Cross-selling): Khách hàng mua ngành hàng A thì thường có xu hướng mua kèm ngành hàng nào khác không? (Ví dụ: Mua thực phẩm tươi sống có hay mua kèm gia vị không?).
    # Tỷ suất lợi nhuận gộp (Gross Profit Margin): Ngành hàng nào đang "gánh" lợi nhuận cho siêu thị? Có ngành hàng doanh thu rất cao nhưng biên lợi nhuận lại quá mỏng không?
    # Cấu trúc chi phí (Cost of Goods Sold - COGS Analysis): Tỷ trọng giá vốn trên doanh thu đổi theo từng tháng như thế nào? Xu hướng nhập hàng có đang bị đắt lên không?
    # Năng suất xử lý hóa đơn theo khung giờ (Throughput): Khung giờ cao điểm hệ thống xử lý được bao nhiêu hóa đơn/phút? Có dấu hiệu bị nghẽn (quá tải) khiến điểm Rating giảm không?
    # Biến động điểm số đánh giá (Rating Volatility): Tìm hiểu xem các điểm số thấp (1-3 sao) thường rơi vào chi nhánh nào, ngành hàng nào, hoặc phương thức thanh toán nào để tìm ra "vấn đề hệ thống" (Bottleneck).
    # Mức độ trung thành (Loyalty Value): Nhóm khách hàng Member đóng góp bao nhiêu % vào tổng lợi nhuận so với nhóm khách vãng lai Normal?
    # Sự khác biệt về hành vi theo giới tính (Gender Preference): Khách hàng Nam và Nữ có xu hướng chọn phương thức thanh toán khác nhau không? Họ thường gom nhóm mua hàng vào các khung giờ nào khác nhau?