import dash
from dash import dcc, html, dash_table, Input, Output, State, ctx, callback
import dash_bootstrap_components as dbc
import pandas as pd
import base64
import io

from data_validator import DataValidator
from data_processor import DataProcessor
from ai_assistant import AIAssistant
from analytics import Analytics
from visualization import ChartBuilder

from database_connector import DatabaseConnector
from apscheduler.schedulers.background import BackgroundScheduler
import time
import atexit

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.LITERA, dbc.icons.FONT_AWESOME],
    suppress_callback_exceptions=True
)
app.title = "Supermarket Dashboard"

# ==========================================
# GLOBAL INSTANCES AND DATA MANAGEMENT
# ==========================================

# Global AI Assistant instance
global_ai_instance = AIAssistant()

# Global Database Connector instance
db_connector = DatabaseConnector()

# Global variable to hold processed data from DB, updated by scheduler
# This will be read by a dcc.Interval callback to update the dcc.Store
global_processed_df_json = None

# Function to load and process data from DB
def load_and_process_db_data():
    global global_processed_df_json
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Attempting to load data from database...")
    try:
        # Assuming your table name is 'sales_data' as per previous discussion
        df_raw = db_connector.fetch_data_to_dataframe(table_name="sales_data")
        if not df_raw.empty:
            processor = DataProcessor(df_raw)
            processed_df = processor.run_pipeline()
            global_processed_df_json = processed_df.to_json(date_format='iso', orient='split')
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Data loaded and processed from database. {len(processed_df)} rows.")
        else:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] No data fetched from database.")
            global_processed_df_json = None # Clear data if nothing fetched
    except Exception as e:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Error loading data from database: {e}")
        global_processed_df_json = None # Clear data on error

# Initial load of data when the app starts
load_and_process_db_data()

# Setup APScheduler for periodic background updates
scheduler = BackgroundScheduler()
# Schedule to run load_and_process_db_data every 5 minutes (adjust as needed)
scheduler.add_job(load_and_process_db_data, 'interval', minutes=5)
scheduler.start()

# Ensure scheduler shuts down when the app exits
atexit.register(lambda: scheduler.shutdown())

# ==========================================
# CÁC THÀNH PHẦN GIAO DIỆN CHÍNH
# ==========================================

# Navbar
navbar = dbc.Navbar(
    dbc.Container(
        [
            html.A(
                dbc.Row(
                    [
                        dbc.Col(html.I(className="fa-solid fa-store fa-2x", style={"color": "white"})),
                        dbc.Col(dbc.NavbarBrand("Supermarket Analytic Dashboard", className="ms-3 fs-3 fw-bold")),
                    ],
                    align="center",
                    className="g-0",
                ),
                href="/",
                style={"textDecoration": "none"},
            ),
        ],
        fluid=True,
    ),
    color="primary",
    dark=True,
    className="mb-4 shadow-sm",
)

# Tab: Data Validation
tab_validation = dbc.Card(
    dbc.CardBody([
        html.Div([
            html.H4([html.I(className="fa-solid fa-upload me-2"), "Tải lên & Kiểm tra dữ liệu"], className="text-primary mb-3"),
            html.P("Hệ thống sẽ tự động phân tích và kiểm tra các lỗi logic trong dữ liệu bán hàng của bạn.", className="text-muted")
        ]),
        dcc.Upload(
            id='upload-data',
            children=html.Div([
                html.I(className="fa-solid fa-cloud-arrow-up fa-3x mb-2 text-primary"),
                html.Br(),
                'Kéo thả hoặc ', html.A('Chọn file CSV', className="text-primary fw-bold")
            ]),
            style={
                'width': '100%', 'height': '150px', 'lineHeight': 'normal',
                'borderWidth': '2px', 'borderStyle': 'dashed', 'borderColor': '#0d6efd',
                'borderRadius': '15px', 'textAlign': 'center', 'marginBottom': '20px',
                'cursor': 'pointer', 'backgroundColor': '#f8f9fa',
                'display': 'flex', 'flexDirection': 'column', 'justifyContent': 'center', 'alignItems': 'center'
            },
            multiple=False
        ),
        html.Div(id='upload-status-alert'),
        html.Hr(className="my-4"),
        dbc.Row([
            dbc.Col([
                html.H5([html.I(className="fa-solid fa-table me-2"), "Xem trước dữ liệu"], className="text-secondary mb-3"),
                html.Div(id='data-table-container', style={"overflowX": "auto"}, className="shadow-sm border rounded")
            ], width=12)
        ])
    ]),
    className="border-0 shadow-sm rounded-3 mt-4"
)

