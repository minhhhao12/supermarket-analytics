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
from data_validator import DataValidator
from ai_assistant import AIAssistant
from dotenv import load_dotenv
load_dotenv()
import google
from google import genai
from google.genai import types
from google.genai.types import GenerateContentResponse
from googleapiclient import errors
from analytics import Analytics
from data_loader import DataLoader
from data_processor import DataProcessor
from visualization import SupermarketApp
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
        df = st.session_state.uploaded_df
        if df is not None:
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
center_canvas, AI_right = st.columns([ 4, 2])
with center_canvas:
    if "uploaded_df" not in st.session_state:
        st.session_state.uploaded_df = None
    if st.session_state.active_page == "Data Validation":
        row1_col1, row1_col2= st.columns(2)
        with row1_col1:
            with st.container(border=True,height=150):
                file_uploaded=st.file_uploader('Upload file CSV of your data',type=["csv"],accept_multiple_files=False,label_visibility="collapsed",key='btn_upload_preview',width="stretch")
        with row1_col2:
                if file_uploaded is not None:
                        df_current = pd.read_csv(file_uploaded)
                        st.success(f" Đã nhận file: **{file_uploaded.name}**")
                        st.session_state.uploaded_df = df_current
                        st.session_state.file_name = file_uploaded.name
                elif st.session_state.uploaded_df is not None:
                    file_name = st.session_state.get("file_name", "Unknown name")
                    st.info(f'holding file {file_name}')
                else:
                    st.warning("upload data file to start")

        row2_col1, row2_col2 = st.columns(2)
        with row2_col1:
         with st.container(border=True):
            if st.session_state.uploaded_df is not None:
                st.dataframe(st.session_state.uploaded_df)
            else:
                st.info("Xin hãy upload file.")
        with row2_col2:
         with st.container(border=True):
                st.subheader("Kết quả quét dữ liệu hệ thống")
                if st.session_state.uploaded_df is not None:
                        validator = DataValidator(st.session_state.uploaded_df)
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
        if df is not None:
            filter_sidebar['Date'] = pd.to_datetime(filter_sidebar['Date'],errors='coerce')
            date_options = sorted(filter_sidebar['Date'].dropna().dt.date.unique())
            if date_options:
                selected_date = st.date_input(label="📅 Chọn ngày xem báo cáo:", value=date_options[0], min_value=date_options[0], max_value=date_options[-1] )
                df_final_filtered = filter_sidebar[filter_sidebar['Date'].dt.date == selected_date]
            else:
                df_final_filtered = filter_sidebar
                sum_tab, avg_tab = st.columns(2)
                with sum_tab:
                    total_sales = df_final_filtered["Sales"].sum()
                    st.metric("Total Sales", f"{df_final_filtered['Sales'].sum():,.0f}",border=True)
                with avg_tab:
                    avg_sales = df_final_filtered["Sales"].mean()
                    st.metric("Average Sales",f"{df_final_filtered['Sales'].mean():,.2f}",border=True )
            if not df_final_filtered.empty:
                # Khởi tạo đối tượng App và truyền DataFrame đã lọc qua cả 2 tầng vào
                app_visualizer = SupermarketApp(df_filtered=df_final_filtered)

                # Ra lệnh kích hoạt vẽ toàn bộ 4 biểu đồ Plotly ra màn hình chính
                app_visualizer.run()
        else:
            st.info("Please upload your data to start")
with AI_right:
    if "ai_instance" not in st.session_state:
        # Giả sử Class của bạn nhận lịch sử chat hoặc cấu hình lúc khởi tạo
        # Nếu class của bạn không cần truyền tham số gì lúc __init__, hãy để trống: AIAssistant()
        st.session_state.ai_instance = AIAssistant()

        # Rút đối tượng AI đã lưu trong bộ nhớ ra để sử dụng xuyên suốt phiên làm việc
    ai = st.session_state.ai_instance

    # Quản lý lịch sử hiển thị trên giao diện (Đồng bộ với thuộc tính chat của class nếu cần)
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {"role": "assistant", "content": "How can I help you analyze the supermarket sales data today?"}
        ]

    # Tạo khung container cố định chiều cao (400px) để cố định giao diện chat
    chat_container = st.container(height=500, key="chat_container")

    # Hiển thị toàn bộ lịch sử chat cũ lên màn hình
    with chat_container:
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.write(message["content"])

    # Ô nhập câu hỏi chat_input của người dùng
    if prompt := st.chat_input("Ask assistant...", key="chat_input"):
        # 1. Hiển thị ngay câu hỏi của User lên màn hình chatbox
        with chat_container:
            with st.chat_message("user"):
                st.write(prompt)

        # 2. Lưu câu hỏi của User vào lịch sử giao diện
        st.session_state.chat_history.append({"role": "user", "content":prompt})

        # 3. LUỒNG CHẠY OOP: Gọi phương thức xử lý từ đối tượng AI của bạn
        # Giả sử class của bạn có một phương thức tên là `.generate_response(prompt)` hoặc `.ask(prompt)`
        # Bạn có thể truyền thêm `df_current` vào nếu muốn AI đọc dữ liệu để phân tích
        with chat_container:
            with st.chat_message("assistant"):
                with st.spinner("AI đang suy nghĩ..."):

                    try:
                        # Gọi hàm xử lý OOP từ file ai_assistant.py của bạn
                        # (Hãy đổi tên hàm .ask(prompt) thành tên hàm thực tế trong file của bạn)
                        ai_response = ai.chat_with_data(prompt)

                        # Hiển thị câu trả lời của AI lên màn hình
                        st.write(ai_response)

                        # 4. Lưu câu trả lời của AI vào lịch sử giao diện để không bị mất khi rerun
                        st.session_state.chat_history.append({"role": "assistant", "content": ai_response})

                    except Exception as e:
                        st.error(f"❌ Lỗi kết nối trợ lý AI: {e}")