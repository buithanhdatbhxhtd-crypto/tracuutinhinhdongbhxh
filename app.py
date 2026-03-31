import streamlit as st
import pandas as pd
import numpy as np
import os
import plotly.graph_objects as go
from unidecode import unidecode
import time

# --- CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="BHXH Thuận An - AI Dashboard v5.0",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- KHỞI TẠO TRẠNG THÁI HỆ THỐNG ---
if 'selected_unit' not in st.session_state:
    st.session_state.selected_unit = None
if 'last_query' not in st.session_state:
    st.session_state.last_query = ""

# --- PHONG CÁCH THIẾT KẾ (CSS NÂNG CAO) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;700;800&display=swap');
    
    :root {
        --primary-color: #2563eb;
        --bg-glass: rgba(255, 255, 255, 0.95);
    }

    * { font-family: 'Plus Jakarta Sans', sans-serif; }
    
    .stApp {
        background: linear-gradient(135deg, #f1f5f9 0%, #cbd5e1 100%);
    }
    
    .glass-panel {
        background: var(--bg-glass);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.6);
        border-radius: 28px;
        padding: 30px;
        box-shadow: 0 20px 40px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }

    .stTextInput input {
        border-radius: 18px !important;
        padding: 1.2rem 1.8rem !important;
        border: 2px solid #e2e8f0 !important;
        background: white !important;
        font-size: 1.15rem !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03) !important;
    }
    .stTextInput input:focus {
        border-color: var(--primary-color) !important;
        box-shadow: 0 0 0 5px rgba(37, 99, 235, 0.15) !important;
    }

    .search-result-card {
        background: white;
        padding: 20px;
        border-radius: 20px;
        border: 1px solid #e2e8f0;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        margin-bottom: 12px;
        border-left: 6px solid #cbd5e1;
    }
    .search-result-card:hover {
        border-left-color: var(--primary-color);
        transform: scale(1.02);
        box-shadow: 0 15px 30px rgba(0,0,0,0.08);
    }

    .main-title {
        background: linear-gradient(90deg, #1e3a8a, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.8rem;
        font-weight: 800;
        letter-spacing: -2px;
        margin-bottom: 0.5rem;
    }
    
    .stMetric {
        background: #f8fafc;
        padding: 15px;
        border-radius: 20px;
        border: 1px solid #f1f5f9;
    }
    </style>
    """, unsafe_allow_html=True)

# --- HÀM TẢI DỮ LIỆU THÔNG MINH ---
@st.cache_data
def load_data(uploaded_file=None):
    df = None
    try:
        if uploaded_file is not None:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
        else:
            # Tìm bất kỳ file nào bắt đầu bằng 'c12' trong thư mục
            files = [f for f in os.listdir('.') if f.lower().startswith('c12')]
            if files:
                target_file = files[0]
                if target_file.lower().endswith('.csv'):
                    df = pd.read_csv(target_file)
                else:
                    # Dùng openpyxl cho xlsx, xlrd cho xls
                    df = pd.read_excel(target_file)
        
        if df is not None:
            # Chuẩn hóa tên cột cực mạnh (loại bỏ dấu tiếng Việt)
            df.columns = [unidecode(str(c)).lower().strip().replace(' ', '_') for c in df.columns]
            
            # Đảm bảo mã đơn vị là chuỗi
            if 'madvi' in df.columns:
                df['madvi'] = df['madvi'].astype(str).str.strip()
            
            # Tạo search index thông minh
            df['search_index'] = df.apply(lambda x: unidecode(str(x.get('madvi', '')) + " " + str(x.get('tendvi', ''))).lower(), axis=1)
            return df
    except Exception as e:
        st.error(f"⚠️ Chi tiết lỗi dữ liệu: {e}")
    return None

# --- GIAO DIỆN CHÍNH ---
st.markdown("<div style='text-align:center'><h1 class='main-title'>💎 BHXH Smart Hub</h1></div>", unsafe_allow_html=True)

df = load_data()

# Nếu không tìm thấy file, hiện giao diện upload
if df is None:
    st.info("👋 Chào bạn! Hệ thống chưa tìm thấy dữ liệu tự động. Hãy tải file lên hoặc kiểm tra tên file trên GitHub.")
    uploaded = st.file_uploader("Tải file dữ liệu (C12... .xls, .xlsx, .csv)", type=['xls', 'xlsx', 'csv'])
    if uploaded:
        df = load_data(uploaded)
        if df is not None: 
            st.success("✅ Đã tải dữ liệu thành công!")
            st.rerun()

# --- KHU VỰC TÌM KIẾM ---
if df is not None:
    st.markdown("### 🔍 Tra cứu đơn vị")
    query = st.text_input("Nhập tên hoặc mã", placeholder="Gõ từ khóa tìm kiếm (vd: 'dak', 'tc024'...) hệ thống sẽ lọc ngay", label_visibility="collapsed")

    # Xử lý khi query thay đổi
    if query != st.session_state.last_query:
        st.session_state.selected_unit = None
        st.session_state.last_query = query

    if query:
        clean_query = unidecode(query).lower()
        results = df[df['search_index'].str.contains(clean_query, na=False)].head(10)

        if not results.empty:
            st.write(f"Tìm thấy **{len(results)}** đơn vị phù hợp:")
            
            for _, row in results.iterrows():
                with st.container():
                    c1, c2 = st.columns([5, 1])
                    with c1:
                        st.markdown(f"""
                        <div class="search-result-card">
                            <span style="color:#2563eb; font-weight:800">{row.get('madvi', 'N/A')}</span><br>
                            <b style="font-size:1.1rem">{row.get('tendvi', 'N/A')}</b>
                        </div>
                        """, unsafe_allow_html=True)
                    with c2:
                        st.write(" ") # Căn chỉnh
                        if st.button(f"Chọn ➔", key=f"sel_{row.get('madvi')}_{_}"):
                            st.session_state.selected_unit = row.get('madvi')
                            st.rerun()
            
            # --- DASHBOARD CHI TIẾT ---
            if st.session_state.selected_unit:
                unit_data = df[df['madvi'] == st.session_state.selected_unit].iloc[0]
                
                st.markdown("<br><hr>", unsafe_allow_html=True)
                st.markdown(f"## 🏢 {unit_data.get('tendvi')}")
                
                col_left, col_right = st.columns([1.6, 1])
                
                with col_left:
                    st.markdown("<div class='glass-panel'>", unsafe_allow_html=True)
                    st.write("#### 📊 Báo cáo tài chính")
                    
                    m1, m2, m3 = st.columns(3)
                    # Sử dụng .get() để tránh lỗi nếu file thiếu cột
                    phai_dong = unit_data.get('so_phai_dong', 0)
                    da_dong = unit_data.get('so_da_dong', 0)
                    debt = unit_data.get('tien_cuoi_ky', 0)
                    
                    m1.metric("Phải đóng", f"{phai_dong:,.0f}đ")
                    m2.metric("Đã đóng", f"{da_dong:,.0f}đ")
                    m3.metric("Nợ cuối kỳ", f"{abs(debt):,.0f}đ", delta=-debt, delta_color="inverse")
                    
                    st.markdown("---")
                    st.write("📍 **Địa chỉ:**", unit_data.get('diachi', 'N/A'))
                    st.write("📞 **Liên hệ:**", f"{unit_data.get('nguoilh', 'N/A')} - {unit_data.get('dienthoai', 'N/A')}")
                    
                    st.info(f"**Nội dung nộp tiền:**\n\n`BHXH {unit_data.get('madvi')} {unit_data.get('tendvi')}`")
                    st.markdown("</div>", unsafe_allow_html=True)

                with col_right:
                    # Biểu đồ Gauge
                    target = phai_dong if phai_dong > 0 else 1
                    percent = min(round((da_dong / target) * 100, 1), 100)
                    
                    fig = go.Figure(go.Indicator(
                        mode = "gauge+number",
                        value = percent,
                        title = {'text': "Hoàn thành (%)", 'font': {'size': 22}},
                        gauge = {
                            'axis': {'range': [0, 100]},
                            'bar': {'color': "#2563eb"},
                            'steps': [
                                {'range': [0, 50], 'color': "#fee2e2"},
                                {'range': [50, 90], 'color': "#fef9c3"},
                                {'range': [90, 100], 'color': "#dcfce7"}]
                        }
                    ))
                    fig.update_layout(height=350, margin=dict(l=20, r=20, t=50, b=20), paper_bgcolor="rgba(0,0,0,0)")
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # QR Code
                    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=250x250&data=BHXH_PAY_{unit_data.get('madvi')}_{debt}"
                    st.markdown(f"<center><img src='{qr_url}' width='180' style='border-radius:20px; border:4px solid white; box-shadow:0 10px 20px rgba(0,0,0,0.1)'><p style='margin-top:10px; color:#64748b'>Quét mã để nộp tiền</p></center>", unsafe_allow_html=True)
                    
                    if st.button("🎊 Xác nhận Tra cứu"):
                        st.balloons()
        else:
            st.error("😢 Không tìm thấy kết quả phù hợp. Hãy thử từ khóa khác!")
    else:
        st.markdown("<br><br><center><img src='https://cdn-icons-png.flaticon.com/512/3772/3772274.png' width='120' style='opacity:0.3'><p style='color:#64748b; margin-top:20px'>Bắt đầu bằng cách nhập tên hoặc mã đơn vị ở trên</p></center>", unsafe_allow_html=True)

# --- FOOTER ---
st.markdown("<br><hr><center style='color:#94a3b8; font-size:0.8rem'>BHXH Thuận An Dashboard v5.0 • Powered by Python AI</center>", unsafe_allow_html=True)
