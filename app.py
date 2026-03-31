import streamlit as st
import pandas as pd
import numpy as np
import os
import plotly.graph_objects as go
from unidecode import unidecode
import time
from datetime import datetime
import google.generativeai as genai
import base64
import streamlit.components.v1 as components

# --- CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="BHXH Thuận An - v21.0 Radiant Elite",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CẤU HÌNH AI GEMINI (MODEL STABLE) ---
api_key = st.secrets.get("GOOGLE_API_KEY", os.environ.get("GOOGLE_API_KEY", ""))
if api_key:
    try:
        genai.configure(api_key=api_key)
    except: pass

def get_ai_response(prompt):
    if not api_key: return "⚠️ **Chưa cấu hình API Key.**"
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        full_prompt = f"Bạn là chuyên gia tư vấn BHXH Thuận An. Hãy trả lời: {prompt}"
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        return f"⚠️ **Lỗi:** {str(e)[:100]}"

# --- KHỞI TẠO STATE ---
if 'selected_unit' not in st.session_state:
    st.session_state.selected_unit = None
if 'current_tab' not in st.session_state:
    st.session_state.current_tab = "📊 Tra cứu C12-TS"
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if 'active_pdf' not in st.session_state:
    st.session_state.active_pdf = None
if 'search_query' not in st.session_state:
    st.session_state.search_query = ""
if 'welcome_done' not in st.session_state:
    st.session_state.welcome_done = False