# Tab: Data Visualization
tab_visualization = html.Div([
    # Khung Bộ Lọc
    dbc.Card(
        dbc.CardBody([
            html.H5([html.I(className="fa-solid fa-filter me-2"), "Bộ lọc dữ liệu"], className="text-primary mb-3"),
            dbc.Row([
                dbc.Col(dcc.Dropdown(id='filter-city', multi=True, placeholder="Thành phố..."), width=12, md=3, className="mb-2"),
                dbc.Col(dcc.Dropdown(id='filter-product', multi=True, placeholder="Ngành hàng..."), width=12, md=3, className="mb-2"),
                dbc.Col(dcc.Dropdown(id='filter-gender', multi=True, placeholder="Giới tính..."), width=12, md=2, className="mb-2"),
                dbc.Col(dcc.Dropdown(id='filter-customer', multi=True, placeholder="Loại KH..."), width=12, md=2, className="mb-2"),
                dbc.Col(dcc.DatePickerSingle(id='filter-date', placeholder="Chọn ngày", className="w-100"), width=12, md=2, className="mb-2"),
            ])
        ]),
        className="border-0 shadow-sm rounded-3 mb-4 mt-4"
    ),

    # Khung KPIs
    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    dbc.Col(html.I(className="fa-solid fa-sack-dollar fa-3x text-primary"), width="auto"),
                    dbc.Col([
                        html.H6("Tổng Doanh Thu", className="text-muted text-uppercase mb-1"),
                        html.H3(id="kpi-total-sales", className="text-dark fw-bold mb-0")
                    ])
                ], align="center")
            ])
        ], className="border-0 shadow-sm rounded-3"), width=12, md=6, className="mb-4"),

        dbc.Col(dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    dbc.Col(html.I(className="fa-solid fa-chart-line fa-3x text-success"), width="auto"),
                    dbc.Col([
                        html.H6("Doanh Thu Trung Bình", className="text-muted text-uppercase mb-1"),
                        html.H3(id="kpi-avg-sales", className="text-dark fw-bold mb-0")
                    ])
                ], align="center")
            ])
        ], className="border-0 shadow-sm rounded-3"), width=12, md=6, className="mb-4"),
    ]),

    # Khung Biểu đồ - Cột 1 (Biểu đồ cũ)
    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardHeader(
                dbc.Row([
                    dbc.Col(html.H6([html.I(className="fa-solid fa-credit-card me-2"), "Cơ cấu thanh toán"], className="mb-0"), width="auto", align="center"),
                    dbc.Col(dcc.Dropdown(id='chart1-type',
                                         options=["Biểu đồ Tròn (Donut/Pie)", "Biểu đồ Cột (Bar Chart)"],
                                         value="Biểu đồ Tròn (Donut/Pie)", clearable=False, style={"minWidth": "200px"}),
                            width="auto", className="ms-auto")
                ], align="center"),
                className="bg-white border-bottom-0 pt-3 pb-0"
            ),
            dbc.CardBody(dcc.Graph(id='fig-payment', config={'displayModeBar': False}))
        ], className="border-0 shadow-sm rounded-3 h-100"), width=12, lg=6, className="mb-4"),

        dbc.Col(dbc.Card([
            dbc.CardHeader(
                dbc.Row([
                    dbc.Col(html.H6([html.I(className="fa-solid fa-tags me-2"), "Doanh thu theo ngành hàng"], className="mb-0"), width="auto", align="center"),
                    dbc.Col(dcc.Dropdown(id='chart2-type',
                                         options=["Biểu đồ Cột Ngang (Horizontal Bar)", "Biểu đồ Cột Dọc (Vertical Bar)", "Biểu đồ Dạng Cây (Treemap)"],
                                         value="Biểu đồ Cột Ngang (Horizontal Bar)", clearable=False, style={"minWidth": "200px"}),
                            width="auto", className="ms-auto")
                ], align="center"),
                className="bg-white border-bottom-0 pt-3 pb-0"
            ),
            dbc.CardBody(dcc.Graph(id='fig-category', config={'displayModeBar': False}))
        ], className="border-0 shadow-sm rounded-3 h-100"), width=12, lg=6, className="mb-4")
    ], className="g-4"),

    # Khung Biểu đồ - Cột 2 (Biểu đồ cũ)
    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardHeader(
                dbc.Row([
                    dbc.Col(html.H6([html.I(className="fa-solid fa-star me-2"), "Phân bố điểm đánh giá"], className="mb-0"), width="auto", align="center"),
                    dbc.Col(dcc.Dropdown(id='chart3-type',
                                         options=["Biểu đồ Tần suất (Histogram)", "Biểu đồ Hộp (Box Plot)", "Biểu đồ Violin"],
                                         value="Biểu đồ Tần suất (Histogram)", clearable=False, style={"minWidth": "200px"}),
                            width="auto", className="ms-auto")
                ], align="center"),
                className="bg-white border-bottom-0 pt-3 pb-0"
            ),
            dbc.CardBody(dcc.Graph(id='fig-rating-dist', config={'displayModeBar': False}))
        ], className="border-0 shadow-sm rounded-3 h-100"), width=12, lg=6, className="mb-4"),

        dbc.Col(dbc.Card([
            dbc.CardHeader(
                dbc.Row([
                    dbc.Col(html.H6([html.I(className="fa-solid fa-heart me-2"), "Độ hài lòng theo ngành hàng"], className="mb-0"), width="auto", align="center"),
                    dbc.Col(dcc.Dropdown(id='chart4-type',
                                         options=["Biểu đồ Cột Ngang (Horizontal Bar)", "Biểu đồ Điểm (Dot Plot)"],
                                         value="Biểu đồ Cột Ngang (Horizontal Bar)", clearable=False, style={"minWidth": "200px"}),
                            width="auto", className="ms-auto")
                ], align="center"),
                className="bg-white border-bottom-0 pt-3 pb-0"
            ),
            dbc.CardBody(dcc.Graph(id='fig-rating-cat', config={'displayModeBar': False}))
        ], className="border-0 shadow-sm rounded-3 h-100"), width=12, lg=6, className="mb-4")
    ], className="g-4"),

    # THÊM CÁC BIỂU ĐỒ MỚI
    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardHeader(html.H6([html.I(className="fa-solid fa-building me-2"), "Hiệu suất Chi nhánh (Doanh thu & Lợi nhuận)"], className="mb-0 pt-2"), className="bg-white border-bottom-0 pb-0"),
            dbc.CardBody(dcc.Graph(id='fig-branch-perf', config={'displayModeBar': False}))
        ], className="border-0 shadow-sm rounded-3 h-100"), width=12, lg=6, className="mb-4"),

        dbc.Col(dbc.Card([
            dbc.CardHeader(html.H6([html.I(className="fa-solid fa-users-viewfinder me-2"), "Cơ cấu Doanh thu (KH & Giới tính)"], className="mb-0 pt-2"), className="bg-white border-bottom-0 pb-0"),
            dbc.CardBody(dcc.Graph(id='fig-customer-gender', config={'displayModeBar': False}))
        ], className="border-0 shadow-sm rounded-3 h-100"), width=12, lg=6, className="mb-4")
    ], className="g-4"),

    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardHeader(html.H6([html.I(className="fa-solid fa-clock me-2"), "Lượng Đơn Hàng Theo Khung Giờ"], className="mb-0 pt-2"), className="bg-white border-bottom-0 pb-0"),
            dbc.CardBody(dcc.Graph(id='fig-shopping-hours', config={'displayModeBar': False}))
        ], className="border-0 shadow-sm rounded-3 h-100"), width=12, lg=6, className="mb-4"),

        dbc.Col(dbc.Card([
            dbc.CardHeader(html.H6([html.I(className="fa-solid fa-arrow-trend-up me-2"), "Dự báo Doanh thu 30 ngày (Linear Regression)"], className="mb-0 pt-2"), className="bg-white border-bottom-0 pb-0"),
            dbc.CardBody(dcc.Graph(id='fig-forecast-revenue', config={'displayModeBar': False}))
        ], className="border-0 shadow-sm rounded-3 h-100"), width=12, lg=6, className="mb-4")
    ], className="g-4")
])

