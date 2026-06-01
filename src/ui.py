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
        st.write('filter city')
        st.write('filter branch')
        st.write('filter product line')
        st.write('filter gender')
    st.markdown("---")
    st.subheader("AI Assistant")
    # Tạo lịch sử trò chuyện trong sessin_state
    if "sidebar_chat_history" not in st.session_state:
        st.session_state.sidebar_chat_history = [
            {"role": "assistant", "content": "How can I help you analyze the supermarket sales data today?"}
        ]
    # tạo khung
    chat_container = st.container(height=250,key="sidebar_chat_container")
    # hiện lịch sử chat
    with chat_container:
        for message in st.session_state.sidebar_chat_history:
            with st.chat_message(message["role"]):
                st.write(message["content"])
    if prompt := st.chat_input("Ask assistant...", key="sidebar_chat_input"):
        # hiện user_input lên chatbox
        with chat_container:
            with st.chat_message("user"):
                st.write(prompt)
        st.session_state.sidebar_chat_history.append({"role": "user", "content": prompt})
##main page
 #va main page
pad_left, center_canvas, pad_right = st.columns([1, 5, 1])
with center_canvas:
    if st.session_state.active_page == "Data Validation":
        row1_col1, row1_col2, row1_col3, row1_col4 = st.columns(4)
        with row1_col1:
                st.button('Validate File',key='btn_validate_preview', width="stretch")
        with row1_col2:
                st.button('Fix File',key='btn_fix_preview', width="stretch")
        with row1_col3:
                st.button('Download File',key='btn_download_preview',  width="stretch")
        if "df" not in st.session_state:
                    st.session_state.df = pd.read_csv("data/raw/supermarket_data_sales.csv")
        row2_col1, row2_col2 = st.columns(2)
        with row2_col1:
                st.write('thong tin phan file da kiemtra')
        with row2_col2:
                st.write('thong bao neu co loi, chi ra phan nao loi')
     #vis main page
    elif st.session_state.active_page == "Data Visualization":
        df['Date'] = pd.to_datetime(df['Date'])
        date_options= sorted(df['Date'].dropna().dt.date.unique())
        selected_date = st.date_input(label="",value=date_options[0])
        filtered_df = df[df['Date'].dt.date == selected_date]

        sum_tab, avg_tab = st.columns(2)
        with sum_tab:
            total_sales = filtered_df["Sales"].sum()
            st.metric("Total Sales", f"{filtered_df['Sales'].sum():,.0f}",border=True)
        with avg_tab:
            avg_sales = filtered_df["Sales"].mean()
            st.metric("Average Sales",f"{filtered_df['Sales'].mean():,.2f}",border=True )
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
