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
    page_title="BHXH Thuận An - v19.1 Radiant Quantum",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CẤU HÌNH AI GEMINI (MODEL STABLE) ---
api_key = st.secrets.get("GOOGLE_API_KEY", os.environ.get("GOOGLE_API_KEY", ""))
if api_key:
    genai.configure(api_key=api_key)

def get_ai_response(prompt):
    if not api_key:
        return "⚠️ **Cấu hình AI:** Vui lòng thêm `GOOGLE_API_KEY` vào Streamlit Secrets để kích hoạt."
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        system_instruction = "Bạn là trợ lý ảo cao cấp của cơ quan Bảo hiểm xã hội cơ sở Thuận An, Lâm Đồng. Hãy hỗ trợ câu hỏi chuyên nghiệp, ngắn gọn, dễ hiểu."
        full_prompt = f"{system_instruction}\n\nĐơn vị hỏi: {prompt}"
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        return f"⚠️ **AI đang bận:** {str(e)[:100]}... Quý đơn vị vui lòng nhắn tin Zalo cho cán bộ nhé!"

# --- KHỞI TẠO STATE ---
if 'selected_unit' not in st.session_state:
    st.session_state.selected_unit = None
if 'current_tab' not in st.session_state:
    st.session_state.current_tab = "📊 Tra cứu C12-TS"
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if 'active_pdf' not in st.session_state:
    st.session_state.active_pdf = None

