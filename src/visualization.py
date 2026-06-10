import plotly.express as px
import plotly.graph_objects as go
from analytics import Analytics

# ==============================
# LỚP VẼ BIỂU ĐỒ (VIEW)
# ==============================
class ChartBuilder:
    def __init__(self, df_filtered):
        self.df = df_filtered
        self.analytics = Analytics(self.df)

    # 1. Biểu đồ Cơ cấu Thanh toán
    def payment_chart(self, chart_type):
        payment_df = self.analytics.calculate_revenue_and_number_of_orders_by_payment_method().reset_index()
        if chart_type == "Biểu đồ Tròn (Donut/Pie)":
            fig = px.pie(payment_df, names='Payment', values='Total_Sales', hole=0.4,
                         color_discrete_sequence=px.colors.qualitative.Pastel)
            fig.update_traces(textinfo='percent+label',
                              hovertemplate="<b>%{label}</b><br>Doanh thu: $%{value:,.0f}")
        else:
            fig = px.bar(payment_df, x='Payment', y='Total_Sales', color='Payment',
                         text='Total_Sales', color_discrete_sequence=px.colors.qualitative.Pastel)
            fig.update_traces(texttemplate='$%{text:,.0f}', textposition='outside',
                              hovertemplate="<b>%{x}</b><br>Doanh thu: $%{y:,.0f}<extra></extra>")
            fig.update_layout(xaxis_title="", yaxis_title="Doanh Thu ($)", showlegend=False)
            fig.update_yaxes(range=[0, payment_df['Total_Sales'].max() * 1.2])
        return fig

    # 2. Biểu đồ Doanh thu theo Ngành hàng
    def category_chart(self, chart_type):
        cat_df = self.analytics.calculate_revenue_by_product_line()[0]
        if chart_type == "Biểu đồ Cột Ngang (Horizontal Bar)":
            fig = px.bar(cat_df, x='Sales', y='Product line', orientation='h', text='Sales',
                         color='Sales', color_continuous_scale='Blues')
            fig.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
            fig.update_layout(xaxis_title="Doanh Thu ($)", yaxis_title="")
        elif chart_type == "Biểu đồ Cột Dọc (Vertical Bar)":
            fig = px.bar(cat_df, x='Product line', y='Sales', text='Sales',
                         color='Sales', color_continuous_scale='Blues')
            fig.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
            fig.update_layout(xaxis_title="Ngành Hàng", yaxis_title="Doanh Thu ($)")
            fig.update_yaxes(range=[0, cat_df['Sales'].max() * 1.2])
        else:
            fig = px.treemap(cat_df, path=['Product line'], values='Sales',
                             color='Sales', color_continuous_scale='Blues')
            fig.update_traces(textinfo="label+value", texttemplate="<b>%{label}</b><br>$%{value:,.0f}")
            fig.update_layout(margin=dict(t=10, l=10, r=10, b=10))
        return fig

    # 3. Biểu đồ Phân bố Điểm Đánh giá
    def rating_distribution(self, chart_type):
        if chart_type == "Biểu đồ Tần suất (Histogram)":
            fig = px.histogram(self.df, x='Rating', nbins=20,
                               color_discrete_sequence=['#FFC107'],
                               labels={'Rating': 'Điểm số (1-10)'})
            fig.update_layout(yaxis_title="Số lượng hóa đơn")
        elif chart_type == "Biểu đồ Hộp (Box Plot)":
            fig = px.box(self.df, x='Rating',
                         color_discrete_sequence=['#FFC107'],
                         labels={'Rating': 'Điểm số (1-10)'})
        else:
            fig = px.violin(self.df, x='Rating', box=True, points="all",
                            color_discrete_sequence=['#FFC107'],
                            labels={'Rating': 'Điểm số (1-10)'})
        return fig

    # 4. Biểu đồ Độ Hài lòng theo Ngành Hàng
    def rating_by_category(self, chart_type):
        rating_cat_df = self.analytics.get_avg_rating_by_product_line()
        if chart_type == "Biểu đồ Cột Ngang (Horizontal Bar)":
            fig = px.bar(rating_cat_df, x='Rating', y='Product line', orientation='h',
                         text='Rating', color='Rating', color_continuous_scale='Reds_r')
            fig.update_traces(texttemplate='<b>%{text:.1f} ⭐</b>', textposition='inside')
        else:
            fig = px.scatter(rating_cat_df, x='Rating', y='Product line',
                             color='Rating', size='Rating', color_continuous_scale='Reds_r')
            fig.update_traces(marker=dict(size=18), text=rating_cat_df['Rating'].round(1),
                              texttemplate='<b>%{text:.1f} ⭐</b>', mode='markers+text',
                              textposition='middle right')
        fig.update_layout(xaxis_title="Điểm Đánh Giá TB", yaxis_title="", xaxis_range=[4, 10.5])
        return fig

    # -- THÊM CÁC BIỂU ĐỒ MỚI DỰA TRÊN ANALYTICS --

    # 5. Biểu đồ Doanh thu và Lợi nhuận theo Chi nhánh
    def branch_performance_chart(self):
        branch_df = self.analytics.calculate_branch_performance()
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=branch_df['Branch'],
            y=branch_df['Total_Sales'],
            name='Tổng Doanh Thu',
            marker_color='indianred'
        ))
        fig.add_trace(go.Bar(
            x=branch_df['Branch'],
            y=branch_df['Total_Profit'],
            name='Tổng Lợi Nhuận',
            marker_color='lightsalmon'
        ))
        fig.update_layout(barmode='group', xaxis_title='Chi nhánh', yaxis_title='USD ($)', title="Hiệu suất Chi nhánh")
        return fig

    # 6. Doanh thu theo loại khách hàng và Giới tính
    def customer_gender_revenue_chart(self):
        df = self.analytics.get_revenue_by_customer_type_and_gender()
        fig = px.sunburst(df, path=['Customer type', 'Gender'], values='Sales',
                          color='Sales', color_continuous_scale='RdBu',
                          title="Cơ cấu Doanh thu theo Khách hàng & Giới tính")
        fig.update_traces(textinfo="label+percent parent+value")
        return fig

    # 7. Khung giờ mua sắm cao điểm
    def shopping_hours_chart(self):
        df = self.analytics.analyze_shopping_hours()
        df = df.sort_values(by='Hour')
        fig = px.line(df, x='Hour', y='Total_Orders', markers=True, 
                      title="Lượng Đơn Hàng Theo Khung Giờ",
                      labels={"Hour": "Giờ trong ngày", "Total_Orders": "Số lượng đơn"})
        fig.update_traces(line_color='#17a2b8', marker=dict(size=8))
        fig.update_layout(xaxis=dict(tickmode='linear', tick0=0, dtick=1))
        return fig
    
    # 8. Dự báo doanh thu 30 ngày (Dạng đường)
    def forecast_revenue_chart(self):
        df = self.analytics.forecast_next_month_revenue()
        fig = px.line(df, x='Day', y='Forecast_Sales', markers=True,
                      title="Dự báo Doanh thu 30 ngày tới (Linear Regression)",
                      labels={"Day": "Ngày", "Forecast_Sales": "Doanh thu dự báo ($)"})
        fig.update_traces(line_color='#28a745', line_dash="dot")
        return fig