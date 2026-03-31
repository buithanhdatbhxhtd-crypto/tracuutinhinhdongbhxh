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
    page_title="BHXH Thuận An - Ultimate Hub v8.0",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- KHỞI TẠO STATE ---
if 'selected_unit' not in st.session_state:
    st.session_state.selected_unit = None
if 'last_query' not in st.session_state:
    st.session_state.last_query = ""

# --- TỔNG LỰC CSS (GIAO DIỆN SIÊU CẤP) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;700;800&display=swap');
    
    :root {
        --primary: #1e40af;
        --accent: #3b82f6;
        --success: #10b981;
        --bg: #f8fafc;
    }

    * { font-family: 'Plus Jakarta Sans', sans-serif; }
    
    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
    }
    
    /* Bảng chữ chạy Marquee */
    .marquee-container {
        background: white;
        color: var(--primary);
        padding: 10px 0;
        font-weight: 600;
        border-radius: 50px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin-bottom: 25px;
        overflow: hidden;
        border: 1px solid #e2e8f0;
    }
    
    /* Hiệu ứng kính Dashboard */
    .dashboard-panel {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.8);
        border-radius: 40px;
        padding: 40px;
        box-shadow: 0 30px 60px -12px rgba(0,0,0,0.08);
    }

    /* Banner Poster */
    .poster-card {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        color: white;
        padding: 30px;
        border-radius: 30px;
        margin-bottom: 20px;
        text-align: center;
        box-shadow: 0 15px 30px rgba(30, 58, 138, 0.2);
    }

    /* Input Tìm kiếm */
    .stTextInput input {
        border-radius: 50px !important;
        padding: 1.6rem 2.8rem !important;
        border: 2px solid #cbd5e1 !important;
        background: white !important;
        font-size: 1.3rem !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.05) !important;
    }

    /* Thẻ Ngân hàng */
    .bank-card {
        background: white;
        padding: 15px;
        border-radius: 20px;
        border: 1px solid #f1f5f9;
        margin-bottom: 10px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .main-title {
        background: linear-gradient(90deg, #1e3a8a, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 4.5rem;
        font-weight: 800;
        letter-spacing: -4px;
        margin-bottom: 0px;
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

# --- HEADER & MARQUEE ---
st.markdown("<div style='text-align:center'><h1 class='main-title'>🛡️ Smart BHXH Hub</h1></div>", unsafe_allow_html=True)

marquee_text = "📍 Địa chỉ: Thôn Thuận Sơn, xã Thuận An, tỉnh Lâm Đồng. 💳 Số tài khoản: 63510009867032 (BIDV) - 5301202919045 (Agribank) - 919035000003 (Vietinbank). Chúc quý đơn vị một ngày làm việc hiệu quả! 🛡️ BHXH Thuận An đồng hành cùng bạn."
st.markdown(f"""
    <div class="marquee-container">
        <marquee scrollamount="8">{marquee_text}</marquee>
    </div>
    """, unsafe_allow_html=True)

df = load_data()

# --- GIAO DIỆN CHÍNH ---
if df is not None:
    # MÀN HÌNH 1: TÌM KIẾM
    if st.session_state.selected_unit is None:
        c1, c2 = st.columns([1.5, 1])
        
        with c1:
            st.markdown("### 🔎 Tra cứu thông tin đơn vị")
            query = st.text_input("Tìm", placeholder="Nhập tên đơn vị hoặc mã đơn vị...", label_visibility="collapsed")
            
            if query:
                clean_query = unidecode(query).lower()
                results = df[df['search_index'].str.contains(clean_query, na=False)].head(8)
                
                if not results.empty:
                    for _, row in results.iterrows():
                        with st.container():
                            col_a, col_b = st.columns([4, 1.2])
                            col_a.markdown(f"""
                                <div style='background:white; padding:20px; border-radius:20px; border-left:8px solid #cbd5e1; margin-bottom:10px;'>
                                    <small style='color:#3b82f6; font-weight:800;'>MÃ: {row.get('madvi')}</small><br>
                                    <b style='font-size:1.2rem;'>{row.get('tendvi')}</b>
                                </div>
                            """, unsafe_allow_html=True)
                            if col_b.button("Xem ngay ➔", key=f"sel_{row.get('madvi')}"):
                                st.session_state.selected_unit = row.get('madvi')
                                st.balloons() # Pháo hoa bóng bay chào mừng
                                with st.status("🚀 Đang khởi tạo Dashboard...", expanded=False):
                                    time.sleep(1)
                                st.rerun()
                else:
                    st.error("Không tìm thấy kết quả.")
            else:
                st.markdown("<br><br><center><img src='https://cdn-icons-png.flaticon.com/512/3772/3772274.png' width='120' style='opacity:0.2'></center>", unsafe_allow_html=True)

        with c2:
            st.markdown("""
            <div class="poster-card">
                <h3>🛡️ BẢO VỆ QUYỀN LỢI</h3>
                <p>BHXH là điểm tựa an sinh xã hội vững chắc cho người lao động và doanh nghiệp.</p>
                <hr style='border: 0.5px solid rgba(255,255,255,0.3)'>
                <small>Tham gia BHXH là tuân thủ pháp luật và thể hiện trách nhiệm với cộng đồng.</small>
            </div>
            """, unsafe_allow_html=True)
            st.image("https://images.unsplash.com/photo-1554224155-1696413575b9?auto=format&fit=crop&q=80&w=400", use_container_width=True, caption="An tâm cống hiến - Vững bước tương lai")

    # MÀN HÌNH 2: DASHBOARD
    else:
        unit_data = df[df['madvi'] == st.session_state.selected_unit].iloc[0]
        
        if st.button("⬅ Quay lại tra cứu"):
            st.session_state.selected_unit = None
            st.rerun()

        st.markdown(f"""
            <div style='background:white; padding:35px; border-radius:35px; border-left:12px solid #1e3a8a; box-shadow: 0 10px 30px rgba(0,0,0,0.05);'>
                <h1 style='margin:0; color:#1e3a8a;'>🏢 {unit_data.get('tendvi')}</h1>
                <p style='margin:5px 0 0 0; color:#64748b; font-size:1.1rem;'>Mã đơn vị: <b>{unit_data.get('madvi')}</b> | Địa chỉ: {unit_data.get('diachi', 'N/A')}</p>
            </div>
        """, unsafe_allow_html=True)

        col_left, col_right = st.columns([1.8, 1])

        with col_left:
            st.markdown("<div class='dashboard-panel'>", unsafe_allow_html=True)
            st.write("### 📊 Thông báo kết quả đóng BHXH")
            
            # Metric grid
            cols = st.columns(3)
            cols[0].metric("Tiền đầu kỳ", f"{unit_data.get('tien_dau_ky', 0):,.0f}đ")
            cols[1].metric("Phải đóng", f"{unit_data.get('so_phai_dong', 0):,.0f}đ")
            cols[2].metric("Điều chỉnh", f"{unit_data.get('dieu_chinh_ky_truoc', 0):,.0f}đ")
            
            st.write("<br>", unsafe_allow_html=True)
            cols2 = st.columns(3)
            cols2[0].metric("Đã đóng", f"{unit_data.get('so_da_dong', 0):,.0f}đ")
            cols2[1].metric("Lệch", f"{unit_data.get('so_bi_lech', 0):,.0f}đ")
            
            debt = unit_data.get('tien_cuoi_ky', 0)
            cols2[2].metric("Số nợ/dư", f"{abs(debt):,.0f}đ", delta=-debt, delta_color="inverse")
            
            # Cú pháp nộp tiền thời gian thực
            now = datetime.now()
            transfer_note = f"{unit_data.get('madvi')} {unit_data.get('tendvi')} đóng bhxh tháng {now.month} năm {now.year}"
            
            st.markdown(f"""
                <div class="transfer-box">
                    <p style='color:#1e40af; font-weight:800; margin:0;'>📝 CÚ PHÁP NỘP TIỀN CHUẨN:</p>
                    <h2 style='color:#1e3a8a; font-family:monospace; margin:15px 0;'>{transfer_note}</h2>
                    <small><i>Lưu ý: Ghi đúng nội dung trên để hệ thống tự động gạch nợ.</i></small>
                </div>
            """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with col_right:
            # Gauge Chart
            phai_dong = unit_data.get('so_phai_dong', 1)
            da_dong = unit_data.get('so_da_dong', 0)
            rate = min(round((da_dong / phai_dong) * 100, 1), 100) if phai_dong > 0 else 0
            
            fig = go.Figure(go.Indicator(
                mode = "gauge+number", value = rate,
                title = {'text': "Tiến độ nộp tiền (%)", 'font': {'size': 20}},
                number = {'suffix': "%", 'font': {'color': '#1e40af'}},
                gauge = {
                    'axis': {'range': [0, 100]},
                    'bar': {'color': "#1e40af"},
                    'steps': [{'range': [0, 50], 'color': '#fee2e2'}, {'range': [50, 90], 'color': '#fef9c3'}, {'range': [90, 100], 'color': '#dcfce7'}]
                }
            ))
            fig.update_layout(height=350, margin=dict(l=30, r=30, t=50, b=20), paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)
            
            # Thông tin ngân hàng
            st.markdown("### 💳 Tài khoản thụ hưởng")
            st.markdown("""
                <div class='bank-card'><span><b>BIDV:</b> 63510009867032</span><small>BHXH Thuận An</small></div>
                <div class='bank-card'><span><b>Agribank:</b> 5301202919045</span><small>BHXH Thuận An</small></div>
                <div class='bank-card'><span><b>Vietinbank:</b> 919035000003</span><small>BHXH Thuận An</small></div>
            """, unsafe_allow_html=True)
            
            qr_data = f"BHXH|{unit_data.get('madvi')}|{debt}"
            st.markdown(f"<center><img src='https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={qr_data}' width='150' style='border-radius:15px; margin-top:15px;'></center>", unsafe_allow_html=True)

# --- FOOTER ---
st.markdown("<br><hr><center style='color:#94a3b8; font-size:0.8rem;'>© 2026 BHXH THUẬN AN - THÔN THUẬN SƠN, XÃ THUẬN AN, LÂM ĐỒNG</center>", unsafe_allow_html=True)
