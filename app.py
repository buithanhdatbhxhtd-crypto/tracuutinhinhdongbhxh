import streamlit as st
import pandas as pd
import numpy as np
import os
import plotly.graph_objects as go
from unidecode import unidecode
import time

# --- CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="BHXH Thuận An - AI Dashboard",
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
        --bg-glass: rgba(255, 255, 255, 0.9);
    }

    * { font-family: 'Plus Jakarta Sans', sans-serif; }
    
    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
    }
    
    /* Hiệu ứng khung gương Glassmorphism */
    .glass-panel {
        background: var(--bg-glass);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.5);
        border-radius: 24px;
        padding: 25px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.03);
    }

    /* Thanh tìm kiếm nổi bật */
    .stTextInput input {
        border-radius: 16px !important;
        padding: 1rem 1.5rem !important;
        border: 2px solid #cbd5e1 !important;
        background: white !important;
        font-size: 1.1rem !important;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    .stTextInput input:focus {
        border-color: var(--primary-color) !important;
        box-shadow: 0 0 0 5px rgba(37, 99, 235, 0.1) !important;
        transform: scale(1.01);
    }

    /* Thẻ gợi ý kết quả */
    .search-result-card {
        background: white;
        padding: 18px;
        border-radius: 18px;
        border: 1px solid #f1f5f9;
        transition: all 0.3s ease;
        margin-bottom: 12px;
        border-left: 5px solid #cbd5e1;
    }
    .search-result-card:hover {
        border-left-color: var(--primary-color);
        box-shadow: 0 10px 20px rgba(0,0,0,0.06);
        transform: translateX(5px);
    }

    /* Định dạng Metric */
    [data-testid="stMetricValue"] {
        font-weight: 800;
        color: #1e293b;
    }
    
    .main-title {
        background: linear-gradient(90deg, #1e40af, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.5rem;
        font-weight: 800;
        letter-spacing: -2px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- HÀM TẢI DỮ LIỆU THÔNG MINH ---
@st.cache_data
def load_data(uploaded_file=None):
    file_candidates = ['c12.xls', 'c12.xlsx', 'c12.csv']
    df = None
    
    try:
        if uploaded_file is not None:
            # Ưu tiên file người dùng tải lên trực tiếp
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
        else:
            # Tìm file trong hệ thống
            for f in file_candidates:
                if os.path.exists(f):
                    if f.endswith('.csv'):
                        df = pd.read_csv(f)
                    else:
                        df = pd.read_excel(f)
                    break
        
        if df is not None:
            # Chuẩn hóa tên cột để tránh lỗi lệch tên giữa các bản Excel
            df.columns = [unidecode(str(c)).lower().strip().replace(' ', '_') for c in df.columns]
            
            # Tìm cột mã đơn vị và tên đơn vị bằng từ khóa
            col_map = {
                'madvi': ['madvi', 'ma_don_vi', 'ma_dv'],
                'tendvi': ['tendvi', 'ten_don_vi', 'ten_dv'],
                'cuoi': ['tien_cuoi_ky', 'so_du_cuoi', 'cuoi_ky']
            }
            
            # Tạo search index
            df['search_index'] = df.apply(lambda x: unidecode(str(x.get('madvi', '')) + " " + str(x.get('tendvi', ''))).lower(), axis=1)
            return df
    except Exception as e:
        st.error(f"Lỗi khi xử lý dữ liệu: {e}")
    return None

# --- GIAO DIỆN CHÍNH ---
st.markdown("<div style='text-align:center'><h1 class='main-title'>💎 BHXH Smart Hub</h1></div>", unsafe_allow_html=True)

# Xử lý file: Nếu không thấy file c12.xls, hiện box upload
df = load_data()
if df is None:
    st.warning("⚡ Hệ thống không tìm thấy file `c12.xls` trên GitHub. Bạn hãy tải file lên để bắt đầu nhé!")
    uploaded = st.file_uploader("Tải file dữ liệu (.xls, .xlsx, .csv)", type=['xls', 'xlsx', 'csv'])
    if uploaded:
        df = load_data(uploaded)
        if df is not None: st.success("Đã tải dữ liệu thành công!")

# --- KHU VỰC TÌM KIẾM ---
if df is not None:
    st.markdown("### 🔍 Tra cứu thông minh")
    query = st.text_input("Nhập tên hoặc mã", placeholder="Gõ tên đơn vị (vd: 'dak', 'thanh hoa'...) hệ thống sẽ tìm ngay", label_visibility="collapsed")

    # Reset selection if query changes
    if query != st.session_state.last_query:
        st.session_state.selected_unit = None
        st.session_state.last_query = query

    if query:
        clean_query = unidecode(query).lower()
        # Tìm kiếm mờ: Kết quả chứa từ khóa
        results = df[df['search_index'].str.contains(clean_query, na=False)].head(8)

        if not results.empty:
            st.write(f"Tìm thấy **{len(results)}** kết quả liên quan:")
            
            # Hiển thị kết quả dạng danh sách thẻ
            for _, row in results.iterrows():
                # Dùng Container để tạo hiệu ứng hover giả lập
                with st.container():
                    c1, c2 = st.columns([4, 1])
                    with c1:
                        st.markdown(f"""
                        <div class="search-result-card">
                            <span style="color:#2563eb; font-weight:800">{row.get('madvi', 'N/A')}</span><br>
                            <b>{row.get('tendvi', 'N/A')}</b>
                        </div>
                        """, unsafe_allow_html=True)
                    with c2:
                        st.write("") # Căn lề
                        if st.button(f"Chọn ➡", key=f"sel_{row.get('madvi')}"):
                            st.session_state.selected_unit = row.get('madvi')
                            st.rerun()
            
            # --- HIỂN THỊ DASHBOARD CHI TIẾT ---
            if st.session_state.selected_unit:
                unit_data = df[df['madvi'] == st.session_state.selected_unit].iloc[0]
                
                st.markdown("<br><hr>", unsafe_allow_html=True)
                st.markdown(f"## 🏢 {unit_data.get('tendvi')}")
                
                # Bố cục Dashboard
                col_left, col_right = st.columns([1.5, 1])
                
                with col_left:
                    st.markdown("<div class='glass-panel'>", unsafe_allow_html=True)
                    st.write("#### 📊 Thông số tài chính")
                    
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Phải đóng", f"{unit_data.get('so_phai_dong', 0):,.0f}đ")
                    m2.metric("Đã đóng", f"{unit_data.get('so_da_dong', 0):,.0f}đ")
                    
                    debt = unit_data.get('tien_cuoi_ky', 0)
                    m3.metric("Còn nợ", f"{abs(debt):,.0f}đ", delta=-debt, delta_color="inverse")
                    
                    st.markdown("---")
                    st.write("📍 **Địa chỉ:**", unit_data.get('diachi', 'Chưa có dữ liệu'))
                    st.write("👤 **Liên hệ:**", f"{unit_data.get('nguoilh', 'N/A')} - {unit_data.get('dienthoai', 'N/A')}")
                    
                    # Nội dung chuyển khoản siêu đẹp
                    st.info(f"**Cú pháp nộp tiền:**\n\n`BHXH {unit_data.get('madvi')} {unit_data.get('tendvi')}`")
                    st.markdown("</div>", unsafe_allow_html=True)

                with col_right:
                    # Biểu đồ Gauge bằng Plotly
                    target = unit_data.get('so_phai_dong', 1)
                    actual = unit_data.get('so_da_dong', 0)
                    percent = min(round((actual / target) * 100, 1), 100) if target > 0 else 0
                    
                    fig = go.Figure(go.Indicator(
                        mode = "gauge+number",
                        value = percent,
                        title = {'text': "Tiến độ nộp tiền (%)", 'font': {'size': 20}},
                        gauge = {
                            'axis': {'range': [0, 100]},
                            'bar': {'color': "#2563eb"},
                            'steps': [
                                {'range': [0, 50], 'color': "#fee2e2"},
                                {'range': [50, 90], 'color': "#fef9c3"},
                                {'range': [90, 100], 'color': "#dcfce7"}]
                        }
                    ))
                    fig.update_layout(height=300, margin=dict(l=20, r=20, t=50, b=20))
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # QR Code tích hợp
                    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=250x250&data=BHXH_PAY_{unit_data.get('madvi')}_{debt}"
                    st.image(qr_url, caption="Quét mã để nộp tiền nhanh", width=200)
                    
                    if st.button("🎊 Xác nhận hoàn thành"):
                        st.balloons()
        else:
            st.error("Không tìm thấy kết quả nào. Bạn hãy thử gõ từ khóa khác nhé!")
    else:
        st.markdown("<br><br><center><h3>👋 Chào mừng bạn quay lại!</h3><p>Hãy nhập tên hoặc mã đơn vị để bắt đầu khám phá.</p></center>", unsafe_allow_html=True)
else:
    st.info("Vui lòng tải file dữ liệu lên để kích hoạt hệ thống.")

# --- FOOTER ---
st.markdown("<br><hr><center style='color:#64748b'>BHXH Thuận An Dashboard v4.0 • AI Powered</center>", unsafe_allow_html=True)
