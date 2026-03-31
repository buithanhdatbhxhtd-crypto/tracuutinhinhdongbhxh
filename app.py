import streamlit as st
import pandas as pd
import numpy as np
import os
import plotly.graph_objects as go
from unidecode import unidecode
import time
from datetime import datetime

# --- CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="BHXH cơ sở Thuận An - Elite Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- KHỞI TẠO STATE ---
if 'selected_unit' not in st.session_state:
    st.session_state.selected_unit = None
if 'last_query' not in st.session_state:
    st.session_state.last_query = ""

# --- TỔNG LỰC CSS (GIAO DIỆN ELITE v9.0) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;700;800&display=swap');
    
    :root {
        --primary: #1e40af;
        --accent: #0ea5e9;
        --success: #10b981;
        --warning: #f59e0b;
        --bg: #f8fafc;
    }

    * { font-family: 'Plus Jakarta Sans', sans-serif; }
    
    .stApp {
        background: linear-gradient(180deg, #ffffff 0%, #f1f5f9 100%);
    }
    
    /* Hero Title Section */
    .hero-title {
        background: linear-gradient(90deg, #1e3a8a, #3b82f6, #60a5fa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 4.8rem;
        font-weight: 800;
        letter-spacing: -3px;
        margin-bottom: 0px;
        text-align: center;
        line-height: 1.1;
    }

    /* Marquee Styling */
    .marquee-container {
        background: #1e3a8a;
        color: white;
        padding: 12px 0;
        font-weight: 500;
        border-radius: 12px;
        box-shadow: 0 10px 25px -5px rgba(30, 58, 138, 0.2);
        margin-bottom: 30px;
        overflow: hidden;
    }
    
    /* Glass Cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.5);
        border-radius: 30px;
        padding: 35px;
        box-shadow: 0 20px 40px rgba(0,0,0,0.04);
        transition: all 0.3s ease;
    }
    
    .glass-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 30px 60px rgba(0,0,0,0.08);
    }

    /* Custom Metric Display */
    .metric-value {
        font-size: 1.8rem;
        font-weight: 800;
        color: #1e293b;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #64748b;
        font-weight: 600;
    }

    /* Poster Section */
    .poster-box {
        background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%);
        color: white;
        padding: 30px;
        border-radius: 32px;
        margin-bottom: 25px;
        box-shadow: 0 15px 35px rgba(30, 58, 138, 0.2);
    }

    /* Input Styling */
    .stTextInput input {
        border-radius: 20px !important;
        padding: 1.5rem 2.5rem !important;
        border: 2px solid #e2e8f0 !important;
        background: white !important;
        font-size: 1.2rem !important;
        transition: all 0.3s ease;
    }
    .stTextInput input:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 5px rgba(59, 130, 246, 0.1) !important;
    }

    /* Transfer Info Box */
    .transfer-box {
        background: #f0f7ff;
        padding: 30px;
        border-radius: 24px;
        border: 2px dashed #3b82f6;
        margin-top: 25px;
    }
    
    .bank-item {
        background: white;
        padding: 12px 20px;
        border-radius: 15px;
        margin-bottom: 10px;
        border: 1px solid #e2e8f0;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- HÀM TẢI DỮ LIỆU ---
@st.cache_data
def load_data(uploaded_file=None):
    df = None
    try:
        files = [f for f in os.listdir('.') if f.lower().startswith('c12')]
        if uploaded_file:
            df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
        elif files:
            target = files[0]
            df = pd.read_csv(target) if target.lower().endswith('.csv') else pd.read_excel(target)
        
        if df is not None:
            df.columns = [unidecode(str(c)).lower().strip().replace(' ', '_') for c in df.columns]
            if 'madvi' in df.columns: df['madvi'] = df['madvi'].astype(str).str.strip()
            df['search_index'] = df.apply(lambda x: unidecode(str(x.get('madvi', '')) + " " + str(x.get('tendvi', ''))).lower(), axis=1)
            return df
    except Exception as e:
        st.error(f"Lỗi: {e}")
    return None

# --- HEADER SECTION ---
st.markdown("<h1 class='hero-title'>BHXH cơ sở Thuận An</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#64748b; font-size:1.2rem; margin-top:-15px; margin-bottom:30px;'>Hệ thống tra cứu thông tin đóng BHXH kỹ thuật số</p>", unsafe_allow_html=True)

# Marquee Info
marquee_text = "📍 Địa chỉ: Thôn Thuận Sơn, xã Thuận An, tỉnh Lâm Đồng. | 💳 Tài khoản Ngân hàng: BIDV: 63510009867032 - Agribank: 5301202919045 - Vietinbank: 919035000003. | Chúc quý đơn vị một ngày làm việc tràn đầy năng lượng! 🛡️"
st.markdown(f"""
    <div class="marquee-container">
        <marquee scrollamount="8" behavior="scroll" direction="left">{marquee_text}</marquee>
    </div>
    """, unsafe_allow_html=True)

df = load_data()

# --- GIAO DIỆN CHÍNH ---
if df is not None:
    # MÀN HÌNH 1: TÌM KIẾM
    if st.session_state.selected_unit is None:
        col_s1, col_s2 = st.columns([1.6, 1])
        
        with col_s1:
            st.markdown("### 🔎 Nhập thông tin tra cứu")
            query = st.text_input("SearchBox", placeholder="Nhập tên công ty hoặc mã đơn vị để tìm nhanh...", label_visibility="collapsed")
            
            if query:
                clean_query = unidecode(query).lower()
                results = df[df['search_index'].str.contains(clean_query, na=False)].head(10)
                
                if not results.empty:
                    st.write(f"Tìm thấy **{len(results)}** kết quả:")
                    for _, row in results.iterrows():
                        with st.container():
                            ca, cb = st.columns([4, 1.5])
                            ca.markdown(f"""
                                <div style='background:white; padding:25px; border-radius:24px; border-left:10px solid #e2e8f0; margin-bottom:15px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);'>
                                    <small style='color:#3b82f6; font-weight:800; text-transform:uppercase;'>Mã: {row.get('madvi')}</small><br>
                                    <b style='font-size:1.3rem; color:#1e293b;'>{row.get('tendvi')}</b>
                                </div>
                            """, unsafe_allow_html=True)
                            if cb.button("Xác nhận ➔", key=f"sel_{row.get('madvi')}_{_}", use_container_width=True):
                                # Hiệu ứng chào mừng
                                st.balloons()
                                with st.status("💎 Đang truy xuất dữ liệu vàng...", expanded=False):
                                    time.sleep(0.8)
                                st.session_state.selected_unit = row.get('madvi')
                                st.rerun()
                else:
                    st.error("Không tìm thấy đơn vị phù hợp. Hãy thử từ khóa khác.")
            else:
                st.markdown("<br><br><center><img src='https://cdn-icons-png.flaticon.com/512/3772/3772274.png' width='140' style='opacity:0.2'></center>", unsafe_allow_html=True)

        with col_s2:
            st.markdown("""
            <div class="poster-box">
                <h2 style='color:white; margin-top:0;'>🛡️ AN SINH XÃ HỘI</h2>
                <p style='font-size:1.1rem; opacity:0.9;'>BHXH Thuận An cam kết bảo vệ quyền lợi tối đa cho người lao động và đồng hành cùng sự phát triển bền vững của doanh nghiệp.</p>
                <hr style='border: 0.5px solid rgba(255,255,255,0.2); margin: 20px 0;'>
                <p style='font-size:0.9rem;'>📍 <b>Địa chỉ:</b> Thôn Thuận Sơn, xã Thuận An, Lâm Đồng</p>
            </div>
            """, unsafe_allow_html=True)
            st.image("https://images.unsplash.com/photo-1454165833767-027eeea15c3e?auto=format&fit=crop&q=80&w=500", use_container_width=True, caption="Kết nối - Minh bạch - Chuyên nghiệp")

    # MÀN HÌNH 2: DASHBOARD CHI TIẾT
    else:
        unit_data = df[df['madvi'] == st.session_state.selected_unit].iloc[0]
        
        if st.button("⬅ Quay lại tìm kiếm"):
            st.session_state.selected_unit = None
            st.rerun()

        st.markdown(f"""
            <div style='background:white; padding:40px; border-radius:35px; border-left:15px solid #1e3a8a; box-shadow: 0 20px 50px rgba(0,0,0,0.06);'>
                <h1 style='margin:0; color:#1e3a8a; font-size:3rem;'>🏢 {unit_data.get('tendvi')}</h1>
                <p style='margin:10px 0 0 0; color:#64748b; font-size:1.2rem;'>Mã đơn vị: <b style='color:#1e3a8a;'>{unit_data.get('madvi')}</b> | Địa chỉ: {unit_data.get('diachi', 'N/A')}</p>
            </div>
        """, unsafe_allow_html=True)

        col_left, col_right = st.columns([1.8, 1])

        with col_left:
            st.markdown("<div class='glass-card' style='margin-top:25px;'>", unsafe_allow_html=True)
            st.write("### 📊 Thông báo kết quả đóng BHXH")
            
            # Metric Grid với CSS Neumorphism
            m_col1, m_col2, m_col3 = st.columns(3)
            m_col1.metric("Tiền đầu kỳ", f"{unit_data.get('tien_dau_ky', 0):,.0f}đ")
            m_col2.metric("Số phải đóng", f"{unit_data.get('so_phai_dong', 0):,.0f}đ")
            m_col3.metric("Điều chỉnh", f"{unit_data.get('dieu_chinh_ky_truoc', 0):,.0f}đ")
            
            st.write("<br>", unsafe_allow_html=True)
            m_col4, m_col5, m_col6 = st.columns(3)
            m_col4.metric("Số đã đóng", f"{unit_data.get('so_da_dong', 0):,.0f}đ")
            m_col5.metric("Số bị lệch", f"{unit_data.get('so_bi_lech', 0):,.0f}đ")
            
            debt = unit_data.get('tien_cuoi_ky', 0)
            label_st = "Tiền còn nợ" if debt > 0 else "Tiền dư có"
            m_col6.metric(label_st, f"{abs(debt):,.0f}đ", delta=-debt, delta_color="inverse")
            
            # Cú pháp nộp tiền chuẩn thời gian thực
            now = datetime.now()
            transfer_note = f"{unit_data.get('madvi')} {unit_data.get('tendvi')} đóng bhxh tháng {now.month} năm {now.year}"
            
            st.markdown(f"""
                <div class="transfer-box">
                    <p style='color:#1e40af; font-weight:800; margin:0; font-size:1rem;'>📝 CÚ PHÁP CHUYỂN KHOẢN CHUẨN:</p>
                    <h2 style='color:#1e3a8a; font-family:monospace; margin:15px 0; font-size:1.5rem;'>{transfer_note}</h2>
                    <p style='margin:0; font-size:0.85rem; color:#64748b;'><i>Hãy đảm bảo ghi đúng nội dung để hệ thống ghi nhận kịp thời.</i></p>
                </div>
            """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with col_right:
            # Gauge Chart Plotly
            phai_dong = unit_data.get('so_phai_dong', 1)
            da_dong = unit_data.get('so_da_dong', 0)
            rate = min(round((da_dong / phai_dong) * 100, 1), 100) if phai_dong > 0 else 0
            
            fig = go.Figure(go.Indicator(
                mode = "gauge+number", value = rate,
                title = {'text': "Tỷ lệ hoàn thành nộp tiền", 'font': {'size': 20, 'color': '#64748b'}},
                number = {'suffix': "%", 'font': {'color': '#1e40af', 'size': 50}},
                gauge = {
                    'axis': {'range': [0, 100], 'tickwidth': 1},
                    'bar': {'color': "#1e40af"},
                    'bgcolor': "white",
                    'borderwidth': 2,
                    'bordercolor': "#e2e8f0",
                    'steps': [
                        {'range': [0, 50], 'color': '#fee2e2'},
                        {'range': [50, 90], 'color': '#fef9c3'},
                        {'range': [90, 100], 'color': '#dcfce7'}
                    ]
                }
            ))
            fig.update_layout(height=400, margin=dict(l=30, r=30, t=60, b=30), paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)
            
            # Thông tin ngân hàng & QR
            st.markdown("### 💳 Tài khoản thụ hưởng")
            st.markdown("""
                <div class='bank-item'><b>BIDV</b> <span>63510009867032</span></div>
                <div class='bank-item'><b>Agribank</b> <span>5301202919045</span></div>
                <div class='bank-item'><b>Vietinbank</b> <span>919035000003</span></div>
            """, unsafe_allow_html=True)
            
            qr_data = f"BHXH|{unit_data.get('madvi')}|{debt}"
            st.markdown(f"""
                <center>
                    <div style='background:white; padding:15px; border-radius:25px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); display:inline-block; margin-top:15px;'>
                        <img src='https://api.qrserver.com/v1/create-qr-code/?size=250x250&data={qr_data}' width='180'>
                    </div>
                    <p style='color:#64748b; font-size:0.8rem; margin-top:10px;'>Quét mã để nộp tiền nhanh</p>
                </center>
            """, unsafe_allow_html=True)

# --- FOOTER ---
st.markdown("<br><hr>", unsafe_allow_html=True)
st.markdown(f"""
    <center style='color:#94a3b8; font-size:0.9rem; padding-bottom:50px;'>
        © {datetime.now().year} BHXH CƠ SỞ THUẬN AN - THÔN THUẬN SƠN, XÃ THUẬN AN, LÂM ĐỒNG<br>
        Hệ thống được phát triển với niềm đam mê công nghệ và sự sáng tạo.
    </center>
""", unsafe_allow_html=True)