# Layout chính
app.layout = html.Div([
    # Lưu trữ dữ liệu ngầm trên trình duyệt
    dcc.Store(id='stored-data', data=global_processed_df_json), # Use data from database
    dcc.Store(id='chat-history', data=[
        {"role": "assistant", "content": "Xin chào! Tôi là AI Assistant. Tôi có thể giúp gì cho bạn hôm nay?"}]),

    # Add dcc.Interval to trigger periodic updates to stored-data from the global variable
    dcc.Interval(
        id='interval-component',
        interval=30*1000, # in milliseconds, update every 30 seconds
        n_intervals=0
    ),

    navbar,

    dbc.Container([
        dbc.Tabs([
            dbc.Tab(tab_validation, label="Dữ liệu", tab_id="tab-validation", label_style={"fontWeight": "bold", "fontSize": "16px"}),
            dbc.Tab(tab_visualization, label="Biểu đồ", tab_id="tab-visualization", label_style={"fontWeight": "bold", "fontSize": "16px"}),
        ], id="tabs", active_tab="tab-validation", className="nav-pills mt-2"),
    ], fluid=True, className="px-4 pb-5 bg-light", style={"minHeight": "100vh"}),

    # MODAL CHO VALIDATION
    dbc.Modal(
        [
            dbc.ModalHeader(id="validation-modal-header"),
            dbc.ModalBody(id="validation-modal-body"),
            dbc.ModalFooter(
                dbc.Button("Đóng", id="modal-close-button", className="ms-auto", n_clicks=0)
            ),
        ],
        id="validation-modal",
        is_open=False,
        centered=True,
        size="lg",
    ),

    # NÚT GỌI AI ASSISTANT (Nổi ở góc phải dưới)
    html.Div(
        dbc.Button([html.I(className="fa-solid fa-robot me-2 fs-5"), "AI Assistant"],
                   id="btn-open-ai", color="info", className="rounded-pill shadow-lg text-white fw-bold px-4 py-2", size="lg",
                   style={"background": "linear-gradient(45deg, #0dcaf0, #0d6efd)", "border": "none"}),
        style={"position": "fixed", "bottom": "40px", "right": "40px", "zIndex": 1000}
    ),

    # OFFCANVAS CHO AI CHATBOT
    dbc.Offcanvas(
        html.Div([
            html.Div(id='chat-display',
                     style={"height": "70vh", "overflowY": "auto", "padding": "15px", "backgroundColor": "#f8f9fa",
                            "borderRadius": "15px", "marginBottom": "20px", "boxShadow": "inset 0 0 10px rgba(0,0,0,0.05)"}),

            # Thêm Loading component bao quanh InputGroup
            dcc.Loading(
                id="loading-chat",
                type="circle",
                color="#0d6efd",
                children=[
                    dbc.InputGroup([
                        dbc.Input(id="chat-input", placeholder="Hỏi AI về dữ liệu của bạn...", type="text", className="rounded-start-pill ps-4"),
                        dbc.Button(html.I(className="fa-solid fa-paper-plane"), id="chat-submit", color="primary", className="rounded-end-pill px-4"),
                    ], className="mb-2 shadow-sm"),
                ]
            ),

            dbc.Button([html.I(className="fa-solid fa-trash me-2"), "Xóa lịch sử trò chuyện"], id="chat-clear", color="outline-danger", size="sm", className="w-100 rounded-pill mt-2")
        ]),
        id="offcanvas-ai",
        title=html.Span([html.I(className="fa-solid fa-robot me-2 text-primary"), "Trợ Lý AI Thông Minh"]),
        is_open=False,
        placement="end",
        style={"width": "450px", "borderLeft": "none", "boxShadow": "-5px 0 15px rgba(0,0,0,0.1)"}
    )
], style={"backgroundColor": "#f4f6f9"})

