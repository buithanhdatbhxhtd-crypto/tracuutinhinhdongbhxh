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
    page_title="BHXH Thuận An - v22.0 Ultimate Masterpiece",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CẤU HÌNH AI GEMINI (MODEL STABLE v1.5 FLASH) ---
api_key = st.secrets.get("GOOGLE_API_KEY", os.environ.get("GOOGLE_API_KEY", ""))
if api_key:
    try:
        genai.configure(api_key=api_key)
    except: pass

def get_ai_response(prompt):
    if not api_key: return "⚠️ **Chưa cấu hình API Key:** Vui lòng thêm `GOOGLE_API_KEY` vào Streamlit Secrets."
    try:
        # Model 1.5 Flash là bản ổn định nhất, phản hồi nhanh nhất hiện nay
        model = genai.GenerativeModel('gemini-1.5-flash')
        system_instruction = "Bạn là trợ lý AI cao cấp của Bảo hiểm xã hội cơ sở Thuận An, Lâm Đồng. Hãy tư vấn chính xác, ngắn gọn và tận tâm."
        full_prompt = f"{system_instruction}\n\nĐơn vị hỏi: {prompt}"
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        return f"⚠️ **Trợ lý AI đang bận:** Vui lòng thử lại sau hoặc chat Zalo cho cán bộ nhé!"

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