# --- TỔNG LỰC CSS (GIAO DIỆN ELITE v21.0 - GLOSSY & MODERN) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    :root {
        --primary: #1e3a8a;
        --secondary: #2563eb;
        --accent: #0ea5e9;
        --neon-blue: #00d2ff;
        --neon-green: #10b981;
        --glass: rgba(255, 255, 255, 0.8);
    }

    * { font-family: 'Plus Jakarta Sans', sans-serif; }
    
    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
    }

    /* --- SIDEBAR SIÊU RÕ NÉT --- */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e3a8a 100%) !important;
    }
    [data-testid="stSidebar"] .stRadio label p {
        color: #ffffff !important;
        font-size: 1.2rem !important;
        font-weight: 800 !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5) !important;
    }

    /* BẢNG LED RGB */
    .led-marquee {
        background: #000;
        color: #00ff00;
        padding: 12px 0;
        font-weight: 800;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0, 255, 0, 0.2);
        border: 2px solid #333;
        margin-bottom: 25px;
        font-family: 'Courier New', Courier, monospace;
        font-size: 1.3rem;
        text-shadow: 0 0 10px #00ff00;
    }

    /* SIÊU Ô TÌM KIẾM GATEWAY */
    .gateway-container {
        max-width: 1000px;
        margin: 0 auto 1rem auto;
        text-align: center;
    }
    .stTextInput input {
        border-radius: 20px !important;
        padding: 15px 45px 15px 85px !important; 
        border: 10px solid var(--secondary) !important;
        font-size: 2.5rem !important; 
        font-weight: 900 !important;
        height: 130px !important; 
        background: white url('https://cdn-icons-png.flaticon.com/512/622/622669.png') no-repeat 25px center !important;
        background-size: 40px !important;
        color: var(--primary) !important;
        box-shadow: 0 30px 60px rgba(59, 130, 246, 0.25) !important;
    }

    /* NÚT TÌM KIẾM MAIN */
    .search-main-btn > div > button {
        background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%) !important;
        color: white !important;
        font-size: 1.4rem !important;
        height: 65px !important;
        width: 100% !important;
        border-radius: 50px !important;
        border: none !important;
        box-shadow: 0 10px 25px rgba(30, 58, 138, 0.3) !important;
    }

    /* --- DASHBOARD ELITE STYLE --- */
    .unit-header-card {
        background: var(--glass);
        backdrop-filter: blur(15px);
        padding: 40px;
        border-radius: 40px;
        border: 2px solid white;
        box-shadow: 0 25px 80px rgba(0,0,0,0.08);
        margin-top: 10px;
        position: relative;
        overflow: hidden;
    }
    .unit-header-card::before {
        content: ""; position: absolute; top: 0; left: 0; width: 8px; height: 100%;
        background: linear-gradient(to bottom, #1e3a8a, #00d2ff);
    }

    .crystal-card {
        background: white;
        padding: 25px;
        border-radius: 30px;
        border: 1px solid #f1f5f9;
        box-shadow: 0 15px 35px rgba(0,0,0,0.04);
        transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        text-align: center;
    }
    .crystal-card:hover {
        transform: translateY(-10px) scale(1.02);
        box-shadow: 0 30px 60px rgba(37, 99, 235, 0.15);
        border-color: var(--secondary);
    }

    .metric-value {
        font-size: 2rem;
        font-weight: 800;
        color: var(--primary);
        margin: 10px 0;
    }
    .metric-label {
        font-size: 0.9rem;
        font-weight: 700;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* HIỆU ỨNG NHẤP NHÁY CHÀO MỪNG */
    @keyframes welcomeGlow {
        0% { text-shadow: 0 0 5px #fff; }
        50% { text-shadow: 0 0 25px #00d2ff, 0 0 40px #2563eb; }
        100% { text-shadow: 0 0 5px #fff; }
    }
    .welcome-text {
        font-size: 2.2rem;
        font-weight: 900;
        color: #1e3a8a;
        animation: welcomeGlow 2s infinite;
        text-align: center;
        margin-bottom: 20px;
    }

    .stButton>button {
        border-radius: 50px !important;
        font-weight: 800 !important;
        text-transform: uppercase;
        padding: 0.6rem 2rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ĐỒNG HỒ REAL-TIME (JS) ---
def live_clock():
    components.html("""
    <div id="clock-crystal" style="
        font-family: 'Plus Jakarta Sans', sans-serif;
        background: rgba(255, 255, 255, 0.15);
        color: white;
        padding: 20px;
        border-radius: 25px;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.3);
        backdrop-filter: blur(15px);
        box-shadow: 0 8px 32px rgba(0,0,0,0.2);
    ">
        <div id="day-val" style="font-size: 1rem; font-weight: 700; opacity: 0.9; margin-bottom: 5px; color: #00d2ff;"></div>
        <div id="time-val" style="font-size: 2.2rem; font-weight: 900; letter-spacing: 2px;"></div>
    </div>
    <script>
        function updateClock() {
            const now = new Date();
            const dateOptions = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
            document.getElementById('day-val').innerText = now.toLocaleDateString('vi-VN', dateOptions).toUpperCase();
            const hours = String(now.getHours()).padStart(2, '0');
            const minutes = String(now.getMinutes()).padStart(2, '0');
            const seconds = String(now.getSeconds()).padStart(2, '0');
            document.getElementById('time-val').innerText = hours + ":" + minutes + ":" + seconds;
        }
        setInterval(updateClock, 1000);
        updateClock();
    </script>
    """, height=150)

# --- DỮ LIỆU CÁN BỘ ---
OFFICERS = [
    {"name": "Bà NGUYỄN THỊ NHÀI", "communes": "Xã Đức Lập, Xã Đắk Mil", "keywords": ["duc lap", "đức lập", "dak mil", "đắk mil"], "phone": "0846.39.29.29", "zalo": "https://zalo.me/0846392929", "color": "#00d2ff"},
    {"name": "Ông BÙI THÀNH ĐẠT", "communes": "Xã Đắk Sắk, Xã Đắk Song", "keywords": ["dak sak", "đắk sắk", "dak song", "đắk song"], "phone": "0986.05.30.06", "zalo": "https://zalo.me/0986053006", "color": "#f59e0b"},
    {"name": "Ông HOÀNG SỸ HẢI", "communes": "Xã Thuận An", "keywords": ["thuan an", "thuận an"], "phone": "0919.06.11.53", "zalo": "https://zalo.me/0919061153", "color": "#10b981"}
]

# --- TẢI DỮ LIỆU ---
@st.cache_data
def load_data():
    try:
        files = [f for f in os.listdir('.') if f.lower().startswith('c12')]
        if not files: return None
        target = files[0]
        df = pd.read_csv(target) if target.lower().endswith('.csv') else pd.read_excel(target)
        if df is not None:
            df.columns = [unidecode(str(c)).lower().strip().replace(' ', '_') for c in df.columns]
            if 'madvi' in df.columns: df['madvi'] = df['madvi'].astype(str).str.strip()
            df['search_index'] = df.apply(lambda x: unidecode(str(x.get('madvi', '')) + " " + str(x.get('tendvi', ''))).lower(), axis=1)
            return df
    except: return None

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<h1 style='text-align:center;'>🛡️ QUANTUM</h1>", unsafe_allow_html=True)
    st.divider()
    menu = ["📊 Tra cứu C12-TS", "🤖 Trợ lý AI Gemini", "📂 Thư viện Văn bản", "📑 Cẩm nang Nghiệp vụ", "🧮 Máy tính BHXH", "📍 Liên hệ BHXH"]
    st.session_state.current_tab = st.radio("MENU", menu, label_visibility="collapsed")
    st.divider()
    live_clock()
    st.caption("v21.0 Radiant Elite | 🛡️ BHXH Thuận An")

# --- HEADER LED ---
marquee_msg = "💎 CHÀO MỪNG QUÝ ĐƠN VỊ ĐẾN VỚI HỆ THỐNG TRA CỨU BHXH THUẬN AN PHIÊN BẢN v21.0 RADIANT ELITE • CẢM ƠN QUÝ ĐƠN VỊ ĐÃ TIN DÙNG •"
st.markdown(f"<div class='led-marquee'><marquee scrollamount='10'>{marquee_msg}</marquee></div>", unsafe_allow_html=True)

df = load_data()

if df is not None:
    # --- TAB 1: TRA CỨU ---
    if st.session_state.current_tab == "📊 Tra cứu C12-TS":
        if st.session_state.selected_unit is None:
            st.markdown("<div class='gateway-container'>", unsafe_allow_html=True)
            st.markdown("<h1 style='color:#1e3a8a; font-size:3.8rem; font-weight:900;'>🛡️ CỔNG TRA CỨU DỮ LIỆU</h1>", unsafe_allow_html=True)
            st.markdown("<p style='color:#64748b; font-size:1.6rem; font-weight:700;'>NHẬP MÃ ĐƠN VỊ HOẶC TÊN CÔNG TY</p>", unsafe_allow_html=True)
            user_input = st.text_input("Gateway", placeholder="Gõ tìm kiếm tại đây...", label_visibility="collapsed")
            st.markdown("</div>", unsafe_allow_html=True)
            
            _, btn_col, _ = st.columns([1, 1, 1])
            with btn_col:
                st.markdown('<div class="search-main-btn">', unsafe_allow_html=True)
                if st.button("🔍 TÌM KIẾM DỮ LIỆU", use_container_width=True):
                    st.session_state.search_query = user_input
                st.markdown('</div>', unsafe_allow_html=True)

            col_news, col_res, col_off = st.columns([0.8, 1.4, 1.1])
            with col_news:
                st.markdown("##### 📢 TIN TỨC")
                st.markdown("<div class='crystal-card' style='min-height:350px; display:flex; flex-direction:column; justify-content:center;'><h4 style='color:#1e3a8a;'>🛡️ AN SINH</h4><p>Tham gia BHXH là hành trình xây dựng tương lai vững chắc.</p><hr><small style='color:#f59e0b; font-weight:800;'>BHXH THUẬN AN</small></div>", unsafe_allow_html=True)

            with col_res:
                final_query = st.session_state.search_query if st.session_state.search_query else user_input
                if final_query:
                    results = df[df['search_index'].str.contains(unidecode(final_query).lower(), na=False)].head(8)
                    if not results.empty:
                        for idx, row in results.iterrows():
                            with st.container():
                                ca, cb = st.columns([3.5, 1.5])
                                ca.markdown(f"<div class='crystal-card' style='padding:20px; border-left:10px solid #2563eb; text-align:left;'><small style='color:#2563eb; font-weight:800;'>MÃ: {row.get('madvi')}</small><br><b style='font-size:1.2rem; color:#1e293b;'>{row.get('tendvi')}</b></div>", unsafe_allow_html=True)
                                if cb.button("XÁC NHẬN ➔", key=f"sel_{row.get('madvi')}_{idx}", use_container_width=True):
                                    st.session_state.selected_unit = row.get('madvi')
                                    st.session_state.welcome_done = False
                                    st.rerun()
                    else: st.error("Không tìm thấy đơn vị.")
                else: st.markdown("<br><center><img src='https://cdn-icons-png.flaticon.com/512/3772/3772274.png' width='160' style='opacity:0.2'></center>", unsafe_allow_html=True)

            with col_off:
                st.markdown("##### 👨‍💼 LIÊN HỆ CÁN BỘ")
                for off in OFFICERS:
                    st.markdown(f"""
                    <div class='crystal-card' style='margin-bottom: 15px; padding: 15px;'>
                        <div style='color:var(--secondary); font-weight: 800; font-size: 0.8rem;'>{off['communes']}</div>
                        <div style='color:var(--primary); font-weight: 900; font-size: 1.1rem; margin: 3px 0;'>{off['name']}</div>
                        <a href='tel:{off['phone'].replace('.','')}' style='text-decoration:none; color:var(--primary); font-weight: 800;'>📱 {off['phone']}</a><br>
                        <a href='{off['zalo']}' target='_blank' style='background:#0068ff; color:white; padding:5px 15px; border-radius:50px; text-decoration:none; display:inline-block; margin-top: 5px; font-weight: 900; font-size: 0.7rem;'>💬 CHAT ZALO</a>
                    </div>
                    """, unsafe_allow_html=True)

        else:
            # --- DASHBOARD CHI TIẾT (PHIÊN BẢN ELITE RADIANT) ---
            if not st.session_state.welcome_done:
                st.balloons()
                st.session_state.welcome_done = True
            
            unit_data = df[df['madvi'] == st.session_state.selected_unit].iloc[0]
            unit_addr = unidecode(str(unit_data.get('diachi', ''))).lower()
            
            if st.button("⬅ QUAY LẠI TRANG TÌM KIẾM"): 
                st.session_state.selected_unit = None
                st.rerun()
            
            st.markdown(f"""
                <div class='welcome-text'>✨ CHÀO MỪNG QUÝ ĐƠN VỊ ĐẾN VỚI HỆ THỐNG ✨</div>
                <div class='unit-header-card'>
                    <div style='display: flex; align-items: center;'>
                        <img src='https://cdn-icons-png.flaticon.com/512/3061/3061341.png' width='70' style='margin-right: 25px;'>
                        <div>
                            <h1 style='margin:0; color:#1e3a8a; font-size: 3rem;'>{unit_data.get('tendvi')}</h1>
                            <p style='margin:5px 0; color:#64748b; font-size: 1.2rem;'>Mã đơn vị: <b style='color:#2563eb;'>{unit_data.get('madvi')}</b> | Địa chỉ: {unit_data.get('diachi', 'N/A')}</p>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            cl, cr = st.columns([1.8, 1])
            with cl:
                st.markdown("<div class='unit-header-card' style='margin-top: 25px;'>", unsafe_allow_html=True)
                st.write("#### 📊 PHÂN TÍCH TÀI CHÍNH CHI TIẾT")
                m1, m2, m3 = st.columns(3)
                with m1: st.markdown(f"<div class='crystal-card'><div class='metric-label'>Đầu kỳ</div><div class='metric-value'>{unit_data.get('tien_dau_ky', 0):,.0f}đ</div></div>", unsafe_allow_html=True)
                with m2: st.markdown(f"<div class='crystal-card'><div class='metric-label'>Phải đóng</div><div class='metric-value'>{unit_data.get('so_phai_dong', 0):,.0f}đ</div></div>", unsafe_allow_html=True)
                with m3: st.markdown(f"<div class='crystal-card'><div class='metric-label'>Điều chỉnh</div><div class='metric-value'>{unit_data.get('dieu_chinh_ky_truoc', 0):,.0f}đ</div></div>", unsafe_allow_html=True)
                
                st.write("<br>", unsafe_allow_html=True)
                m4, m5, m6 = st.columns(3)
                with m4: st.markdown(f"<div class='crystal-card'><div class='metric-label'>Đã đóng</div><div class='metric-value' style='color:#10b981;'>{unit_data.get('so_da_dong', 0):,.0f}đ</div></div>", unsafe_allow_html=True)
                with m5: st.markdown(f"<div class='crystal-card'><div class='metric-label'>Lệch</div><div class='metric-value' style='color:#ef4444;'>{unit_data.get('so_bi_lech', 0):,.0f}đ</div></div>", unsafe_allow_html=True)
                debt = unit_data.get('tien_cuoi_ky', 0)
                status_color = "#ef4444" if debt > 0 else "#10b981"
                status_label = "CÒN NỢ" if debt > 0 else "DƯ CÓ"
                with m6: st.markdown(f"<div class='crystal-card' style='border: 2px solid {status_color};'><div class='metric-label'>{status_label}</div><div class='metric-value' style='color:{status_color};'>{abs(debt):,.0f}đ</div></div>", unsafe_allow_html=True)
                
                st.info(f"📝 NỘI DUNG CK: {unit_data.get('madvi')} {unit_data.get('tendvi')} đóng bhxh tháng {datetime.now().month} năm {datetime.now().year}")
                st.markdown("</div>", unsafe_allow_html=True)
            
            with cr:
                rate = min(round((unit_data.get('so_da_dong', 0) / unit_data.get('so_phai_dong', 1)) * 100, 1), 100)
                fig = go.Figure(go.Indicator(
                    mode="gauge+number", value=rate, 
                    title={'text': "TỶ LỆ HOÀN THÀNH (%)", 'font': {'size': 20, 'color': '#1e3a8a', 'weight': 'bold'}},
                    number={'suffix': "%", 'font': {'color': '#2563eb', 'size': 60}},
                    gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#2563eb"}}
                ))
                fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=450)
                st.plotly_chart(fig, use_container_width=True)
                
                # CHUYÊN QUẢN TRỰC TIẾP
                for off in OFFICERS:
                    if any(kw in unit_addr for kw in off['keywords']):
                        st.markdown(f"""
                        <div class='crystal-card' style='background: #000; color: white;'>
                            <small style='color:#39ff14; font-weight:900;'>CHUYÊN QUẢN PHỤ TRÁCH</small>
                            <h3 style='color:{off['color']}; margin:10px 0;'>{off['name']}</h3>
                            <a href='tel:{off['phone'].replace('.','')}' style='color:white; font-size: 1.5rem; text-decoration:none; font-weight:800;'>📱 {off['phone']}</a><br>
                            <a href='{off['zalo']}' target='_blank' style='background:#0068ff; color:white; padding:10px 30px; border-radius:50px; text-decoration:none; display:inline-block; margin-top:15px; font-weight:800;'>GỬI TIN NHẮN ZALO</a>
                        </div>
                        """, unsafe_allow_html=True)

    # --- CÁC TAB KHÁC ---
    elif st.session_state.current_tab == "🤖 Trợ lý AI Gemini":
        st.markdown("## 🧠 TRỢ LÝ AI THÔNG MINH")
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]): st.markdown(msg["content"])
        if prompt := st.chat_input("Hỏi tôi bất cứ điều gì..."):
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            with st.chat_message("assistant"):
                with st.spinner("AI đang truy xuất dữ liệu..."):
                    resp = get_ai_response(prompt)
                    st.markdown(resp); st.session_state.chat_history.append({"role": "assistant", "content": resp})

    elif st.session_state.current_tab == "📂 Thư viện Văn bản":
        st.markdown("## 📂 THƯ VIỆN VĂN BẢN KỸ THUẬT SỐ")
        pdfs = [f for f in os.listdir('.') if f.lower().endswith('.pdf')]
        if not pdfs: st.warning("Hãy tải file .pdf lên thư mục GitHub.")
        else:
            c1, c2 = st.columns([1, 2.5])
            with c1:
                for f in pdfs:
                    if st.button(f"📄 {f}", use_container_width=True): st.session_state.active_pdf = f
            with c2:
                if st.session_state.active_pdf:
                    st.success(f"📌 ĐANG XEM: {st.session_state.active_pdf}")
                    with open(st.session_state.active_pdf, "rb") as f:
                        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
                        st.markdown(f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800px" style="border:10px solid white; border-radius:30px; box-shadow:0 20px 50px rgba(0,0,0,0.1);"></iframe>', unsafe_allow_html=True)

st.markdown("<br><hr><center style='color:#94a3b8; font-size:0.9rem; padding-bottom:60px;'>© 2026 BHXH CƠ SỞ THUẬN AN | Elite Quantum Nexus v21.0</center>", unsafe_allow_html=True)