# ==========================================
# CALLBACKS (XỬ LÝ LOGIC TƯƠNG TÁC)
# ==========================================


# New callback to update stored-data from the global variable periodically
@app.callback(
    Output('stored-data', 'data', allow_duplicate=True),
    Input('interval-component', 'n_intervals'),
    prevent_initial_call=True
)
def update_stored_data_from_global(n_intervals):
    # This callback is triggered by the interval component
    # It reads the global_processed_df_json which is updated by the APScheduler job
    if global_processed_df_json is not None:
        return global_processed_df_json
    return dash.no_update


# 1. Xử lý Upload Dữ liệu & Validation -> Hiển thị trên Modal
@app.callback(
    Output('stored-data', 'data', allow_duplicate=True), # Added allow_duplicate=True
    Output('upload-status-alert', 'children'),
    Output('data-table-container', 'children'),
    Output('validation-modal', 'is_open'),
    Output('validation-modal-header', 'children'),
    Output('validation-modal-body', 'children'),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename'),
    prevent_initial_call=True
)
def process_upload(contents, filename):
    if contents is None:
        return dash.no_update, dash.no_update, dash.no_update, False, "", ""

    try:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))

        # Chạy Validation
        validator = DataValidator(df)
        ket_qua = validator.run_all_validators()

        modal_title = ""
        val_ui = ""

        # Giao diện kết quả Validation
        if not ket_qua:
            modal_title = html.Span([html.I(className="fa-solid fa-circle-check me-2 text-success"), "Dữ liệu Hoàn Hảo!"])
            val_ui = dbc.Alert(
                "Tuyệt vời! Dữ liệu hoàn toàn sạch sẽ, không phát hiện lỗi logic.",
                color="success",
                className="shadow-sm rounded-3"
            )
        else:
            modal_title = html.Span([html.I(className="fa-solid fa-triangle-exclamation me-2 text-danger"), "Phát Hiện Lỗi Dữ Liệu"])
            val_ui = html.Div([
                dbc.Alert(
                    f"Hệ thống đã phát hiện {len(ket_qua['errors'])} lỗi logic trong file của bạn:",
                    color="danger",
                    className="shadow-sm rounded-3 mb-2"
                ),
                dbc.ListGroup(
                    [dbc.ListGroupItem(err, className="text-danger bg-light") for err in ket_qua['errors']],
                    flush=True,
                    className="rounded-3"
                )
            ])

        # Bảng dữ liệu thu gọn
        table_ui = dash_table.DataTable(
            data=df.head(1000).to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df.columns],
            page_size=10,
            style_table={'overflowX': 'auto', 'minWidth': '100%'},
            style_header={'backgroundColor': '#f8f9fa', 'fontWeight': 'bold', 'borderBottom': '2px solid #dee2e6'},
            style_cell={'padding': '10px', 'textAlign': 'left', 'fontFamily': 'inherit'},
            style_data={'borderBottom': '1px solid #f0f0f0'}
        )

        success_alert = dbc.Alert([
            html.I(className="fa-solid fa-file-csv me-2"),
            f"Đã tải thành công: {filename}."
        ], color="info", className="mt-3 shadow-sm rounded-3")

        return df.to_json(date_format='iso', orient='split'), success_alert, table_ui, True, modal_title, val_ui

    except Exception as e:
        modal_title = html.Span([html.I(className="fa-solid fa-circle-xmark me-2 text-danger"), "Lỗi Xử Lý File"])
        modal_body = dbc.Alert(f"Lỗi đọc hoặc xử lý file: {e}", color="danger")
        return dash.no_update, html.Div(), dash.no_update, True, modal_title, modal_body


