import streamlit as st
import pandas as pd
import numpy as np
import os
import plotly.graph_objects as go
from unidecode import unidecode
import time
from datetime import datetime
import base64
import requests
import streamlit.components.v1 as components

# --- CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="BHXH Thuận An - v29.0 The Apex",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CẤU HÌNH AI GEMINI BẰNG REST API (PHƯƠNG PHÁP MỚI TỐI GIẢN) ---
raw_api_key = st.secrets.get("GOOGLE_API_KEY", os.environ.get("GOOGLE_API_KEY", ""))
api_key = str(raw_api_key).strip().strip('"').strip("'") if raw_api_key else ""

def get_ai_response(prompt, context=""):
    if not api_key: 
        return "⚠️ **Chưa cấu hình API Key:** Vui lòng kiểm tra lại Streamlit Secrets."
    
    system_instruction = "Bạn là trợ lý AI cao cấp của Bảo hiểm xã hội cơ sở Thuận An, Lâm Đồng. Trả lời tận tâm, chính xác, lịch sự."
    if context:
        full_prompt = f"{system_instruction}\n\n[DỮ LIỆU ĐƠN VỊ ĐANG TRA CỨU]:\n{context}\n\n[CÂU HỎI]: {prompt}"
    else:
        full_prompt = f"{system_instruction}\n\n[CÂU HỎI]: {prompt}"
        
    # PHƯƠNG PHÁP KHẢ THI HƠN: Payload "sạch" hoàn toàn
    # Đã loại bỏ safetySettings (Nguyên nhân gây lỗi HTTP 400 ở tài khoản miễn phí khiến model nhảy lung tung sinh ra 404)
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{"parts": [{"text": full_prompt}]}]
    }
    
    # Chỉ gọi đích danh 1 model chuẩn, phổ biến và ổn định nhất của Google hiện hành
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=20)
        
        if response.status_code == 200:
            res_json = response.json()
            candidates = res_json.get('candidates', [])
            if not candidates:
                return "⚠️ **AI:** Câu hỏi bị từ chối do vi phạm chính sách nội dung của Google."
            
            cand = candidates[0]
            if 'content' in cand and 'parts' in cand['content']:
                return cand['content']['parts'][0]['text']
            elif cand.get('finishReason') == 'SAFETY':
                return "⚠️ **AI:** Nội dung câu trả lời bị hệ thống an toàn của Google chặn."
            else:
                return "⚠️ **AI:** Cấu trúc dữ liệu phản hồi bị rỗng."
        else:
            # Nếu API báo lỗi, hiển thị đích danh lỗi của chính gemini-1.5-flash để không bị mù mờ thông tin
            err_msg = response.json().get('error', {}).get('message', 'Lỗi không xác định')
            if "API key not valid" in err_msg:
                return "⚠️ **Lỗi API Key:** Khóa API không hợp lệ hoặc đã bị xoá trên Google AI Studio."
            if "429" in str(response.status_code) or "quota" in err_msg.lower():
                return "⚠️ **Hệ thống AI đang quá tải:** Đã hết lượt hỏi trong phút này. Vui lòng chờ 1 phút!"
            
            return f"⚠️ **Lỗi từ Google API:** {err_msg}"
            
    except requests.exceptions.RequestException as e:
        return f"⚠️ **Lỗi kết nối mạng:** Không thể kết nối đến máy chủ Google."
    except Exception as e:
        return f"⚠️ **Lỗi xử lý nội bộ:** {str(e)}"

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

