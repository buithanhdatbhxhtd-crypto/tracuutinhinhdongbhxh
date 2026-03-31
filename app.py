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

# --- CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="BHXH Thuận An - v18.0 Quantum Nexus",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CẤU HÌNH AI GEMINI ---
# Lấy API Key từ Secrets của Streamlit (Cài đặt trong: Settings -> Secrets -> GOOGLE_API_KEY = "...")
api_key = st.secrets.get("GOOGLE_API_KEY", os.environ.get("GOOGLE_API_KEY", ""))
if api_key:
    genai.configure(api_key=api_key)

def get_ai_response(prompt):
    if not api_key:
        return "⚠️ **Cấu hình AI chưa hoàn tất:** Vui lòng thêm `GOOGLE_API_KEY` vào Streamlit Secrets để sử dụng tính năng này."
    try:
        model = genai.GenerativeModel('gemini-2.5-flash-preview-09-2025')
        full_prompt = f"Bạn là trợ lý ảo cao cấp của BHXH cơ sở Thuận An. Hãy hỗ trợ câu hỏi sau một cách chuyên nghiệp và ngắn gọn: {prompt}"
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        return f"⚠️ **Trợ lý AI đang bận:** {str(e)[:100]}... Quý đơn vị vui lòng thử lại sau hoặc chat Zalo với cán bộ nhé!"

# --- KHỞI TẠO STATE ---
if 'selected_unit' not in st.session_state:
    st.session_state.selected_unit = None
if 'current_tab' not in st.session_state:
    st.session_state.current_tab = "📊 Tra cứu C12-TS"
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if 'active_pdf' in st.session_state and not os.path.exists(st.session_state.active_pdf):
    st.session_state.active_pdf = None