# Callback để đóng Modal
@app.callback(
    Output('validation-modal', 'is_open', allow_duplicate=True),
    Input('modal-close-button', 'n_clicks'),
    prevent_initial_call=True,
)
def close_validation_modal(n_clicks):
    if n_clicks:
        return False
    return dash.no_update


# 2. Cập nhật Filters (Dropdowns) khi có dữ liệu
@app.callback(
    Output('filter-city', 'options'), Output('filter-product', 'options'),
    Output('filter-gender', 'options'), Output('filter-customer', 'options'),
    Output('filter-date', 'min_date_allowed'), Output('filter-date', 'max_date_allowed'),
    Input('stored-data', 'data')
)
def update_dropdowns(json_data):
    if json_data is None:
        return [], [], [], [], None, None
    df = pd.read_json(io.StringIO(json_data), orient='split')
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    dates = df['Date'].dropna()

    return (
        [{'label': c, 'value': c} for c in df['City'].unique()],
        [{'label': c, 'value': c} for c in df['Product line'].unique()],
        [{'label': c, 'value': c} for c in df['Gender'].unique()],
        [{'label': c, 'value': c} for c in df['Customer type'].unique()],
        dates.min().date() if not dates.empty else None,
        dates.max().date() if not dates.empty else None
    )


# 3. Cập nhật Dashboard (Biểu đồ & KPIs)
@app.callback(
    Output('kpi-total-sales', 'children'), Output('kpi-avg-sales', 'children'),
    Output('fig-payment', 'figure'), Output('fig-category', 'figure'),
    Output('fig-rating-dist', 'figure'), Output('fig-rating-cat', 'figure'),
    Output('fig-branch-perf', 'figure'), Output('fig-customer-gender', 'figure'),
    Output('fig-shopping-hours', 'figure'), Output('fig-forecast-revenue', 'figure'),
    Input('stored-data', 'data'),
    Input('filter-city', 'value'), Input('filter-product', 'value'),
    Input('filter-gender', 'value'), Input('filter-customer', 'value'), Input('filter-date', 'date'),
    Input('chart1-type', 'value'), Input('chart2-type', 'value'),
    Input('chart3-type', 'value'), Input('chart4-type', 'value')
)
def update_dashboard(json_data, cities, products, genders, customers, date, c1, c2, c3, c4):
    if json_data is None:
        return "$0", "$0", {}, {}, {}, {}, {}, {}, {}, {}

    df = pd.read_json(io.StringIO(json_data), orient='split')
    processor=DataProcessor(df)
    df=processor.run_pipeline()
    # Lọc dữ liệu
    if cities:
        df = df[df['City'].isin(cities)]
    if products:
        df = df[df['Product line'].isin(products)]
    if genders:
        df = df[df['Gender'].isin(genders)]
    if customers:
        df = df[df['Customer type'].isin(customers)]
    # if date:
    #     df = df[df['Date'].dt.date == pd.to_datetime(date).date()]

    if df.empty:
        return "$0", "$0", {}, {}, {}, {}, {}, {}, {}, {}

    # KPIs
    kpi_tot = f"${df['Sales'].sum():,.0f}"
    kpi_avg = f"${df['Sales'].mean():,.2f}"

    # Vẽ biểu đồ
    builder = ChartBuilder(df)
    fig1 = builder.payment_chart(c1)
    fig2 = builder.category_chart(c2)
    fig3 = builder.rating_distribution(c3)
    fig4 = builder.rating_by_category(c4)

    # Biểu đồ mới
    fig5 = builder.branch_performance_chart()
    fig6 = builder.customer_gender_revenue_chart()
    fig7 = builder.shopping_hours_chart()

    # Cần kiểm tra xem có đủ dữ liệu lịch sử để dự báo hay không
    try:
        fig8 = builder.forecast_revenue_chart()
    except Exception:
        # Trong trường hợp không đủ dữ liệu (ví dụ đã filter quá nhỏ)
        import plotly.graph_objects as go
        fig8 = go.Figure()
        fig8.add_annotation(text="Không đủ dữ liệu để dự báo", x=0.5, y=0.5, showarrow=False)

    # Styling chung cho tất cả các biểu đồ
    for fig in [fig1, fig2, fig3, fig4, fig5, fig6, fig7, fig8]:
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=30, b=20, l=20, r=20),
            font=dict(family="inherit", color="#495057"),
            title_font=dict(size=16, color="#212529"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )

    return kpi_tot, kpi_avg, fig1, fig2, fig3, fig4, fig5, fig6, fig7, fig8


