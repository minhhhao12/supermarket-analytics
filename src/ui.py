import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import os
import matplotlib.ticker as ticker
import plotly.express as px
from pathlib import Path
import altair as alt
from visualization import vis_filter_chart
from data_validator import DataValidator
#Data
st.set_page_config(page_title="admin", layout="wide")
# File CSS
def load_css(css_file):
    with open(css_file, "r", encoding="utf-8") as f:
        st.markdown(
            f"<style>{f.read()}</style>",
            unsafe_allow_html=True
        )
BASE_DIR = Path(__file__).parent
css_path = BASE_DIR / "assets" / "styles.css"
load_css(css_path)
#file data(cvs)
if "df" not in st.session_state:
    try:
        st.session_state.df = pd.read_csv("data/raw/supermarket_data_sales.csv")
    except FileNotFoundError:
        st.error("⚠️ 'supermarket_data_sales.csv' not found in your directory!")
        st.stop()
df = st.session_state.df
# khi chạy chương trình thì default đến trang Validation
if "active_page" not in st.session_state:
    st.session_state.active_page = "Data Validation"
#sidebar
with st.sidebar:
    st.markdown("**Admin Tools**")
    # Nút Validation (va)
    is_val_active = st.session_state.active_page == "Data Validation"
    val_label = "**DATA VALIDATION**" if is_val_active else "Data Validation"
    if st.button(val_label,  width="stretch", type="primary" if is_val_active else "secondary",key='btn_va'):
        st.session_state.active_page = "Data Validation"
        st.rerun()

    # Nút Visualization (vis)
    is_vis_active = st.session_state.active_page == "Data Visualization"
    vis_label = "**DATA VISUALIZATION**" if is_vis_active else "Data Visualization"
    if st.button(vis_label,  width="stretch", type="primary" if is_vis_active else "secondary",key='btn_vis'):
        st.session_state.active_page = "Data Visualization"
        st.rerun()
    if st.session_state.active_page == "Data Visualization":
        #city hay branch
        selected_city = st.multiselect(label="Chọn thành phố", options=df['City'].unique().tolist())
        selected_product = st.multiselect(label="Chọn sản phẩm", options=df['Product line'].unique().tolist())
        selected_Gender = st.multiselect(label="Chọn giới tính", options=df['Gender'].unique().tolist())
        selected_Customertypes = st.multiselect(label="Chọn loại khách hàng",options=df['Customer type'].unique().tolist())

        city_filter = selected_city if selected_city else df['City'].unique().tolist()
        product_filter = selected_product if selected_product else df['Product line'].unique().tolist()
        gender_filter = selected_Gender if selected_Gender else df['Gender'].unique().tolist()
        customer_filter = selected_Customertypes if selected_Customertypes else df['Customer type'].unique().tolist()
        filter_sidebar= df[
        (df['City'].isin(city_filter)) & (df['Product line'].isin(product_filter)) & (df['Gender'].isin(gender_filter)) & (df['Customer type'].isin(customer_filter))
        ]

##main page
 #va main page
center_canvas, pad_right = st.columns([ 5, 1])
with center_canvas:
    if st.session_state.active_page == "Data Validation":
        row1_col1, row1_col2, row1_col3, row1_col4 = st.columns(4)
        with row1_col1:
            with st.container(border=True, height=150):
                btn_validate=st.button('Validate File',key='btn_validate_preview', width="stretch")
        with row1_col2:
            with st.container(border=True, height=150):
                btn_fix=st.button('Fix File',key='btn_fix_preview', width="stretch")
        with row1_col3:
            with st.container(border=True,height=150):
                file_uploaded=st.file_uploader('Upload file CSV of your data',type=["csv"],accept_multiple_files=False,label_visibility="collapsed",key='btn_upload_preview',width="stretch")
        with row1_col4:
                if file_uploaded is not None:
                    with st.container(border=True, height=150):
                        df_current = pd.read_csv(file_uploaded)
                        st.success(f"📥 Đã nhận file: **{file_uploaded.name}**")
        row2_col1, row2_col2 = st.columns(2)
        with row2_col1:
         with st.container(border=True, height=450):
            if file_uploaded:
                st.dataframe(df_current)
            else:
                st.info("Xin hãy upload file.")
        with row2_col2:
         with st.container(border=True, height=200):
            if btn_validate:
                st.subheader("📊 Kết quả quét dữ liệu hệ thống")
                if file_uploaded:
                        validator = DataValidator(df_current)
                        ket_qua = validator.run_all_validators()
                        if not ket_qua:
                            st.success(
                                "🎉 Tuyệt vời! Dữ liệu hoàn toàn sạch sẽ, không phát hiện lỗi logic hoặc sai lệch tiền tệ.")
                        else:
                            st.error(f"❌ Phát hiện {len(ket_qua['errors'])} lỗi nghiêm trọng trong file dữ liệu:")
                            for error in ket_qua:
                                st.info(f"👉 {error}")
                else: st.info("bạn chưa upload file")
     #vis main page
    elif st.session_state.active_page == "Data Visualization":
        filter_sidebar['Date'] = pd.to_datetime(filter_sidebar['Date'],errors='coerce')
        date_options = sorted(filter_sidebar['Date'].dropna().dt.date.unique())
        selected_date = st.date_input(label="📅 Chọn ngày xem báo cáo:", value=date_options[0], min_value=date_options[0], max_value=date_options[-1] )

        df_filtered = filter_sidebar[filter_sidebar['Date'].dt.date == selected_date]

        sum_tab, avg_tab = st.columns(2)
        with sum_tab:
            total_sales = df_filtered["Sales"].sum()
            st.metric("Total Sales", f"{df_filtered['Sales'].sum():,.0f}",border=True)
        with avg_tab:
            avg_sales = df_filtered["Sales"].mean()
            st.metric("Average Sales",f"{df_filtered['Sales'].mean():,.2f}",border=True )
        row1_col1, row1_col2,= st.columns(2)
        with row1_col1:
            st.write('chart')
        with row1_col2:
            st.write('chart')
        row2_col1, row2_col2 = st.columns(2)
        with row2_col1:
            st.write('chart')
        with row2_col2:
            st.write('chart')
with pad_right:
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {"role": "assistant", "content": "How can I help you analyze the supermarket sales data today?"}
        ]
    # tạo khung
    chat_container = st.container(height=400,key="chat_container")
    # hiện lịch sử chat
    with chat_container:
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.write(message["content"])
    if prompt := st.chat_input("Ask assistant...", key="chat_input"):
        # hiện user_input lên chatbox
        with chat_container:
            with st.chat_message("user"):
                st.write(prompt)
        st.session_state.chat_history.append({"role": "user", "content": prompt})