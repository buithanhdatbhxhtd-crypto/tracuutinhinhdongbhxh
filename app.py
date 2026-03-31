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

# --- CẤU HÌNH API GEMINI (KHÔNG CẦN NHẬP KEY) ---
# Môi trường sẽ tự động cung cấp API Key qua biến hệ thống
api_key = "" 
genai.configure(api_key=api_key)

# --- CƠ CHẾ GỌI AI VỚI EXPONENTIAL BACKOFF (TỰ ĐỘNG THỬ LẠI) ---
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
                return "⚠️ Hệ thống AI đang bận hoặc quá tải. Vui lòng thử lại sau giây lát hoặc liên hệ cán bộ chuyên quản để được hỗ trợ trực tiếp."
            time.sleep(delay)
            delay *= 2

# --- CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="BHXH Thuận An - v17.0 Quantum Digital",
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

# --- TỔNG LỰC CSS (GIAO DIỆN QUANTUM DIGITAL v17.0) ---
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
        --neon-pink: #ff00ff;
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
        text-shadow: 0 0 10px #00ff00, 0 0 20px #00ff00;
        border-top: 3px solid var(--neon-blue);
    }

    /* SIÊU Ô TÌM KIẾM - KHỔNG LỒ & KHÔNG CHE CHỮ */
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

    /* THẺ CÁN BỘ MATRIX NEON */
    .officer-matrix-card {
        background: #050505;
        padding: 25px;
        border-radius: 30px;
        border: 4px solid #111;
        margin-bottom: 25px;
        text-align: center;
        transition: all 0.4s ease;
    }
    .officer-matrix-card:hover { 
        transform: translateY(-12px) rotate(1deg);
        border-color: #333;
    }

    .card-nhai { border-color: #00d2ff !important; box-shadow: 0 0 15px rgba(0, 210, 255, 0.3); }
    .card-dat { border-color: #ffaa00 !important; box-shadow: 0 0 15px rgba(255, 170, 0, 0.3); }
    .card-hai { border-color: #39ff14 !important; box-shadow: 0 0 15px rgba(57, 255, 20, 0.3); }

    /* PDF DOCUMENT CARD */
    .pdf-card {
        background: white;
        padding: 20px;
        border-radius: 20px;
        border-left: 10px solid #ef4444;
        box-shadow: 0 10px 20px rgba(0,0,0,0.05);
        margin-bottom: 15px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    /* BUTTONS */
    .stButton>button {
        border-radius: 50px !important;
        font-weight: 800 !important;
        padding: 0.8rem 2rem !important;
        transition: all 0.3s ease !important;
        text-transform: uppercase;
    }
    
    [data-testid="stSidebar"] { background-color: #020617; }
    </style>
    """, unsafe_allow_html=True)

# --- DỮ LIỆU CÁN BỘ ---
OFFICERS = [
    {"name": "Bà NGUYỄN THỊ NHÀI", "scope": "Xã Đức Lập, Xã Đắk Mil", "phone": "0846.39.29.29", "zalo": "https://zalo.me/0846392929", "class": "card-nhai", "color": "#00d2ff", "areas": ["duc lap", "dak mil", "đức lập", "đắk mil"]},
    {"name": "Ông BÙI THÀNH ĐẠT", "scope": "Xã Đắk Sắk, Xã Đắk Song", "phone": "0986.05.30.06", "zalo": "https://zalo.me/0986053006", "class": "card-dat", "color": "#ffaa00", "areas": ["dak sak", "dak song", "đắk sắk", "đắk song"]},
    {"name": "Ông HOÀNG SỸ HẢI", "scope": "Xã Thuận An", "phone": "0919.06.11.53", "zalo": "https://zalo.me/0919061153", "class": "card-hai", "color": "#39ff14", "areas": ["thuan an", "thuận an"]}
]

# --- HÀM TRA CỨU PDF ---
def get_pdf_files():
    files = [f for f in os.listdir('.') if f.lower().endswith('.pdf')]
    return files

def display_pdf(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

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

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown("<h1 style='color:white; text-align:center;'>🛡️ QUANTUM HUB</h1>", unsafe_allow_html=True)
    st.divider()
    tabs = ["📊 Tra cứu C12-TS", "🤖 Trợ lý AI Gemini", "📂 Văn bản PDF Mới", "📑 Cẩm nang Thủ tục", "🧮 Máy tính BHXH", "📍 Vị trí & Liên hệ"]
    for t in tabs:
        if st.button(t, use_container_width=True, key=f"tab_{t}"):
            st.session_state.current_tab = t
            st.rerun()
    st.divider()
    st.info("Phiên bản v17.0 - Quantum Digital")

# --- HEADER (LED MARQUEE RGB) ---
marquee_msg = "💎 CHÀO MỪNG ĐẾN VỚI HỆ THỐNG TRA CỨU BHXH THUẬN AN PHIÊN BẢN v17.0 QUANTUM DIGITAL • TÍCH HỢP TRÍ TUỆ NHÂN TẠO GEMINI VÀ THƯ VIỆN PDF TRỰC TUYẾN • ĐỊA CHỈ: THÔN THUẬN SƠN, XÃ THUẬN AN, TỈNH LÂM ĐỒNG •"
st.markdown(f"<div class='led-marquee'><marquee scrollamount='10'>{marquee_msg}</marquee></div>", unsafe_allow_html=True)

df = load_data()

if df is not None:
    
    # --- TAB 1: TRA CỨU C12-TS ---
    if st.session_state.current_tab == "📊 Tra cứu C12-TS":
        if st.session_state.selected_unit is None:
            st.markdown("<div class='mega-search-wrapper'>", unsafe_allow_html=True)
            st.markdown("<h1 style='color:#1e3a8a; font-size:3.8rem; font-weight:900; margin-bottom:10px;'>🛡️ CỔNG TRA CỨU DỮ LIỆU</h1>", unsafe_allow_html=True)
            st.markdown("<p style='color:#64748b; font-size:1.6rem; margin-bottom:45px; font-weight:700;'>NHẬP MÃ ĐƠN VỊ HOẶC TÊN CÔNG TY</p>", unsafe_allow_html=True)
            query = st.text_input("Gateway", placeholder="🔍 Nhập tại đây để xem số liệu C12-TS...", label_visibility="collapsed")
            st.markdown("</div>", unsafe_allow_html=True)

            col_post, col_res, col_info = st.columns([0.8, 1.4, 1.1])

            with col_post:
                st.markdown("##### 📢 TIN TỨC MỚI NHẤT")
                p_list = [
                    {"t": "🛡️ AN SINH 2026", "c": "Áp dụng mức đóng mới theo Nghị quyết Chính phủ từ ngày 01/01/2026."},
                    {"t": "🏥 TIỆN ÍCH VssID", "c": "Người dân có thể đổi mật khẩu VssID bằng khuôn mặt cực kỳ an toàn."},
                    {"t": "🤰 HỖ TRỢ THAI SẢN", "c": "BHXH Thuận An cam kết chi trả chế độ thai sản trong 3-5 ngày làm việc."}
                ]
                p = p_list[datetime.now().minute % len(p_list)]
                st.markdown(f"""
                    <div style='background:white; padding:40px; border-radius:35px; border:2.5px solid #e2e8f0; text-align:center; min-height:350px; display:flex; flex-direction:column; justify-content:center; box-shadow: 0 20px 40px rgba(0,0,0,0.06);'>
                        <h3 style='color:#1e3a8a; margin:0;'>{p['t']}</h3>
                        <p style='font-size:1.1rem; color:#64748b; margin:20px 0;'>{p['c']}</p>
                        <hr style='border: 0.5px solid #eee;'>
                        <small style='color:#ffaa00; font-weight:800;'>BHXH THUẬN AN ĐỒNG HÀNH</small>
                    </div>
                """, unsafe_allow_html=True)

            with col_res:
                if query:
                    clean_query = unidecode(query).lower()
                    results = df[df['search_index'].str.contains(clean_query, na=False)].head(8)
                    if not results.empty:
                        for idx, row in results.iterrows():
                            with st.container():
                                ca, cb = st.columns([3.5, 1.5])
                                ca.markdown(f"""
                                    <div style='background:white; padding:25px; border-radius:25px; border-left:12px solid #2563eb; margin-bottom:15px; box-shadow:0 8px 20px rgba(0,0,0,0.04);'>
                                        <small style='color:#2563eb; font-weight:800;'>MÃ: {row.get('madvi')}</small><br>
                                        <b style='font-size:1.4rem; color:#1e293b;'>{row.get('tendvi')}</b>
                                    </div>
                                """, unsafe_allow_html=True)
                                if cb.button("XÁC NHẬN ➔", key=f"sel_{row.get('madvi')}_{idx}", use_container_width=True):
                                    st.session_state.selected_unit = row.get('madvi')
                                    st.session_state.show_loading = True
                                    st.rerun()
                else:
                    st.markdown("<br><center><img src='https://cdn-icons-png.flaticon.com/512/3772/3772274.png' width='160' style='opacity:0.2'><h3 style='color:#94a3b8;'>Hệ thống Quantum v17.0 Sẵn sàng</h3></center>", unsafe_allow_html=True)

            with col_info:
                st.markdown("##### 👨‍💼 CÁN BỘ CHUYÊN QUẢN & ZALO")
                for off in OFFICERS:
                    st.markdown(f"""
                    <div class="officer-matrix-card {off['class']}">
                        <div style="color:{off['color']}; font-weight:900; font-size:1.2rem;">{off['name']}</div>
                        <div style="color:#aaa; font-size:0.85rem; margin:5px 0;">Phụ trách: {off['scope']}</div>
                        <a href="tel:{off['phone'].replace('.','')}" style="text-decoration:none; color:white; font-weight:800; font-size:1.2rem;">📱 {off['phone']}</a><br>
                        <a href="{off['zalo']}" target="_blank" style="background:#0068ff; color:white; padding:8px 20px; border-radius:50px; text-decoration:none; display:inline-block; margin-top:10px; font-weight:800; font-size:0.9rem;">💬 Chat Zalo</a>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("##### 🏦 SỐ TÀI KHOẢN CỦA BHXH CƠ SỞ THUẬN AN")
                st.markdown("""
                    <div style="background:#111; padding:15px; border-radius:15px; border-left:5px solid #00d2ff; margin-bottom:10px;">
                        <div style="color:#00d2ff; font-weight:800; font-size:0.8rem;">BIDV: 63510009867032</div>
                        <div style="color:#00d2ff; font-weight:800; font-size:0.8rem;">AGRIBANK: 5301202919045</div>
                        <div style="color:#00d2ff; font-weight:800; font-size:0.8rem;">VIETINBANK: 919035000003</div>
                    </div>
                """, unsafe_allow_html=True)

        # MÀN HÌNH LOADING
        elif st.session_state.show_loading:
            st.markdown("<br><br><br>", unsafe_allow_html=True)
            with st.status("💎 KHỞI TẠO QUANTUM DASHBOARD...", expanded=True) as status:
                st.write("📡 Kết nối vệ tinh dữ liệu BHXH...")
                time.sleep(0.7)
                st.write("🔄 Đồng bộ chỉ số tài chính...")
                time.sleep(0.5)
                status.update(label="TẢI DỮ LIỆU HOÀN TẤT!", state="complete")
            st.session_state.show_loading = False
            st.balloons()
            st.rerun()

        # DASHBOARD CHI TIẾT
        else:
            unit_data = df[df['madvi'] == st.session_state.selected_unit].iloc[0]
            unit_addr = unidecode(str(unit_data.get('diachi', ''))).lower()
            if st.button("⬅ QUAY LẠI TRANG TÌM KIẾM"): st.session_state.selected_unit = None; st.rerun()

            st.markdown(f"""
                <div style='background:white; padding:45px; border-radius:45px; border-left:25px solid #1e3a8a; box-shadow: 0 30px 80px rgba(0,0,0,0.08); margin-top:20px;'>
                    <h2 style='margin:0; color:#1e3a8a;'>🏢 {unit_data.get('tendvi')}</h2>
                    <p style='margin:10px 0 0 0; color:#64748b;'>Mã đơn vị: <b>{unit_data.get('madvi')}</b> | Địa chỉ: {unit_data.get('diachi', 'N/A')}</p>
                </div>
            """, unsafe_allow_html=True)

            col_l, col_r = st.columns([1.8, 1])
            with col_l:
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
                
                now = datetime.now()
                transfer_note = f"{unit_data.get('madvi')} {unit_data.get('tendvi')} đóng bhxh tháng {now.month} năm {now.year}"
                st.markdown(f"""
                    <div style='background:#eff6ff; padding:30px; border-radius:30px; border:4px dashed #2563eb; margin-top:30px; text-align:center;'>
                        <p style='color:#1e40af; font-weight:800; text-transform:uppercase;'>📝 CÚ PHÁP CHUYỂN KHOẢN CHUẨN:</p>
                        <h3 style='color:#1e3a8a; font-family:monospace; font-size:1.8rem;'>{transfer_note}</h3>
                    </div>
                """, unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

            with col_r:
                rate = min(round((unit_data.get('so_da_dong', 0) / unit_data.get('so_phai_dong', 1)) * 100, 1), 100)
                fig = go.Figure(go.Indicator(mode = "gauge+number", value = rate, title = {'text': "TỶ LỆ HOÀN THÀNH (%)"}, gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': "#1e40af"}}))
                st.plotly_chart(fig, use_container_width=True)
                for off in OFFICERS:
                    if any(area in unit_addr for area in off['areas']):
                        st.markdown(f"<div class='officer-matrix-card {off['class']}' style='background:#000;'><small style='color:#39ff14; font-weight:900;'>PHỤ TRÁCH TRỰC TIẾP</small><h4 style='color:{off['color']}; margin:10px 0;'>{off['name']}</h4><a href='tel:{off['phone'].replace('.','')}' style='color:white; text-decoration:none; font-weight:800; font-size:1.5rem;'>📱 {off['phone']}</a><br><a href='{off['zalo']}' target='_blank' style='background:#0068ff; color:white; padding:8px 30px; border-radius:50px; text-decoration:none; display:inline-block; margin-top:10px; font-weight:800;'>CHAT ZALO</a></div>", unsafe_allow_html=True)

    # --- TAB 2: AI GEMINI ---
    elif st.session_state.current_tab == "🤖 Trợ lý AI Gemini":
        st.markdown("## 🤖 TRỢ LÝ AI THÔNG MINH (GEMINI 2.5)")
        st.write("Hỏi AI bất kỳ điều gì về chính sách BHXH, BHYT, BHTN hoặc thủ tục hành chính.")
        
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]): st.markdown(msg["content"])

        if prompt := st.chat_input("Ví dụ: Mức lương cơ sở 2026 là bao nhiêu?"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            with st.chat_message("assistant"):
                with st.spinner("AI đang trích xuất dữ liệu..."):
                    response = call_gemini_with_retry(f"Bạn là chuyên gia BHXH Thuận An. Hãy trả lời câu hỏi: {prompt}")
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})

    # --- TAB 3: VĂN BẢN PDF ---
    elif st.session_state.current_tab == "📂 Văn bản PDF Mới":
        st.markdown("## 📂 THƯ VIỆN VĂN BẢN BHXH THUẬN AN & TỈNH")
        pdf_files = get_pdf_files()
        if not pdf_files:
            st.warning("Hiện chưa có file PDF nào trong thư mục. Hãy upload file .pdf lên GitHub để xem tại đây.")
        else:
            col1, col2 = st.columns([1, 2])
            with col1:
                st.write("##### Danh sách văn bản:")
                for f in pdf_files:
                    if st.button(f"📄 {f}", use_container_width=True):
                        st.session_state.active_pdf = f
            with col2:
                if 'active_pdf' in st.session_state:
                    st.write(f"##### Đang xem: {st.session_state.active_pdf}")
                    display_pdf(st.session_state.active_pdf)
                    with open(st.session_state.active_pdf, "rb") as f:
                        st.download_button("📥 Tải file về máy", f, file_name=st.session_state.active_pdf)

    # --- CÁC TAB CÒN LẠI ---
    elif st.session_state.current_tab == "📑 Cẩm nang Thủ tục":
        st.markdown("## 📑 CẨM NANG NGHIỆP VỤ"); st.info("Sổ tay hướng dẫn báo tăng/giảm lao động, giải quyết thai sản, hưu trí...")
    elif st.session_state.current_tab == "🧮 Máy tính BHXH":
        st.markdown("## 🧮 DỰ TOÁN MỨC ĐÓNG"); sal = st.number_input("Lương đóng BHXH:", value=5000000); st.success(f"Tổng tiền đóng (32%): **{(sal*0.32):,.0f}đ**")
    elif st.session_state.current_tab == "📍 Vị trí & Liên hệ":
        st.markdown("## 📍 BHXH CƠ SỞ THUẬN AN"); st.write("🏠 Thôn Thuận Sơn, xã Thuận An, tỉnh Lâm Đồng."); st.write("📞 Hotline: 1900 9068")

st.markdown("<br><hr><center style='color:#94a3b8; font-size:0.9rem; padding-bottom:60px;'>© 2026 BHXH CƠ SỞ THUẬN AN | Elite Quantum Hub v17.0 Beyond AI</center>", unsafe_allow_html=True)