# 4. Logic Đóng/Mở Trợ lý AI
@app.callback(
    Output("offcanvas-ai", "is_open"),
    Input("btn-open-ai", "n_clicks"),
    State("offcanvas-ai", "is_open"),
)
def toggle_ai(n1, is_open):
    if n1:
        return not is_open
    return is_open


# 5. Logic Chatbot AI
@app.callback(
    Output('chat-history', 'data'),
    Output('chat-display', 'children', allow_duplicate=True),
    Output('chat-input', 'value'),
    Input('chat-submit', 'n_clicks'),
    Input('chat-clear', 'n_clicks'),
    State('chat-input', 'value'),
    State('chat-history', 'data'),
    State('stored-data', 'data'),
    prevent_initial_call=True
)
def manage_chat(n_submit, n_clear, user_text, history, json_data):
    trigger = ctx.triggered_id

    # Nếu người dùng bấm Clear
    if trigger == 'chat-clear':
        global_ai_instance.clear_chat_history() # Xóa lịch sử trong Gemini
        new_hist = [{"role": "assistant", "content": "Lịch sử đã xóa. Tôi có thể giúp gì tiếp?"}]
        return new_hist, render_chat(new_hist), ""

    # Nếu submit tin nhắn
    if trigger == 'chat-submit' and user_text:
        history.append({"role": "user", "content": user_text})

        # Gọi AIAssistant
        ai_response = "Xin lỗi, hãy tải file dữ liệu lên trước."
        if json_data:
            df = pd.read_json(io.StringIO(json_data), orient='split')
            # Cập nhật dữ liệu mới nhất vào instance AI
            analytic_node = Analytics(df)
            global_ai_instance.analytics = analytic_node

            try:
                # Chat với API
                ai_response = global_ai_instance.chat_with_data(user_text)
            except Exception as e:
                ai_response = f"Lỗi AI: {str(e)}"

        history.append({"role": "assistant", "content": ai_response})
        return history, render_chat(history), ""

    return history, render_chat(history), dash.no_update


