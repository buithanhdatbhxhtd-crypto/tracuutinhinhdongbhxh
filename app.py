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

# --- CẤU HÌNH API GEMINI ---
# Streamlit Cloud sẽ tự động lấy API Key nếu bạn cấu hình trong Secrets
# Hoặc hệ thống môi trường sẽ cung cấp.
api_key = os.environ.get("GOOGLE_API_KEY", "")
genai.configure(api_key=api_key)

# --- CƠ CHẾ GỌI AI AN TOÀN ---
def call_gemini_smart(prompt):
    system_instr = "Bạn là trợ lý ảo chuyên gia của BHXH cơ sở Thuận An, Lâm Đồng. Trả lời chuyên nghiệp, hỗ trợ đơn vị tra cứu đóng BHXH."
    try:
        # Kiểm tra sự tồn tại của GenerativeModel để tránh AttributeError
        if hasattr(genai, 'GenerativeModel'):
            model = genai.GenerativeModel(
                model_name='gemini-2.5-flash-preview-09-2025',
                system_instruction=system_instr
            )
            response = model.generate_content(prompt)
            return response.text
        else:
            return "⚠️ Thư viện AI đang được cập nhật trên máy chủ. Vui lòng thử lại sau hoặc liên hệ cán bộ chuyên quản."
    except Exception as e:
        return f"⚠️ Trợ lý AI đang bận. Lỗi: {str(e)[:100]}... Vui lòng liên hệ cán bộ để được hỗ trợ."

# --- CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="BHXH Thuận An - v17.3 Quantum Digital",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- KHỞI TẠO STATE (CHỐNG TREO CODE) ---
if 'selected_unit' not in st.session_state:
    st.session_state.selected_unit = None
if 'current_tab' not in st.session_state:
    st.session_state.current_tab = "📊 Tra cứu C12-TS"
if "messages" not in st.session_state:
    st.session_state.messages = []
if 'active_pdf' not in st.session_state:
    st.session_state.active_pdf = None