# --- TỔNG LỰC CSS (GIAO DIỆN RADIANT v19.1) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    :root {
        --primary: #1e3a8a;
        --secondary: #2563eb;
        --accent: #0ea5e9;
        --neon-blue: #00d2ff;
        --neon-green: #10b981;
        --bg-gradient: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
    }

    * { font-family: 'Plus Jakarta Sans', sans-serif; }
    
    .stApp {
        background: var(--bg-gradient);
    }

    /* ĐỒNG HỒ THỜI GIAN THỰC */
    .live-clock-container {
        background: white;
        padding: 10px 20px;
        border-radius: 50px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        display: inline-flex;
        align-items: center;
        margin-bottom: 20px;
        border: 2px solid var(--secondary);
    }
    .clock-text {
        font-size: 1.1rem;
        font-weight: 800;
        color: var(--primary);
    }

    /* BẢNG LED RGB CAO CẤP */
    .led-marquee {
        background: #000;
        color: #00ff00;
        padding: 15px 0;
        font-weight: 800;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0, 255, 0, 0.2);
        border: 2px solid #333;
        margin-bottom: 30px;
        font-family: 'Courier New', Courier, monospace;
        font-size: 1.3rem;
        text-shadow: 0 0 10px #00ff00;
        border-top: 3px solid var(--neon-blue);
    }

    /* SIÊU Ô TÌM KIẾM GATEWAY v19.1 */
    .gateway-container {
        max-width: 1000px;
        margin: 0 auto 3rem auto;
        text-align: center;
    }

    div[data-testid="stTextInput"] > div {
        height: auto !important;
        background: transparent !important;
    }

    .stTextInput input {
        border-radius: 30px !important;
        padding: 15px 45px !important; 
        border: 10px solid var(--secondary) !important;
        font-size: 2.5rem !important; 
        font-weight: 900 !important;
        height: 130px !important; 
        background: white !important;
        color: var(--primary) !important;
        box-shadow: 0 30px 60px rgba(59, 130, 246, 0.3) !important;
        text-align: center !important;
        line-height: normal !important;
        transition: all 0.4s ease;
    }
    
    .stTextInput input:focus {
        border-color: var(--neon-blue) !important;
        transform: scale(1.02);
        box-shadow: 0 40px 100px rgba(0, 210, 255, 0.4) !important;
    }

    /* THẺ DASHBOARD TRẮNG RỰC RỠ */
    .radiant-card {
        background: white;
        padding: 25px;
        border-radius: 30px;
        box-shadow: 0 15px 40px rgba(0,0,0,0.06);
        border: 1px solid #f1f5f9;
        transition: all 0.3s ease;
    }
    .radiant-card:hover { transform: translateY(-5px); box-shadow: 0 20px 50px rgba(0,0,0,0.1); }

    /* THẺ CÁN BỘ & BANK MATRIX (BRIGHT MODE) */
    .matrix-card-bright {
        background: white;
        padding: 22px;
        border-radius: 25px;
        border: 3px solid #f1f5f9;
        margin-bottom: 20px;
        text-align: center;
        box-shadow: 0 10px 25px rgba(0,0,0,0.04);
    }
    .matrix-card-bright:hover { border-color: var(--secondary); transform: scale(1.02); }

    /* PDF VIEWER RADIANT */
    .pdf-bright-container {
        border-radius: 35px;
        border: 12px solid white;
        box-shadow: 0 40px 100px rgba(0,0,0,0.12);
        overflow: hidden;
        background: #f8fafc;
        height: 800px;
        width: 100%;
        margin-top: 20px;
    }

    /* SIDEBAR GLASSMORPISM */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e3a8a 0%, #0f172a 100%);
    }
    [data-testid="stSidebar"] .stButton>button {
        background: rgba(255, 255, 255, 0.05) !important;
        color: white !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
    }
    [data-testid="stSidebar"] .stButton>button:hover {
        background: var(--secondary) !important;
        border-color: var(--neon-blue) !important;
    }

    /* BUTTONS MAIN AREA */
    .stButton>button {
        border-radius: 50px !important;
        font-weight: 800 !important;
        text-transform: uppercase;
        padding: 0.8rem 2.5rem !important;
        transition: all 0.3s ease !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- DỮ LIỆU CÁN BỘ CHUYÊN QUẢN ---
OFFICERS = [
    {"name": "Bà NGUYỄN THỊ NHÀI", "communes": "Xã Đức Lập, Xã Đắk Mil", "areas": ["đức lập", "duc lap", "đắk mil", "dak mil"], "phone": "0846.39.29.29", "zalo": "https://zalo.me/0846392929", "color": "#2563eb"},
    {"name": "Ông BÙI THÀNH ĐẠT", "communes": "Xã Đắk Sắk, Xã Đắk Song", "areas": ["đắk sắk", "dak sak", "đắk song", "dak song"], "phone": "0986.05.30.06", "zalo": "https://zalo.me/0986053006", "color": "#f59e0b"},
    {"name": "Ông HOÀNG SỸ HẢI", "communes": "Xã Thuận An", "areas": ["thuận an", "thuan an"], "phone": "0919.06.11.53", "zalo": "https://zalo.me/0919061153", "color": "#10b981"}
]

# --- HÀM XỬ LÝ VĂN BẢN PDF ---
def get_local_pdfs():
    return [f for f in os.listdir('.') if f.lower().endswith('.pdf')]

def embed_pdf_radiant(file_path):
    try:
        with open(file_path, "rb") as f:
            pdf_bytes = f.read()
            base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
        
        # Nhúng bằng thẻ object
        pdf_display = f"""
        <div class="pdf-bright-container">
            <object data="data:application/pdf;base64,{base64_pdf}" type="application/pdf" width="100%" height="100%">
                <div style="padding: 100px 40px; text-align: center; background: white; height: 100%;">
                    <h2 style="color: #ef4444;">⚠️ TRÌNH DUYỆT ĐANG CHẶN PDF</h2>
                    <p style="font-size: 1.2rem; color: #64748b;">Do chính sách bảo mật của Chrome/Edge, Quý đơn vị vui lòng nhấn nút <b>"TẢI VĂN BẢN"</b> hoặc <b>"MỞ TAB MỚI"</b> bên dưới để xem nội dung.</p>
                    <img src="https://cdn-icons-png.flaticon.com/512/337/337946.png" width="150" style="opacity: 0.3; margin-top: 20px;">
                </div>
            </object>
        </div>
        """
        st.markdown(pdf_display, unsafe_allow_html=True)
        
        st.write("<br>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            st.download_button(label="📥 TẢI VĂN BẢN VỀ MÁY", data=pdf_bytes, file_name=file_path, mime="application/pdf", use_container_width=True)
        with c2:
            st.markdown(f'<a href="data:application/pdf;base64,{base64_pdf}" target="_blank" style="text-decoration:none; background:#1e3a8a; color:white; padding:12px; border-radius:50px; font-weight:900; display:block; text-align:center; box-shadow: 0 10px 20px rgba(30,58,138,0.2);">🚀 XEM TRÊN TAB MỚI</a>', unsafe_allow_html=True)
        return True
    except Exception as e:
        st.error(f"Lỗi: {e}")
        return False

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

# --- SIDEBAR RADIANT ---
with st.sidebar:
    st.markdown("<h1 style='color:white; text-align:center; font-size: 1.8rem; font-weight: 900;'>🛡️ QUANTUM HUB</h1>", unsafe_allow_html=True)
    st.divider()
    
    menu = ["📊 Tra cứu C12-TS", "🤖 Trợ lý AI Gemini", "📂 Thư viện Văn bản", "📑 Cẩm nang Nghiệp vụ", "🧮 Máy tính BHXH", "📍 Liên hệ BHXH"]
    selected_tab = st.radio("CÔNG CỤ TIỆN ÍCH", menu, label_visibility="collapsed")
    st.session_state.current_tab = selected_tab
    
    st.divider()
    # Hiển thị ngày tháng trong sidebar
    now = datetime.now()
    st.markdown(f"""
        <div style='background:rgba(255,255,255,0.1); padding:15px; border-radius:20px; text-align:center; color:white;'>
            <small>HÔM NAY</small><br>
            <b style='font-size:1.2rem;'>{now.strftime('%d/%m/%Y')}</b>
        </div>
    """, unsafe_allow_html=True)
    st.caption("v19.1 Radiant | Elite Digital")

# --- HEADER & LIVE CLOCK ---
col_head, col_clock = st.columns([3, 1])
with col_head:
    marquee_msg = "🛡️ CHÀO MỪNG QUÝ ĐƠN VỊ ĐẾN VỚI HỆ THỐNG TRA CỨU BHXH THUẬN AN PHIÊN BẢN v19.1 RADIANT QUANTUM • TRA CỨU NHANH - CHÍNH XÁC - MINH BẠCH •"
    st.markdown(f"<div class='led-marquee'><marquee scrollamount='10'>{marquee_msg}</marquee></div>", unsafe_allow_html=True)
with col_clock:
    # Hiển thị thời gian thực (tĩnh theo mỗi lần tương tác trong Streamlit)
    st.markdown(f"""
        <div class='live-clock-container'>
            <span class='clock-text'>⏰ {datetime.now().strftime('%H:%M:%S')}</span>
        </div>
    """, unsafe_allow_html=True)

df = load_data_engine()

if df is not None:
    # --- TAB 1: TRA CỨU ---
    if st.session_state.current_tab == "📊 Tra cứu C12-TS":
        if st.session_state.selected_unit is None:
            st.markdown("<div class='gateway-container'>", unsafe_allow_html=True)
            st.markdown("<h1 style='color:#1e3a8a; font-size:4rem; font-weight:900;'>🛡️ CỔNG TRA CỨU DỮ LIỆU</h1>", unsafe_allow_html=True)
            st.markdown("<p style='color:#64748b; font-size:1.5rem; font-weight:700;'>MỜI NHẬP MÃ ĐƠN VỊ HOẶC TÊN CÔNG TY</p>", unsafe_allow_html=True)
            query = st.text_input("Gateway", placeholder="Gõ mã hoặc tên vào đây...", label_visibility="collapsed")
            st.markdown("</div>", unsafe_allow_html=True)

            col_news, col_res, col_off = st.columns([0.8, 1.4, 1.1])
            with col_news:
                st.markdown("##### 📢 TIN TỨC MỚI")
                st.markdown("<div class='radiant-card' style='text-align:center; min-height:350px; display:flex; flex-direction:column; justify-content:center;'><h4 style='color:#1e3a8a;'>🛡️ AN SINH</h4><p style='color:#64748b;'>Hưởng lương hưu hàng tháng là giải pháp an toàn nhất cho tương lai.</p><hr><small style='color:#f59e0b; font-weight:800;'>BHXH THUẬN AN ĐỒNG HÀNH</small></div>", unsafe_allow_html=True)

            with col_res:
                if query:
                    clean_query = unidecode(query).lower()
                    results = df[df['search_index'].str.contains(clean_query, na=False)].head(8)
                    for idx, row in results.iterrows():
                        with st.container():
                            ca, cb = st.columns([3.5, 1.5])
                            ca.markdown(f"<div class='radiant-card' style='padding:20px; border-left:12px solid #2563eb; margin-bottom:12px;'><small style='color:#2563eb; font-weight:800;'>MÃ: {row.get('madvi')}</small><br><b style='font-size:1.3rem; color:#1e293b;'>{row.get('tendvi')}</b></div>", unsafe_allow_html=True)
                            if cb.button("XÁC NHẬN ➔", key=f"sel_{row.get('madvi')}_{idx}", use_container_width=True):
                                st.session_state.selected_unit = row.get('madvi'); st.rerun()
                else: st.markdown("<br><center><img src='https://cdn-icons-png.flaticon.com/512/3772/3772274.png' width='160' style='opacity:0.2'></center>", unsafe_allow_html=True)

            with col_off:
                st.markdown("##### 👨‍💼 LIÊN HỆ CÁN BỘ THEO XÃ")
                for off in OFFICERS:
                    st.markdown(f"""
                    <div class="matrix-card-bright">
                        <small style="color:{off['color']}; font-weight:800; text-transform:uppercase;">{off['communes']}</small>
                        <div style="color:var(--primary); font-weight:900; font-size:1.2rem; margin-top:5px;">{off['name']}</div>
                        <a href="tel:{off['phone'].replace('.','')}" style="text-decoration:none; color:var(--primary); font-weight:800; font-size:1.2rem; display:block; margin:8px 0;">📱 {off['phone']}</a>
                        <a href="{off['zalo']}" target="_blank" style="background:#0068ff; color:white; padding:8px 25px; border-radius:50px; text-decoration:none; display:inline-block; font-weight:900; font-size:0.8rem; box-shadow: 0 4px 10px rgba(0,104,255,0.2);">💬 CHAT ZALO</a>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown("##### 🏦 SỐ TÀI KHOẢN CỦA BHXH THUẬN AN")
                st.markdown('<div class="radiant-card" style="padding:15px; border-left:8px solid #00d2ff; background: #f0f9ff;"><b style="color:#1e3a8a; font-size:0.9rem;">BIDV: 63510009867032<br>AGRIBANK: 5301202919045<br>VIETINBANK: 919035000003</b></div>', unsafe_allow_html=True)

        else:
            # DASHBOARD CHI TIẾT
            unit_data = df[df['madvi'] == st.session_state.selected_unit].iloc[0]
            unit_addr = unidecode(str(unit_data.get('diachi', ''))).lower()
            if st.button("⬅ QUAY LẠI TRANG TÌM KIẾM"): st.session_state.selected_unit = None; st.rerun()
            st.markdown(f"<div class='radiant-card' style='border-left:25px solid #1e3a8a; margin-top:20px;'><h2 style='margin:0; color:#1e3a8a;'>🏢 {unit_data.get('tendvi')}</h2><p style='margin:5px 0;'>Mã đơn vị: <b>{unit_data.get('madvi')}</b> | Địa chỉ: {unit_data.get('diachi', 'N/A')}</p></div>", unsafe_allow_html=True)
            
            cl, cr = st.columns([1.8, 1])
            with cl:
                st.markdown("<div class='radiant-card' style='margin-top:30px;'>", unsafe_allow_html=True)
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
                for off in OFFICERS:
                    if any(area in unit_addr for area in off['areas']):
                        st.markdown(f"<div class='radiant-card' style='background:linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%); color:white; text-align:center;'><small style='color:#39ff14; font-weight:900;'>PHỤ TRÁCH TRỰC TIẾP</small><h4 style='color:white; margin:10px 0;'>{off['name']}</h4><a href='tel:{off['phone'].replace('.','')}' style='color:white; text-decoration:none; font-weight:800; font-size:1.5rem;'>📱 {off['phone']}</a><br><a href='{off['zalo']}' target='_blank' style='background:white; color:#0068ff; padding:8px 30px; border-radius:50px; text-decoration:none; display:inline-block; margin-top:15px; font-weight:900;'>CHAT ZALO</a></div>", unsafe_allow_html=True)

    # --- TAB 2: AI GEMINI ---
    elif st.session_state.current_tab == "🤖 Trợ lý AI Gemini":
        st.markdown("## 🧠 TRỢ LÝ AI THÔNG MINH (GEMINI 1.5)")
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]): st.markdown(msg["content"])
        if prompt := st.chat_input("Hỏi AI bất cứ điều gì..."):
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            with st.chat_message("assistant"):
                with st.spinner("AI đang tư duy..."):
                    resp = get_ai_response(prompt)
                    st.markdown(resp); st.session_state.chat_history.append({"role": "assistant", "content": resp})

    # --- TAB 3: VĂN BẢN PDF (RADIANT VIEW) ---
    elif st.session_state.current_tab == "📂 Thư viện Văn bản":
        st.markdown("## 📂 THƯ VIỆN VĂN BẢN KỸ THUẬT SỐ")
        pdfs = get_local_pdfs()
        if not pdfs: st.warning("Hãy tải file .pdf lên thư mục GitHub.")
        else:
            c1, c2 = st.columns([1, 2.5])
            with c1:
                st.write("##### DANH SÁCH VĂN BẢN:")
                for f in pdfs:
                    if st.button(f"📄 {f}", use_container_width=True, key=f"pdf_{f}"):
                        st.session_state.active_pdf = f
            with c2:
                if st.session_state.active_pdf:
                    st.success(f"📌 ĐANG XEM: {st.session_state.active_pdf}")
                    embed_pdf_radiant(st.session_state.active_pdf)

    # --- CÁC TAB KHÁC ---
    elif st.session_state.current_tab == "📑 Cẩm nang Nghiệp vụ": st.markdown("## 📑 CẨM NANG NGHIỆP VỤ")
    elif st.session_state.current_tab == "🧮 Máy tính BHXH":
        st.markdown("## 🧮 DỰ TOÁN ĐÓNG BHXH"); sal = st.number_input("Lương đóng:", value=5000000); st.success(f"Tổng đóng (32%): {(sal*0.32):,.0f}đ")
    elif st.session_state.current_tab == "📍 Liên hệ BHXH":
        st.markdown("## 📍 THÔNG TIN LIÊN HỆ"); st.write("🏠 Cơ sở: Thôn Thuận Sơn, Thuận An, Đắk Mil, Đắk Nông."); st.write("📞 Hotline: 1900 9068")

st.markdown("<br><hr><center style='color:#94a3b8; font-size:0.9rem; padding-bottom:60px;'>© 2026 BHXH CƠ SỞ THUẬN AN | Radiant Quantum Hub v19.1</center>", unsafe_allow_html=True)
