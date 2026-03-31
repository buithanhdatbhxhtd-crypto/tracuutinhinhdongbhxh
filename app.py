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
    page_title="BHXH Thuận An - v24.0 Ultimate Pro",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CẤU HÌNH AI GEMINI PRO 1.5 ---
api_key = st.secrets.get("GOOGLE_API_KEY", os.environ.get("GOOGLE_API_KEY", ""))
if api_key:
    try:
        genai.configure(api_key=api_key)
    except: pass

def get_ai_response(prompt, context=""):
    if not api_key: return "⚠️ **Chưa cấu hình API Key:** Vui lòng thêm `GOOGLE_API_KEY` vào Streamlit Secrets."
    try:
        model = genai.GenerativeModel('gemini-1.5-pro')
        system_instruction = "Bạn là trợ lý AI cao cấp (Pro Edition) của Bảo hiểm xã hội cơ sở Thuận An, Lâm Đồng. Bạn am hiểu sâu sắc luật BHXH, BHYT. Trả lời tận tâm, chính xác."
        
        # Context-Aware: Bơm dữ liệu đơn vị vào AI nếu có
        if context:
            full_prompt = f"{system_instruction}\n\nThông tin đơn vị đang tra cứu:\n{context}\n\nĐơn vị hỏi: {prompt}"
        else:
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