# --- TỔNG LỰC CSS (GIAO DIỆN THE APEX v29.0) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    :root {
        --primary: #1e3a8a; --secondary: #2563eb; --neon-blue: #00d2ff;
        --glass: rgba(255, 255, 255, 0.95);
    }

    * { font-family: 'Plus Jakarta Sans', sans-serif; box-sizing: border-box; }
    .stApp { background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%); }

    /* SIDEBAR ĐẲNG CẤP */
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #0f172a 0%, #1e3a8a 100%) !important; }
    [data-testid="stSidebar"] .stRadio label p {
        color: #ffffff !important; font-size: 1.25rem !important; font-weight: 800 !important;
        text-shadow: 2px 2px 5px rgba(0,0,0,0.5) !important; padding: 10px 0 !important;
    }
    [data-testid="stSidebar"] h1 { color: white !important; text-shadow: 0 0 15px var(--neon-blue); }

    /* BẢNG LED RGB */
    .led-marquee {
        background: #000; color: #39ff14; padding: 15px 0; font-weight: 800; border-radius: 15px;
        box-shadow: 0 10px 30px rgba(57, 255, 20, 0.15); border: 2px solid #333; margin-bottom: 25px;
        font-size: 1.35rem; letter-spacing: 1px; text-transform: uppercase;
    }

    /* SIÊU Ô TÌM KIẾM GATEWAY - CĂN CHỈNH TUYỆT ĐỐI CHỐNG CẮT CHỮ */
    .gateway-container { max-width: 1000px; margin: 0 auto 1.5rem auto; text-align: center; }
    
    div[data-testid="stTextInput"] > div { 
        height: 130px !important; /* Khoá cứng khung ngoài */
        background: transparent !important; border:none !important; box-shadow:none !important; 
        padding: 0 !important; margin: 0 !important; 
    }
    
    .stTextInput input {
        border-radius: 20px !important; 
        padding: 0 45px 0 110px !important; /* Dùng 0 cho top/bottom để tránh đẩy chữ */
        border: 8px solid var(--secondary) !important; 
        font-size: 2.8rem !important; 
        font-weight: 900 !important;
        height: 130px !important; 
        line-height: 114px !important; /* (130 - 16px border) để căn giữa dọc chuẩn xác */
        background: white url('https://cdn-icons-png.flaticon.com/512/622/622669.png') no-repeat 35px center !important;
        background-size: 50px !important; 
        color: var(--primary) !important;
        box-shadow: 0 30px 80px rgba(37, 99, 235, 0.25) !important;
    }
    .stTextInput input:focus { border-color: var(--neon-blue) !important; transform: scale(1.02); }

    /* RADIANT CARDS */
    .crystal-card {
        background: white; padding: 30px; border-radius: 25px; box-shadow: 0 15px 40px rgba(0,0,0,0.05);
        border: 1px solid #f1f5f9; transition: all 0.3s; text-align: center; position: relative;
    }
    .crystal-card:hover { transform: translateY(-8px); box-shadow: 0 25px 60px rgba(37, 99, 235, 0.1); border-color: #cbd5e1; }
    .metric-val { font-size: 2.5rem; font-weight: 900; color: var(--primary); margin-top: 5px; }
    .metric-lbl { font-size: 1rem; font-weight: 800; color: #64748b; text-transform: uppercase; }

    /* EXECUTIVE DASHBOARD WIDGETS */
    .exec-widget { background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%); color: white; padding: 25px; border-radius: 25px; box-shadow: 0 15px 35px rgba(30, 58, 138, 0.2); text-align: left; }
    .exec-title { font-size: 1rem; font-weight: 800; color: #93c5fd; text-transform: uppercase; }
    .exec-number { font-size: 3.5rem; font-weight: 900; color: white; text-shadow: 0 0 20px rgba(255,255,255,0.4); margin: 5px 0; }

    .bank-card { background: linear-gradient(135deg, #f0fdfa 0%, #e0f2fe 100%); border: 3px solid #60a5fa; border-radius: 25px; padding: 30px; margin-top: 20px; }
    .stCodeBlock code { font-size: 1.5rem !important; font-weight: 900 !important; color: #1e3a8a !important; }
    .stButton>button { border-radius: 50px !important; font-weight: 800 !important; text-transform: uppercase; padding: 0.8rem 3rem !important; transition: all 0.3s ease !important; }
    .btn-main > div > button { background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%) !important; color: white !important; font-size: 1.5rem !important; height: 75px !important; width: 80% !important; border: none !important; box-shadow: 0 15px 35px rgba(30, 58, 138, 0.3) !important; }
    .btn-main > div > button:hover { transform: scale(1.05) !important; }
    </style>
    """, unsafe_allow_html=True)

# --- ĐỒNG HỒ REAL-TIME (JS) ---
def live_clock():
    components.html("""
    <div style="font-family: 'Plus Jakarta Sans', sans-serif; background: rgba(255,255,255,0.1); color: white; padding: 20px; border-radius: 25px; text-align: center; border: 1px solid rgba(255,255,255,0.2);">
        <div id="day-str" style="font-size: 1.1rem; font-weight: 700; opacity: 0.9; margin-bottom: 5px; color: #00d2ff;"></div>
        <div id="time-str" style="font-size: 2.5rem; font-weight: 900; letter-spacing: 2px;"></div>
    </div>
    <script>
        function updateClock() {
            const now = new Date();
            document.getElementById('day-str').innerText = now.toLocaleDateString('vi-VN', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }).toUpperCase();
            document.getElementById('time-str').innerText = String(now.getHours()).padStart(2, '0') + ":" + String(now.getMinutes()).padStart(2, '0') + ":" + String(now.getSeconds()).padStart(2, '0');
        }
        setInterval(updateClock, 1000); updateClock();
    </script>
    """, height=180)

# --- DATA HUB (CÁN BỘ) ---
OFFICERS = [
    {"name": "Bà NGUYỄN THỊ NHÀI", "communes": "Xã Đức Lập, Xã Đắk Mil", "keywords": ["duc lap", "đức lập", "dak mil", "đắk mil", "dc0039c", "đức hòa", "duc hoa"], "phone": "0846.39.29.29", "zalo": "https://zalo.me/0846392929", "color": "#00d2ff"},
    {"name": "Ông BÙI THÀNH ĐẠT", "communes": "Xã Đắk Sắk, Xã Đắk Song", "keywords": ["dak sak", "đắk sắk", "dak song", "đắk song"], "phone": "0986.05.30.06", "zalo": "https://zalo.me/0986053006", "color": "#ffaa00"},
    {"name": "Ông HOÀNG SỸ HẢI", "communes": "Xã Thuận An", "keywords": ["thuan an", "thuận an"], "phone": "0919.06.11.53", "zalo": "https://zalo.me/0919061153", "color": "#39ff14"}
]

def render_vip_bank_accounts(unit_code="[Mã Đơn Vị]", unit_name="[Tên Đơn Vị]"):
    st.markdown("<div class='bank-card'><h2 style='color:#1e3a8a; margin-top:0; font-weight:900; text-align:center;'>🏦 THÔNG TIN CHUYỂN KHOẢN ĐÓNG BHXH</h2><p style='color:#475569; text-align:center; font-weight:600;'>Kế toán đơn vị vui lòng nhấn <b style='color:#2563eb;'>Copy</b> ở góc phải mỗi số tài khoản để sao chép.</p></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: st.info("🏦 **BIDV**"); st.code("63510009867032", language="text")
    with c2: st.success("🏦 **AGRIBANK**"); st.code("5301202919045", language="text")
    with c3: st.warning("🏦 **VIETINBANK**"); st.code("919035000003", language="text")
    st.markdown(f"<div style='background:#eff6ff; padding:25px; border-radius:20px; border:3px dashed #3b82f6; text-align:center; margin-top: 15px;'><div style='color:#1e40af; font-weight:900; font-size:1.1rem; margin-bottom: 10px;'>📝 Nội dung chuyển khoản chuẩn xác nhất:</div><code style='font-size:1.6rem; color:#1e3a8a; font-weight:900; background:white; padding:15px 25px; border-radius:12px; display:inline-block;'>{unit_code} {unit_name} dong bhxh thang {datetime.now().month} nam {datetime.now().year}</code></div>", unsafe_allow_html=True)

# --- HÀM XUẤT DATA ---
@st.cache_data
def convert_df(df_export):
    return df_export.to_csv(index=False).encode('utf-8-sig')

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
    st.markdown("<h1 style='text-align:center;'>🛡️ QUANTUM PRO</h1>", unsafe_allow_html=True)
    st.divider()
    menu = ["📊 Tra cứu C12-TS", "🤖 Trợ lý AI Gemini", "📂 Thư viện Văn bản", "📑 Cẩm nang Nghiệp vụ", "🧮 Máy tính BHXH", "📍 Liên hệ BHXH"]
    st.session_state.current_tab = st.radio("CHỨC NĂNG HỆ THỐNG", menu, label_visibility="collapsed")
    st.divider()
    live_clock()
    st.caption("v29.0 The Apex | Powered by Google API")

# --- HEADER LED ---
marquee_msg = "💎 HỆ THỐNG TRA CỨU DỮ LIỆU BHXH THUẬN AN PHIÊN BẢN ĐỈNH CAO v29.0 • HOẠT ĐỘNG ỔN ĐỊNH - BẢO MẬT - MINH BẠCH • TÍCH HỢP TRÍ TUỆ NHÂN TẠO GEMINI REST API •"
st.markdown(f"<div class='led-marquee'><marquee scrollamount='10'>{marquee_msg}</marquee></div>", unsafe_allow_html=True)

df = load_data()

if df is not None:
    # --- TAB 1: TRA CỨU ---
    if st.session_state.current_tab == "📊 Tra cứu C12-TS":
        if st.session_state.selected_unit is None:
            st.markdown("<div class='gateway-container'>", unsafe_allow_html=True)
            st.markdown("<h1 style='color:#1e3a8a; font-size:4.2rem; font-weight:900; margin-bottom: 5px;'>🛡️ CỔNG TRA CỨU DỮ LIỆU</h1>", unsafe_allow_html=True)
            st.markdown("<p style='color:#64748b; font-size:1.7rem; font-weight:800; margin-bottom: 25px;'>MỜI NHẬP MÃ ĐƠN VỊ HOẶC TÊN CÔNG TY</p>", unsafe_allow_html=True)
            user_input = st.text_input("Gateway", placeholder="Gõ từ khóa tìm kiếm...", label_visibility="collapsed")
            st.markdown("</div>", unsafe_allow_html=True)
            
            st.markdown('<div class="btn-main" style="text-align:center; margin-bottom: 3rem;">', unsafe_allow_html=True)
            if st.button("🔍 TIẾN HÀNH TRA CỨU", use_container_width=False):
                st.session_state.search_query = user_input
            st.markdown('</div>', unsafe_allow_html=True)

            if not st.session_state.search_query and not user_input:
                st.markdown("<h3 style='color:#1e3a8a; text-align:center; margin-bottom: 20px; font-weight:900;'>📈 TỔNG QUAN HỆ THỐNG BHXH THUẬN AN</h3>", unsafe_allow_html=True)
                e1, e2, e3 = st.columns(3)
                total_units = len(df)
                total_debt = df['tien_cuoi_ky'].sum() if 'tien_cuoi_ky' in df.columns else 0
                with e1: st.markdown(f"<div class='exec-widget'><div class='exec-title'>Tổng số đơn vị quản lý</div><div class='exec-number'>{total_units:,}</div><div style='color:#93c5fd;'>Đơn vị đang hoạt động</div></div>", unsafe_allow_html=True)
                with e2: st.markdown(f"<div class='exec-widget' style='background: linear-gradient(135deg, #047857 0%, #10b981 100%);'><div class='exec-title' style='color:#a7f3d0;'>Trạng thái Hệ thống</div><div class='exec-number'>ONLINE</div><div style='color:#a7f3d0;'>Bảo mật SSL 256-bit</div></div>", unsafe_allow_html=True)
                with e3: st.markdown(f"<div class='exec-widget' style='background: linear-gradient(135deg, #be123c 0%, #f43f5e 100%);'><div class='exec-title' style='color:#fecdd3;'>Trợ lý AI Gemini</div><div class='exec-number'>ACTIVE</div><div style='color:#fecdd3;'>Xử lý ngữ cảnh đa chiều</div></div>", unsafe_allow_html=True)
                st.write("<br>", unsafe_allow_html=True)

            col_news, col_res, col_off = st.columns([0.8, 1.4, 1.1])
            with col_news:
                st.markdown("##### 📢 TIN TỨC")
                st.markdown("<div class='crystal-card' style='min-height:380px; display:flex; flex-direction:column; justify-content:center;'><h4 style='color:#1e3a8a; font-size: 1.5rem;'>🛡️ BẢO MẬT PRO</h4><p style='font-size: 1.1rem; color: #475569;'>Hệ thống tra cứu đã được bọc lõi REST API, loại bỏ toàn bộ lỗi cắt chữ và lỗi kết nối.</p><hr><small style='color:#10b981; font-weight:900;'>PHIÊN BẢN v29.0</small></div>", unsafe_allow_html=True)

            with col_res:
                final_q = st.session_state.search_query if st.session_state.search_query else user_input
                if final_q:
                    results = df[df['search_index'].str.contains(unidecode(final_q).lower(), na=False)].head(8)
                    if not results.empty:
                        for idx, row in results.iterrows():
                            with st.container():
                                ca, cb = st.columns([3.5, 1.5])
                                ca.markdown(f"<div class='crystal-card' style='padding:22px; border-left:12px solid #2563eb; text-align:left; min-height: 100px;'><small style='color:#2563eb; font-weight:900; letter-spacing:1px; font-size:1rem;'>MÃ: {row.get('madvi')}</small><br><b style='font-size:1.4rem; color:#0f172a;'>{row.get('tendvi')}</b></div>", unsafe_allow_html=True)
                                if cb.button("XÁC NHẬN ➔", key=f"sel_{row.get('madvi')}_{idx}", use_container_width=True):
                                    st.session_state.selected_unit = row.get('madvi'); st.session_state.welcome_done = False; st.rerun()
                    else: st.error("Không tìm thấy dữ liệu khớp với từ khóa.")
                elif not user_input:
                    st.markdown("<br><center><img src='https://cdn-icons-png.flaticon.com/512/3772/3772274.png' width='180' style='opacity:0.25'></center>", unsafe_allow_html=True)

            with col_off:
                st.markdown("##### 👨‍💼 CÁN BỘ PHỤ TRÁCH")
                for off in OFFICERS:
                    st.markdown(f"""
                    <div class='crystal-card' style='margin-top: 15px; padding: 22px;'>
                        <div style='color:var(--secondary); font-weight: 800; font-size: 0.9rem; text-transform: uppercase;'>{off['communes']}</div>
                        <div style='color:var(--primary); font-weight: 900; font-size: 1.3rem; margin: 8px 0;'>{off['name']}</div>
                        <a href='tel:{off['phone'].replace('.','')}' style='text-decoration:none; color:var(--primary); font-weight: 800; font-size: 1.3rem;'>📱 {off['phone']}</a><br>
                    </div>
                    """, unsafe_allow_html=True)

        else:
            # --- DASHBOARD KẾT QUẢ ---
            if not st.session_state.welcome_done:
                st.balloons(); st.session_state.welcome_done = True
            
            unit_data = df[df['madvi'] == st.session_state.selected_unit].iloc[0]
            unit_addr = unidecode(str(unit_data.get('diachi', ''))).lower()
            
            st.button("⬅ QUAY LẠI TÌM KIẾM ĐƠN VỊ KHÁC", on_click=lambda: st.session_state.update(selected_unit=None))
            
            st.markdown(f"""
                <div class='crystal-card' style='border-left:25px solid #1e3a8a; text-align:left; margin-top: 25px;'>
                    <h1 style='margin:0; color:#0f172a; font-size: 3.6rem; font-weight: 900;'>🏢 {unit_data.get('tendvi')}</h1>
                    <p style='margin:12px 0 0 0; color:#64748b; font-size: 1.4rem;'>Mã: <b style='color:#2563eb; background:#eff6ff; padding:4px 12px; border-radius:8px;'>{unit_data.get('madvi')}</b> | Địa chỉ: {unit_data.get('diachi', 'N/A')}</p>
                </div>
            """, unsafe_allow_html=True)
            
            cl, cr = st.columns([1.8, 1])
            with cl:
                st.write("<h3 style='color:#1e3a8a; margin-top: 35px; font-weight: 800;'>📊 BÁO CÁO TÀI CHÍNH CHI TIẾT</h3>", unsafe_allow_html=True)
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
                
                st.write("<br>", unsafe_allow_html=True)
                csv_data = convert_df(pd.DataFrame([unit_data]))
                st.download_button(label="📥 TẢI DỮ LIỆU BÁO CÁO (FILE EXCEL/CSV)", data=csv_data, file_name=f"BaoCao_BHXH_{unit_data.get('madvi')}.csv", mime='text/csv', use_container_width=True)

            with cr:
                rate = min(round((unit_data.get('so_da_dong', 0) / unit_data.get('so_phai_dong', 1)) * 100, 1), 100)
                fig = go.Figure(go.Indicator(
                    mode="gauge+number", value=rate, 
                    title={'text': "<b>TỶ LỆ HOÀN THÀNH (%)</b>", 'font': {'size': 24, 'color': '#1e3a8a'}}, 
                    number={'suffix': "%", 'font': {'color': '#2563eb', 'size': 70}}, 
                    gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#2563eb"}}
                )).update_layout(paper_bgcolor="rgba(0,0,0,0)", height=380, margin=dict(t=50, b=0))
                st.plotly_chart(fig, use_container_width=True)
                
                for off in OFFICERS:
                    if any(kw in unit_addr for kw in off['keywords']) or any(kw in unit_data.get('madvi','').lower() for kw in off['keywords']):
                        st.markdown(f"<div class='crystal-card' style='background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%); color: white; margin-top:0px;'><small style='color:#39ff14; font-weight:900; letter-spacing: 1.5px;'>👨‍💼 CÁN BỘ PHỤ TRÁCH TRỰC TIẾP</small><h2 style='color:#fff; margin:15px 0; font-size: 2rem;'>{off['name']}</h2><a href='tel:{off['phone'].replace('.','')}' style='color:#00d2ff; font-size: 2rem; text-decoration:none; font-weight:900; text-shadow: 0 0 15px #00d2ff;'>📱 {off['phone']}</a><br><a href='{off['zalo']}' target='_blank' style='background:white; color:#1e3a8a; padding:15px 40px; border-radius:50px; text-decoration:none; display:inline-block; margin-top:25px; font-weight:900; font-size: 1.1rem; box-shadow: 0 10px 25px rgba(0,0,0,0.3); text-transform: uppercase;'>💬 NHẮN TIN ZALO NGAY</a></div>", unsafe_allow_html=True)
                        break

            render_vip_bank_accounts(unit_data.get('madvi'), unit_data.get('tendvi'))

    # --- TAB 2: AI ---
    elif st.session_state.current_tab == "🤖 Trợ lý AI Gemini":
        st.markdown("## 🧠 TRỢ LÝ AI TƯ VẤN BẢO HIỂM")
        
        context = ""
        if st.session_state.selected_unit:
            unit = df[df['madvi'] == st.session_state.selected_unit].iloc[0]
            context = f"Đơn vị: {unit['tendvi']}, Mã: {unit['madvi']}, Nợ: {unit['tien_cuoi_ky']} VNĐ."
            st.success(f"🤖 AI đã liên kết với dữ liệu của **{unit['tendvi']}**. Bạn có thể hỏi về số nợ hiện tại!")
        else:
            st.info("🤖 AI đã nâng cấp hệ thống REST API cực kỳ an toàn. Hãy đặt câu hỏi!")

        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]): st.markdown(msg["content"])
            
        if prompt := st.chat_input("Ví dụ: Mức đóng BHYT hiện tại là bao nhiêu? Hoặc tại sao tôi bị nợ?"):
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            with st.chat_message("assistant"):
                with st.spinner("AI đang phân tích siêu tốc..."):
                    resp = get_ai_response(prompt, context)
                    st.markdown(resp)
                    st.session_state.chat_history.append({"role": "assistant", "content": resp})

    # --- TAB 3: PDF ---
    elif st.session_state.current_tab == "📂 Thư viện Văn bản":
        st.markdown("## 📂 THƯ VIỆN VĂN BẢN ĐIỀU HÀNH")
        pdfs = [f for f in os.listdir('.') if f.lower().endswith('.pdf')]
        if not pdfs: st.warning("Thư viện đang trống. Vui lòng tải file PDF lên GitHub.")
        else:
            c1, c2 = st.columns([1, 2.5])
            with c1:
                st.markdown("<h4 style='color:#1e3a8a;'>📚 Danh sách tài liệu</h4>", unsafe_allow_html=True)
                for f in pdfs:
                    if st.button(f"📄 {f}", use_container_width=True): st.session_state.active_pdf = f
            with c2:
                if st.session_state.active_pdf:
                    st.success(f"📌 ĐANG XEM TÀI LIỆU AN TOÀN: {st.session_state.active_pdf}")
                    # GIỮ NGUYÊN HOÀN TOÀN CƠ CHẾ HIỂN THỊ PDF Ở BẢN V29 CỦA BẠN (KHÔNG CHỈNH SỬA GÌ)
                    with open(st.session_state.active_pdf, "rb") as f_pdf:
                        b64_pdf = base64.b64encode(f_pdf.read()).decode('utf-8')
                        st.markdown(f'<div style="border-radius: 35px; border: 15px solid white; box-shadow: 0 50px 150px rgba(0,0,0,0.15); background: white; height: 850px; width: 100%; margin-top: 10px;"><object data="data:application/pdf;base64,{b64_pdf}" type="application/pdf" width="100%" height="100%"><div style="padding: 100px 40px; text-align: center; background: white; height: 100%;"><h2 style="color: #ef4444;">⚠️ TRÌNH DUYỆT CHẶN XEM TRỰC TIẾP</h2><p style="font-size: 1.2rem; color: #64748b;">Quý đơn vị vui lòng nhấn nút <b>"MỞ TRONG TAB MỚI"</b> hoặc <b>"TẢI VỀ"</b> bên dưới để xem văn bản.</p></div></object></div>', unsafe_allow_html=True)
                        st.write("<br>", unsafe_allow_html=True)
                        c1_pdf, c2_pdf = st.columns(2)
                        with c1_pdf: st.download_button(label="📥 TẢI VĂN BẢN VỀ MÁY", data=base64.b64decode(b64_pdf), file_name=st.session_state.active_pdf, mime="application/pdf", use_container_width=True)
                        with c2_pdf: st.markdown(f'<a href="data:application/pdf;base64,{b64_pdf}" target="_blank" style="text-decoration:none; background:#1e3a8a; color:white; padding:12px; border-radius:50px; font-weight:900; display:block; text-align:center; box-shadow: 0 10px 20px rgba(30,58,138,0.2);">🚀 XEM TRÊN TAB MỚI</a>', unsafe_allow_html=True)

    # --- CÁC TAB KHÁC ---
    elif st.session_state.current_tab == "📑 Cẩm nang Nghiệp vụ": 
        st.markdown("## 📑 CẨM NANG NGHIỆP VỤ")
        st.info("Khu vực hướng dẫn giải quyết các chế độ BHXH, BHYT, BHTN.")
    elif st.session_state.current_tab == "🧮 Máy tính BHXH":
        st.markdown("## 🧮 MÁY TÍNH DỰ TOÁN ĐÓNG BHXH")
        sal = st.number_input("Nhập mức lương đóng (VNĐ):", value=5000000)
        st.success(f"Tổng số tiền dự kiến nộp (32%): **{(sal*0.32):,.0f}đ**")
    elif st.session_state.current_tab == "📍 Liên hệ BHXH":
        st.markdown("## 📍 THÔNG TIN LIÊN HỆ")
        st.write("🏠 **Cơ quan:** Bảo hiểm xã hội cơ sở Thuận An")
        st.write("📍 **Địa chỉ:** Thôn Thuận Sơn, xã Thuận An, huyện Đắk Mil, tỉnh Đắk Nông.")
        st.write("📞 **Tổng đài:** 1900 9068")

st.markdown("<br><hr><center style='color:#94a3b8; font-size:0.95rem; padding-bottom:60px;'>© 2026 BHXH CƠ SỞ THUẬN AN | v29.0 The Apex</center>", unsafe_allow_html=True)