# --- TỔNG LỰC CSS (GIAO DIỆN MASTERPIECE v22.0) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    :root {
        --primary: #1e3a8a;
        --secondary: #2563eb;
        --accent: #0ea5e9;
        --neon-blue: #00d2ff;
        --glass: rgba(255, 255, 255, 0.85);
    }

    * { font-family: 'Plus Jakarta Sans', sans-serif; }
    
    .stApp {
        background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
    }

    /* --- SIDEBAR SIÊU RÕ NÉT (ULTRA CONTRAST) --- */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e3a8a 100%) !important;
    }
    
    /* Ép chữ danh mục thành trắng tuyết, to và có bóng đổ */
    [data-testid="stSidebar"] .stRadio label p {
        color: #ffffff !important;
        font-size: 1.3rem !important;
        font-weight: 800 !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.6) !important;
        padding: 8px 0 !important;
    }
    
    /* Tiêu đề sidebar rực rỡ */
    [data-testid="stSidebar"] h1 {
        color: white !important;
        text-shadow: 0 0 15px var(--neon-blue);
        letter-spacing: 2px;
    }

    /* BẢNG LED RGB */
    .led-marquee {
        background: #000;
        color: #39ff14;
        padding: 12px 0;
        font-weight: 800;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(57, 255, 20, 0.15);
        border: 2px solid #333;
        margin-bottom: 25px;
        font-family: 'Courier New', Courier, monospace;
        font-size: 1.35rem;
    }

    /* SIÊU Ô TÌM KIẾM GATEWAY - CĂN GIỮA TUYỆT ĐỐI */
    .gateway-container {
        max-width: 1000px;
        margin: 0 auto 1rem auto;
        text-align: center;
    }

    div[data-testid="stTextInput"] > div {
        height: auto !important;
        background: transparent !important;
        padding: 0 !important;
    }

    .stTextInput input {
        border-radius: 20px !important;
        padding: 0 45px 0 95px !important; /* Căn chỉnh cho icon kính lúp */
        border: 10px solid var(--secondary) !important;
        font-size: 3rem !important; 
        font-weight: 900 !important;
        height: 150px !important; 
        line-height: 150px !important; /* CĂN GIỮA CHỮ THEO TRỤC DỌC */
        background: white url('https://cdn-icons-png.flaticon.com/512/622/622669.png') no-repeat 30px center !important;
        background-size: 50px !important;
        color: var(--primary) !important;
        box-shadow: 0 40px 100px rgba(59, 130, 246, 0.3) !important;
        display: block !important;
    }
    
    .stTextInput input:focus {
        border-color: var(--neon-blue) !important;
        transform: scale(1.02);
    }

    /* DASHBOARD RADIANT CARDS */
    .crystal-card {
        background: white;
        padding: 30px;
        border-radius: 35px;
        box-shadow: 0 15px 45px rgba(0,0,0,0.05);
        border: 1px solid #f1f5f9;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        text-align: center;
    }
    .crystal-card:hover {
        transform: translateY(-12px);
        box-shadow: 0 35px 70px rgba(37, 99, 235, 0.12);
    }

    .metric-val { font-size: 2.2rem; font-weight: 900; color: var(--primary); margin-top: 5px; }
    .metric-lbl { font-size: 0.9rem; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 1.5px; }

    /* HIỆU ỨNG CHÀO MỪNG */
    @keyframes welcomeFlash {
        0%, 100% { color: #1e3a8a; }
        50% { color: #2563eb; text-shadow: 0 0 20px #00d2ff; }
    }
    .welcome-banner {
        font-size: 2.5rem; font-weight: 900; animation: welcomeFlash 2s infinite; text-align: center; margin-bottom: 20px;
    }

    .stButton>button {
        border-radius: 50px !important;
        font-weight: 800 !important;
        text-transform: uppercase;
        padding: 0.8rem 3rem !important;
        transition: all 0.3s ease !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ĐỒNG HỒ REAL-TIME (JS) ---
def live_clock():
    components.html("""
    <div id="clock-nexus" style="
        font-family: 'Plus Jakarta Sans', sans-serif;
        background: rgba(255, 255, 255, 0.15);
        color: white;
        padding: 20px;
        border-radius: 25px;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.3);
        backdrop-filter: blur(15px);
        box-shadow: 0 10px 35px rgba(0,0,0,0.2);
    ">
        <div id="day-str" style="font-size: 1rem; font-weight: 700; opacity: 0.9; margin-bottom: 5px; color: #00d2ff;"></div>
        <div id="time-str" style="font-size: 2.3rem; font-weight: 900; letter-spacing: 2px;"></div>
    </div>
    <script>
        function updateClock() {
            const now = new Date();
            const dateOptions = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
            document.getElementById('day-str').innerText = now.toLocaleDateString('vi-VN', dateOptions).toUpperCase();
            const h = String(now.getHours()).padStart(2, '0');
            const m = String(now.getMinutes()).padStart(2, '0');
            const s = String(now.getSeconds()).padStart(2, '0');
            document.getElementById('time-str').innerText = h + ":" + m + ":" + s;
        }
        setInterval(updateClock, 1000);
        updateClock();
    </script>
    """, height=160)

# --- DATA HUB ---
OFFICERS = [
    {"name": "Bà NGUYỄN THỊ NHÀI", "communes": "Xã Đức Lập, Xã Đắk Mil", "keywords": ["duc lap", "đức lập", "dak mil", "đắk mil"], "phone": "0846.39.29.29", "zalo": "https://zalo.me/0846392929", "color": "#00d2ff"},
    {"name": "Ông BÙI THÀNH ĐẠT", "communes": "Xã Đắk Sắk, Xã Đắk Song", "keywords": ["dak sak", "đắk sắk", "dak song", "đắk song"], "phone": "0986.05.30.06", "zalo": "https://zalo.me/0986053006", "color": "#ffaa00"},
    {"name": "Ông HOÀNG SỸ HẢI", "communes": "Xã Thuận An", "keywords": ["thuan an", "thuận an"], "phone": "0919.06.11.53", "zalo": "https://zalo.me/0919061153", "color": "#39ff14"}
]

# --- HÀM TẢI DỮ LIỆU ---
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

# --- SIDEBAR MASTER ---
with st.sidebar:
    st.markdown("<h1 style='text-align:center;'>🛡️ QUANTUM</h1>", unsafe_allow_html=True)
    st.divider()
    menu = ["📊 Tra cứu C12-TS", "🤖 Trợ lý AI Gemini", "📂 Thư viện Văn bản", "📑 Cẩm nang Nghiệp vụ", "🧮 Máy tính BHXH", "📍 Liên hệ BHXH"]
    st.session_state.current_tab = st.radio("CHỨC NĂNG HỆ THỐNG", menu, label_visibility="collapsed")
    st.divider()
    live_clock()
    st.caption("v22.0 Ultimate Masterpiece | 🛡️ BHXH Thuận An")

# --- HEADER LED ---
marquee_msg = "💎 HỆ THỐNG TRA CỨU DỮ LIỆU BHXH THUẬN AN PHIÊN BẢN v22.0 • SỰ LỰA CHỌN TIN CẬY CỦA ĐƠN VỊ • TRA CỨU NHANH - NỘP TIỀN ĐÚNG CÚ PHÁP •"
st.markdown(f"<div class='led-marquee'><marquee scrollamount='10'>{marquee_msg}</marquee></div>", unsafe_allow_html=True)

df = load_data()

if df is not None:
    # --- TAB 1: TRA CỨU ---
    if st.session_state.current_tab == "📊 Tra cứu C12-TS":
        if st.session_state.selected_unit is None:
            st.markdown("<div class='gateway-container'>", unsafe_allow_html=True)
            st.markdown("<h1 style='color:#1e3a8a; font-size:4rem; font-weight:900;'>🛡️ CỔNG TRA CỨU DỮ LIỆU</h1>", unsafe_allow_html=True)
            st.markdown("<p style='color:#64748b; font-size:1.6rem; font-weight:700;'>NHẬP MÃ ĐƠN VỊ HOẶC TÊN CÔNG TY</p>", unsafe_allow_html=True)
            user_input = st.text_input("Gateway", placeholder="Gõ tìm kiếm tại đây...", label_visibility="collapsed")
            st.markdown("</div>", unsafe_allow_html=True)
            
            _, btn_col, _ = st.columns([1, 1.2, 1])
            with btn_col:
                st.markdown('<div style="text-align:center; margin-bottom: 3rem;">', unsafe_allow_html=True)
                if st.button("🔍 TÌM KIẾM DỮ LIỆU", use_container_width=True):
                    st.session_state.search_query = user_input
                st.markdown('</div>', unsafe_allow_html=True)

            col_news, col_res, col_off = st.columns([0.8, 1.4, 1.1])
            with col_news:
                st.markdown("##### 📢 TIN TỨC")
                st.markdown("<div class='crystal-card' style='min-height:380px; display:flex; flex-direction:column; justify-content:center;'><h4 style='color:#1e3a8a;'>🛡️ AN SINH</h4><p>Hệ thống hỗ trợ đơn vị tra cứu minh bạch số tiền đóng BHXH.</p><hr><small style='color:#f59e0b; font-weight:800;'>BHXH THUẬN AN ĐỒNG HÀNH</small></div>", unsafe_allow_html=True)

            with col_res:
                final_q = st.session_state.search_query if st.session_state.search_query else user_input
                if final_q:
                    results = df[df['search_index'].str.contains(unidecode(final_q).lower(), na=False)].head(8)
                    if not results.empty:
                        for idx, row in results.iterrows():
                            with st.container():
                                ca, cb = st.columns([3.5, 1.5])
                                ca.markdown(f"<div class='crystal-card' style='padding:22px; border-left:12px solid #2563eb; text-align:left;'><small style='color:#2563eb; font-weight:800;'>MÃ: {row.get('madvi')}</small><br><b style='font-size:1.3rem; color:#1e293b;'>{row.get('tendvi')}</b></div>", unsafe_allow_html=True)
                                if cb.button("XÁC NHẬN ➔", key=f"sel_{row.get('madvi')}_{idx}", use_container_width=True):
                                    st.session_state.selected_unit = row.get('madvi'); st.session_state.welcome_done = False; st.rerun()
                    else: st.error("Không tìm thấy đơn vị.")
                else: st.markdown("<br><center><img src='https://cdn-icons-png.flaticon.com/512/3772/3772274.png' width='160' style='opacity:0.25'></center>", unsafe_allow_html=True)

            with col_off:
                st.markdown("##### 👨‍💼 LIÊN HỆ CÁN BỘ")
                for off in OFFICERS:
                    st.markdown(f"""
                    <div class='crystal-card' style='margin-bottom: 15px; padding: 18px;'>
                        <div style='color:var(--secondary); font-weight: 800; font-size: 0.85rem;'>{off['communes']}</div>
                        <div style='color:var(--primary); font-weight: 900; font-size: 1.2rem; margin: 3px 0;'>{off['name']}</div>
                        <a href='tel:{off['phone'].replace('.','')}' style='text-decoration:none; color:var(--primary); font-weight: 800; font-size: 1.2rem;'>📱 {off['phone']}</a><br>
                        <a href='{off['zalo']}' target='_blank' style='background:#0068ff; color:white; padding:8px 25px; border-radius:50px; text-decoration:none; display:inline-block; margin-top: 10px; font-weight: 900; font-size: 0.8rem;'>💬 CHAT ZALO</a>
                    </div>
                    """, unsafe_allow_html=True)

        else:
            # --- DASHBOARD CHI TIẾT MASTER ---
            if not st.session_state.welcome_done:
                st.balloons(); st.session_state.welcome_done = True
            
            unit_data = df[df['madvi'] == st.session_state.selected_unit].iloc[0]
            unit_addr = unidecode(str(unit_data.get('diachi', ''))).lower()
            
            if st.button("⬅ QUAY LẠI TRANG TÌM KIẾM"): st.session_state.selected_unit = None; st.rerun()
            
            st.markdown(f"""
                <div class='welcome-banner'>✨ CHÀO MỪNG QUÝ ĐƠN VỊ TRUY CẬP HỆ THỐNG ✨</div>
                <div class='crystal-card' style='border-left:25px solid #1e3a8a; text-align:left; background: rgba(255,255,255,0.9); backdrop-filter: blur(10px);'>
                    <h1 style='margin:0; color:#1e3a8a; font-size: 3.2rem;'>🏢 {unit_data.get('tendvi')}</h1>
                    <p style='margin:5px 0; color:#64748b; font-size: 1.3rem;'>Mã đơn vị: <b style='color:#2563eb;'>{unit_data.get('madvi')}</b> | Địa chỉ: {unit_data.get('diachi', 'N/A')}</p>
                </div>
            """, unsafe_allow_html=True)
            
            cl, cr = st.columns([1.8, 1])
            with cl:
                st.markdown("<div style='margin-top: 30px;'>", unsafe_allow_html=True)
                st.write("#### 📊 BÁO CÁO TÌNH HÌNH TÀI CHÍNH CHI TIẾT")
                m1, m2, m3 = st.columns(3)
                with m1: st.markdown(f"<div class='crystal-card'><div class='metric-lbl'>Đầu kỳ</div><div class='metric-val'>{unit_data.get('tien_dau_ky', 0):,.0f}đ</div></div>", unsafe_allow_html=True)
                with m2: st.markdown(f"<div class='crystal-card'><div class='metric-lbl'>Phải đóng</div><div class='metric-val'>{unit_data.get('so_phai_dong', 0):,.0f}đ</div></div>", unsafe_allow_html=True)
                with m3: st.markdown(f"<div class='crystal-card'><div class='metric-lbl'>Điều chỉnh</div><div class='metric-val'>{unit_data.get('dieu_chinh_ky_truoc', 0):,.0f}đ</div></div>", unsafe_allow_html=True)
                
                st.write("<br>", unsafe_allow_html=True)
                m4, m5, m6 = st.columns(3)
                with m4: st.markdown(f"<div class='crystal-card'><div class='metric-lbl'>Đã đóng</div><div class='metric-val' style='color:#10b981;'>{unit_data.get('so_da_dong', 0):,.0f}đ</div></div>", unsafe_allow_html=True)
                with m5: st.markdown(f"<div class='crystal-card'><div class='metric-lbl'>Lệch</div><div class='metric-val' style='color:#ef4444;'>{unit_data.get('so_bi_lech', 0):,.0f}đ</div></div>", unsafe_allow_html=True)
                debt = unit_data.get('tien_cuoi_ky', 0)
                status_clr = '#ef4444' if debt > 0 else '#10b981'
                with m6: st.markdown(f"<div class='crystal-card' style='border: 3px solid {status_clr};'><div class='metric-lbl'>{'CÒN NỢ' if debt > 0 else 'DƯ CÓ'}</div><div class='metric-val' style='color:{status_clr};'>{abs(debt):,.0f}đ</div></div>", unsafe_allow_html=True)
                
                st.info(f"📝 NỘI DUNG CK CHUẨN: {unit_data.get('madvi')} {unit_data.get('tendvi')} đóng bhxh tháng {datetime.now().month} năm {datetime.now().year}")
                st.markdown("</div>", unsafe_allow_html=True)
            
            with cr:
                rate = min(round((unit_data.get('so_da_dong', 0) / unit_data.get('so_phai_dong', 1)) * 100, 1), 100)
                st.plotly_chart(go.Figure(go.Indicator(mode="gauge+number", value=rate, title={'text': "TỶ LỆ HOÀN THÀNH (%)", 'font': {'size': 20, 'color': '#1e3a8a', 'weight': 'bold'}}, number={'suffix': "%", 'font': {'color': '#2563eb', 'size': 60}}, gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#2563eb"}})).update_layout(paper_bgcolor="rgba(0,0,0,0)", height=420), use_container_width=True)
                
                for off in OFFICERS:
                    if any(kw in unit_addr for kw in off['keywords']):
                        st.markdown(f"<div class='crystal-card' style='background: #000; color: white;'><small style='color:#39ff14; font-weight:900;'>PHỤ TRÁCH TRỰC TIẾP</small><h3 style='color:{off['color']}; margin:10px 0;'>{off['name']}</h3><a href='tel:{off['phone'].replace('.','')}' style='color:white; font-size: 1.5rem; text-decoration:none; font-weight:800;'>📱 {off['phone']}</a><br><a href='{off['zalo']}' target='_blank' style='background:#0068ff; color:white; padding:10px 30px; border-radius:50px; text-decoration:none; display:inline-block; margin-top:15px; font-weight:800;'>GỬI TIN NHẮN ZALO</a></div>", unsafe_allow_html=True)

    # --- TAB 2: AI ---
    elif st.session_state.current_tab == "🤖 Trợ lý AI Gemini":
        st.markdown("## 🧠 TRỢ LÝ AI THÔNG MINH (GEMINI 1.5 FLASH)"); st.info("Sử dụng model ổn định nhất để tránh lỗi version.")
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]): st.markdown(msg["content"])
        if prompt := st.chat_input("Hỏi tôi bất cứ điều gì..."):
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            with st.chat_message("assistant"):
                with st.spinner("AI đang tư duy..."):
                    resp = get_ai_response(prompt); st.markdown(resp); st.session_state.chat_history.append({"role": "assistant", "content": resp})

    # --- TAB 3: PDF ---
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
                        b64 = base64.b64encode(f.read()).decode('utf-8')
                        st.markdown(f'<iframe src="data:application/pdf;base64,{b64}" width="100%" height="850px" style="border:10px solid white; border-radius:35px; box-shadow:0 30px 80px rgba(0,0,0,0.1);"></iframe>', unsafe_allow_html=True)

    # --- CÁC TAB KHÁC ---
    elif st.session_state.current_tab == "📑 Cẩm nang Nghiệp vụ": st.markdown("## 📑 CẨM NANG NGHIỆP VỤ")
    elif st.session_state.current_tab == "🧮 Máy tính BHXH":
        st.markdown("## 🧮 DỰ TOÁN ĐÓNG BHXH"); sal = st.number_input("Lương đóng:", value=5000000); st.success(f"Tổng đóng: {(sal*0.32):,.0f}đ")
    elif st.session_state.current_tab == "📍 Liên hệ BHXH":
        st.markdown("## 📍 LIÊN HỆ"); st.write("🏠 Cơ sở: Thôn Thuận Sơn, Thuận An, Đắk Mil, Đắk Nông.")

st.markdown("<br><hr><center style='color:#94a3b8; font-size:0.95rem; padding-bottom:60px;'>© 2026 BHXH CƠ SỞ THUẬN AN | v22.0 Ultimate Masterpiece</center>", unsafe_allow_html=True)
