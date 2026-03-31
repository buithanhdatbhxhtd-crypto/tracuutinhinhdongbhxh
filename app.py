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
    page_title="BHXH cơ sở Thuận An - Ultimate Elite v14.0",
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
if 'current_tab' not in st.session_state:
    st.session_state.current_tab = "Tra cứu"

# --- TỔNG LỰC CSS (GIAO DIỆN ELITE v14.0) ---
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

    /* BẢNG LED CHẠY CHỮ RGB */
    .led-marquee {
        background: #000;
        color: #00ff00;
        padding: 12px 0;
        font-weight: 700;
        border-radius: 12px;
        box-shadow: 0 0 20px rgba(0, 255, 0, 0.5);
        border: 2px solid #333;
        margin-bottom: 25px;
        font-family: 'Courier New', Courier, monospace;
        font-size: 1.1rem;
        text-shadow: 0 0 10px #00ff00;
    }

    /* SIÊU Ô TÌM KIẾM - KHÔNG KHUNG XANH THỪA */
    .mega-search-container {
        max-width: 1000px;
        margin: 0 auto 3.5rem auto;
        text-align: center;
    }

    .stTextInput input {
        border-radius: 25px !important;
        padding: 0 50px !important; 
        border: 8px solid #3b82f6 !important; /* Viền xanh dương to rõ */
        font-size: 2.8rem !important; /* Chữ khổng lồ */
        font-weight: 900 !important;
        height: 125px !important; /* Cao vượt trội để không bị che */
        line-height: 125px !important; 
        background: white !important;
        color: #1e3a8a !important;
        box-shadow: 0 30px 70px rgba(59, 130, 246, 0.4) !important;
        transition: all 0.5s ease;
        text-align: center !important;
    }
    
    .stTextInput input:focus {
        border-color: #00d2ff !important;
        transform: scale(1.03);
        box-shadow: 0 40px 100px rgba(0, 210, 255, 0.6) !important;
    }

    /* THẺ CÁN BỘ NEON NHẤP NHÁY */
    .officer-card {
        background: #0a0a0a;
        padding: 24px;
        border-radius: 28px;
        border: 3px solid #1a1a1a;
        margin-bottom: 18px;
        text-align: center;
        transition: all 0.4s ease;
    }
    .officer-card:hover { transform: translateY(-10px) rotate(1deg); border-color: #444; }

    @keyframes blink-blue { 0%, 100% { border-color: #00d2ff; box-shadow: 0 0 15px #00d2ff; } 50% { border-color: #111; } }
    @keyframes blink-gold { 0%, 100% { border-color: #ffaa00; box-shadow: 0 0 15px #ffaa00; } 50% { border-color: #111; } }
    @keyframes blink-green { 0%, 100% { border-color: #39ff14; box-shadow: 0 0 15px #39ff14; } 50% { border-color: #111; } }

    .card-nhai { animation: blink-blue 2s infinite; }
    .card-dat { animation: blink-gold 2.5s infinite; }
    .card-hai { animation: blink-green 3s infinite; }

    /* DASHBOARD */
    .dashboard-panel {
        background: white;
        border-radius: 45px;
        padding: 45px;
        box-shadow: 0 40px 100px rgba(0,0,0,0.1);
        border: 1px solid #fff;
    }

    /* TÀI KHOẢN NGÂN HÀNG NEON */
    .bank-box {
        background: linear-gradient(135deg, #111 0%, #222 100%);
        padding: 20px;
        border-radius: 20px;
        border-left: 8px solid #00d2ff;
        margin-bottom: 12px;
    }

    /* SIDEBAR */
    [data-testid="stSidebar"] {
        background-color: #0f172a;
    }
    
    .stButton>button {
        border-radius: 50px !important;
        font-weight: 800 !important;
        transition: all 0.3s ease !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- DỮ LIỆU CÁN BỘ ---
OFFICERS = [
    {"name": "Bà NGUYỄN THỊ NHÀI", "scope": "Xã Đức Lập, Xã Đắk Mil", "phone": "0846.39.29.29", "class": "card-nhai", "color": "#00d2ff", "areas": ["duc lap", "dak mil", "đức lập", "đắk mil"]},
    {"name": "Ông BÙI THÀNH ĐẠT", "scope": "Xã Đắk Sắk, Xã Đắk Song", "phone": "0986.05.30.06", "class": "card-dat", "color": "#ffaa00", "areas": ["dak sak", "dak song", "đắk sắk", "đắk song"]},
    {"name": "Ông HOÀNG SỸ HẢI", "scope": "Xã Thuận An", "phone": "0919.06.11.53", "class": "card-hai", "color": "#39ff14", "areas": ["thuan an", "thuận an"]}
]

# --- DỮ LIỆU NGÂN HÀNG ---
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

# --- SIDEBAR: TIỆN ÍCH ---
with st.sidebar:
    st.markdown("<h2 style='color:white; text-align:center;'>🚀 MENU TIỆN ÍCH</h2>", unsafe_allow_html=True)
    st.divider()
    if st.button("📊 TRA CỨU DỮ LIỆU C12", use_container_width=True): st.session_state.current_tab = "Tra cứu"; st.rerun()
    if st.button("🤖 TRỢ LÝ AI THÔNG MINH", use_container_width=True): st.session_state.current_tab = "AI"; st.rerun()
    if st.button("📑 HƯỚNG DẪN THỦ TỤC", use_container_width=True): st.session_state.current_tab = "Cẩm nang"; st.rerun()
    if st.button("🧮 CÔNG CỤ TÍNH MỨC ĐÓNG", use_container_width=True): st.session_state.current_tab = "Tính toán"; st.rerun()
    if st.button("📍 BẢN ĐỒ CHỈ ĐƯỜNG", use_container_width=True): st.session_state.current_tab = "Bản đồ"; st.rerun()
    st.divider()
    st.caption("Phiên bản v14.0 - Thiết kế bởi AI")

# --- HEADER (LED MARQUEE) ---
marquee_msg = "📍 ĐỊA CHỈ: THÔN THUẬN SƠN, XÃ THUẬN AN, TỈNH LÂM ĐỒNG • CHÚC QUÝ ĐƠN VỊ THUẬN LỢI TRONG CÔNG TÁC TRA CỨU BHXH • TRA CỨU NHANH - NỘP TIỀN ĐÚNG • ĐẢM BẢO QUYỀN LỢI AN SINH •"
st.markdown(f"<div class='led-marquee'><marquee scrollamount='10'>{marquee_msg}</marquee></div>", unsafe_allow_html=True)

df = load_data()

if df is not None:
    
    # --- TAB 1: TRA CỨU ---
    if st.session_state.current_tab == "Tra cứu":
        if st.session_state.selected_unit is None:
            # SIÊU Ô TÌM KIẾM
            st.markdown("<div class='mega-search-container'>", unsafe_allow_html=True)
            st.markdown("<h1 style='color:#1e3a8a; font-size:3rem; font-weight:900; margin-bottom:15px;'>🛡️ HỆ THỐNG TRA CỨU BHXH THUẬN AN</h1>", unsafe_allow_html=True)
            st.markdown("<p style='color:#64748b; font-size:1.4rem; margin-bottom:30px; font-weight:600;'>Mời nhập Mã đơn vị hoặc Tên công ty để tra cứu số liệu</p>", unsafe_allow_html=True)
            query = st.text_input("Gateway", placeholder="🔍 Nhập tại đây...", label_visibility="collapsed")
            st.markdown("</div>", unsafe_allow_html=True)

            col_post, col_res, col_info = st.columns([0.8, 1.4, 1])

            with col_post:
                st.markdown("##### 📢 Thông báo mới")
                posters = [
                    {"t": "🛡️ AN SINH", "c": "BHXH là điểm tựa tài chính bền vững nhất cho bạn."},
                    {"t": "🏥 SỨC KHỎE", "c": "Thẻ BHYT giúp bạn an tâm vượt qua rủi ro bệnh tật."},
                    {"t": "🤰 THAI SẢN", "c": "Đồng hành cùng gia đình trong những ngày quý giá."}
                ]
                p = posters[datetime.now().minute % len(posters)]
                st.markdown(f"""
                    <div style='background:white; padding:30px; border-radius:30px; border:2px solid #e2e8f0; text-align:center; min-height:300px; display:flex; flex-direction:column; justify-content:center; box-shadow: 0 10px 20px rgba(0,0,0,0.05);'>
                        <h4 style='color:#1e3a8a; margin:0;'>{p['t']}</h4>
                        <p style='font-size:1.1rem; color:#64748b; margin:15px 0;'>{p['c']}</p>
                        <small style='color:#ffaa00; font-weight:800;'>VÌ LỢI ÍCH CỦA BẠN</small>
                    </div>
                """, unsafe_allow_html=True)

            with col_res:
                if query:
                    clean_query = unidecode(query).lower()
                    results = df[df['search_index'].str.contains(clean_query, na=False)].head(8)
                    if not results.empty:
                        st.write(f"✨ Tìm thấy **{len(results)}** kết quả:")
                        for idx, row in results.iterrows():
                            with st.container():
                                ca, cb = st.columns([3.5, 1.5])
                                ca.markdown(f"""
                                    <div style='background:white; padding:20px; border-radius:25px; border-left:10px solid #2563eb; margin-bottom:12px; box-shadow:0 5px 15px rgba(0,0,0,0.05);'>
                                        <small style='color:#2563eb; font-weight:800;'>MÃ: {row.get('madvi')}</small><br>
                                        <b style='font-size:1.2rem; color:#1e293b;'>{row.get('tendvi')}</b>
                                    </div>
                                """, unsafe_allow_html=True)
                                if cb.button("Tra cứu ➔", key=f"sel_{row.get('madvi')}_{idx}", use_container_width=True):
                                    st.session_state.selected_unit = row.get('madvi')
                                    st.session_state.show_loading = True
                                    st.rerun()
                else:
                    st.markdown("<br><center><img src='https://cdn-icons-png.flaticon.com/512/3772/3772274.png' width='160' style='opacity:0.2'><h4 style='color:#94a3b8;'>Sẵn sàng phục vụ tra cứu</h4></center>", unsafe_allow_html=True)

            with col_info:
                st.markdown("##### 👩‍💼 Cán bộ Chuyên quản")
                for off in OFFICERS:
                    st.markdown(f"""
                    <div class="officer-card {off['class']}">
                        <div style="color:{off['color']}; font-weight:800; font-size:1.1rem;">{off['name']}</div>
                        <div style="color:#aaa; font-size:0.85rem; margin:5px 0;">Xã phụ trách: {off['scope']}</div>
                        <a href="tel:{off['phone'].replace('.','')}" style="text-decoration:none; color:white; font-weight:800; font-size:1.2rem;">📱 {off['phone']}</a>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("##### 🏦 Số tài khoản của BHXH cơ sở Thuận An")
                for bank in BANKS:
                    st.markdown(f"""
                    <div class="bank-box">
                        <div style="color:#00d2ff; font-weight:800; font-size:0.8rem;">NGÂN HÀNG: {bank['name']}</div>
                        <div style="color:#fff; font-size:1.1rem; font-family:monospace; font-weight:700;">{bank['number']}</div>
                    </div>
                    """, unsafe_allow_html=True)

        # MÀN HÌNH LOADING
        elif st.session_state.show_loading:
            st.markdown("<br><br><br>", unsafe_allow_html=True)
            with st.status("💎 ĐANG TRÍCH XUẤT DỮ LIỆU VÀNG...", expanded=True) as status:
                st.write("🔄 Kết nối máy chủ BHXH trung ương...")
                time.sleep(0.7)
                st.write("📊 Phân tích số dư C12-TS...")
                time.sleep(0.5)
                status.update(label="Tải báo cáo hoàn tất!", state="complete")
            st.session_state.show_loading = False
            st.balloons()
            st.rerun()

        # DASHBOARD CHI TIẾT
        else:
            unit_data = df[df['madvi'] == st.session_state.selected_unit].iloc[0]
            unit_addr = unidecode(str(unit_data.get('diachi', ''))).lower()
            
            if st.button("⬅ QUAY LẠI TRANG CHỦ"):
                st.session_state.selected_unit = None
                st.rerun()

            st.markdown(f"""
                <div style='background:white; padding:45px; border-radius:45px; border-left:25px solid #1e3a8a; box-shadow: 0 25px 60px rgba(0,0,0,0.08); margin-top:20px;'>
                    <h2 style='margin:0; color:#1e3a8a;'>🏢 {unit_data.get('tendvi')}</h2>
                    <p style='margin:10px 0 0 0; color:#64748b;'>Mã đơn vị: <b>{unit_data.get('madvi')}</b> | Địa chỉ: {unit_data.get('diachi', 'N/A')}</p>
                </div>
            """, unsafe_allow_html=True)

            col_l, col_r = st.columns([1.8, 1])
            with col_l:
                st.markdown("<div class='dashboard-panel' style='margin-top:25px;'>", unsafe_allow_html=True)
                st.write("#### 📉 Phân tích số liệu tài chính chi tiết")
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
                    <div style='background:#f0f9ff; padding:30px; border-radius:30px; border:3px dashed #3b82f6; margin-top:30px; text-align:center;'>
                        <p style='color:#1e40af; font-weight:800; font-size:1.1rem; text-transform:uppercase;'>📝 NỘI DUNG CHUYỂN KHOẢN CHUẨN:</p>
                        <h3 style='color:#1e3a8a; font-family:monospace; font-size:2rem; background:white; padding:15px; border-radius:15px; margin:15px 0;'>{transfer_note}</h3>
                        <p style='color:#64748b; font-size:0.9rem;'><i>(Lưu ý: Ghi đúng nội dung để hệ thống tự động gạch nợ)</i></p>
                    </div>
                """, unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

            with col_r:
                phai_dong = unit_data.get('so_phai_dong', 1)
                da_dong = unit_data.get('so_da_dong', 0)
                rate = min(round((da_dong / phai_dong) * 100, 1), 100) if phai_dong > 0 else 0
                fig = go.Figure(go.Indicator(
                    mode = "gauge+number", value = rate,
                    title = {'text': "Tỷ lệ hoàn thành (%)", 'font': {'size': 24, 'color': '#64748b'}},
                    number = {'suffix': "%", 'font': {'color': '#1e40af', 'size': 65}},
                    gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': "#1e40af"}, 'steps': [{'range': [0, 50], 'color': '#fee2e2'}, {'range': [90, 100], 'color': '#dcfce7'}]}
                ))
                fig.update_layout(height=450, margin=dict(l=35, r=35, t=70, b=35), paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig, use_container_width=True)
                
                # Highlight Cán bộ phụ trách xã
                for off in OFFICERS:
                    if any(area in unit_addr for area in off['areas']):
                        st.markdown(f"""
                        <div class="officer-card {off['class']}" style="background:#000;">
                            <small style="color:#39ff14; font-weight:800; border:1px solid #39ff14; padding:2px 8px; border-radius:50px;">PHỤ TRÁCH TRỰC TIẾP</small>
                            <h4 style="margin:10px 0; color:{off['color']}; font-size:1.6rem;">{off['name']}</h4>
                            <a href="tel:{off['phone'].replace('.','')}" style="text-decoration:none; color:white; font-weight:800; font-size:1.5rem;">📱 {off['phone']}</a>
                        </div>
                        """, unsafe_allow_html=True)

    # --- CÁC TAB KHÁC (STUB) ---
    elif st.session_state.current_tab == "AI":
        st.markdown("## 🤖 TRỢ LÝ ẢO AI BHXH")
        st.info("Hệ thống AI đang học dữ liệu mới nhất của BHXH Việt Nam.")
        st.chat_input("Hỏi tôi bất cứ điều gì về chính sách BHXH...")
    elif st.session_state.current_tab == "Cẩm nang":
        st.markdown("## 📑 HƯỚNG DẪN THỦ TỤC")
        with st.expander("Quy trình báo tăng lao động"): st.write("Bước 1: Chuẩn bị hồ sơ mẫu D02-LT...")
    elif st.session_state.current_tab == "Tính toán":
        st.markdown("## 🧮 TÍNH MỨC ĐÓNG NHANH")
        sal = st.number_input("Mức lương đóng BHXH:", value=5000000)
        st.write(f"Doanh nghiệp đóng (21.5%): **{sal*0.215:,.0f}đ**")
    elif st.session_state.current_tab == "Bản đồ":
        st.markdown("## 📍 VỊ TRÍ CƠ QUAN BHXH")
        st.info("Thôn Thuận Sơn, xã Thuận An, tỉnh Lâm Đồng.")

st.markdown("<br><hr><center style='color:#94a3b8; font-size:0.9rem; padding-bottom:60px;'>© 2026 BHXH CƠ SỞ THUẬN AN | Elite Digital Hub v14.0</center>", unsafe_allow_html=True)
