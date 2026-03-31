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

# --- CẤU HÌNH API GEMINI (SỬ DỤNG KEY TỪ MÔI TRƯỜNG) ---
api_key = "" 
genai.configure(api_key=api_key)

# --- CƠ CHẾ GỌI AI VỚI EXPONENTIAL BACKOFF ---
def call_gemini_with_retry(prompt):
    retries = 5
    delay = 1
    for i in range(retries):
        try:
            model = genai.GenerativeModel('gemini-2.5-flash-preview-09-2025')
            response = model.generate_content(prompt)
            return response.text
        except Exception:
            if i == retries - 1:
                return "⚠️ Hệ thống AI đang bận. Vui lòng thử lại sau giây lát hoặc liên hệ cán bộ chuyên quản để được hỗ trợ trực tiếp."
            time.sleep(delay)
            delay *= 2

# --- CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="BHXH Thuận An - v17.1 Quantum Digital",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- KHỞI TẠO STATE ---
if 'selected_unit' not in st.session_state:
    st.session_state.selected_unit = None
if 'last_query' not in st.session_state:
    st.session_state.last_query = ""
if 'show_loading' not in st.session_state:
    st.session_state.show_loading = False
if 'current_tab' not in st.session_state:
    st.session_state.current_tab = "📊 Tra cứu C12-TS"
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- TỔNG LỰC CSS (GIAO DIỆN QUANTUM DIGITAL v17.1) ---
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

    /* SIÊU Ô TÌM KIẾM KHÔNG CHE CHỮ */
    .mega-search-wrapper {
        max-width: 1100px;
        margin: 0 auto 3rem auto;
        text-align: center;
    }

    div[data-testid="stTextInput"] > div {
        height: auto !important;
        background: transparent !important;
    }

    .stTextInput input {
        border-radius: 35px !important;
        padding: 20px 60px !important; 
        border: 12px solid var(--secondary) !important;
        font-size: 3.2rem !important; 
        font-weight: 900 !important;
        height: 160px !important; 
        background: white !important;
        color: var(--primary) !important;
        box-shadow: 0 50px 100px rgba(59, 130, 246, 0.5) !important;
        transition: all 0.6s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        text-align: center !important;
        line-height: normal !important;
    }
    
    .stTextInput input:focus {
        border-color: var(--neon-blue) !important;
        transform: scale(1.03) translateY(-8px);
        box-shadow: 0 60px 140px rgba(0, 210, 255, 0.6) !important;
    }

    /* THẺ CÁN BỘ MATRIX */
    .officer-matrix-card {
        background: #050505;
        padding: 25px;
        border-radius: 30px;
        border: 4px solid #111;
        margin-bottom: 25px;
        text-align: center;
        transition: all 0.4s ease;
    }
    .officer-matrix-card:hover { transform: translateY(-12px); }

    .card-nhai { border-color: #00d2ff !important; box-shadow: 0 0 15px rgba(0, 210, 255, 0.3); }
    .card-dat { border-color: #ffaa00 !important; box-shadow: 0 0 15px rgba(255, 170, 0, 0.3); }
    .card-hai { border-color: #39ff14 !important; box-shadow: 0 0 15px rgba(57, 255, 20, 0.3); }

    /* PDF PREVIEW STYLING */
    .pdf-container {
        border-radius: 20px;
        overflow: hidden;
        border: 4px solid #fff;
        box-shadow: 0 20px 50px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }

    /* BUTTONS */
    .stButton>button {
        border-radius: 50px !important;
        font-weight: 800 !important;
        padding: 0.8rem 2rem !important;
        text-transform: uppercase;
    }
    
    [data-testid="stSidebar"] { background-color: #020617; }
    </style>
    """, unsafe_allow_html=True)

# --- HÀM XỬ LÝ VĂN BẢN PDF (FIXED) ---
def get_pdf_files():
    return [f for f in os.listdir('.') if f.lower().endswith('.pdf')]

def display_pdf(file_path):
    try:
        with open(file_path, "rb") as f:
            base64_pdf = base64.b64encode(f.read()).decode('utf-8')
        
        # Sử dụng thẻ object + link dự phòng để tối ưu hiển thị
        pdf_display = f"""
        <div class="pdf-container">
            <object data="data:application/pdf;base64,{base64_pdf}" type="application/pdf" width="100%" height="800px">
                <div style="padding: 20px; text-align: center; background: #fee2e2; color: #ef4444; font-weight: bold; border-radius: 15px;">
                    ⚠️ Trình duyệt của bạn không thể xem PDF trực tiếp tại đây.<br>
                    Vui lòng sử dụng nút "Mở trong tab mới" hoặc "Tải file về" bên dưới.
                </div>
            </object>
        </div>
        """
        st.markdown(pdf_display, unsafe_allow_html=True)
        
        # Link mở tab mới (Cách an toàn nhất nếu Iframe bị chặn)
        href = f'<a href="data:application/pdf;base64,{base64_pdf}" target="_blank" style="text-decoration: none; background: #2563eb; color: white; padding: 10px 25px; border-radius: 50px; font-weight: 800; display: inline-block; margin-top: 10px;">🚀 MỞ VĂN BẢN TRONG TAB MỚI</a>'
        st.markdown(href, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Lỗi hiển thị PDF: {e}")

# --- HÀM TẢI DỮ LIỆU EXCEL ---
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

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<h1 style='color:white; text-align:center;'>🛡️ QUANTUM HUB</h1>", unsafe_allow_html=True)
    st.divider()
    tabs = ["📊 Tra cứu C12-TS", "🤖 Trợ lý AI Gemini", "📂 Văn bản PDF Mới", "📑 Cẩm nang Thủ tục", "🧮 Máy tính BHXH", "📍 Vị trí & Liên hệ"]
    for t in tabs:
        if st.button(t, use_container_width=True, key=f"tab_{t}"):
            st.session_state.current_tab = t
            st.rerun()
    st.divider()
    st.info("Phiên bản v17.1 - Fixed PDF View")

# --- HEADER (LED MARQUEE) ---
marquee_msg = "💎 CHÀO MỪNG ĐẾN VỚI HỆ THỐNG TRA CỨU BHXH THUẬN AN PHIÊN BẢN v17.1 • ĐÃ FIX LỖI XEM VĂN BẢN PDF • TÍCH HỢP TRÍ TUỆ NHÂN TẠO GEMINI • HÀNH CHÍNH CÔNG KỸ THUẬT SỐ •"
st.markdown(f"<div class='led-marquee'><marquee scrollamount='10'>{marquee_msg}</marquee></div>", unsafe_allow_html=True)

df = load_data()

if df is not None:
    # --- TAB 1: TRA CỨU ---
    if st.session_state.current_tab == "📊 Tra cứu C12-TS":
        if st.session_state.selected_unit is None:
            st.markdown("<div class='mega-search-wrapper'>", unsafe_allow_html=True)
            st.markdown("<h1 style='color:#1e3a8a; font-size:3.8rem; font-weight:900; margin-bottom:10px;'>🛡️ CỔNG TRA CỨU DỮ LIỆU</h1>", unsafe_allow_html=True)
            st.markdown("<p style='color:#64748b; font-size:1.6rem; margin-bottom:45px; font-weight:700;'>NHẬP MÃ ĐƠN VỊ HOẶC TÊN CÔNG TY</p>", unsafe_allow_html=True)
            query = st.text_input("Gateway", placeholder="🔍 Nhập để tìm kiếm...", label_visibility="collapsed")
            st.markdown("</div>", unsafe_allow_html=True)

            col_post, col_res, col_info = st.columns([0.8, 1.4, 1.1])
            with col_post:
                st.markdown("##### 📢 TIN TỨC")
                p_list = [{"t": "🛡️ AN SINH", "c": "Hưởng lương hưu hàng tháng là quyền lợi tốt nhất của NLĐ."}, {"t": "🏥 BHYT", "c": "Cấp thẻ BHYT điện tử ngay trên ứng dụng VssID."}, {"t": "🤰 THAI SẢN", "c": "BHXH Thuận An ưu tiên chi trả thai sản nhanh chóng."}]
                p = p_list[datetime.now().minute % len(p_list)]
                st.markdown(f"<div style='background:white; padding:40px; border-radius:35px; border:2px solid #e2e8f0; text-align:center; min-height:350px; display:flex; flex-direction:column; justify-content:center; box-shadow: 0 20px 40px rgba(0,0,0,0.06);'><h3 style='color:#1e3a8a; margin:0;'>{p['t']}</h3><p style='font-size:1.1rem; color:#64748b; margin:20px 0;'>{p['c']}</p><hr><small style='color:#ffaa00; font-weight:800;'>BHXH THUẬN AN</small></div>", unsafe_allow_html=True)

            with col_res:
                if query:
                    results = df[df['search_index'].str.contains(unidecode(query).lower(), na=False)].head(8)
                    for idx, row in results.iterrows():
                        with st.container():
                            ca, cb = st.columns([3.5, 1.5])
                            ca.markdown(f"<div style='background:white; padding:25px; border-radius:25px; border-left:12px solid #2563eb; margin-bottom:15px; box-shadow:0 8px 20px rgba(0,0,0,0.04);'><small style='color:#2563eb; font-weight:800;'>MÃ: {row.get('madvi')}</small><br><b style='font-size:1.4rem; color:#1e293b;'>{row.get('tendvi')}</b></div>", unsafe_allow_html=True)
                            if cb.button("XÁC NHẬN ➔", key=f"sel_{row.get('madvi')}_{idx}", use_container_width=True):
                                st.session_state.selected_unit = row.get('madvi'); st.session_state.show_loading = True; st.rerun()
                else: st.markdown("<br><center><img src='https://cdn-icons-png.flaticon.com/512/3772/3772274.png' width='160' style='opacity:0.2'></center>", unsafe_allow_html=True)

            with col_info:
                st.markdown("##### 👨‍💼 CÁN BỘ & ZALO")
                for off in OFFICERS:
                    st.markdown(f"<div class='officer-matrix-card {off['class']}'><div style='color:{off['color']}; font-weight:900; font-size:1.2rem;'>{off['name']}</div><div style='color:#aaa; font-size:0.85rem; margin:5px 0;'>Phụ trách: {off['scope']}</div><a href='tel:{off['phone'].replace('.','')}' style='text-decoration:none; color:white; font-weight:800; font-size:1.2rem;'>📱 {off['phone']}</a><br><a href='{off['zalo']}' target='_blank' style='background:#0068ff; color:white; padding:8px 20px; border-radius:50px; text-decoration:none; display:inline-block; margin-top:10px; font-weight:800;'>💬 Chat Zalo</a></div>", unsafe_allow_html=True)
                st.markdown("##### 🏦 SỐ TÀI KHOẢN BHXH THUẬN AN")
                st.markdown('<div style="background:#111; padding:15px; border-radius:15px; border-left:5px solid #00d2ff; color:#00d2ff; font-weight:800; font-size:0.8rem;">BIDV: 63510009867032<br>AGRIBANK: 5301202919045<br>VIETINBANK: 919035000003</div>', unsafe_allow_html=True)

        elif st.session_state.show_loading:
            with st.status("💎 KHỞI TẠO DASHBOARD...", expanded=True) as s:
                st.write("📡 Đồng bộ số liệu..."); time.sleep(0.7); s.update(label="Xong!", state="complete")
            st.session_state.show_loading = False; st.balloons(); st.rerun()

        else:
            unit_data = df[df['madvi'] == st.session_state.selected_unit].iloc[0]
            if st.button("⬅ QUAY LẠI"): st.session_state.selected_unit = None; st.rerun()
            st.markdown(f"<div style='background:white; padding:45px; border-radius:45px; border-left:25px solid #1e3a8a; box-shadow: 0 30px 80px rgba(0,0,0,0.08); margin-top:20px;'><h2 style='margin:0; color:#1e3a8a;'>🏢 {unit_data.get('tendvi')}</h2><p>Mã: <b>{unit_data.get('madvi')}</b> | Địa chỉ: {unit_data.get('diachi', 'N/A')}</p></div>", unsafe_allow_html=True)
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

    # --- TAB 2: AI GEMINI ---
    elif st.session_state.current_tab == "🤖 Trợ lý AI Gemini":
        st.markdown("## 🤖 TRỢ LÝ AI THÔNG MINH")
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]): st.markdown(msg["content"])
        if prompt := st.chat_input("Hỏi tôi về chính sách BHXH..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            with st.chat_message("assistant"):
                with st.spinner("Đang suy nghĩ..."):
                    response = call_gemini_with_retry(f"BHXH Thuận An: {prompt}")
                    st.markdown(response); st.session_state.messages.append({"role": "assistant", "content": response})

    # --- TAB 3: VĂN BẢN PDF (FIXED VIEW) ---
    elif st.session_state.current_tab == "📂 Văn bản PDF Mới":
        st.markdown("## 📂 THƯ VIỆN VĂN BẢN")
        pdf_files = get_pdf_files()
        if not pdf_files: st.warning("Hãy upload file .pdf lên GitHub để xem tại đây.")
        else:
            col1, col2 = st.columns([1, 2.5])
            with col1:
                st.write("##### Chọn văn bản:")
                for f in pdf_files:
                    if st.button(f"📄 {f}", use_container_width=True): st.session_state.active_pdf = f
            with col2:
                if 'active_pdf' in st.session_state:
                    st.write(f"##### Đang xem: {st.session_state.active_pdf}")
                    display_pdf(st.session_state.active_pdf)
                    with open(st.session_state.active_pdf, "rb") as f:
                        st.download_button("📥 TẢI VĂN BẢN VỀ MÁY", f, file_name=st.session_state.active_pdf, use_container_width=True)

    # --- CÁC TAB KHÁC ---
    elif st.session_state.current_tab == "📑 Cẩm nang Thủ tục": st.markdown("## 📑 CẨM NANG NGHIỆP VỤ")
    elif st.session_state.current_tab == "🧮 Máy tính BHXH": st.markdown("## 🧮 DỰ TOÁN MỨC ĐÓNG"); sal = st.number_input("Lương:", value=5000000); st.success(f"Tổng: {(sal*0.32):,.0f}đ")
    elif st.session_state.current_tab == "📍 Vị trí & Liên hệ": st.markdown("## 📍 LIÊN HỆ"); st.write("🏠 Thôn Thuận Sơn, Thuận An, Lâm Đồng.")

st.markdown("<br><hr><center style='color:#94a3b8; font-size:0.9rem; padding-bottom:60px;'>© 2026 BHXH CƠ SỞ THUẬN AN | Elite Quantum Hub v17.1</center>", unsafe_allow_html=True)
