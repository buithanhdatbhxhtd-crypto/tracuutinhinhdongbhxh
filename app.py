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
    page_title="BHXH Thuận An - v20.3 Crystal Nexus",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CẤU HÌNH AI GEMINI (TỐI ƯU CHO AI STUDIO) ---
# Secrets: Settings -> Secrets -> GOOGLE_API_KEY = "key_cua_ban"
api_key = st.secrets.get("GOOGLE_API_KEY", os.environ.get("GOOGLE_API_KEY", ""))

if api_key:
    try:
        genai.configure(api_key=api_key)
    except Exception as e:
        st.sidebar.error(f"Lỗi cấu hình AI: {e}")

def get_ai_response(prompt):
    if not api_key:
        return "⚠️ **Chưa cấu hình API Key:** Vui lòng thêm `GOOGLE_API_KEY` vào Streamlit Secrets."
    try:
        # Sử dụng model gemini-1.5-flash ổn định nhất
        model = genai.GenerativeModel('gemini-1.5-flash')
        system_instruction = "Bạn là trợ lý AI chuyên gia của Bảo hiểm xã hội cơ sở Thuận An, Lâm Đồng. Hãy tư vấn chính sách BHXH, BHYT ngắn gọn, dễ hiểu."
        full_prompt = f"{system_instruction}\n\nĐơn vị hỏi: {prompt}"
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        return f"⚠️ **Trợ lý AI đang bận:** Vui lòng liên hệ cán bộ chuyên quản qua Zalo nhé!"

# --- KHỞI TẠO STATE ---
if 'selected_unit' not in st.session_state:
    st.session_state.selected_unit = None
if 'current_tab' not in st.session_state:
    st.session_state.current_tab = "📊 Tra cứu C12-TS"
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if 'active_pdf' not in st.session_state:
    st.session_state.active_pdf = None

