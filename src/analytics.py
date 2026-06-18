import pandas as pd
from pandas import DataFrame
from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler


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
    def analyze_low_rating_bottlenecks(self) -> tuple:
        low_rating_df = self.df[self.df['Rating']<5]
        if low_rating_df.empty:
            return ()
        by_branch =low_rating_df.groupby('Branch')['Invoice ID'].count().reset_index()
        by_product =low_rating_df.groupby('Product line')['Invoice ID'].count().reset_index()
        return by_branch, by_product

    # Mức độ trung thành (Loyalty Value): Nhóm khách hàng Member đóng góp bao nhiêu % vào tổng lợi nhuận so với nhóm khách vãng lai Normal?
    def calculate_loyalty_value(self)->pd.DataFrame:
        df_revenue_customer_type=self.df.groupby('Customer type')[['Sales','gross income']].sum().reset_index()
        df_revenue=self.df['gross income'].sum()
        df_revenue_customer_type['percentage of total profit']=((df_revenue_customer_type['gross income']/df_revenue)*100).round(2)
        return df_revenue_customer_type

    #Tính giá trị đơn hàng trung bình (Tổng Sales / Tổng số Invoice ID) phân theo từng Chi nhánh, Loại khách hàng. Giá trị: Biết được nhóm nào đang mua giỏ hàng "giá trị cao" để tập trung upsell.
    def calculate_average_order_value(self)->pd.DataFrame:
        df_average_order_value=self.df.groupby(['Branch','Customer type']).agg(
            Total_Sales=('Sales','sum'),
            Total_Orders=('Invoice ID','count')
        )
        df_average_order_value['average_order_value']=(df_average_order_value['Total_Sales']/df_average_order_value['Total_Orders']).round(2)
        df_average_order_value=df_average_order_value.sort_values(by='average_order_value',ascending=False)
        return df_average_order_value

    #Phân tích số lượng sản phẩm trung bình trên một đơn hàng theo Ngành hàng:analyze_basket_size
    def analyze_basket_size(self)->pd.DataFrame:
        df=self.df.groupby('Product line').agg(
            total_quantity=('Quantity','sum'),
            total_order=('Invoice ID','count')
        ).reset_index()
        df['average order item']=(df['total_quantity']/df['total_order']).round(1)
        return df

    def analyze_rating_vs_sales_correlation(self) -> float:
        # Tính hệ số tương quan (Correlation) giữa điểm Rating và Doanh số Sales.
        # Giúp biết được khách mua đơn hàng lớn thì có khó tính hơn (cho điểm thấp hơn) không
        correlation = self.df['Rating'].corr(self.df['Sales'])
        return round(correlation, 4)

    def get_executive_summary(self) -> dict:
        # Tổng hợp các chỉ số sức khỏe tài chính cốt lõi của siêu thị (KPIs).
        total_sales = self.df['Sales'].sum()
        total_profit = self.df['gross income'].sum()
        total_orders = self.df['Invoice ID'].count()

        summary = {
            "Total_Revenue": round(total_sales, 2),
            "Total_Profit": round(total_profit, 2),
            "Total_Orders": int(total_orders),
            "Overall_Gross_Margin_Percent": round((total_profit / total_sales) * 100, 2),
            "Overall_AOV": round(total_sales / total_orders, 2),
            "Overall_Avg_Rating": round(self.df['Rating'].mean(), 2)
        }
        return summary

    #Dự báo doanh thu 30 ngày tiếp theo
    def forecast_next_month_revenue(self)->pd.DataFrame:
        df_daily_revenue=self.df.groupby(['Year','Month','Day'])['Sales'].sum().reset_index()
        df_daily_revenue['Day_Index']=df_daily_revenue.index
        X=df_daily_revenue[['Day_Index']]
        y=df_daily_revenue['Sales']
        model=LinearRegression()
        model.fit(X,y)

        last_index=df_daily_revenue['Day_Index'].max()
        future_df=pd.DataFrame({
            'Day_Index':range(last_index+1,last_index+31)
        })
        forecast_sale=model.predict(future_df)
        forecast_df=pd.DataFrame(
            {
                "Day": range(1, 31),
                "Forecast_Sales": forecast_sale.round(2),
            }
        )
        return forecast_df

    # Sử dụng thuật toán K-Means để phân cụm hành vi mua sắm của khách hàng
    # dựa trên số lượng đơn hàng và tổng chi tiêu của họ.
    def advanced_customer_segmentation(self) -> pd.DataFrame:
        # 1. Trích xuất đặc trưng hành vi khách hàng từ Invoice ID
        features = self.df.groupby(['Customer type', 'Gender']).agg(
            Total_Sales=('Sales', 'sum'),
            Total_Orders=('Invoice ID', 'count'),
            Avg_Quantity=('Quantity', 'mean')
        ).reset_index()

        # 2. Chuẩn hóa dữ liệu trước khi chạy K-Means
        scaler=StandardScaler()
        scaled_features = scaler.fit_transform(features[['Total_Sales', 'Total_Orders', 'Avg_Quantity']])

        # 3. Chạy thuật toán K-Means với k=3 (3 nhóm khách hàng)
        kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
        features['Cluster'] = kmeans.fit_predict(scaled_features)

        # Đổi tên cluster thành cho dễ hiểu
        cluster_mapping={0:'Khách hàng Phổ thông', 1:'Khách hàng Tiềm năng', 2:'Khách hàng VIP'}
        features['Customer_Segment'] = features['Cluster'].map(cluster_mapping)
        return features.sort_values(by='Total_Sales', ascending=False)

    def calculate_correlation_matrix(self) -> pd.DataFrame:
        """Tính toán ma trận tương quan giữa các cột số quan trọng."""
        numeric_cols = ['Unit price', 'Quantity', 'Tax 5%', 'Sales', 'cogs', 'gross income', 'Rating']
        corr_matrix = self.df[numeric_cols].corr()
        return corr_matrix
