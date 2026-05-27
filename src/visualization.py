import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Phân Tích Siêu Thị", page_icon="🛒", layout="wide")

# ==========================================
# 2. ĐỌC VÀ XỬ LÝ DỮ LIỆU
# ==========================================
# Sử dụng cache để web không phải load lại dữ liệu mỗi lần tương tác
@st.cache_data
def load_data():
    # Đường dẫn tới file dữ liệu của bạn
    df = pd.read_csv("data/raw/supermarket_data_sales.csv")
    df.columns = df.columns.str.strip()
    return df

df = load_data()

# ==========================================
# 3. THANH ĐIỀU HƯỚNG (SIDEBAR) - BỘ LỌC DỮ LIỆU
# ==========================================
st.sidebar.header("🔍 Bộ Lọc Dữ Liệu")

# Lọc theo Chi nhánh / Thành phố
city_options = df['City'].unique().tolist()
selected_city = st.sidebar.multiselect("Chọn Thành Phố:", city_options, default=city_options)

# Lọc theo Giới tính
gender_options = df['Gender'].unique().tolist()
selected_gender = st.sidebar.multiselect("Chọn Giới Tính:", gender_options, default=gender_options)

# Lọc theo Loại khách hàng
customer_options = df['Customer type'].unique().tolist()
selected_customer = st.sidebar.multiselect("Loại Khách Hàng:", customer_options, default=customer_options)

df_filtered = df[
    (df['City'].isin(selected_city)) &
    (df['Gender'].isin(selected_gender)) &
    (df['Customer type'].isin(selected_customer))
]

# ==========================================
# 4. KHU VỰC THỐNG KÊ TỔNG QUAN (KPIs)
# ==========================================


row1_col1, row1_col2 = st.columns(2)

