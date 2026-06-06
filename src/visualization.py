import streamlit as st
import pandas as pd
import plotly.express as px


st.set_page_config(page_title="Phân Tích Siêu Thị", page_icon="🛒", layout="wide")

# ==============================
# 0. HÀM ĐỌC DỮ LIỆU (Tối ưu Cache)
# ==============================
@st.cache_data
def load_data(file_path: str):
    df = pd.read_csv(file_path)
    df.columns = df.columns.str.strip()
    return df

# ==============================
# 1. LỚP QUẢN LÝ DỮ LIỆU (MODEL)
# ==============================
class DataHandler:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.df = load_data(self.file_path)

    def filter_data(self, selected_city, selected_gender, selected_customer):
        return self.df[
            (self.df['City'].isin(selected_city)) &
            (self.df['Gender'].isin(selected_gender)) &
            (self.df['Customer type'].isin(selected_customer))
        ]

# ==============================
# 2. LỚP VẼ BIỂU ĐỒ (VIEW)
# ==============================
class ChartBuilder:
    def __init__(self, df_filtered):
        self.df = df_filtered

    def payment_chart(self, chart_type):
        payment_df = self.df.groupby('Payment', as_index=False)['Sales'].sum()
        if chart_type == "Biểu đồ Tròn (Donut/Pie)":
            fig = px.pie(payment_df, names='Payment', values='Sales', hole=0.4,
                         color_discrete_sequence=px.colors.qualitative.Pastel)
            fig.update_traces(textinfo='percent+label',
                              hovertemplate="<b>%{label}</b><br>Doanh thu: %{value:,.0f} ₫")
        else:
            fig = px.bar(payment_df, x='Payment', y='Sales', color='Payment',
                         text='Sales', color_discrete_sequence=px.colors.qualitative.Pastel)
            fig.update_traces(texttemplate='%{text:,.0f} ₫', textposition='outside',
                              hovertemplate="<b>%{x}</b><br>Doanh thu: %{y:,.0f} ₫<extra></extra>")
            fig.update_layout(xaxis_title="", yaxis_title="Doanh Thu (VND)", showlegend=False)
            fig.update_yaxes(range=[0, payment_df['Sales'].max() * 1.2])
        return fig

    def category_chart(self, chart_type):
        cat_df = self.df.groupby('Product line', as_index=False)['Sales'].sum().sort_values(by='Sales')
        if chart_type == "Biểu đồ Cột Ngang (Horizontal Bar)":
            fig = px.bar(cat_df, x='Sales', y='Product line', orientation='h', text='Sales',
                         color='Sales', color_continuous_scale='Blues')
            fig.update_traces(texttemplate='%{text:,.0f} ₫', textposition='outside')
            fig.update_layout(xaxis_title="Doanh Thu (VND)", yaxis_title="")
        elif chart_type == "Biểu đồ Cột Dọc (Vertical Bar)":
            fig = px.bar(cat_df, x='Product line', y='Sales', text='Sales',
                         color='Sales', color_continuous_scale='Blues')
            fig.update_traces(texttemplate='%{text:,.0f} ₫', textposition='outside')
            fig.update_layout(xaxis_title="Ngành Hàng", yaxis_title="Doanh Thu (VND)")
            fig.update_yaxes(range=[0, cat_df['Sales'].max() * 1.2])
        else:
            fig = px.treemap(cat_df, path=['Product line'], values='Sales',
                             color='Sales', color_continuous_scale='Blues')
            fig.update_traces(textinfo="label+value", texttemplate="<b>%{label}</b><br>%{value:,.0f} ₫")
            fig.update_layout(margin=dict(t=10, l=10, r=10, b=10))
        return fig

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

    def rating_by_category(self, chart_type):
        rating_cat_df = self.df.groupby('Product line', as_index=False)['Rating'].mean().sort_values(by='Rating')
        if chart_type == "Biểu đồ Cột Ngang (Horizontal Bar)":
            fig = px.bar(rating_cat_df, x='Rating', y='Product line', orientation='h',
                         text='Rating', color='Rating', color_continuous_scale='Reds_r')
            fig.update_traces(texttemplate='<b>%{text:.1f} ⭐</b>', textposition='inside')
        else:
            fig = px.scatter(rating_cat_df, x='Rating', y='Product line',
                             color='Rating', size='Rating', color_continuous_scale='Reds_r')
            fig.update_traces(marker=dict(size=18), text=rating_cat_df['Rating'],
                              texttemplate='<b>%{text:.1f} ⭐</b>', mode='markers+text',
                              textposition='middle right')
        fig.update_layout(xaxis_title="Điểm Đánh Giá TB", yaxis_title="", xaxis_range=[4, 10.5])
        return fig

# ==============================
# 3. LỚP ỨNG DỤNG STREAMLIT (CONTROLLER)
# ==============================
class SupermarketApp:
    def __init__(self, df_filtered):
        self.df_filtered = df_filtered

    def run(self):

        chart_builder = ChartBuilder(self.df_filtered)

        row1_col1, row1_col2 = st.columns(2)
        with row1_col1:
            st.subheader("💳 Cơ Cấu Phương Thức Thanh Toán")
            chart_type = st.selectbox("Tùy chọn hiển thị:",
                                      options=["Biểu đồ Tròn (Donut/Pie)", "Biểu đồ Cột (Bar Chart)"])
            st.plotly_chart(chart_builder.payment_chart(chart_type), width='stretch')

        with row1_col2:
            st.subheader("🛍️ Doanh Thu Theo Từng Ngành Hàng")
            chart_type_2 = st.selectbox("Tùy chọn hiển thị:",
                                        options=["Biểu đồ Cột Ngang (Horizontal Bar)",
                                                 "Biểu đồ Cột Dọc (Vertical Bar)",
                                                 "Biểu đồ Dạng Cây (Treemap)"],
                                        key="selectbox_nganh_hang")
            st.plotly_chart(chart_builder.category_chart(chart_type_2), width='stretch')

        row2_col1, row2_col2 = st.columns(2)
        with row2_col1:
            st.subheader("⭐ Phân Bố Điểm Đánh Giá Của Khách Hàng")
            chart_type_3 = st.selectbox("Tùy chọn hiển thị phân bố:",
                                        options=["Biểu đồ Tần suất (Histogram)",
                                                 "Biểu đồ Hộp (Box Plot)",
                                                 "Biểu đồ Violin"],
                                        key="selectbox_rating_dist")
            st.plotly_chart(chart_builder.rating_distribution(chart_type_3), width='stretch')

        with row2_col2:
            st.subheader("📉 Mức Độ Hài Lòng Theo Ngành Hàng")
            chart_type_4 = st.selectbox("Tùy chọn hiển thị xếp hạng:",
                                        options=["Biểu đồ Cột Ngang (Horizontal Bar)",
                                                 "Biểu đồ Điểm (Dot Plot)"],
                                        key="selectbox_rating_cat")
            st.plotly_chart(chart_builder.rating_by_category(chart_type_4), width='stretch')

# ==============================
# 4. MAIN - ĐIỂM KÍCH HOẠT
# ==============================
if __name__ == "__main__":
    FILE_PATH = "data/raw/supermarket_data_sales.csv"
    try:
        data_handler = DataHandler(FILE_PATH)
        app = SupermarketApp(data_handler)
        app.run()
    except FileNotFoundError:
        st.error(f"Không tìm thấy dữ liệu tại đường dẫn: {FILE_PATH}. Vui lòng kiểm tra lại!")