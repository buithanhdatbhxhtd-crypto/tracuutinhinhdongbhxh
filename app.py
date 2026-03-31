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
    page_title="BHXH cơ sở Thuận An - Elite Digital v12.5",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- KHỞI TẠO STATE ---
if 'selected_unit' not in st.session_state:
    st.session_state.selected_unit = None
if 'last_query' not in st.session_state:
    st.session_state.last_query = ""
if 'show_loading' not in st.session_state:
    st.session_state.show_loading = False

# --- TỔNG LỰC CSS (GIAO DIỆN ELITE v12.5 - FIX CLIPPING & SEARCH ZONE) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    :root {
        --primary: #1e3a8a;
        --secondary: #2563eb;
        --accent: #0ea5e9;
        --neon-blue: #00d2ff;
        --neon-gold: #ffaa00;
        --neon-green: #39ff14;
    }

    * { font-family: 'Plus Jakarta Sans', sans-serif; }
    
    .stApp {
        background: linear-gradient(135deg, #f0f4f8 0%, #d9e2ec 100%);
    }

    /* TIÊU ĐỀ CHÍNH */
    .hero-banner { text-align: center; padding: 1rem 0; }
    .hero-title {
        background: linear-gradient(90deg, #1e3a8a, #2563eb, #0ea5e9);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.5rem;
        font-weight: 800;
        letter-spacing: -2px;
        margin-bottom: 0px;
    }

    /* BẢNG LED CHẠY CHỮ */
    .led-marquee {
        background: #000;
        color: #00ff00;
        padding: 10px 0;
        font-weight: 700;
        border-radius: 12px;
        box-shadow: 0 0 20px rgba(0, 255, 0, 0.3);
        border: 2px solid #333;
        margin-bottom: 25px;
        font-family: 'Courier New', Courier, monospace;
        font-size: 0.95rem;
    }

    /* KHUNG XANH TÌM KIẾM (VỊ TRÍ SỐ 2) - FIX LỖI CHE CHỮ */
    .search-zone {
        background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%);
        padding: 35px;
        border-radius: 30px;
        box-shadow: 0 20px 40px rgba(30, 58, 138, 0.2);
        margin-bottom: 30px;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.2);
    }

    /* FIX TRIỆT ĐỂ Ô INPUT BỊ CHE */
    .stTextInput input {
        border-radius: 15px !important;
        padding: 0 25px !important; /* Xóa padding dọc dư thừa */
        border: 4px solid #fff !important;
        font-size: 1.6rem !important; 
        font-weight: 700 !important;
        height: 75px !important; /* Fix chiều cao cố định */
        line-height: 75px !important; /* Căn giữa chữ theo chiều dọc */
        background: white !important;
        color: #1e3a8a !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1) !important;
        transition: all 0.3s ease;
    }
    
    .stTextInput input:focus {
        border-color: #00d2ff !important;
        transform: scale(1.01);
    }

    /* THẺ CÁN BỘ & TÀI KHOẢN */
    .officer-card {
        background: #0a0a0a;
        padding: 18px;
        border-radius: 20px;
        border: 2px solid #222;
        margin-bottom: 12px;
        text-align: center;
    }
    .card-nhai { animation: blink-blue 2s infinite; }
    .card-dat { animation: blink-gold 2.5s infinite; }
    .card-hai { animation: blink-green 3s infinite; }

    @keyframes blink-blue { 0%, 100% { border-color: #00d2ff; } 50% { border-color: #111; } }
    @keyframes blink-gold { 0%, 100% { border-color: #ffaa00; } 50% { border-color: #111; } }
    @keyframes blink-green { 0%, 100% { border-color: #39ff14; } 50% { border-color: #111; } }

    .bank-account-card {
        background: #111;
        padding: 15px;
        border-radius: 15px;
        border: 1px solid #333;
        margin-bottom: 8px;
    }
    .bank-name { color: #00d2ff; font-weight: 800; font-size: 0.85rem; }
    .bank-number { color: #fff; font-size: 1.2rem; font-family: monospace; letter-spacing: 1px; }

    /* DASHBOARD */
    .dashboard-panel {
        background: white;
        border-radius: 40px;
        padding: 40px;
        box-shadow: 0 30px 70px rgba(0,0,0,0.1);
    }
    
    /* BUTTONS */
    .stButton>button {
        border-radius: 50px !important;
        font-weight: 800 !important;
        transition: all 0.2s ease !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- DATA: CÁN BỘ & NGÂN HÀNG ---
OFFICERS = [
    {"name": "Bà NGUYỄN THỊ NHÀI", "scope": "Xã Đức Lập, Xã Đắk Mil", "phone": "0846.39.29.29", "class": "card-nhai", "color": "#00d2ff", "areas": ["duc lap", "dak mil", "đức lập", "đắk mil"]},
    {"name": "Ông BÙI THÀNH ĐẠT", "scope": "Xã Đắk Sắk, Xã Đắk Song", "phone": "0986.05.30.06", "class": "card-dat", "color": "#ffaa00", "areas": ["dak sak", "dak song", "đắk sắk", "đắk song"]},
    {"name": "Ông HOÀNG SỸ HẢI", "scope": "Xã Thuận An", "phone": "0919.06.11.53", "class": "card-hai", "color": "#39ff14", "areas": ["thuan an", "thuận an"]}
]

BANKS = [
    {"name": "BIDV", "number": "63510009867032"},
    {"name": "AGRIBANK", "number": "5301202919045"},
    {"name": "VIETINBANK", "number": "919035000003"}
]

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
    except: return None

# --- HEADER ---
st.markdown("<div class='hero-banner'><h1 class='hero-title'>BHXH cơ sở Thuận An</h1></div>", unsafe_allow_html=True)
st.markdown(f"<div class='led-marquee'><marquee scrollamount='10'>📍 THÔN THUẬN SƠN, XÃ THUẬN AN, TỈNH LÂM ĐỒNG • HỆ THỐNG TRA CỨU C12-TS TRỰC TUYẾN • LIÊN HỆ CÁN BỘ CHUYÊN QUẢN ĐỂ ĐƯỢC HỖ TRỢ •</marquee></div>", unsafe_allow_html=True)

df = load_data()

if df is not None:
    # MÀN HÌNH 1: TRANG CHỦ
    if st.session_state.selected_unit is None:
        
        # KHUNG XANH TÌM KIẾM (VỊ TRÍ SỐ 2)
        st.markdown("<div class='search-zone'>", unsafe_allow_html=True)
        st.markdown("<h3 style='color:white; margin-top:0; font-size:1.5rem;'>🔍 NHẬP MÃ HOẶC TÊN ĐƠN VỊ CẦN TRA CỨU</h3>", unsafe_allow_html=True)
        query = st.text_input("Gateway", placeholder="Ví dụ: TC0243, Daknoco...", label_visibility="collapsed")
        st.markdown("</div>", unsafe_allow_html=True)

        # BỐ CỤC 3 CỘT
        col_post, col_res, col_info = st.columns([0.8, 1.4, 1])

        with col_post:
            st.markdown("##### 🛡️ Thông báo")
            posters = [
                {"t": "🛡️ AN SINH", "c": "BHXH là điểm tựa tài chính vững chắc."},
                {"t": "🏥 BHYT", "c": "Bảo vệ sức khỏe gia đình bạn."},
                {"t": "🤰 THAI SẢN", "c": "Đồng hành cùng mẹ và bé."}
            ]
            p = posters[datetime.now().minute % len(posters)]
            st.markdown(f"""
                <div style='background:white; padding:20px; border-radius:20px; border:1px solid #e2e8f0; text-align:center;'>
                    <h4 style='color:#1e3a8a; margin:0;'>{p['t']}</h4>
                    <p style='font-size:0.9rem; color:#64748b; margin:10px 0;'>{p['c']}</p>
                    <hr style='border: 0.5px solid #eee;'>
                    <small style='color:#ffaa00; font-weight:700;'>An tâm cống hiến</small>
                </div>
            """, unsafe_allow_html=True)

        with col_res:
            if query:
                clean_query = unidecode(query).lower()
                results = df[df['search_index'].str.contains(clean_query, na=False)].head(8)
                if not results.empty:
                    st.write(f"✨ Kết quả ({len(results)}):")
                    for idx, row in results.iterrows():
                        with st.container():
                            ca, cb = st.columns([3, 1.2])
                            ca.markdown(f"""
                                <div style='background:white; padding:15px; border-radius:15px; border-left:6px solid #2563eb; margin-bottom:10px; box-shadow:0 4px 6px rgba(0,0,0,0.03);'>
                                    <small style='color:#2563eb; font-weight:800;'>MÃ: {row.get('madvi')}</small><br>
                                    <b style='font-size:1.1rem;'>{row.get('tendvi')}</b>
                                </div>
                            """, unsafe_allow_html=True)
                            if cb.button("Xác nhận ➔", key=f"sel_{row.get('madvi')}_{idx}", use_container_width=True):
                                st.session_state.selected_unit = row.get('madvi')
                                st.session_state.show_loading = True
                                st.rerun()
                else:
                    st.error("Không tìm thấy dữ liệu.")
            else:
                st.markdown("<br><center><img src='https://cdn-icons-png.flaticon.com/512/3772/3772274.png' width='120' style='opacity:0.2'><h4 style='color:#94a3b8;'>Hệ thống sẵn sàng</h4></center>", unsafe_allow_html=True)

        with col_info:
            st.markdown("##### 👩‍💼 Cán bộ Chuyên quản")
            for off in OFFICERS:
                st.markdown(f"""
                <div class="officer-card {off['class']}">
                    <div style="color:{off['color']}; font-weight:800; font-size:0.95rem;">{off['name']}</div>
                    <div style="color:#aaa; font-size:0.75rem; margin:4px 0;">Xã: {off['scope']}</div>
                    <a href="tel:{off['phone'].replace('.','')}" style="text-decoration:none; color:white; font-weight:700; font-size:1.1rem;">📱 {off['phone']}</a>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("##### 🏦 Tài khoản Ngân hàng")
            for bank in BANKS:
                st.markdown(f"""
                <div class="bank-account-card">
                    <div class="bank-name">{bank['name']}</div>
                    <div class="bank-number">{bank['number']}</div>
                </div>
                """, unsafe_allow_html=True)

    # MÀN HÌNH LOADING
    elif st.session_state.show_loading:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        with st.status("💎 Đang xử lý dữ liệu...", expanded=True) as status:
            st.write("🔄 Đang trích xuất báo cáo C12-TS...")
            time.sleep(1)
            status.update(label="Hoàn tất!", state="complete")
        st.session_state.show_loading = False
        st.balloons()
        st.rerun()

    # MÀN HÌNH 2: DASHBOARD CHI TIẾT
    else:
        unit_data = df[df['madvi'] == st.session_state.selected_unit].iloc[0]
        unit_addr = unidecode(str(unit_data.get('diachi', ''))).lower()
        
        if st.button("⬅ QUAY LẠI TRANG CHỦ"):
            st.session_state.selected_unit = None
            st.rerun()

        st.markdown(f"""
            <div style='background:white; padding:35px; border-radius:35px; border-left:15px solid #1e3a8a; box-shadow: 0 20px 50px rgba(0,0,0,0.06); margin-top:15px;'>
                <h2 style='margin:0; color:#1e3a8a;'>🏢 {unit_data.get('tendvi')}</h2>
                <p style='margin:5px 0 0 0; color:#64748b;'>Mã: <b>{unit_data.get('madvi')}</b> | Địa chỉ: {unit_data.get('diachi', 'N/A')}</p>
            </div>
        """, unsafe_allow_html=True)

        col_l, col_r = st.columns([1.8, 1])
        with col_l:
            st.markdown("<div class='dashboard-panel' style='margin-top:25px;'>", unsafe_allow_html=True)
            st.write("#### 📊 Báo cáo kết quả đóng BHXH")
            m1, m2, m3 = st.columns(3)
            m1.metric("Tiền đầu kỳ", f"{unit_data.get('tien_dau_ky', 0):,.0f}đ")
            m2.metric("Số phải đóng", f"{unit_data.get('so_phai_dong', 0):,.0f}đ")
            m3.metric("Điều chỉnh", f"{unit_data.get('dieu_chinh_ky_truoc', 0):,.0f}đ")
            
            st.write("<br>", unsafe_allow_html=True)
            m4, m5, m6 = st.columns(3)
            m4.metric("Số đã đóng", f"{unit_data.get('so_da_dong', 0):,.0f}đ")
            m5.metric("Số bị lệch", f"{unit_data.get('so_bi_lech', 0):,.0f}đ")
            debt = unit_data.get('tien_cuoi_ky', 0)
            m6.metric("CÒN NỢ" if debt > 0 else "DƯ CÓ", f"{abs(debt):,.0f}đ", delta=-debt, delta_color="inverse")
            
            now = datetime.now()
            transfer_note = f"{unit_data.get('madvi')} {unit_data.get('tendvi')} đóng bhxh tháng {now.month} năm {now.year}"
            st.markdown(f"""
                <div style='background:#f0f9ff; padding:25px; border-radius:25px; border:2px dashed #3b82f6; margin-top:25px; text-align:center;'>
                    <p style='color:#1e40af; font-weight:800; font-size:0.9rem;'>📝 NỘI DUNG CHUYỂN KHOẢN CHUẨN:</p>
                    <h3 style='color:#1e3a8a; font-family:monospace;'>{transfer_note}</h3>
                </div>
            """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with col_r:
            phai_dong = unit_data.get('so_phai_dong', 1)
            da_dong = unit_data.get('so_da_dong', 0)
            rate = min(round((da_dong / phai_dong) * 100, 1), 100) if phai_dong > 0 else 0
            fig = go.Figure(go.Indicator(
                mode = "gauge+number", value = rate,
                title = {'text': "Hoàn thành (%)", 'font': {'size': 20}},
                gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': "#1e40af"}, 'steps': [{'range': [0, 50], 'color': '#fee2e2'}, {'range': [90, 100], 'color': '#dcfce7'}]}
            ))
            fig.update_layout(height=350, margin=dict(l=30, r=30, t=50, b=30), paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)
            
            # Highlight Cán bộ phụ trách xã
            for off in OFFICERS:
                if any(area in unit_addr for area in off['areas']):
                    st.markdown(f"""
                    <div class="officer-card {off['class']}" style="background:#000;">
                        <small style="color:#39ff14; font-weight:800;">PHỤ TRÁCH TRỰC TIẾP</small>
                        <h4 style="margin:5px 0; color:{off['color']}; font-size:1.4rem;">{off['name']}</h4>
                        <a href="tel:{off['phone'].replace('.','')}" style="text-decoration:none; color:white; font-weight:800; font-size:1.4rem;">📱 {off['phone']}</a>
                    </div>
                    """, unsafe_allow_html=True)

st.markdown("<br><hr><center style='color:#94a3b8; font-size:0.8rem;'>© 2026 BHXH CƠ SỞ THUẬN AN | Elite Digital Hub v12.5</center>", unsafe_allow_html=True)