# --- TỔNG LỰC CSS (GIAO DIỆN CRYSTAL v20.3) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    :root {
        --primary: #1e3a8a;
        --secondary: #2563eb;
        --accent: #0ea5e9;
        --neon-blue: #00d2ff;
        --neon-green: #10b981;
    }

    * { font-family: 'Plus Jakarta Sans', sans-serif; }
    
    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
    }

    /* --- FIX SIDEBAR SIÊU RÕ NÉT --- */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e3a8a 100%) !important;
    }
    
    /* ÉP CHỮ DANH MỤC TRẮNG SÁNG TUYỆT ĐỐI */
    [data-testid="stSidebar"] .stRadio label p {
        color: #ffffff !important;
        font-size: 1.25rem !important;
        font-weight: 800 !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5) !important;
        padding: 5px 0 !important;
    }

    /* BẢNG LED RGB v20.3 */
    .led-marquee {
        background: #000;
        color: #00ff00;
        padding: 12px 0;
        font-weight: 800;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0, 255, 0, 0.2);
        border: 2px solid #333;
        margin-bottom: 30px;
        font-family: 'Courier New', Courier, monospace;
        font-size: 1.35rem;
        text-shadow: 0 0 10px #00ff00;
        border-top: 3px solid var(--neon-blue);
    }

    /* SIÊU Ô TÌM KIẾM GATEWAY VỚI KÍNH LÚP */
    .gateway-container {
        max-width: 1000px;
        margin: 0 auto 3rem auto;
        text-align: center;
        position: relative;
    }

    div[data-testid="stTextInput"] > div {
        height: auto !important;
        background: transparent !important;
        padding: 10px 0 !important;
    }

    /* Thêm biểu tượng kính lúp giả lập qua placeholder hoặc CSS */
    .stTextInput input {
        border-radius: 30px !important;
        padding: 15px 45px 15px 80px !important; /* Chừa chỗ cho icon kính lúp bên trái */
        border: 10px solid var(--secondary) !important;
        font-size: 2.8rem !important; 
        font-weight: 900 !important;
        height: 140px !important; 
        background: white url('https://cdn-icons-png.flaticon.com/512/622/622669.png') no-repeat 25px center !important;
        background-size: 45px !important;
        color: var(--primary) !important;
        box-shadow: 0 50px 100px rgba(59, 130, 246, 0.4) !important;
        line-height: normal !important;
        transition: all 0.4s ease;
    }
    
    .stTextInput input:focus {
        border-color: var(--neon-blue) !important;
        transform: scale(1.02);
    }

    /* THẺ CÁN BỘ MATRIX - HIỆN THỊ XÃ */
    .matrix-card {
        background: #050505;
        padding: 25px;
        border-radius: 30px;
        border: 4px solid #111;
        margin-bottom: 25px;
        text-align: center;
    }
    
    .officer-name { color: #fff; font-size: 1.3rem; font-weight: 900; margin: 10px 0; }
    .officer-commune { color: #00d2ff; font-weight: 700; font-size: 0.9rem; text-transform: uppercase; }

    /* DASHBOARD RADIANT */
    .radiant-card {
        background: white;
        padding: 35px;
        border-radius: 40px;
        box-shadow: 0 25px 60px rgba(0,0,0,0.06);
        border: 1px solid #f1f5f9;
        margin-top: 20px;
    }

    .stButton>button {
        border-radius: 50px !important;
        font-weight: 800 !important;
        text-transform: uppercase;
        padding: 0.8rem 2.5rem !important;
        transition: all 0.3s ease !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ĐỒNG HỒ REAL-TIME (JS) ---
def live_clock_v20_3():
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

# --- DỮ LIỆU CÁN BỘ (ĐỊNH NGHĨA KEYWORDS ĐỂ MAPPING ĐỊA CHỈ) ---
OFFICERS = [
    {
        "name": "Bà NGUYỄN THỊ NHÀI", 
        "communes": "Xã Đức Lập, Xã Đắk Mil", 
        "keywords": ["duc lap", "đức lập", "dak mil", "đắk mil"],
        "phone": "0846.39.29.29", 
        "zalo": "https://zalo.me/0846392929", 
        "color": "#00d2ff"
    },
    {
        "name": "Ông BÙI THÀNH ĐẠT", 
        "communes": "Xã Đắk Sắk, Xã Đắk Song", 
        "keywords": ["dak sak", "đắk sắk", "dak song", "đắk song"],
        "phone": "0986.05.30.06", 
        "zalo": "https://zalo.me/0986053006", 
        "color": "#ffaa00"
    },
    {
        "name": "Ông HOÀNG SỸ HẢI", 
        "communes": "Xã Thuận An", 
        "keywords": ["thuan an", "thuận an"],
        "phone": "0919.06.11.53", 
        "zalo": "https://zalo.me/0919061153", 
        "color": "#39ff14"
    }
]

# --- HÀM XỬ LÝ VĂN BẢN PDF ---
def get_local_pdfs():
    return [f for f in os.listdir('.') if f.lower().endswith('.pdf')]

def embed_pdf_v20_3(file_path):
    try:
        with open(file_path, "rb") as f:
            pdf_bytes = f.read()
            base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
        
        pdf_display = f'<div class="pdf-container"><object data="data:application/pdf;base64,{base64_pdf}" type="application/pdf" width="100%" height="100%"></object></div>'
        st.markdown(pdf_display, unsafe_allow_html=True)
        st.write("<br>", unsafe_allow_html=True)
        st.download_button(label="📥 TẢI VĂN BẢN VỀ MÁY", data=pdf_bytes, file_name=file_path, mime="application/pdf", use_container_width=True)
        return True
    except: return False

# --- TẢI DỮ LIỆU ---
@st.cache_data
def load_data_engine():
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
    selected_tab = st.radio("MENU", menu, label_visibility="collapsed")
    st.session_state.current_tab = selected_tab
    
    st.divider()
    live_clock_v20_3()
    st.caption("v20.3 Crystal Nexus | Fixed UI & AI")

# --- HEADER LED ---
marquee_msg = "💎 HỆ THỐNG TRA CỨU BHXH THUẬN AN PHIÊN BẢN v20.3 CRYSTAL • ĐÃ CẬP NHẬT KÍNH LÚP TÌM KIẾM VÀ FIX LỖI CÁN BỘ PHỤ TRÁCH •"
st.markdown(f"<div class='led-marquee'><marquee scrollamount='10'>{marquee_msg}</marquee></div>", unsafe_allow_html=True)

df = load_data_engine()

if df is not None:
    # --- TAB 1: TRA CỨU ---
    if st.session_state.current_tab == "📊 Tra cứu C12-TS":
        if st.session_state.selected_unit is None:
            st.markdown("<div class='gateway-container'>", unsafe_allow_html=True)
            st.markdown("<h1 style='color:#1e3a8a; font-size:4rem; font-weight:900;'>🛡️ CỔNG TRA CỨU DỮ LIỆU</h1>", unsafe_allow_html=True)
            st.markdown("<p style='color:#64748b; font-size:1.6rem; font-weight:700;'>NHẬP MÃ ĐƠN VỊ HOẶC TÊN CÔNG TY</p>", unsafe_allow_html=True)
            query = st.text_input("Gateway", placeholder="Gõ tìm kiếm tại đây...", label_visibility="collapsed")
            st.markdown("</div>", unsafe_allow_html=True)

            col_news, col_res, col_off = st.columns([0.8, 1.4, 1.1])
            with col_news:
                st.markdown("##### 📢 TIN TỨC")
                st.markdown("<div style='background:white; padding:30px; border-radius:30px; border:1px solid #e2e8f0; text-align:center; min-height:350px; display:flex; flex-direction:column; justify-content:center; box-shadow: 0 20px 40px rgba(0,0,0,0.06);'><h4 style='color:#1e3a8a;'>🛡️ AN SINH</h4><p>Tham gia BHXH là hình thức đầu tư an toàn cho tương lai.</p><hr><small style='color:#f59e0b; font-weight:800;'>BHXH THUẬN AN</small></div>", unsafe_allow_html=True)

            with col_res:
                if query:
                    clean_query = unidecode(query).lower()
                    results = df[df['search_index'].str.contains(clean_query, na=False)].head(8)
                    for idx, row in results.iterrows():
                        with st.container():
                            ca, cb = st.columns([3.5, 1.5])
                            ca.markdown(f"<div style='background:white; padding:20px; border-radius:25px; border-left:12px solid #2563eb; margin-bottom:12px; box-shadow:0 8px 20px rgba(0,0,0,0.04);'><small style='color:#2563eb; font-weight:800;'>MÃ: {row.get('madvi')}</small><br><b style='font-size:1.3rem; color:#1e293b;'>{row.get('tendvi')}</b></div>", unsafe_allow_html=True)
                            if cb.button("XÁC NHẬN ➔", key=f"sel_{row.get('madvi')}_{idx}", use_container_width=True):
                                st.session_state.selected_unit = row.get('madvi'); st.rerun()
                else: st.markdown("<br><center><img src='https://cdn-icons-png.flaticon.com/512/3772/3772274.png' width='160' style='opacity:0.2'></center>", unsafe_allow_html=True)

            with col_off:
                st.markdown("##### 👨‍💼 LIÊN HỆ CÁN BỘ")
                for off in OFFICERS:
                    st.markdown(f"""
                    <div style='background: white; border-radius: 20px; padding: 20px; border: 1px solid #eee; margin-bottom: 15px; text-align: center; box-shadow: 0 5px 15px rgba(0,0,0,0.02);'>
                        <div class='officer-commune'>{off['communes']}</div>
                        <div class='officer-name' style='color:var(--primary);'>{off['name']}</div>
                        <a href='tel:{off['phone'].replace('.','')}' style='text-decoration:none; color:var(--primary); font-weight: 800; font-size: 1.1rem;'>📱 {off['phone']}</a><br>
                        <a href='{off['zalo']}' target='_blank' style='background:#0068ff; color:white; padding:8px 25px; border-radius:50px; text-decoration:none; display:inline-block; margin-top: 10px; font-weight: 900; font-size: 0.8rem;'>💬 CHAT ZALO</a>
                    </div>
                    """, unsafe_allow_html=True)

        else:
            unit_data = df[df['madvi'] == st.session_state.selected_unit].iloc[0]
            unit_addr = unidecode(str(unit_data.get('diachi', ''))).lower()
            if st.button("⬅ QUAY LẠI"): st.session_state.selected_unit = None; st.rerun()
            st.markdown(f"<div class='radiant-card' style='border-left:25px solid #1e3a8a;'><h2 style='margin:0; color:#1e3a8a;'>🏢 {unit_data.get('tendvi')}</h2><p>Mã đơn vị: <b>{unit_data.get('madvi')}</b> | Địa chỉ: {unit_data.get('diachi', 'N/A')}</p></div>", unsafe_allow_html=True)
            
            cl, cr = st.columns([1.8, 1])
            with cl:
                st.markdown("<div class='radiant-card'>", unsafe_allow_html=True)
                st.write("#### 📈 PHÂN TÍCH TÀI CHÍNH")
                m1, m2, m3 = st.columns(3)
                m1.metric("Đầu kỳ", f"{unit_data.get('tien_dau_ky', 0):,.0f}đ")
                m2.metric("Phải đóng", f"{unit_data.get('so_phai_dong', 0):,.0f}đ")
                m3.metric("Điều chỉnh", f"{unit_data.get('dieu_chinh_ky_truoc', 0):,.0f}đ")
                st.write("<br>", unsafe_allow_html=True)
                m4, m5, m6 = st.columns(3)
                m4.metric("Đã đóng", f"{unit_data.get('so_da_dong', 0):,.0f}đ")
                m5.metric("Lệch", f"{unit_data.get('so_bi_lech', 0):,.0f}đ")
                debt = unit_data.get('tien_cuoi_ky', 0)
                m6.metric("CÒN NỢ" if debt > 0 else "DƯ CÓ", f"{abs(debt):,.0f}đ", delta=-debt, delta_color="inverse")
                st.info(f"📝 NỘI DUNG CK: {unit_data.get('madvi')} {unit_data.get('tendvi')} đóng bhxh tháng {datetime.now().month} năm {datetime.now().year}")
                st.markdown("</div>", unsafe_allow_html=True)
            with cr:
                rate = min(round((unit_data.get('so_da_dong', 0) / unit_data.get('so_phai_dong', 1)) * 100, 1), 100)
                st.plotly_chart(go.Figure(go.Indicator(mode="gauge+number", value=rate, title={'text': "HOÀN THÀNH (%)"}, gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#1e40af"}})), use_container_width=True)
                
                # HIỂN THỊ CÁN BỘ PHỤ TRÁCH TRỰC TIẾP DỰA TRÊN ĐỊA CHỈ
                st.markdown("##### 👨‍💼 CHUYÊN QUẢN TRỰC TIẾP")
                found_off = False
                for off in OFFICERS:
                    if any(kw in unit_addr for kw in off['keywords']):
                        found_off = True
                        st.markdown(f"""
                        <div style='background: #000; border-radius: 20px; padding: 20px; text-align: center;'>
                            <small style='color:#39ff14; font-weight:900;'>PHỤ TRÁCH TRỰC TIẾP</small>
                            <h4 style='color:{off['color']}; margin:10px 0;'>{off['name']}</h4>
                            <a href='tel:{off['phone'].replace('.','')}' style='color:white; text-decoration:none; font-weight:800; font-size:1.5rem;'>📱 {off['phone']}</a><br>
                            <a href='{off['zalo']}' target='_blank' style='background:#0068ff; color:white; padding:8px 30px; border-radius:50px; text-decoration:none; display:inline-block; margin-top:10px; font-weight:800;'>CHAT ZALO</a>
                        </div>
                        """, unsafe_allow_html=True)
                if not found_off:
                    st.warning("Vui lòng liên hệ bất kỳ cán bộ nào để được hỗ trợ xã này.")

    # --- TAB 2: AI GEMINI ---
    elif st.session_state.current_tab == "🤖 Trợ lý AI Gemini":
        st.markdown("## 🧠 TRỢ LÝ AI THÔNG MINH (GEMINI 1.5 FLASH)")
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]): st.markdown(msg["content"])
        if prompt := st.chat_input("Hỏi tôi bất cứ điều gì..."):
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            with st.chat_message("assistant"):
                with st.spinner("AI đang truy xuất dữ liệu..."):
                    resp = get_ai_response(prompt)
                    st.markdown(resp); st.session_state.chat_history.append({"role": "assistant", "content": resp})

    # --- TAB 3: VĂN BẢN PDF ---
    elif st.session_state.current_tab == "📂 Thư viện Văn bản":
        st.markdown("## 📂 THƯ VIỆN VĂN BẢN KỸ THUẬT SỐ")
        pdfs = get_local_pdfs()
        if not pdfs: st.warning("Hãy tải file .pdf lên thư mục GitHub.")
        else:
            c1, c2 = st.columns([1, 2.5])
            with c1:
                for f in pdfs:
                    if st.button(f"📄 {f}", use_container_width=True, key=f"pdf_{f}"): st.session_state.active_pdf = f
            with c2:
                if st.session_state.active_pdf:
                    st.success(f"📌 ĐANG XEM: {st.session_state.active_pdf}")
                    embed_pdf_v20_3(st.session_state.active_pdf)

    # --- CÁC TAB KHÁC ---
    elif st.session_state.current_tab == "📑 Cẩm nang Nghiệp vụ": st.markdown("## 📑 CẨM NANG NGHIỆP VỤ")
    elif st.session_state.current_tab == "🧮 Máy tính BHXH":
        st.markdown("## 🧮 DỰ TOÁN ĐÓNG BHXH"); sal = st.number_input("Lương đóng:", value=5000000); st.success(f"Tổng đóng: {(sal*0.32):,.0f}đ")
    elif st.session_state.current_tab == "📍 Liên hệ BHXH":
        st.markdown("## 📍 LIÊN HỆ"); st.write("🏠 Cơ sở: Thôn Thuận Sơn, Thuận An, Đắk Mil, Đắk Nông.")

st.markdown("<br><hr><center style='color:#94a3b8; font-size:0.9rem; padding-bottom:60px;'>© 2026 BHXH CƠ SỞ THUẬN AN | Elite Quantum Nexus v20.3</center>", unsafe_allow_html=True)