# --- TỔNG LỰC CSS (GIAO DIỆN PRO MASTERPIECE v24.0) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    :root {
        --primary: #1e3a8a;
        --secondary: #2563eb;
        --accent: #0ea5e9;
        --neon-blue: #00d2ff;
        --glass: rgba(255, 255, 255, 0.9);
    }

    * { font-family: 'Plus Jakarta Sans', sans-serif; box-sizing: border-box; }
    
    .stApp { background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%); }

    /* --- SIDEBAR ĐẲNG CẤP --- */
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #0f172a 0%, #1e3a8a 100%) !important; }
    [data-testid="stSidebar"] .stRadio label p {
        color: #ffffff !important; font-size: 1.25rem !important; font-weight: 800 !important;
        text-shadow: 2px 2px 5px rgba(0,0,0,0.5) !important; padding: 8px 0 !important;
    }
    [data-testid="stSidebar"] h1 { color: white !important; text-shadow: 0 0 15px var(--neon-blue); }

    /* BẢNG LED RGB */
    .led-marquee {
        background: #000; color: #39ff14; padding: 12px 0; font-weight: 800; border-radius: 15px;
        box-shadow: 0 10px 30px rgba(57, 255, 20, 0.15); border: 2px solid #333; margin-bottom: 25px;
        font-family: 'Courier New', Courier, monospace; font-size: 1.35rem; letter-spacing: 1px;
    }

    /* SIÊU Ô TÌM KIẾM GATEWAY v24.0 */
    .gateway-container { max-width: 1000px; margin: 0 auto 1.5rem auto; text-align: center; }
    div[data-testid="stTextInput"] > div { height: auto !important; background: transparent !important; padding: 0 !important; border:none !important; box-shadow:none !important; }
    
    .stTextInput input {
        border-radius: 20px !important;
        padding: 30px 45px 30px 100px !important; 
        border: 8px solid var(--secondary) !important;
        font-size: 2.8rem !important; font-weight: 900 !important;
        min-height: 140px !important; line-height: 1.3 !important;
        background: white url('https://cdn-icons-png.flaticon.com/512/622/622669.png') no-repeat 30px center !important;
        background-size: 45px !important;
        color: var(--primary) !important;
        box-shadow: 0 30px 80px rgba(37, 99, 235, 0.25) !important;
        display: block !important;
    }
    .stTextInput input:focus { border-color: var(--neon-blue) !important; transform: scale(1.02); box-shadow: 0 40px 100px rgba(0, 210, 255, 0.4) !important; }

    /* DASHBOARD RADIANT CARDS */
    .crystal-card {
        background: white; padding: 30px; border-radius: 25px; box-shadow: 0 15px 40px rgba(0,0,0,0.05);
        border: 1px solid #f1f5f9; transition: all 0.3s; text-align: center; position: relative; overflow: hidden;
    }
    .crystal-card:hover { transform: translateY(-8px); box-shadow: 0 25px 60px rgba(37, 99, 235, 0.1); border-color: #cbd5e1; }
    .metric-val { font-size: 2.4rem; font-weight: 900; color: var(--primary); margin-top: 5px; }
    .metric-lbl { font-size: 0.95rem; font-weight: 800; color: #64748b; text-transform: uppercase; letter-spacing: 1px; }

    /* BANK CARD VIP */
    .bank-card {
        background: linear-gradient(135deg, #fffbeb 0%, #fff7ed 100%);
        border: 3px solid #fbbf24; border-radius: 25px; padding: 30px;
        box-shadow: 0 20px 50px rgba(245, 158, 11, 0.15); margin-top: 20px;
    }
    
    /* STYLE CHO CODE BLOCK (NÚT COPY) */
    .stCodeBlock { background: transparent !important; }
    .stCodeBlock code { font-size: 1.4rem !important; font-weight: 900 !important; color: #1e3a8a !important; }

    .stButton>button {
        border-radius: 50px !important; font-weight: 800 !important; text-transform: uppercase;
        padding: 0.8rem 3rem !important; transition: all 0.3s ease !important;
    }
    .btn-main > div > button {
        background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%) !important; color: white !important;
        font-size: 1.5rem !important; height: 75px !important; width: 80% !important; border: none !important;
        box-shadow: 0 15px 35px rgba(30, 58, 138, 0.3) !important;
    }
    .btn-main > div > button:hover { transform: scale(1.05) !important; box-shadow: 0 20px 45px rgba(30, 58, 138, 0.5) !important; }
    </style>
    """, unsafe_allow_html=True)

# --- ĐỒNG HỒ REAL-TIME (JS) ---
def live_clock():
    components.html("""
    <div style="font-family: 'Plus Jakarta Sans', sans-serif; background: rgba(255,255,255,0.1); color: white; padding: 20px; border-radius: 25px; text-align: center; border: 1px solid rgba(255,255,255,0.2); box-shadow: 0 10px 30px rgba(0,0,0,0.2);">
        <div id="day-str" style="font-size: 1rem; font-weight: 700; opacity: 0.9; margin-bottom: 5px; color: #00d2ff;"></div>
        <div id="time-str" style="font-size: 2.3rem; font-weight: 900; letter-spacing: 2px;"></div>
    </div>
    <script>
        function updateClock() {
            const now = new Date();
            const opts = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
            document.getElementById('day-str').innerText = now.toLocaleDateString('vi-VN', opts).toUpperCase();
            const h = String(now.getHours()).padStart(2, '0');
            const m = String(now.getMinutes()).padStart(2, '0');
            const s = String(now.getSeconds()).padStart(2, '0');
            document.getElementById('time-str').innerText = h + ":" + m + ":" + s;
        }
        setInterval(updateClock, 1000); updateClock();
    </script>
    """, height=160)

# --- DATA HUB (CÁN BỘ) ---
OFFICERS = [
    {"name": "Bà NGUYỄN THỊ NHÀI", "communes": "Xã Đức Lập, Xã Đắk Mil", "keywords": ["duc lap", "đức lập", "dak mil", "đắk mil", "dc0039c"], "phone": "0846.39.29.29", "zalo": "https://zalo.me/0846392929", "color": "#00d2ff"},
    {"name": "Ông BÙI THÀNH ĐẠT", "communes": "Xã Đắk Sắk, Xã Đắk Song", "keywords": ["dak sak", "đắk sắk", "dak song", "đắk song"], "phone": "0986.05.30.06", "zalo": "https://zalo.me/0986053006", "color": "#ffaa00"},
    {"name": "Ông HOÀNG SỸ HẢI", "communes": "Xã Thuận An", "keywords": ["thuan an", "thuận an"], "phone": "0919.06.11.53", "zalo": "https://zalo.me/0919061153", "color": "#39ff14"}
]

# --- HÀM RENDER NGÂN HÀNG VIP (ONE-CLICK COPY) ---
def render_vip_bank_accounts(unit_code="[Mã Đơn Vị]", unit_name="[Tên Đơn Vị]"):
    st.markdown("""
        <div class="bank-card">
            <h2 style='color:#b45309; margin-top:0; font-weight: 900; text-align: center; font-size: 2rem;'>🏦 THÔNG TIN CHUYỂN KHOẢN ĐÓNG BHXH</h2>
            <p style='color:#475569; font-size:1.1rem; text-align: center; font-weight: 600;'>Kế toán đơn vị vui lòng nhấn vào biểu tượng <b>Copy</b> ở góc phải mỗi số tài khoản để sao chép nhanh.</p>
        </div>
    """, unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.info("🏦 **NGÂN HÀNG BIDV**")
        st.code("63510009867032", language="text")
    with c2:
        st.success("🏦 **NGÂN HÀNG AGRIBANK**")
        st.code("5301202919045", language="text")
    with c3:
        st.warning("🏦 **NGÂN HÀNG VIETINBANK**")
        st.code("919035000003", language="text")
        
    st.markdown(f"""
        <div style='background:#eff6ff; padding:20px; border-radius:15px; border:2px dashed #3b82f6; text-align:center; margin-top: 10px;'>
            <div style='color:#1e40af; font-weight:800; font-size:1rem; margin-bottom: 10px;'>📝 NỘI DUNG CHUYỂN KHOẢN CHUẨN XÁC NẤT:</div>
            <code style='font-size: 1.5rem; color: #1e3a8a; font-weight: 900; background: white; padding: 10px 20px; border-radius: 10px;'>{unit_code} {unit_name} dong bhxh thang {datetime.now().month} nam {datetime.now().year}</code>
        </div>
    """, unsafe_allow_html=True)

# --- HÀM XUẤT DATA SANG CSV ---
@st.cache_data
def convert_df(df_export):
    return df_export.to_csv(index=False).encode('utf-8-sig')

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
    st.markdown("<h1 style='text-align:center;'>🛡️ QUANTUM PRO</h1>", unsafe_allow_html=True)
    st.divider()
    menu = ["📊 Tra cứu C12-TS", "🤖 Trợ lý AI Gemini Pro", "📂 Thư viện Văn bản", "📑 Cẩm nang Nghiệp vụ", "🧮 Máy tính BHXH", "📍 Liên hệ BHXH"]
    st.session_state.current_tab = st.radio("CHỨC NĂNG HỆ THỐNG", menu, label_visibility="collapsed")
    st.divider()
    live_clock()
    st.caption("v24.0 Ultimate Pro | Powered by Gemini 1.5")

# --- HEADER LED ---
marquee_msg = "💎 HỆ THỐNG TRA CỨU DỮ LIỆU BHXH THUẬN AN PHIÊN BẢN PRO v24.0 • TÍCH HỢP TRÍ TUỆ NHÂN TẠO NHẬN THỨC NGỮ CẢNH • NÚT COPY TÀI KHOẢN NGÂN HÀNG THÔNG MINH •"
st.markdown(f"<div class='led-marquee'><marquee scrollamount='10'>{marquee_msg}</marquee></div>", unsafe_allow_html=True)

df = load_data()

if df is not None:
    # --- TAB 1: TRA CỨU ---
    if st.session_state.current_tab == "📊 Tra cứu C12-TS":
        if st.session_state.selected_unit is None:
            st.markdown("<div class='gateway-container'>", unsafe_allow_html=True)
            st.markdown("<h1 style='color:#1e3a8a; font-size:4rem; font-weight:900; margin-bottom: 5px;'>🛡️ CỔNG TRA CỨU DỮ LIỆU</h1>", unsafe_allow_html=True)
            st.markdown("<p style='color:#64748b; font-size:1.6rem; font-weight:800; margin-bottom: 20px;'>NHẬP MÃ ĐƠN VỊ HOẶC TÊN CÔNG TY</p>", unsafe_allow_html=True)
            user_input = st.text_input("Gateway", placeholder="Gõ tìm kiếm tại đây...", label_visibility="collapsed")
            st.markdown("</div>", unsafe_allow_html=True)
            
            st.markdown('<div class="btn-main" style="text-align:center; margin-bottom: 4rem;">', unsafe_allow_html=True)
            if st.button("🔍 TIẾN HÀNH TRA CỨU", use_container_width=False):
                st.session_state.search_query = user_input
            st.markdown('</div>', unsafe_allow_html=True)

            col_news, col_res, col_off = st.columns([0.8, 1.4, 1.1])
            with col_news:
                st.markdown("##### 📢 TIN TỨC")
                st.markdown("<div class='crystal-card' style='min-height:380px; display:flex; flex-direction:column; justify-content:center;'><h4 style='color:#1e3a8a;'>🛡️ ĐẶC QUYỀN</h4><p>Tính năng Copy số tài khoản ngân hàng bằng 1 click đã được cập nhật ở trang kết quả.</p><hr><small style='color:#10b981; font-weight:900;'>PHIÊN BẢN v24.0</small></div>", unsafe_allow_html=True)

            with col_res:
                final_q = st.session_state.search_query if st.session_state.search_query else user_input
                if final_q:
                    results = df[df['search_index'].str.contains(unidecode(final_q).lower(), na=False)].head(8)
                    if not results.empty:
                        for idx, row in results.iterrows():
                            with st.container():
                                ca, cb = st.columns([3.5, 1.5])
                                ca.markdown(f"<div class='crystal-card' style='padding:22px; border-left:12px solid #2563eb; text-align:left; min-height: 100px;'><small style='color:#2563eb; font-weight:900; letter-spacing:1px;'>MÃ: {row.get('madvi')}</small><br><b style='font-size:1.35rem; color:#0f172a;'>{row.get('tendvi')}</b></div>", unsafe_allow_html=True)
                                if cb.button("XÁC NHẬN ➔", key=f"sel_{row.get('madvi')}_{idx}", use_container_width=True):
                                    st.session_state.selected_unit = row.get('madvi'); st.session_state.welcome_done = False; st.rerun()
                    else: st.error("Không tìm thấy dữ liệu khớp với từ khóa.")
                else: st.markdown("<br><center><img src='https://cdn-icons-png.flaticon.com/512/3772/3772274.png' width='180' style='opacity:0.25'></center>", unsafe_allow_html=True)

            with col_off:
                st.markdown("##### 👨‍💼 CÁN BỘ PHỤ TRÁCH")
                for off in OFFICERS:
                    st.markdown(f"""
                    <div class='crystal-card' style='margin-top: 15px; padding: 20px;'>
                        <div style='color:var(--secondary); font-weight: 800; font-size: 0.85rem; text-transform: uppercase;'>{off['communes']}</div>
                        <div style='color:var(--primary); font-weight: 900; font-size: 1.25rem; margin: 5px 0;'>{off['name']}</div>
                        <a href='tel:{off['phone'].replace('.','')}' style='text-decoration:none; color:var(--primary); font-weight: 800; font-size: 1.2rem;'>📱 {off['phone']}</a><br>
                    </div>
                    """, unsafe_allow_html=True)

        else:
            # --- DASHBOARD KẾT QUẢ ĐỈNH CAO ---
            if not st.session_state.welcome_done:
                st.balloons(); st.session_state.welcome_done = True
            
            unit_data = df[df['madvi'] == st.session_state.selected_unit].iloc[0]
            unit_addr = unidecode(str(unit_data.get('diachi', ''))).lower()
            
            st.button("⬅ QUAY LẠI TÌM KIẾM ĐƠN VỊ KHÁC", on_click=lambda: st.session_state.update(selected_unit=None))
            
            st.markdown(f"""
                <div class='crystal-card' style='border-left:25px solid #1e3a8a; text-align:left; background: rgba(255,255,255,0.95); margin-top: 20px;'>
                    <h1 style='margin:0; color:#0f172a; font-size: 3.5rem; font-weight: 900;'>🏢 {unit_data.get('tendvi')}</h1>
                    <p style='margin:10px 0 0 0; color:#64748b; font-size: 1.3rem;'>Mã: <b style='color:#2563eb; background:#eff6ff; padding:2px 10px; border-radius:5px;'>{unit_data.get('madvi')}</b> | Địa chỉ: {unit_data.get('diachi', 'N/A')}</p>
                </div>
            """, unsafe_allow_html=True)
            
            cl, cr = st.columns([1.8, 1])
            with cl:
                st.write("<h3 style='color:#1e3a8a; margin-top: 30px;'>📊 BÁO CÁO SỐ LIỆU TÀI CHÍNH</h3>", unsafe_allow_html=True)
                m1, m2, m3 = st.columns(3)
                with m1: st.markdown(f"<div class='crystal-card'><div class='metric-lbl'>Đầu kỳ</div><div class='metric-val'>{unit_data.get('tien_dau_ky', 0):,.0f}</div></div>", unsafe_allow_html=True)
                with m2: st.markdown(f"<div class='crystal-card'><div class='metric-lbl'>Phải đóng</div><div class='metric-val'>{unit_data.get('so_phai_dong', 0):,.0f}</div></div>", unsafe_allow_html=True)
                with m3: st.markdown(f"<div class='crystal-card'><div class='metric-lbl'>Điều chỉnh</div><div class='metric-val'>{unit_data.get('dieu_chinh_ky_truoc', 0):,.0f}</div></div>", unsafe_allow_html=True)
                
                st.write("<br>", unsafe_allow_html=True)
                m4, m5, m6 = st.columns(3)
                with m4: st.markdown(f"<div class='crystal-card'><div class='metric-lbl'>Đã đóng</div><div class='metric-val' style='color:#10b981;'>{unit_data.get('so_da_dong', 0):,.0f}</div></div>", unsafe_allow_html=True)
                with m5: st.markdown(f"<div class='crystal-card'><div class='metric-lbl'>Lệch</div><div class='metric-val' style='color:#ef4444;'>{unit_data.get('so_bi_lech', 0):,.0f}</div></div>", unsafe_allow_html=True)
                debt = unit_data.get('tien_cuoi_ky', 0)
                status_clr = '#ef4444' if debt > 0 else '#10b981'
                with m6: st.markdown(f"<div class='crystal-card' style='border: 4px solid {status_clr};'><div class='metric-lbl'>{'SỐ TIỀN CÒN NỢ' if debt > 0 else 'SỐ TIỀN DƯ CÓ'}</div><div class='metric-val' style='color:{status_clr};'>{abs(debt):,.0f}</div></div>", unsafe_allow_html=True)
                
                # Nút tải báo cáo
                st.write("<br>", unsafe_allow_html=True)
                csv_data = convert_df(pd.DataFrame([unit_data]))
                st.download_button(label="📥 TẢI BÁO CÁO NÀY (FILE EXCEL/CSV)", data=csv_data, file_name=f"BaoCao_BHXH_{unit_data.get('madvi')}.csv", mime='text/csv', use_container_width=True)

            with cr:
                rate = min(round((unit_data.get('so_da_dong', 0) / unit_data.get('so_phai_dong', 1)) * 100, 1), 100)
                fig = go.Figure(go.Indicator(mode="gauge+number", value=rate, title={'text': "TỶ LỆ HOÀN THÀNH (%)", 'font': {'size': 22, 'color': '#1e3a8a', 'weight': '900'}}, number={'suffix': "%", 'font': {'color': '#2563eb', 'size': 65}}, gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#2563eb"}})).update_layout(paper_bgcolor="rgba(0,0,0,0)", height=350, margin=dict(t=50, b=0))
                st.plotly_chart(fig, use_container_width=True)
                
                for off in OFFICERS:
                    if any(kw in unit_addr for kw in off['keywords']) or any(kw in unit_data.get('madvi','').lower() for kw in off['keywords']):
                        st.markdown(f"<div class='crystal-card' style='background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%); color: white; margin-top:0px;'><small style='color:#39ff14; font-weight:900; letter-spacing: 1px;'>👨‍💼 CÁN BỘ PHỤ TRÁCH TRỰC TIẾP</small><h2 style='color:#fff; margin:15px 0;'>{off['name']}</h2><a href='tel:{off['phone'].replace('.','')}' style='color:#00d2ff; font-size: 1.8rem; text-decoration:none; font-weight:900; text-shadow: 0 0 10px #00d2ff;'>📱 {off['phone']}</a><br><a href='{off['zalo']}' target='_blank' style='background:white; color:#1e3a8a; padding:12px 35px; border-radius:50px; text-decoration:none; display:inline-block; margin-top:20px; font-weight:900; box-shadow: 0 5px 15px rgba(0,0,0,0.3); text-transform: uppercase;'>💬 LIÊN HỆ ZALO NGAY</a></div>", unsafe_allow_html=True)
                        break

            # HIỂN THỊ NGÂN HÀNG VIP BÊN DƯỚI BÁO CÁO ĐỂ KẾ TOÁN COPY
            render_vip_bank_accounts(unit_data.get('madvi'), unit_data.get('tendvi'))

    # --- TAB 2: AI CONTEXT AWARE ---
    elif st.session_state.current_tab == "🤖 Trợ lý AI Gemini Pro":
        st.markdown("## 🧠 TRỢ LÝ AI CAO CẤP (GEMINI 1.5 PRO)")
        
        # Bơm ngữ cảnh đơn vị nếu đang tra cứu
        context = ""
        if st.session_state.selected_unit:
            unit = df[df['madvi'] == st.session_state.selected_unit].iloc[0]
            context = f"Tên công ty: {unit['tendvi']}, Mã: {unit['madvi']}, Đang nợ: {unit['tien_cuoi_ky']} VNĐ. Hãy tư vấn dựa trên số liệu này."
            st.success(f"🤖 AI đã nhận diện dữ liệu của **{unit['tendvi']}**. Bạn có thể hỏi về số nợ hiện tại!")
        else:
            st.info("Hệ thống AI Pro đã sẵn sàng. Hãy đặt câu hỏi chung về luật BHXH.")

        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]): st.markdown(msg["content"])
            
        if prompt := st.chat_input("Ví dụ: Tại sao tôi bị nợ tiền? Hoặc: Mức đóng BHYT hiện tại là bao nhiêu?"):
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            with st.chat_message("assistant"):
                with st.spinner("AI Pro đang phân tích dữ liệu siêu tốc..."):
                    resp = get_ai_response(prompt, context)
                    st.markdown(resp)
                    st.session_state.chat_history.append({"role": "assistant", "content": resp})

    # --- TAB 3: PDF (ANTI BLOCK KÈM NÚT TẢI) ---
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
                        pdf_data = f.read()
                        b64 = base64.b64encode(pdf_data).decode('utf-8')
                        
                        st.markdown(f'<iframe src="data:application/pdf;base64,{b64}" width="100%" height="800px" style="border:8px solid white; border-radius:30px; box-shadow:0 30px 80px rgba(0,0,0,0.15);"></iframe>', unsafe_allow_html=True)
                        st.write("<br>", unsafe_allow_html=True)
                        
                        col_dl, col_open = st.columns(2)
                        with col_dl:
                            st.download_button(label="📥 TẢI VĂN BẢN VỀ MÁY CHUẨN NHẤT", data=pdf_data, file_name=st.session_state.active_pdf, mime="application/pdf", use_container_width=True)
                        with col_open:
                            st.markdown(f'<a href="data:application/pdf;base64,{b64}" target="_blank" style="text-decoration:none; background:linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%); color:white; padding:15px; border-radius:50px; font-weight:900; display:block; text-align:center; box-shadow: 0 10px 20px rgba(30,58,138,0.3); text-transform:uppercase;">🚀 MỞ BẰNG TRÌNH DUYỆT (NẾU BỊ CHẶN)</a>', unsafe_allow_html=True)

    # --- CÁC TAB KHÁC ---
    elif st.session_state.current_tab == "📑 Cẩm nang Nghiệp vụ": st.markdown("## 📑 CẨM NANG NGHIỆP VỤ")
    elif st.session_state.current_tab == "🧮 Máy tính BHXH":
        st.markdown("## 🧮 DỰ TOÁN ĐÓNG BHXH"); sal = st.number_input("Lương đóng:", value=5000000); st.success(f"Tổng đóng: {(sal*0.32):,.0f}đ")
    elif st.session_state.current_tab == "📍 Liên hệ BHXH":
        st.markdown("## 📍 LIÊN HỆ"); st.write("🏠 Cơ sở: Thôn Thuận Sơn, Thuận An, Đắk Mil, Đắk Nông.")

st.markdown("<br><hr><center style='color:#94a3b8; font-size:0.95rem; padding-bottom:60px;'>© 2026 BHXH CƠ SỞ THUẬN AN | v24.0 Ultimate Pro Masterpiece</center>", unsafe_allow_html=True)