# 6. Hiển thị Lịch sử Chat khi mở Offcanvas
@app.callback(
    Output('chat-display', 'children', allow_duplicate=True),
    Input('offcanvas-ai', 'is_open'),
    State('chat-history', 'data'),
    prevent_initial_call=True
)
def show_chat_on_open(is_open, history):
    if is_open:
        return render_chat(history)
    return dash.no_update


def render_chat(history):
    """Hàm tạo giao diện HTML cho list tin nhắn"""
    chat_bubbles = []
    for msg in history:
        is_user = msg["role"] == "user"
        align = "end" if is_user else "start"
        bg_color = "#0d6efd" if is_user else "#ffffff"
        text_color = "white" if is_user else "#212529"
        border = "none" if is_user else "1px solid #dee2e6"
        chat_bubbles.append(
            html.Div(
                html.Div(dcc.Markdown(msg["content"]), style={
                    "display": "inline-block", "padding": "12px 18px",
                    "borderRadius": "20px", "backgroundColor": bg_color, "color": text_color,
                    "border": border, "boxShadow": "0 2px 5px rgba(0,0,0,0.05)",
                    "maxWidth": "85%", "marginBottom": "12px", "textAlign": "left",
                    "borderBottomRightRadius": "5px" if is_user else "20px",
                    "borderBottomLeftRadius": "20px" if is_user else "5px",
                }),
                style={"textAlign": align, "width": "100%"}
            )
        )
    return chat_bubbles