# BIỂU ĐỒ 1: Cơ cấu Phương thức thanh toán (Pie Chart)
with row1_col1:
    st.subheader("💳 Cơ Cấu Phương Thức Thanh Toán")
    
    
    chart_type = st.selectbox(
        "Tùy chọn hiển thị:",
        options=["Biểu đồ Tròn (Donut/Pie)", "Biểu đồ Cột (Bar Chart)"],
        index=0 
    )
    
    # 2. Gom nhóm dữ liệu
    payment_df = df_filtered.groupby('Payment', as_index=False)['Sales'].sum()
    
   
    if chart_type == "Biểu đồ Tròn (Donut/Pie)":
        fig_payment = px.pie(payment_df, names='Payment', values='Sales', hole=0.4,
                             color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_payment.update_traces(textinfo='percent+label', 
                                  hovertemplate="<b>%{label}</b><br>Doanh thu: %{value:,.0f} ₫")
    else:
        fig_payment = px.bar(payment_df, x='Payment', y='Sales', color='Payment',
                             text='Sales', color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_payment.update_traces(texttemplate='%{text:,.0f} ₫', textposition='outside',
                                  hovertemplate="<b>%{x}</b><br>Doanh thu: %{y:,.0f} ₫<extra></extra>")
        fig_payment.update_layout(xaxis_title="", yaxis_title="Doanh Thu (VND)", showlegend=False)
        fig_payment.update_yaxes(range=[0, payment_df['Sales'].max() * 1.2]) 
        
    # 4. Hiển thị biểu đồ ra màn hình
    st.plotly_chart(fig_payment, width='stretch')
# BIỂU ĐỒ 2: Doanh thu theo Ngành hàng (Bar Chart)
with row1_col2:
    st.subheader("🛍️ Doanh Thu Theo Từng Ngành Hàng")
    
   
    chart_type_2 = st.selectbox(
        "Tùy chọn hiển thị:",
        options=["Biểu đồ Cột Ngang (Horizontal Bar)", "Biểu đồ Cột Dọc (Vertical Bar)", "Biểu đồ Dạng Cây (Treemap)"],
        index=0,
        key="selectbox_nganh_hang" 
    )
    
    
    cat_df = df_filtered.groupby('Product line', as_index=False)['Sales'].sum().sort_values(by='Sales')
    
    if chart_type_2 == "Biểu đồ Cột Ngang (Horizontal Bar)":
        fig_cat = px.bar(cat_df, x='Sales', y='Product line', orientation='h', text='Sales',
                         color='Sales', color_continuous_scale='Blues')
        fig_cat.update_traces(texttemplate='%{text:,.0f} ₫', textposition='outside')
        fig_cat.update_layout(xaxis_title="Doanh Thu (VND)", yaxis_title="")
        
    elif chart_type_2 == "Biểu đồ Cột Dọc (Vertical Bar)":
        fig_cat = px.bar(cat_df, x='Product line', y='Sales', text='Sales',
                         color='Sales', color_continuous_scale='Blues')
        fig_cat.update_traces(texttemplate='%{text:,.0f} ₫', textposition='outside')
        fig_cat.update_layout(xaxis_title="Ngành Hàng", yaxis_title="Doanh Thu (VND)")
        fig_cat.update_yaxes(range=[0, cat_df['Sales'].max() * 1.2]) 
        
    else:
        # Lựa chọn 3: Biểu đồ Treemap (Dạng khối vuông)
        fig_cat = px.treemap(cat_df, path=['Product line'], values='Sales', 
                             color='Sales', color_continuous_scale='Blues')
        fig_cat.update_traces(textinfo="label+value", texttemplate="<b>%{label}</b><br>%{value:,.0f} ₫")
        
        fig_cat.update_layout(margin=dict(t=10, l=10, r=10, b=10))

    st.plotly_chart(fig_cat, width='stretch')

row2_col1, row2_col2 = st.columns(2)

# BIỂU ĐỒ 3: Phân bố Sao đánh giá (Histogram)
with row2_col1:
    st.subheader("⭐ Phân Bố Điểm Đánh Giá Của Khách Hàng")
    chart_type_3 = st.selectbox(
        "Tùy chọn hiển thị phân bố:",
        options=["Biểu đồ Tần suất (Histogram)", "Biểu đồ Hộp (Box Plot)", "Biểu đồ Violin"],
        index=0,
        key="selectbox_rating_dist"
    )
    
    # 2. Vẽ biểu đồ theo lựa chọn
    if chart_type_3 == "Biểu đồ Tần suất (Histogram)":
        fig_rating = px.histogram(df_filtered, x='Rating', nbins=20, 
                                  color_discrete_sequence=['#FFC107'],
                                  labels={'Rating': 'Điểm số (1-10)'})
        fig_rating.update_layout(yaxis_title="Số lượng hóa đơn")
        
    elif chart_type_3 == "Biểu đồ Hộp (Box Plot)":
        fig_rating = px.box(df_filtered, x='Rating', 
                            color_discrete_sequence=['#FFC107'],
                            labels={'Rating': 'Điểm số (1-10)'})
        fig_rating.update_layout(yaxis_title="")
        
    else: # Biểu đồ Violin
        fig_rating = px.violin(df_filtered, x='Rating', box=True, points="all",
                               color_discrete_sequence=['#FFC107'],
                               labels={'Rating': 'Điểm số (1-10)'})
        fig_rating.update_layout(yaxis_title="")

    # 3. Hiển thị
    st.plotly_chart(fig_rating, width='stretch')
# BIỂU ĐỒ 4: Đánh giá trung bình theo Ngành hàng
with row2_col2:
    st.subheader("📉 Mức Độ Hài Lòng Theo Ngành Hàng")
    chart_type_4 = st.selectbox(
        "Tùy chọn hiển thị xếp hạng:",
        options=["Biểu đồ Cột Ngang (Horizontal Bar)", "Biểu đồ Điểm (Dot Plot)"],
        index=0,
        key="selectbox_rating_cat"
    )
    
   
    rating_cat_df = df_filtered.groupby('Product line', as_index=False)['Rating'].mean().sort_values(by='Rating')
    
    
    if chart_type_4 == "Biểu đồ Cột Ngang (Horizontal Bar)":
        fig_rating_cat = px.bar(rating_cat_df, x='Rating', y='Product line', orientation='h',
                                text='Rating', color='Rating', color_continuous_scale='Reds_r')
        fig_rating_cat.update_traces(texttemplate='<b>%{text:.1f} ⭐</b>', textposition='inside')
        
    else: 
        fig_rating_cat = px.scatter(rating_cat_df, x='Rating', y='Product line',
                                    color='Rating', size='Rating', color_continuous_scale='Reds_r')
  
        fig_rating_cat.update_traces(marker=dict(size=18), text=rating_cat_df['Rating'],
                                     texttemplate='<b>%{text:.1f} ⭐</b>', mode='markers+text', 
                                     textposition='middle right')

    
    fig_rating_cat.update_layout(xaxis_title="Điểm Đánh Giá TB", yaxis_title="", xaxis_range=[4, 10.5])
    
   
    st.plotly_chart(fig_rating_cat, width='stretch')