# --- TỔNG LỰC CSS (GIAO DIỆN NEXUS v18.0) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    :root {
        --primary: #1e3a8a;
        --secondary: #2563eb;
        --accent: #0ea5e9;
        --neon-blue: #00d2ff;
        --neon-green: #39ff14;
        --neon-gold: #ffaa00;
    }

    * { font-family: 'Plus Jakarta Sans', sans-serif; }
    
    .stApp {
        background: radial-gradient(circle at 10% 20%, #f1f5f9 0%, #e2e8f0 100%);
    }

    /* BẢNG LED RGB QUANTUM */
    .led-marquee {
        background: linear-gradient(90deg, #000, #111, #000);
        color: #00ff00;
        padding: 15px 0;
        font-weight: 800;
        border-radius: 15px;
        box-shadow: 0 0 35px rgba(0, 255, 0, 0.4);
        border: 2px solid #333;
        margin-bottom: 30px;
        font-family: 'Courier New', Courier, monospace;
        font-size: 1.25rem;
        text-shadow: 0 0 10px #00ff00;
        border-top: 2px solid var(--neon-blue);
    }

    /* SIÊU Ô TÌM KIẾM GATEWAY - KHÔNG CHE CHỮ */
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

    .stTextInput input {
        border-radius: 30px !important;
        padding: 15px 50px !important; 
        border: 10px solid var(--secondary) !important;
        font-size: 3rem !important; 
        font-weight: 900 !important;
        height: 160px !important; 
        background: white !important;
        color: var(--primary) !important;
        box-shadow: 0 50px 100px rgba(59, 130, 246, 0.4) !important;
        text-align: center !important;
        line-height: normal !important;
        transition: all 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
    }
    
    .stTextInput input:focus {
        border-color: var(--neon-blue) !important;
        transform: scale(1.03) translateY(-10px);
        box-shadow: 0 70px 150px rgba(0, 210, 255, 0.5) !important;
    }

    /* THẺ CÁN BỘ MATRIX */
    .matrix-card {
        background: #050505;
        padding: 25px;
        border-radius: 30px;
        border: 4px solid #111;
        margin-bottom: 25px;
        text-align: center;
        transition: all 0.4s;
    }
    .matrix-card:hover { transform: translateY(-12px); border-color: #333; }
    
    .online-indicator {
        height: 12px; width: 12px; background: var(--neon-green); 
        border-radius: 50%; display: inline-block; margin-right: 8px;
        animation: pulse 1.5s infinite;
    }
    @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; } }

    /* PDF VIEWER FIX */
    .pdf-nexus {
        border-radius: 30px;
        border: 8px solid white;
        box-shadow: 0 40px 100px rgba(0,0,0,0.2);
        overflow: hidden;
        background: #fff;
    }

    /* BUTTONS */
    .stButton>button {
        border-radius: 50px !important;
        font-weight: 800 !important;
        text-transform: uppercase;
        padding: 0.8rem 2.5rem !important;
        transition: all 0.3s ease !important;
    }
    
    [data-testid="stSidebar"] { background-color: #020617; }
    </style>
    """, unsafe_allow_html=True)

# --- DỮ LIỆU CÁN BỘ & ZALO ---
OFFICERS = [
    {"name": "Bà NGUYỄN THỊ NHÀI", "scope": "Xã Đức Lập, Đắk Mil", "phone": "0846.39.29.29", "zalo": "https://zalo.me/0846392929", "color": "#00d2ff"},
    {"name": "Ông BÙI THÀNH ĐẠT", "scope": "Xã Đắk Sắk, Đắk Song", "phone": "0986.05.30.06", "zalo": "https://zalo.me/0986053006", "color": "#ffaa00"},
    {"name": "Ông HOÀNG SỸ HẢI", "scope": "Xã Thuận An", "phone": "0919.06.11.53", "zalo": "https://zalo.me/0919061153", "color": "#39ff14"}
]

# --- HÀM XỬ LÝ VĂN BẢN PDF ---
def get_local_pdfs():
    return [f for f in os.listdir('.') if f.lower().endswith('.pdf')]

def embed_pdf_nexus(file_path):
    try:
        with open(file_path, "rb") as f:
            pdf_data = f.read()
            base64_pdf = base64.b64encode(pdf_data).decode('utf-8')
        
        # Nhúng với iframe Nexus
        pdf_display = f"""
        <div class="pdf-nexus">
            <iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="900px" style="border:none;"></iframe>
        </div>
        """
        st.markdown(pdf_display, unsafe_allow_html=True)
        
        # Link khẩn cấp nếu trình duyệt chặn
        st.markdown(f"""
            <div style="text-align: center; margin-top: 20px;">
                <a href="data:application/pdf;base64,{base64_pdf}" download="{file_path}" 
                   style="text-decoration:none; background:#10b981; color:white; padding:15px 40px; border-radius:50px; font-weight:900; display:inline-block; margin-right:15px;">
                   📥 TẢI VĂN BẢN VỀ MÁY
                </a>
                <a href="data:application/pdf;base64,{base64_pdf}" target="_blank" 
                   style="text-decoration:none; background:#2563eb; color:white; padding:15px 40px; border-radius:50px; font-weight:900; display:inline-block;">
                   🚀 XEM TOÀN MÀN HÌNH
                </a>
            </div>
        """, unsafe_allow_html=True)
        return True
    except Exception as e:
        st.error(f"Lỗi hệ thống PDF: {e}")
        return False

# --- HÀM TẢI DỮ LIỆU EXCEL ---
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

# --- SIDEBAR NEXUS ---
with st.sidebar:
    st.markdown("<h1 style='color:white; text-align:center;'>🛡️ QUANTUM HUB</h1>", unsafe_allow_html=True)
    st.divider()
    menu = {
        "📊 Tra cứu C12-TS": "📈",
        "🤖 Trợ lý AI Gemini": "🧠",
        "📂 Văn bản PDF Mới": "📄",
        "📑 Cẩm nang Thủ tục": "📚",
        "🧮 Máy tính BHXH": "🧮",
        "📍 Vị trí & Liên hệ": "🏠"
    }
    for label, icon in menu.items():
        if st.button(f"{icon} {label}", use_container_width=True):
            st.session_state.current_tab = label
            st.rerun()
    st.divider()
    st.success(f"Dữ liệu: {datetime.now().strftime('%d/%m/%Y')}")
    st.caption("v18.0 Quantum Nexus | Beyond Digital")

# --- HEADER LED ---
marquee_text = "💎 HỆ THỐNG TRA CỨU BHXH THUẬN AN PHIÊN BẢN v18.0 QUANTUM NEXUS • ĐÃ CẬP NHẬT TRÍ TUỆ NHÂN TẠO GEMINI CAO CẤP • TẢI VÀ XEM VĂN BẢN PDF TRỰC TUYẾN • TRA CỨU NHANH - NỘP TIỀN ĐÚNG CÚ PHÁP •"
st.markdown(f"<div class='led-marquee'><marquee scrollamount='10'>{marquee_text}</marquee></div>", unsafe_allow_html=True)

df = load_data_engine()

if df is not None:
    
    # --- TAB 1: TRA CỨU (CHÍNH) ---
    if st.session_state.current_tab == "📊 Tra cứu C12-TS":
        if st.session_state.selected_unit is None:
            st.markdown("<div class='gateway-container'>", unsafe_allow_html=True)
            st.markdown("<h1 style='color:#1e3a8a; font-size:4rem; font-weight:900;'>🛡️ CỔNG TRA CỨU DỮ LIỆU</h1>", unsafe_allow_html=True)
            st.markdown("<p style='color:#64748b; font-size:1.6rem; font-weight:700;'>NHẬP MÃ ĐƠN VỊ HOẶC TÊN CÔNG TY</p>", unsafe_allow_html=True)
            query = st.text_input("Gateway", placeholder="Gõ tìm kiếm...", label_visibility="collapsed")
            st.markdown("</div>", unsafe_allow_html=True)

            col_news, col_res, col_off = st.columns([0.8, 1.4, 1.1])
            with col_news:
                st.markdown("##### 📢 TIN TỨC MỚI")
                st.markdown("<div style='background:white; padding:40px; border-radius:35px; border:2.5px solid #e2e8f0; text-align:center; min-height:350px; display:flex; flex-direction:column; justify-content:center; box-shadow: 0 20px 40px rgba(0,0,0,0.06);'><h3 style='color:#1e3a8a;'>🛡️ AN SINH</h3><p style='font-size:1.1rem; color:#64748b;'>Hưởng lương hưu là sự bảo đảm vững chắc nhất cho tuổi già của bạn.</p><hr><small style='color:#ffaa00; font-weight:800;'>BHXH THUẬN AN ĐỒNG HÀNH</small></div>", unsafe_allow_html=True)

            with col_res:
                if query:
                    results = df[df['search_index'].str.contains(unidecode(query).lower(), na=False)].head(8)
                    for idx, row in results.iterrows():
                        with st.container():
                            ca, cb = st.columns([3.5, 1.5])
                            ca.markdown(f"<div style='background:white; padding:25px; border-radius:25px; border-left:12px solid #2563eb; margin-bottom:15px; box-shadow:0 8px 20px rgba(0,0,0,0.04);'><small style='color:#2563eb; font-weight:800;'>MÃ: {row.get('madvi')}</small><br><b style='font-size:1.4rem; color:#1e293b;'>{row.get('tendvi')}</b></div>", unsafe_allow_html=True)
                            if cb.button("XÁC NHẬN ➔", key=f"sel_{row.get('madvi')}_{idx}", use_container_width=True):
                                st.session_state.selected_unit = row.get('madvi'); st.rerun()
                else: st.markdown("<br><center><img src='https://cdn-icons-png.flaticon.com/512/3772/3772274.png' width='160' style='opacity:0.2'></center>", unsafe_allow_html=True)

            with col_off:
                st.markdown("##### 👨‍💼 LIÊN HỆ CÁN BỘ & ZALO")
                for off in OFFICERS:
                    st.markdown(f"""
                    <div class="matrix-card">
                        <div class="online-indicator"></div><small style="color:white; font-weight:800;">TRỰC TUYẾN</small>
                        <div style="color:{off['color']}; font-weight:900; font-size:1.2rem; margin-top:5px;">{off['name']}</div>
                        <div style="color:#aaa; font-size:0.85rem; margin:5px 0;">Phụ trách: {off['scope']}</div>
                        <a href="tel:{off['phone'].replace('.','')}" style="text-decoration:none; color:white; font-weight:800; font-size:1.2rem;">📱 {off['phone']}</a><br>
                        <a href="{off['zalo']}" target="_blank" style="background:#0068ff; color:white; padding:8px 25px; border-radius:50px; text-decoration:none; display:inline-block; margin-top:10px; font-weight:900; font-size:0.8rem;">💬 CHAT ZALO</a>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown("##### 🏦 TÀI KHOẢN BHXH THUẬN AN")
                st.markdown('<div style="background:#111; padding:15px; border-radius:15px; border-left:5px solid #00d2ff; color:#00d2ff; font-weight:800; font-size:0.85rem;">BIDV: 63510009867032<br>AGRIBANK: 5301202919045<br>VIETINBANK: 919035000003</div>', unsafe_allow_html=True)

        else:
            unit_data = df[df['madvi'] == st.session_state.selected_unit].iloc[0]
            if st.button("⬅ QUAY LẠI TRANG TÌM KIẾM"): st.session_state.selected_unit = None; st.rerun()
            st.markdown(f"<div style='background:white; padding:45px; border-radius:45px; border-left:25px solid #1e3a8a; box-shadow: 0 30px 80px rgba(0,0,0,0.08); margin-top:20px;'><h2 style='margin:0; color:#1e3a8a;'>🏢 {unit_data.get('tendvi')}</h2><p>Mã đơn vị: <b>{unit_data.get('madvi')}</b> | Địa chỉ: {unit_data.get('diachi', 'N/A')}</p></div>", unsafe_allow_html=True)
            
            cl, cr = st.columns([1.8, 1])
            with cl:
                st.markdown("<div style='background:white; border-radius:40px; padding:40px; box-shadow:0 30px 60px rgba(0,0,0,0.05); margin-top:30px;'>", unsafe_allow_html=True)
                st.write("#### 📉 PHÂN TÍCH TÀI CHÍNH")
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

    # --- TAB 2: AI GEMINI (FULL POWER) ---
    elif st.session_state.current_tab == "🤖 Trợ lý AI Gemini":
        st.markdown("## 🧠 TRỢ LÝ AI THÔNG MINH (GEMINI 2.5)")
        st.write("Giải đáp mọi thắc mắc về chính sách BHXH, BHYT.")
        
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]): st.markdown(msg["content"])
        
        if prompt := st.chat_input("Hỏi tôi bất cứ điều gì..."):
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            with st.chat_message("assistant"):
                with st.spinner("AI đang tư duy..."):
                    resp = get_ai_response(prompt)
                    st.markdown(resp)
                    st.session_state.chat_history.append({"role": "assistant", "content": resp})

    # --- TAB 3: VĂN BẢN PDF (NEXUS VIEW) ---
    elif st.session_state.current_tab == "📂 Văn bản PDF Mới":
        st.markdown("## 📂 THƯ VIỆN VĂN BẢN KỸ THUẬT SỐ")
        pdfs = get_local_pdfs()
        if not pdfs:
            st.warning("Hệ thống chưa tìm thấy văn bản nào (.pdf) trong thư mục gốc GitHub.")
        else:
            c1, c2 = st.columns([1, 2.5])
            with c1:
                st.write("##### DANH SÁCH VĂN BẢN:")
                for f in pdfs:
                    if st.button(f"📄 {f}", use_container_width=True, key=f"pdf_{f}"):
                        st.session_state.active_pdf = f
            with c2:
                if st.session_state.active_pdf and os.path.exists(st.session_state.active_pdf):
                    st.success(f"📌 ĐANG XEM: {st.session_state.active_pdf}")
                    embed_pdf_nexus(st.session_state.active_pdf)

    # --- CÁC TAB KHÁC ---
    elif st.session_state.current_tab == "📑 Cẩm nang Thủ tục": st.markdown("## 📑 CẨM NANG NGHIỆP VỤ")
    elif st.session_state.current_tab == "🧮 Máy tính BHXH":
        st.markdown("## 🧮 DỰ TOÁN ĐÓNG BHXH"); sal = st.number_input("Lương:", value=5000000); st.success(f"Tổng: {(sal*0.32):,.0f}đ")
    elif st.session_state.current_tab == "📍 Vị trí & Liên hệ":
        st.markdown("## 📍 LIÊN HỆ"); st.write("🏠 Cơ sở: Thôn Thuận Sơn, Thuận An, Đắk Mil, Đắk Nông."); st.write("📞 Hotline: 1900 9068")

st.markdown("<br><hr><center style='color:#94a3b8; font-size:0.9rem; padding-bottom:60px;'>© 2026 BHXH CƠ SỞ THUẬN AN | Elite Quantum Nexus v18.0</center>", unsafe_allow_html=True)