# --- TỔNG LỰC CSS (FIX CLIPPING & ENHANCED UI) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    :root {
        --primary: #1e3a8a;
        --secondary: #2563eb;
        --neon-blue: #00d2ff;
        --neon-gold: #ffaa00;
        --neon-green: #39ff14;
    }

    * { font-family: 'Plus Jakarta Sans', sans-serif; }
    
    .stApp {
        background: radial-gradient(circle at 50% 50%, #f1f5f9 0%, #cbd5e1 100%);
    }

    /* BẢNG LED RGB QUANTUM */
    .led-marquee {
        background: linear-gradient(90deg, #000, #111, #000);
        color: #00ff00;
        padding: 15px 0;
        font-weight: 800;
        border-radius: 15px;
        box-shadow: 0 0 30px rgba(0, 255, 0, 0.4);
        border: 2px solid #333;
        margin-bottom: 30px;
        font-family: 'Courier New', Courier, monospace;
        font-size: 1.25rem;
        text-shadow: 0 0 10px #00ff00;
        border-top: 3px solid var(--neon-blue);
    }

    /* SIÊU Ô TÌM KIẾM - CỰC ĐẠI & KHÔNG CHE CHỮ */
    .mega-search-wrapper {
        max-width: 1100px;
        margin: 0 auto 3rem auto;
        text-align: center;
    }

    /* Fix container Streamlit để không cắt chữ */
    div[data-testid="stTextInput"] > div {
        height: auto !important;
        background: transparent !important;
        padding: 10px 0 !important;
    }

    .stTextInput input {
        border-radius: 30px !important;
        padding: 10px 40px !important; 
        border: 10px solid var(--secondary) !important;
        font-size: 3rem !important; 
        font-weight: 900 !important;
        height: 150px !important; 
        background: white !important;
        color: var(--primary) !important;
        box-shadow: 0 50px 100px rgba(59, 130, 246, 0.4) !important;
        text-align: center !important;
        line-height: normal !important;
        transition: all 0.4s ease;
    }
    
    .stTextInput input:focus {
        border-color: var(--neon-blue) !important;
        transform: scale(1.02);
    }

    /* THẺ CÁN BỘ MATRIX NEON */
    .officer-matrix-card {
        background: #050505;
        padding: 25px;
        border-radius: 30px;
        border: 4px solid #111;
        margin-bottom: 20px;
        text-align: center;
    }
    .card-nhai { border-color: #00d2ff !important; }
    .card-dat { border-color: #ffaa00 !important; }
    .card-hai { border-color: #39ff14 !important; }

    /* PDF VIEWER FIX */
    .pdf-frame-container {
        border: 5px solid white;
        border-radius: 20px;
        box-shadow: 0 20px 50px rgba(0,0,0,0.15);
        overflow: hidden;
        background: #f8fafc;
    }

    [data-testid="stSidebar"] { background-color: #020617; }
    
    .stButton>button {
        border-radius: 50px !important;
        font-weight: 800 !important;
        text-transform: uppercase;
    }
    </style>
    """, unsafe_allow_html=True)

# --- DỮ LIỆU CÁN BỘ ---
OFFICERS = [
    {"name": "Bà NGUYỄN THỊ NHÀI", "scope": "Xã Đức Lập, Xã Đắk Mil", "phone": "0846.39.29.29", "zalo": "https://zalo.me/0846392929", "class": "card-nhai", "color": "#00d2ff"},
    {"name": "Ông BÙI THÀNH ĐẠT", "scope": "Xã Đắk Sắk, Xã Đắk Song", "phone": "0986.05.30.06", "zalo": "https://zalo.me/0986053006", "class": "card-dat", "color": "#ffaa00"},
    {"name": "Ông HOÀNG SỸ HẢI", "scope": "Xã Thuận An", "phone": "0919.06.11.53", "zalo": "https://zalo.me/0919061153", "class": "card-hai", "color": "#39ff14"}
]

# --- XỬ LÝ PDF ---
def get_pdf_files():
    return [f for f in os.listdir('.') if f.lower().endswith('.pdf')]

def display_pdf_smart(file_path):
    try:
        with open(file_path, "rb") as f:
            pdf_bytes = f.read()
            base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
        
        # Nhúng bằng iframe với nguồn dữ liệu trực tiếp
        pdf_display = f"""
        <div class="pdf-frame-container">
            <iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800px" style="border:none;"></iframe>
        </div>
        """
        st.markdown(pdf_display, unsafe_allow_html=True)
        return pdf_bytes
    except Exception as e:
        st.error(f"Không thể đọc file PDF: {e}")
        return None

# --- TẢI DỮ LIỆU EXCEL ---
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
    st.markdown("<h1 style='color:white; text-align:center;'>🛡️ QUANTUM HUB</h1>", unsafe_allow_html=True)
    st.divider()
    tabs = ["📊 Tra cứu C12-TS", "🤖 Trợ lý AI Gemini", "📂 Văn bản PDF Mới", "📑 Cẩm nang Thủ tục", "🧮 Máy tính BHXH", "📍 Vị trí & Liên hệ"]
    selected_tab = st.radio("CHUYÊN MỤC", tabs, label_visibility="collapsed")
    st.session_state.current_tab = selected_tab
    st.divider()
    st.info("Phiên bản v17.3 - Stable Engine")

# --- HEADER ---
marquee_msg = "🛡️ CHÚC QUÝ ĐƠN VỊ THUẬN LỢI TRONG CÔNG TÁC TRA CỨU BHXH • TRA CỨU NHANH C12-TS • HỆ THỐNG ĐÃ FIX LỖI ỔN ĐỊNH •"
st.markdown(f"<div class='led-marquee'><marquee scrollamount='10'>{marquee_msg}</marquee></div>", unsafe_allow_html=True)

df = load_data()

if df is not None:
    # --- TAB 1: TRA CỨU ---
    if st.session_state.current_tab == "📊 Tra cứu C12-TS":
        if st.session_state.selected_unit is None:
            st.markdown("<div class='mega-search-wrapper'>", unsafe_allow_html=True)
            st.markdown("<h1 style='color:#1e3a8a; font-size:3.5rem; font-weight:900;'>🛡️ CỔNG TRA CỨU DỮ LIỆU</h1>", unsafe_allow_html=True)
            st.markdown("<p style='color:#64748b; font-size:1.5rem; font-weight:700;'>NHẬP MÃ ĐƠN VỊ HOẶC TÊN CÔNG TY</p>", unsafe_allow_html=True)
            query = st.text_input("Gateway", placeholder="Gõ tìm kiếm...", label_visibility="collapsed")
            st.markdown("</div>", unsafe_allow_html=True)

            col_post, col_res, col_info = st.columns([0.8, 1.4, 1.1])
            with col_post:
                st.markdown("##### 📢 TIN TỨC")
                st.markdown("<div style='background:white; padding:30px; border-radius:30px; border:2px solid #e2e8f0; text-align:center; min-height:300px; display:flex; flex-direction:column; justify-content:center; box-shadow: 0 20px 40px rgba(0,0,0,0.06);'><h4 style='color:#1e3a8a;'>🛡️ AN SINH</h4><p>Hưởng lương hưu hàng tháng là bảo đảm tốt nhất cho tuổi già.</p><hr><small style='color:#ffaa00; font-weight:800;'>BHXH THUẬN AN</small></div>", unsafe_allow_html=True)

            with col_res:
                if query:
                    clean_query = unidecode(query).lower()
                    results = df[df['search_index'].str.contains(clean_query, na=False)].head(8)
                    for idx, row in results.iterrows():
                        with st.container():
                            ca, cb = st.columns([3.5, 1.5])
                            ca.markdown(f"<div style='background:white; padding:25px; border-radius:25px; border-left:12px solid #2563eb; margin-bottom:15px; box-shadow:0 8px 20px rgba(0,0,0,0.04);'><small style='color:#2563eb; font-weight:800;'>MÃ: {row.get('madvi')}</small><br><b style='font-size:1.4rem; color:#1e293b;'>{row.get('tendvi')}</b></div>", unsafe_allow_html=True)
                            if cb.button("XÁC NHẬN ➔", key=f"sel_{row.get('madvi')}_{idx}", use_container_width=True):
                                st.session_state.selected_unit = row.get('madvi'); st.rerun()
                else: st.markdown("<br><center><img src='https://cdn-icons-png.flaticon.com/512/3772/3772274.png' width='160' style='opacity:0.2'></center>", unsafe_allow_html=True)

            with col_info:
                st.markdown("##### 👨‍💼 CÁN BỘ & ZALO")
                for off in OFFICERS:
                    st.markdown(f"<div class='officer-matrix-card {off['class']}'><div style='color:{off['color']}; font-weight:900; font-size:1.1rem;'>{off['name']}</div><div style='color:#aaa; font-size:0.8rem; margin:5px 0;'>Phụ trách xã</div><a href='tel:{off['phone'].replace('.','')}' style='text-decoration:none; color:white; font-weight:800; font-size:1.1rem;'>📱 {off['phone']}</a><br><a href='{off['zalo']}' target='_blank' style='background:#0068ff; color:white; padding:8px 20px; border-radius:50px; text-decoration:none; display:inline-block; margin-top:10px; font-weight:800; font-size:0.8rem;'>💬 Chat Zalo</a></div>", unsafe_allow_html=True)
                st.markdown("##### 🏦 SỐ TÀI KHOẢN BHXH THUẬN AN")
                st.markdown('<div style="background:#111; padding:15px; border-radius:15px; border-left:5px solid #00d2ff; color:#00d2ff; font-weight:800; font-size:0.8rem;">BIDV: 63510009867032<br>AGRIBANK: 5301202919045<br>VIETINBANK: 919035000003</div>', unsafe_allow_html=True)

        else:
            unit_data = df[df['madvi'] == st.session_state.selected_unit].iloc[0]
            if st.button("⬅ QUAY LẠI"): st.session_state.selected_unit = None; st.rerun()
            st.markdown(f"<div style='background:white; padding:45px; border-radius:45px; border-left:25px solid #1e3a8a; box-shadow: 0 30px 80px rgba(0,0,0,0.08); margin-top:20px;'><h2 style='margin:0; color:#1e3a8a;'>🏢 {unit_data.get('tendvi')}</h2><p>Mã đơn vị: <b>{unit_data.get('madvi')}</b></p></div>", unsafe_allow_html=True)
            col_l, col_r = st.columns([1.8, 1])
            with col_l:
                st.markdown("<div style='background:white; border-radius:40px; padding:40px; box-shadow:0 30px 60px rgba(0,0,0,0.05); margin-top:30px;'>", unsafe_allow_html=True)
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
                now = datetime.now()
                st.info(f"📝 CÚ PHÁP: {unit_data.get('madvi')} {unit_data.get('tendvi')} đóng bhxh tháng {now.month} năm {now.year}")
                st.markdown("</div>", unsafe_allow_html=True)
            with col_r:
                rate = min(round((unit_data.get('so_da_dong', 0) / unit_data.get('so_phai_dong', 1)) * 100, 1), 100)
                st.plotly_chart(go.Figure(go.Indicator(mode="gauge+number", value=rate, title={'text': "HOÀN THÀNH (%)"}, gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#1e40af"}})), use_container_width=True)

    # --- TAB 2: AI GEMINI (FIXED ERROR) ---
    elif st.session_state.current_tab == "🤖 Trợ lý AI Gemini":
        st.markdown("## 🤖 TRỢ LÝ AI THÔNG MINH (GEMINI 2.5)")
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]): st.markdown(msg["content"])
        if prompt := st.chat_input("Hỏi tôi về chính sách BHXH..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            with st.chat_message("assistant"):
                with st.spinner("AI đang trích xuất dữ liệu..."):
                    response = call_gemini_smart(prompt)
                    st.markdown(response); st.session_state.messages.append({"role": "assistant", "content": response})

    # --- TAB 3: VĂN BẢN PDF (STABLE ENGINE) ---
    elif st.session_state.current_tab == "📂 Văn bản PDF Mới":
        st.markdown("## 📂 THƯ VIỆN VĂN BẢN KỸ THUẬT SỐ")
        pdf_files = get_pdf_files()
        if not pdf_files: st.warning("Hãy upload file .pdf lên GitHub.")
        else:
            c1, c2 = st.columns([1, 2.5])
            with c1:
                st.write("##### Chọn văn bản:")
                for f in pdf_files:
                    if st.button(f"📄 {f}", use_container_width=True, key=f"pdf_{f}"):
                        st.session_state.active_pdf = f
            with c2:
                if st.session_state.active_pdf:
                    st.success(f"📌 Đang xem: {st.session_state.active_pdf}")
                    p_bytes = display_pdf_smart(st.session_state.active_pdf)
                    if p_bytes:
                        st.download_button("📥 TẢI VĂN BẢN VỀ MÁY", p_bytes, file_name=st.session_state.active_pdf, use_container_width=True)

    # --- CÁC TAB KHÁC ---
    elif st.session_state.current_tab == "📑 Cẩm nang Thủ tục": st.markdown("## 📑 CẨM NANG NGHIỆP VỤ")
    elif st.session_state.current_tab == "🧮 Máy tính BHXH":
        st.markdown("## 🧮 DỰ TOÁN MỨC ĐÓNG"); sal = st.number_input("Lương:", value=5000000); st.success(f"Tổng: {(sal*0.32):,.0f}đ")
    elif st.session_state.current_tab == "📍 Vị trí & Liên hệ": st.markdown("## 📍 LIÊN HỆ"); st.write("🏠 Thôn Thuận Sơn, Thuận An, Lâm Đồng.")

st.markdown("<br><hr><center style='color:#94a3b8; font-size:0.9rem; padding-bottom:60px;'>© 2026 BHXH CƠ SỞ THUẬN AN | Elite Quantum Hub v17.3</center>", unsafe_allow_html=True)
