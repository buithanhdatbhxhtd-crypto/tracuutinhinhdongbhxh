import streamlit as st
import pandas as pd
import numpy as np
import os
import plotly.graph_objects as go
from unidecode import unidecode
import time
from datetime import datetime
import base64
import streamlit.components.v1 as components

# --- CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="BHXH Thuận An - v35.0 Cosmic Nexus",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CẤU HÌNH AI NỘI BỘ (OFFLINE SMART ENGINE 2.0) ---
# ĐƯỢC GIỮ NGUYÊN 100% THEO YÊU CẦU: Bất tử trước mọi lỗi mạng, không cần API Key.

def get_ai_response(prompt, context=""):
    prompt_lower = unidecode(prompt).lower()
    response = ""

    # Mô phỏng độ trễ suy nghĩ của AI chuyên nghiệp
    time.sleep(1.0)

    # 1. Xử lý nhận thức ngữ cảnh (Dữ liệu công ty đang tra cứu)
    if context and any(word in prompt_lower for word in ["no", "thieu", "dong", "tai sao", "kiem tra", "tien", "tinh hinh"]):
        response += f"📊 **Dữ liệu phân tích tự động từ hệ thống:**\n{context}\n"
        if "nợ: 0 " in context.lower() or "-0 " in context.lower():
            response += "👉 **Phân tích thông minh:** Đơn vị hiện tại đã hoàn thành 100% nghĩa vụ tài chính BHXH, không phát sinh nợ đọng. Xin chân thành cảm ơn sự đồng hành của Quý đơn vị!\n\n---\n"
        else:
            response += "👉 **Phân tích thông minh:** Đơn vị hiện đang có khoản nợ/lệch so với dữ liệu trên hệ thống. Quý đơn vị vui lòng kiểm tra lại Ủy nhiệm chi (UNC) tháng gần nhất hoặc liên hệ Cán bộ chuyên quản qua Zalo để tiến hành đối chiếu, điều chỉnh kịp thời.\n\n---\n"

    # 2. Bộ não tri thức BHXH (Knowledge Base)
    if any(word in prompt_lower for word in ["muc dong", "bao nhieu phan tram", "ty le", "phan tram"]):
        response += "💡 **Quy định Mức đóng BHXH, BHYT, BHTN hiện hành (áp dụng trên quỹ Lương):**\n"
        response += "- **BHXH** (Hưu trí, tử tuất, ốm đau, thai sản): 25.5% (Doanh nghiệp: 17.5%, NLĐ: 8%)\n"
        response += "- **BHYT**: 4.5% (Doanh nghiệp: 3%, NLĐ: 1.5%)\n"
        response += "- **BHTN**: 2% (Doanh nghiệp: 1%, NLĐ: 1%)\n"
        response += "🔥 **Tổng cộng:** **32%** (Trong đó Doanh nghiệp chịu 21.5%, Người lao động trích từ lương 10.5%)."
        
    elif any(word in prompt_lower for word in ["thai san", "sinh con", "mang thai", "nghi de"]):
        response += "💡 **Chế độ Thai sản cho Người lao động:**\n"
        response += "- **Điều kiện hưởng:** Đóng đủ 6 tháng BHXH trở lên trong vòng 12 tháng trước khi sinh con.\n"
        response += "- **Mức hưởng:** 100% mức bình quân tiền lương tháng đóng BHXH của 6 tháng liền kề trước khi nghỉ sinh.\n"
        response += "- **Thời gian nghỉ:** 6 tháng tiêu chuẩn.\n"
        response += "📌 **Thủ tục:** Giấy chứng sinh/khai sinh bản sao và Doanh nghiệp lập Mẫu 01B-HSB điện tử gửi cơ quan BHXH."

    elif any(word in prompt_lower for word in ["chot so", "nghi viec", "thoi viec", "huy the"]):
        response += "💡 **Thủ tục Chốt sổ BHXH khi NLĐ nghỉ việc:**\n"
        response += "1. **Báo giảm:** Lập hồ sơ báo giảm lao động trên phần mềm kê khai (VNPT, Viettel, EFY...).\n"
        response += "2. **Hoàn thành tài chính:** Đóng đầy đủ tiền BHXH, BHYT, BHTN của NLĐ tính đến hết tháng nghỉ việc.\n"
        response += "3. **Gửi hồ sơ chốt:** Nộp Tờ bìa sổ và các tờ rời (Kèm Mẫu TK1-TS nếu có sai sót) qua bưu điện về cơ quan BHXH."

    elif any(word in prompt_lower for word in ["c12", "tra cuu", "thong bao"]):
        response += "💡 **Về Thông báo C12-TS:**\n"
        response += "Hệ thống Cosmic Nexus hiện tại đã số hóa hoàn toàn dữ liệu C12. Quý đơn vị chỉ cần truy cập **Trang chủ (Cổng tra cứu)**, nhập Mã Đơn vị (VD: TA0001) để xem bảng Dashboard tài chính trực quan, minh bạch thay vì chờ file PDF C12 thủ công."

    elif any(word in prompt_lower for word in ["chao", "hello", "hi", "xin chao"]):
        response += "👋 Xin chào! Tôi là Trợ lý AI Nội bộ của BHXH Thuận An. Chào mừng Quý đơn vị đến với hệ thống v35.0. Tôi có thể hỗ trợ gì về chính sách BHXH, BHYT, BHTN hôm nay?"

    else:
        if not response:
            response += "💡 Cảm ơn Quý đơn vị đã đặt câu hỏi.\n\n"
            response += "Hệ thống AI hiện đang chạy ở chế độ **Bảo mật Nội bộ (Offline Engine)** để đảm bảo an toàn dữ liệu 100%.\n"
            response += "👉 Vui lòng hỏi các từ khóa phổ biến như: *Mức đóng, thai sản, chốt sổ, báo giảm, nợ...*\n"
            response += "📞 Đối với các vấn đề chuyên sâu, Quý đơn vị vui lòng nhấn nút **Chat Zalo** với cán bộ chuyên quản ở Trang chủ để được xử lý trong chớp mắt!"

    return response

# --- KHỞI TẠO STATE ---
if 'selected_unit' not in st.session_state: st.session_state.selected_unit = None
if 'current_tab' not in st.session_state: st.session_state.current_tab = "📊 Tra cứu C12-TS"
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if 'active_pdf' not in st.session_state: st.session_state.active_pdf = None
if 'search_query' not in st.session_state: st.session_state.search_query = ""
if 'welcome_done' not in st.session_state: st.session_state.welcome_done = False

# --- TỔNG LỰC CSS (GIAO DIỆN COSMIC NEXUS v35.0 - NÂNG CẤP HIỆU ỨNG TƯƠNG LAI) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800;900&display=swap');
    
    :root {
        --primary: #0f172a; --secondary: #3b82f6; --accent: #0ea5e9; --neon-blue: #00f2fe; --neon-purple: #8b5cf6;
    }

    * { font-family: 'Plus Jakarta Sans', sans-serif; box-sizing: border-box; }
    .stApp { background: #f8fafc; background-image: radial-gradient(#e2e8f0 1px, transparent 1px); background-size: 25px 25px; }

    /* SIDEBAR ĐẲNG CẤP VŨ TRỤ */
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #020617 0%, #1e3a8a 100%) !important; box-shadow: 5px 0 20px rgba(0,0,0,0.1); }
    [data-testid="stSidebar"] .stRadio label p {
        color: #f8fafc !important; font-size: 1.25rem !important; font-weight: 800 !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5) !important; padding: 12px 0 !important; letter-spacing: 0.5px;
    }
    [data-testid="stSidebar"] h1 { color: white !important; text-shadow: 0 0 25px var(--neon-blue); letter-spacing: 2px; }

    /* BẢNG LED RGB ANIMATION */
    @keyframes ledGlow { 0%, 100% { box-shadow: 0 0 20px #39ff14; } 50% { box-shadow: 0 0 40px #39ff14, 0 0 10px #39ff14 inset; } }
    .led-marquee {
        background: #000; color: #39ff14; padding: 15px 0; font-weight: 900; border-radius: 15px;
        border: 2px solid #111; margin-bottom: 25px; font-size: 1.4rem; letter-spacing: 2px; text-transform: uppercase;
        animation: ledGlow 2.5s infinite; border-top: 3px solid #39ff14; border-bottom: 3px solid #39ff14;
    }

    /* SIÊU Ô TÌM KIẾM GATEWAY - BÓNG ĐỔ ĐA TẦNG */
    .gateway-container { max-width: 1000px; margin: 0 auto 1.5rem auto; text-align: center; }
    div[data-testid="stTextInput"] > div { height: 130px !important; background: transparent !important; border:none !important; box-shadow:none !important; padding: 0 !important; margin: 0 !important; }
    
    .stTextInput input {
        border-radius: 25px !important; padding: 0 45px 0 110px !important; 
        border: 8px solid transparent !important; background-clip: padding-box !important;
        font-size: 2.8rem !important; font-weight: 900 !important;
        height: 130px !important; line-height: 114px !important; 
        background: white url('https://cdn-icons-png.flaticon.com/512/622/622669.png') no-repeat 35px center !important;
        background-size: 50px !important; color: var(--primary) !important;
        box-shadow: 0 20px 50px rgba(59, 130, 246, 0.2), inset 0 0 0 4px var(--secondary) !important;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    .stTextInput input:focus { transform: translateY(-5px); box-shadow: 0 30px 60px rgba(0, 242, 254, 0.4), inset 0 0 0 6px var(--neon-blue) !important; }

    /* ANIMATED HEADER CARD (GLASSMORPHISM 3.0) */
    @keyframes gradientBG { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
    .premium-header {
        background: linear-gradient(-45deg, #1e3a8a, #3b82f6, #8b5cf6, #020617);
        background-size: 400% 400%; animation: gradientBG 12s ease infinite;
        color: white; padding: 45px; border-radius: 35px; box-shadow: 0 25px 60px rgba(30, 58, 138, 0.3);
        margin-top: 25px; border: 1px solid rgba(255,255,255,0.15); backdrop-filter: blur(25px); position: relative; overflow: hidden;
    }
    .premium-header::after {
        content: ''; position: absolute; top: -50%; left: -50%; width: 200%; height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 60%);
        animation: spin 15s linear infinite; pointer-events: none;
    }
    @keyframes spin { 100% { transform: rotate(360deg); } }
    .premium-header h1 { font-size: 3.8rem; font-weight: 900; margin: 0; text-shadow: 2px 2px 15px rgba(0,0,0,0.4); position: relative; z-index: 2; }
    .premium-header p { font-size: 1.5rem; font-weight: 600; margin: 10px 0 0 0; color: #e0f2fe; position: relative; z-index: 2; }

    /* RADIANT CARDS 3D - HOVER GLOW MỚI NHẤT V35 */
    .crystal-card {
        background: rgba(255, 255, 255, 0.9); padding: 30px; border-radius: 25px; box-shadow: 0 10px 30px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0; transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275); position: relative; overflow: hidden;
        backdrop-filter: blur(10px);
    }
    .crystal-card::before { content: ''; position: absolute; top: 0; left: 0; width: 6px; height: 100%; background: var(--secondary); transition: all 0.3s; }
    .crystal-card:hover { transform: translateY(-10px); box-shadow: 0 25px 50px rgba(0, 242, 254, 0.25); border-color: #bae6fd; }
    .crystal-card:hover::before { width: 100%; opacity: 0.05; }
    
    .metric-val { font-size: 2.6rem; font-weight: 900; color: var(--primary); margin-top: 8px; letter-spacing: -1px; }
    .metric-lbl { font-size: 1.05rem; font-weight: 800; color: #64748b; text-transform: uppercase; letter-spacing: 1px; }

    /* SMART SUMMARY BANNER */
    .ai-summary {
        background: linear-gradient(90deg, #f0fdfa 0%, #e0f2fe 100%);
        border-left: 8px solid #10b981; padding: 20px 30px; border-radius: 20px;
        margin: 25px 0; font-size: 1.2rem; color: #0f172a; font-weight: 600;
        box-shadow: 0 10px 25px rgba(16, 185, 129, 0.15);
    }

    .bank-card { background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%); border: 3px solid #fbbf24; border-radius: 25px; padding: 30px; margin-top: 25px; box-shadow: 0 15px 35px rgba(245, 158, 11, 0.15); }
    .stCodeBlock code { font-size: 1.6rem !important; font-weight: 900 !important; color: #b45309 !important; background: white !important; border-radius: 10px !important;}
    
    /* ANIMATED PULSING BUTTON V35 */
    @keyframes pulse-btn {
        0% { box-shadow: 0 0 0 0 rgba(14, 165, 233, 0.7); }
        70% { box-shadow: 0 0 0 20px rgba(14, 165, 233, 0); }
        100% { box-shadow: 0 0 0 0 rgba(14, 165, 233, 0); }
    }
    .stButton>button { border-radius: 50px !important; font-weight: 800 !important; text-transform: uppercase; padding: 0.8rem 3rem !important; transition: all 0.3s ease !important; }
    .btn-main > div > button { 
        background: linear-gradient(135deg, #2563eb 0%, #0ea5e9 100%) !important; color: white !important; 
        font-size: 1.6rem !important; height: 80px !important; width: 80% !important; border: none !important; 
        box-shadow: 0 15px 35px rgba(37, 99, 235, 0.4) !important; letter-spacing: 2px;
        animation: pulse-btn 2.5s infinite;
    }
    .btn-main > div > button:hover { transform: scale(1.05) translateY(-3px) !important; box-shadow: 0 20px 45px rgba(37, 99, 235, 0.6) !important; animation: none; }
    </style>
    """, unsafe_allow_html=True)

# --- ĐỒNG HỒ REAL-TIME (JS) ---
def live_clock():
    components.html("""
    <div style="font-family: 'Plus Jakarta Sans', sans-serif; background: rgba(255,255,255,0.1); color: white; padding: 20px; border-radius: 25px; text-align: center; border: 1px solid rgba(255,255,255,0.2);">
        <div id="day-str" style="font-size: 1.1rem; font-weight: 700; opacity: 0.9; margin-bottom: 5px; color: #00f2fe;"></div>
        <div id="time-str" style="font-size: 2.8rem; font-weight: 900; letter-spacing: 3px; text-shadow: 0 0 20px rgba(0,242,254,0.5);"></div>
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

# --- HÀM RENDER PDF (CHỐNG BLOCK CHROME 100% - ĐƯỢC GIỮ NGUYÊN HOÀN TOÀN TỪ V29/V33/V34) ---
def render_pdf_unblockable(file_path):
    try:
        with open(file_path, "rb") as f:
            pdf_data = f.read()
            base64_pdf = base64.b64encode(pdf_data).decode('utf-8').replace('\n', '')
            
        js_code = f"""
        <script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js"></script>
        <script>pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';</script>
        <div id="pdf-container" style="display: flex; flex-direction: column; align-items: center; background-color: #e2e8f0; padding: 30px; border-radius: 25px; border: 5px solid white; box-shadow: inset 0 0 20px rgba(0,0,0,0.05);">
            <h3 id="loading-msg" style="color: #2563eb; font-family: 'Plus Jakarta Sans', sans-serif;">⏳ Hệ thống đang giải mã tài liệu an toàn...</h3>
        </div>
        <script>
            try {{
                const pdfData = atob('{base64_pdf}');
                const loadingTask = pdfjsLib.getDocument({{data: pdfData}});
                loadingTask.promise.then(pdf => {{
                    const container = document.getElementById('pdf-container');
                    container.innerHTML = ''; 
                    for (let pageNum = 1; pageNum <= pdf.numPages; pageNum++) {{
                        pdf.getPage(pageNum).then(page => {{
                            const scale = 1.5;
                            const viewport = page.getViewport({{scale: scale}});
                            const canvas = document.createElement('canvas');
                            const ctx = canvas.getContext('2d');
                            canvas.height = viewport.height;
                            canvas.width = viewport.width;
                            canvas.style.maxWidth = '100%';
                            canvas.style.marginBottom = '25px';
                            canvas.style.boxShadow = '0 20px 40px rgba(0,0,0,0.2)';
                            canvas.style.borderRadius = '12px';
                            container.appendChild(canvas);
                            page.render({{canvasContext: ctx, viewport: viewport}});
                        }});
                    }}
                }}).catch(err => {{ document.getElementById('loading-msg').innerHTML = '⚠️ Không thể vẽ tài liệu. Vui lòng tải về máy.'; }});
            }} catch (e) {{ document.getElementById('loading-msg').innerHTML = '⚠️ Lỗi giải mã Dữ liệu. Vui lòng tải về máy.'; }}
        </script>
        """
        components.html(js_code, height=900, scrolling=True)
        st.write("<br>", unsafe_allow_html=True)
        col_dl, col_open = st.columns(2)
        with col_dl: st.download_button(label="📥 TẢI BẢN GỐC VỀ MÁY", data=pdf_data, file_name=file_path, mime="application/pdf", use_container_width=True)
        with col_open: st.markdown(f'<a href="data:application/pdf;base64,{base64_pdf}" download="{file_path}" style="text-decoration:none; background:linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%); color:white; padding:15px; border-radius:50px; font-weight:900; display:block; text-align:center; box-shadow: 0 10px 20px rgba(30,58,138,0.3); font-size: 1.1rem; border: 2px solid white;">🚀 LƯU TRỮ TRỰC TIẾP</a>', unsafe_allow_html=True)
        return True
    except Exception as e:
        st.error(f"Lỗi hệ thống: {e}")
        return False

# --- DATA HUB (CÁN BỘ) ---
OFFICERS = [
    {"name": "Bà NGUYỄN THỊ NHÀI", "communes": "Xã Đức Lập, Xã Đắk Mil", "keywords": ["duc lap", "đức lập", "dak mil", "đắk mil", "dc0039c", "đức hòa", "duc hoa"], "phone": "0846.39.29.29", "zalo": "https://zalo.me/0846392929", "color": "#00d2ff"},
    {"name": "Ông BÙI THÀNH ĐẠT", "communes": "Xã Đắk Sắk, Xã Đắk Song", "keywords": ["dak sak", "đắk sắk", "dak song", "đắk song"], "phone": "0986.05.30.06", "zalo": "https://zalo.me/0986053006", "color": "#ffaa00"},
    {"name": "Ông HOÀNG SỸ HẢI", "communes": "Xã Thuận An", "keywords": ["thuan an", "thuận an"], "phone": "0919.06.11.53", "zalo": "https://zalo.me/0919061153", "color": "#39ff14"}
]

def render_vip_bank_accounts(unit_code="[Mã Đơn Vị]", unit_name="[Tên Đơn Vị]"):
    st.markdown("<div class='bank-card'><h2 style='color:#b45309; margin-top:0; font-weight:900; text-align:center;'>🏦 THÔNG TIN CHUYỂN KHOẢN ĐÓNG BHXH</h2><p style='color:#475569; text-align:center; font-weight:600; font-size:1.1rem;'>Kế toán đơn vị vui lòng nhấn <b style='color:#ea580c;'>Copy</b> ở góc phải mỗi số tài khoản để sao chép chính xác nhất.</p></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: st.info("🏦 **BIDV**"); st.code("63510009867032", language="text")
    with c2: st.success("🏦 **AGRIBANK**"); st.code("5301202919045", language="text")
    with c3: st.warning("🏦 **VIETINBANK**"); st.code("919035000003", language="text")
    st.markdown(f"<div style='background:#fefce8; padding:30px; border-radius:20px; border:3px dashed #eab308; text-align:center; margin-top: 15px;'><div style='color:#b45309; font-weight:900; font-size:1.2rem; margin-bottom: 10px;'>📝 Nội dung chuyển khoản chuẩn xác nhất:</div><code style='font-size:1.7rem; color:#1e3a8a; font-weight:900; background:white; padding:15px 30px; border-radius:15px; display:inline-block; box-shadow: 0 10px 20px rgba(0,0,0,0.05);'>{unit_code} {unit_name} dong bhxh thang {datetime.now().month} nam {datetime.now().year}</code></div>", unsafe_allow_html=True)

# --- HÀM XUẤT DATA ---
@st.cache_data
def convert_df(df_export): return df_export.to_csv(index=False).encode('utf-8-sig')

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
    st.markdown("<h1 style='text-align:center;'>🚀 COSMIC NEXUS</h1>", unsafe_allow_html=True)
    st.divider()
    menu = ["📊 Tra cứu C12-TS", "🤖 Trợ lý AI Thông Minh", "📂 Thư viện Văn bản", "📑 Cẩm nang Nghiệp vụ", "🧮 Máy tính BHXH", "📍 Liên hệ BHXH"]
    st.session_state.current_tab = st.radio("CHỨC NĂNG HỆ THỐNG", menu, label_visibility="collapsed")
    st.divider()
    live_clock()
    st.caption("v35.0 Cosmic Nexus | Advanced Pro 3.1 Edition")

# --- HEADER LED ---
marquee_msg = "🌟 HỆ THỐNG TRA CỨU DỮ LIỆU BHXH THUẬN AN PHIÊN BẢN v35.0 KỶ NGUYÊN KHÔNG GIAN • GIAO DIỆN HOLOGRAPHIC 3.0 • SIÊU MÁY TÍNH TRỰC QUAN ĐA CHIỀU 🌟"
st.markdown(f"<div class='led-marquee'><marquee scrollamount='10'>{marquee_msg}</marquee></div>", unsafe_allow_html=True)

df = load_data()

if df is not None:
    # --- TAB 1: TRA CỨU ---
    if st.session_state.current_tab == "📊 Tra cứu C12-TS":
        if st.session_state.selected_unit is None:
            st.markdown("<div class='gateway-container'>", unsafe_allow_html=True)
            st.markdown("<h1 style='color:#0f172a; font-size:4.5rem; font-weight:900; margin-bottom: 5px; text-shadow: 2px 2px 0px #cbd5e1;'>🛡️ CỔNG TRA CỨU DỮ LIỆU</h1>", unsafe_allow_html=True)
            st.markdown("<p style='color:#475569; font-size:1.8rem; font-weight:800; margin-bottom: 30px;'>NHẬP MÃ ĐƠN VỊ HOẶC TÊN CÔNG TY</p>", unsafe_allow_html=True)
            user_input = st.text_input("Gateway", placeholder="Gõ từ khóa tìm kiếm...", label_visibility="collapsed")
            st.markdown("</div>", unsafe_allow_html=True)
            
            st.markdown('<div class="btn-main" style="text-align:center; margin-bottom: 4rem;">', unsafe_allow_html=True)
            if st.button("🚀 TIẾN HÀNH TRA CỨU", use_container_width=False):
                st.session_state.search_query = user_input
            st.markdown('</div>', unsafe_allow_html=True)

            # EXECUTIVE DASHBOARD
            if not st.session_state.search_query and not user_input:
                st.markdown("<h3 style='color:#1e3a8a; text-align:center; margin-bottom: 20px; font-weight:900;'>📈 BẢNG ĐIỀU KHIỂN TỔNG QUAN (EXECUTIVE DASHBOARD)</h3>", unsafe_allow_html=True)
                e1, e2, e3 = st.columns(3)
                total_units = len(df)
                with e1: st.markdown(f"<div class='exec-widget'><div class='exec-title'>TỔNG SỐ ĐƠN VỊ QUẢN LÝ</div><div class='exec-number'>{total_units:,}</div><div style='color:#93c5fd;'>Doanh nghiệp đang hoạt động</div></div>", unsafe_allow_html=True)
                with e2: st.markdown(f"<div class='exec-widget' style='background: linear-gradient(135deg, #047857 0%, #10b981 100%);'><div class='exec-title' style='color:#a7f3d0;'>TRẠNG THÁI HỆ THỐNG</div><div class='exec-number'>ONLINE</div><div style='color:#a7f3d0;'>Bảo mật cấp độ Enterprise</div></div>", unsafe_allow_html=True)
                with e3: st.markdown(f"<div class='exec-widget' style='background: linear-gradient(135deg, #8b5cf6 0%, #e11d48 100%);'><div class='exec-title' style='color:#fecdd3;'>TRỢ LÝ AI NỘI BỘ</div><div class='exec-number'>ACTIVE</div><div style='color:#fecdd3;'>Xử lý thông minh Offline 100%</div></div>", unsafe_allow_html=True)
                st.write("<br>", unsafe_allow_html=True)

            col_news, col_res, col_off = st.columns([0.8, 1.4, 1.1])
            with col_news:
                st.markdown("##### 📢 TIN TỨC V35")
                st.markdown("<div class='crystal-card' style='min-height:380px; display:flex; flex-direction:column; justify-content:center; background: linear-gradient(180deg, #ffffff 0%, #f0f9ff 100%);'><h4 style='color:#2563eb; font-size: 1.5rem; font-weight: 900;'>🚀 KỶ NGUYÊN KHÔNG GIAN</h4><p style='font-size: 1.15rem; color: #334155; font-weight: 500;'>Cập nhật giao diện Glowing Tương Lai. Nút bấm mang hiệu ứng nhịp thở và hoàn thiện thông tin địa chỉ.</p><hr><small style='color:#10b981; font-weight:900; font-size: 1.1rem;'>VERSION 35.0</small></div>", unsafe_allow_html=True)

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
            # --- DASHBOARD KẾT QUẢ v35 ---
            if not st.session_state.welcome_done:
                st.balloons(); st.session_state.welcome_done = True
            
            unit_data = df[df['madvi'] == st.session_state.selected_unit].iloc[0]
            unit_addr = unidecode(str(unit_data.get('diachi', ''))).lower()
            
            st.button("⬅ QUAY LẠI TÌM KIẾM ĐƠN VỊ KHÁC", on_click=lambda: st.session_state.update(selected_unit=None))
            
            # DYNAMIC GREETING
            current_hour = datetime.now().hour
            if current_hour < 12: greeting = "🌅 CHÀO BUỔI SÁNG"
            elif current_hour < 18: greeting = "☀️ CHÀO BUỔI CHIỀU"
            else: greeting = "🌙 CHÀO BUỔI TỐI"

            st.markdown(f"""
                <div class='premium-header'>
                    <div style='font-size: 1.2rem; color: #bae6fd; font-weight: 800; margin-bottom: 5px; text-transform: uppercase; position: relative; z-index: 2;'>{greeting}, ĐƠN VỊ:</div>
                    <h1>🏢 {unit_data.get('tendvi')}</h1>
                    <p>MÃ ĐƠN VỊ: <span style='background:rgba(255,255,255,0.2); padding: 5px 15px; border-radius: 10px;'>{unit_data.get('madvi')}</span> &nbsp;|&nbsp; ĐỊA CHỈ: {unit_data.get('diachi', 'N/A')}</p>
                </div>
            """, unsafe_allow_html=True)

            # AI SMART SUMMARY
            debt_val = unit_data.get('tien_cuoi_ky', 0)
            status_text = "✨ Đã hoàn thành 100% nghĩa vụ đóng BHXH, không có nợ đọng." if debt_val <= 0 else f"⚠️ Hiện đang lệch/nợ: {abs(debt_val):,.0f} VNĐ. Cần kiểm tra UNC để nộp bù."
            st.markdown(f"""
                <div class='ai-summary'>
                    <span style='font-size: 1.5rem;'>🤖</span> <b>AI Tự Động Phân Tích:</b> Doanh nghiệp đã đóng <b>{unit_data.get('so_da_dong', 0):,.0f} VNĐ</b> / <b>{unit_data.get('so_phai_dong', 0):,.0f} VNĐ</b>. {status_text}
                </div>
            """, unsafe_allow_html=True)
            
            cl, cr = st.columns([1.8, 1])
            with cl:
                st.write("<h3 style='color:#1e3a8a; margin-top: 15px; font-weight: 900;'>📊 BÁO CÁO TÀI CHÍNH CHI TIẾT</h3>", unsafe_allow_html=True)
                m1, m2, m3 = st.columns(3)
                with m1: st.markdown(f"<div class='crystal-card'><div class='metric-lbl'>Đầu kỳ</div><div class='metric-val'>{unit_data.get('tien_dau_ky', 0):,.0f}</div></div>", unsafe_allow_html=True)
                with m2: st.markdown(f"<div class='crystal-card'><div class='metric-lbl'>Phải đóng</div><div class='metric-val'>{unit_data.get('so_phai_dong', 0):,.0f}</div></div>", unsafe_allow_html=True)
                with m3: st.markdown(f"<div class='crystal-card'><div class='metric-lbl'>Điều chỉnh</div><div class='metric-val'>{unit_data.get('dieu_chinh_ky_truoc', 0):,.0f}</div></div>", unsafe_allow_html=True)
                
                st.write("<br>", unsafe_allow_html=True)
                m4, m5, m6 = st.columns(3)
                with m4: st.markdown(f"<div class='crystal-card'><div class='metric-lbl'>Đã đóng</div><div class='metric-val' style='color:#10b981;'>{unit_data.get('so_da_dong', 0):,.0f}</div></div>", unsafe_allow_html=True)
                with m5: st.markdown(f"<div class='crystal-card'><div class='metric-lbl'>Lệch</div><div class='metric-val' style='color:#ef4444;'>{unit_data.get('so_bi_lech', 0):,.0f}</div></div>", unsafe_allow_html=True)
                status_clr = '#ef4444' if debt_val > 0 else '#10b981'
                with m6: st.markdown(f"<div class='crystal-card' style='border: 4px solid {status_clr}; background: {status_clr}11;'><div class='metric-lbl'>{'SỐ TIỀN CÒN NỢ' if debt_val > 0 else 'SỐ TIỀN DƯ CÓ'}</div><div class='metric-val' style='color:{status_clr};'>{abs(debt_val):,.0f}</div></div>", unsafe_allow_html=True)
                
                st.write("<br>", unsafe_allow_html=True)
                csv_data = convert_df(pd.DataFrame([unit_data]))
                st.download_button(label="📥 TẢI BÁO CÁO NÀY (EXCEL/CSV)", data=csv_data, file_name=f"BaoCao_BHXH_{unit_data.get('madvi')}.csv", mime='text/csv', use_container_width=True)

            with cr:
                rate = min(round((unit_data.get('so_da_dong', 0) / unit_data.get('so_phai_dong', 1)) * 100, 1), 100)
                st.markdown("<p style='font-weight: 800; color: #1e3a8a; text-align: center; font-size: 1.2rem; margin-bottom: 5px;'>THANH TIẾN ĐỘ</p>", unsafe_allow_html=True)
                st.progress(int(rate))

                fig = go.Figure(go.Indicator(
                    mode="gauge+number", value=rate, 
                    title={'text': "<b>TỶ LỆ HOÀN THÀNH (%)</b>", 'font': {'size': 24, 'color': '#1e3a8a'}}, 
                    number={'suffix': "%", 'font': {'color': '#2563eb', 'size': 70}}, 
                    gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#2563eb"}}
                )).update_layout(paper_bgcolor="rgba(0,0,0,0)", height=350, margin=dict(t=30, b=0))
                st.plotly_chart(fig, use_container_width=True)
                
                for off in OFFICERS:
                    if any(kw in unit_addr for kw in off['keywords']) or any(kw in unit_data.get('madvi','').lower() for kw in off['keywords']):
                        st.markdown(f"<div class='crystal-card' style='background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%); color: white; margin-top:0px;'><small style='color:#39ff14; font-weight:900; letter-spacing: 1.5px;'>👨‍💼 CÁN BỘ PHỤ TRÁCH TRỰC TIẾP</small><h2 style='color:#fff; margin:15px 0; font-size: 2.2rem;'>{off['name']}</h2><a href='tel:{off['phone'].replace('.','')}' style='color:#00f2fe; font-size: 2.2rem; text-decoration:none; font-weight:900; text-shadow: 0 0 15px #00f2fe;'>📱 {off['phone']}</a><br><a href='{off['zalo']}' target='_blank' style='background:white; color:#1e3a8a; padding:15px 40px; border-radius:50px; text-decoration:none; display:inline-block; margin-top:25px; font-weight:900; font-size: 1.1rem; box-shadow: 0 10px 25px rgba(0,0,0,0.3); text-transform: uppercase; transition: all 0.3s;'>💬 CHAT ZALO NGAY</a></div>", unsafe_allow_html=True)
                        break

            render_vip_bank_accounts(unit_data.get('madvi'), unit_data.get('tendvi'))

    # --- TAB 2: AI NỘI BỘ (ĐƯỢC BẢO LƯU 100%) ---
    elif st.session_state.current_tab == "🤖 Trợ lý AI Thông Minh":
        st.markdown("## 🧠 TRỢ LÝ THÔNG MINH BHXH (CHẾ ĐỘ OFFLINE 2.0)")
        
        context = ""
        if st.session_state.selected_unit:
            unit = df[df['madvi'] == st.session_state.selected_unit].iloc[0]
            context = f"Tên đơn vị: {unit['tendvi']}\nMã đơn vị: {unit['madvi']}\nSố tiền nợ/dư cuối kỳ: {unit['tien_cuoi_ky']:,} VNĐ."
            st.success(f"🤖 Trợ lý đã liên kết dữ liệu của **{unit['tendvi']}**. Hệ thống hoạt động 100% Offline bảo mật, không cần API Key.")
        else:
            st.info("🤖 Trợ lý thông minh đã kích hoạt chế độ Không cần API Key. Bất tử trước mọi lỗi mạng! Đảm bảo phản hồi ngay lập tức!")

        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]): st.markdown(msg["content"])
            
        if prompt := st.chat_input("Hãy hỏi các từ khóa: mức đóng, thai sản, chốt sổ, nợ tiền..."):
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            with st.chat_message("assistant"):
                with st.spinner("Đang truy xuất CSDL nội bộ..."):
                    resp = get_ai_response(prompt, context)
                    st.markdown(resp)
                    st.session_state.chat_history.append({"role": "assistant", "content": resp})

    # --- TAB 3: PDF (ĐƯỢC BẢO LƯU 100%) ---
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
                    render_pdf_unblockable(st.session_state.active_pdf)

    # --- TAB 4: CẨM NANG NGHIỆP VỤ ---
    elif st.session_state.current_tab == "📑 Cẩm nang Nghiệp vụ": 
        st.markdown("## 📑 CẨM NANG NGHIỆP VỤ SỐ HOÁ")
        st.markdown("<p style='font-size: 1.2rem; color: #475569; margin-bottom: 30px;'>Hướng dẫn chi tiết từng bước giải quyết các chế độ BHXH, BHYT, BHTN dành cho Đơn vị sử dụng lao động.</p>", unsafe_allow_html=True)
        
        with st.expander("🤰 1. Hồ sơ giải quyết chế độ THAI SẢN", expanded=True):
            st.markdown("""
            **Điều kiện hưởng:** Đóng đủ 6 tháng BHXH trở lên trong thời gian 12 tháng trước khi sinh con.
            - **Hồ sơ gồm:**
              1. Bản sao Giấy chứng sinh hoặc Bản sao Giấy khai sinh của con.
              2. Danh sách đề nghị giải quyết hưởng chế độ (Mẫu 01B-HSB) do đơn vị lập.
            - **Thời hạn nộp:** Trong vòng 45 ngày kể từ ngày NLĐ trở lại làm việc.
            - **Mức hưởng:** 100% mức bình quân tiền lương tháng đóng BHXH của 6 tháng liền kề trước khi nghỉ.
            """)
            
        with st.expander("🤒 2. Hồ sơ giải quyết chế độ ỐM ĐAU"):
            st.markdown("""
            **Điều kiện hưởng:** Bị ốm đau, tai nạn phải nghỉ việc và có xác nhận của cơ sở KCB có thẩm quyền.
            - **Hồ sơ gồm:**
              1. Giấy ra viện (nếu điều trị nội trú) hoặc Giấy chứng nhận nghỉ việc hưởng BHXH (mẫu C65-HD) nếu điều trị ngoại trú.
              2. Danh sách đề nghị giải quyết hưởng chế độ (Mẫu 01B-HSB) do đơn vị lập.
            - **Mức hưởng:** 75% mức tiền lương đóng BHXH của tháng liền kề trước khi nghỉ việc.
            """)
            
        with st.expander("🛑 3. Trình tự CHỐT SỔ BHXH khi NLĐ nghỉ việc"):
            st.markdown("""
            **Trình tự thực hiện (Rất quan trọng):**
            1. **Báo giảm lao động:** Đơn vị lập hồ sơ báo giảm trên phần mềm giao dịch điện tử (VNPT, Viettel, EFY...) vào tháng NLĐ chính thức nghỉ việc.
            2. **Hoàn thành nghĩa vụ tài chính:** Đơn vị phải đóng đầy đủ tiền BHXH, BHYT, BHTN của toàn bộ NLĐ tính đến hết tháng báo giảm. Nếu còn nợ, cơ quan BHXH sẽ không thể chốt sổ.
            3. **Nộp hồ sơ giấy:** Đơn vị thu hồi Tờ bìa sổ và các tờ rời của NLĐ (kèm theo Mẫu TK1-TS nếu cần điều chỉnh thông tin) và gửi qua dịch vụ bưu chính về cơ quan BHXH để tiến hành in tờ rời chốt sổ.
            """)

    # --- TAB 5: MÁY TÍNH BHXH ---
    elif st.session_state.current_tab == "🧮 Máy tính BHXH":
        st.markdown("## 🧮 SIÊU MÁY TÍNH DỰ TOÁN ĐÓNG BHXH V35")
        st.markdown("<p style='font-size: 1.2rem; color: #475569; margin-bottom: 20px;'>Nhập mức lương cơ sở hoặc quỹ lương để hệ thống tự động phân tách nghĩa vụ tài chính bằng Biểu đồ trực quan.</p>", unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        with col1:
            sal = st.number_input("💰 Nhập mức lương đóng BHXH (VNĐ):", value=5000000, step=100000)
            
        # Tính toán
        nld_bhxh = sal * 0.08
        nld_bhyt = sal * 0.015
        nld_bhtn = sal * 0.01
        nld_total = nld_bhxh + nld_bhyt + nld_bhtn

        dn_bhxh = sal * 0.175
        dn_bhyt = sal * 0.03
        dn_bhtn = sal * 0.01
        dn_total = dn_bhxh + dn_bhyt + dn_bhtn
        
        st.markdown("### 📊 CHI TIẾT PHÂN BỔ TRÍCH NỘP (32%)")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"""
            <div class='crystal-card' style='border-top: 6px solid #0ea5e9; text-align: left;'>
                <h4 style='color: #64748b; margin-top:0;'>👤 NGƯỜI LAO ĐỘNG (10.5%)</h4>
                <h2 style='color:#0ea5e9; font-size: 2.8rem; margin: 10px 0;'>{nld_total:,.0f} <span style='font-size:1.2rem;'>VNĐ</span></h2>
                <hr>
                <p style='font-size: 1.1rem;'><b>BHXH (8%):</b> {nld_bhxh:,.0f} VNĐ</p>
                <p style='font-size: 1.1rem;'><b>BHYT (1.5%):</b> {nld_bhyt:,.0f} VNĐ</p>
                <p style='font-size: 1.1rem;'><b>BHTN (1%):</b> {nld_bhtn:,.0f} VNĐ</p>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class='crystal-card' style='border-top: 6px solid #8b5cf6; text-align: left;'>
                <h4 style='color: #64748b; margin-top:0;'>🏢 DOANH NGHIỆP (21.5%)</h4>
                <h2 style='color:#8b5cf6; font-size: 2.8rem; margin: 10px 0;'>{dn_total:,.0f} <span style='font-size:1.2rem;'>VNĐ</span></h2>
                <hr>
                <p style='font-size: 1.1rem;'><b>BHXH (17.5%):</b> {dn_bhxh:,.0f} VNĐ</p>
                <p style='font-size: 1.1rem;'><b>BHYT (3%):</b> {dn_bhyt:,.0f} VNĐ</p>
                <p style='font-size: 1.1rem;'><b>BHTN (1%):</b> {dn_bhtn:,.0f} VNĐ</p>
            </div>
            """, unsafe_allow_html=True)
            
        # BIỂU ĐỒ DONUT CHART MÀU SẮC CYBERPUNK (V35)
        st.write("<br>", unsafe_allow_html=True)
        fig_pie = go.Figure(data=[go.Pie(
            labels=['DOANH NGHIỆP (21.5%)', 'NGƯỜI LAO ĐỘNG (10.5%)'],
            values=[dn_total, nld_total],
            hole=.5,
            marker_colors=['#8b5cf6', '#0ea5e9'],
            textinfo='label+percent',
            textfont_size=15,
            textfont_color='white'
        )])
        fig_pie.update_layout(
            title_text="BIỂU ĐỒ CƠ CẤU TRÍCH NỘP",
            title_x=0.5,
            title_font_color="#1e3a8a",
            title_font_size=22,
            showlegend=False,
            margin=dict(t=50, b=20, l=20, r=20),
            height=400,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig_pie, use_container_width=True)

        with st.expander("🔍 BẢNG TÓM TẮT CHI TIẾT TỪNG QUỸ BẢO HIỂM (Bấm để xem)"):
            df_breakdown = pd.DataFrame({
                'Quỹ Bảo Hiểm': ['Hưu trí - Tử tuất', 'Ốm đau - Thai sản', 'TNLĐ - BNN', 'Bảo hiểm Y tế (BHYT)', 'Bảo hiểm Thất nghiệp (BHTN)'],
                'Tỷ lệ Doanh nghiệp đóng': ['14%', '3%', '0.5%', '3%', '1%'],
                'Tỷ lệ NLĐ trích lương': ['8%', '0%', '0%', '1.5%', '1%'],
                'Tổng cộng': ['22%', '3%', '0.5%', '4.5%', '2%']
            })
            st.table(df_breakdown)
            
        st.markdown(f"""
            <div class='ai-summary' style='text-align:center; padding: 30px; margin-top: 30px; border-left: none; background: linear-gradient(90deg, #eff6ff 0%, #dbeafe 100%); border-bottom: 8px solid #1e3a8a;'>
                <h3 style='margin:0; color:#475569;'>🚀 TỔNG CỘNG ĐƠN VỊ PHẢI CHUYỂN KHOẢN (32%)</h3>
                <span style='font-size: 3.5rem; color: #1e3a8a; font-weight: 900;'>{(nld_total + dn_total):,.0f} VNĐ</span>
            </div>
        """, unsafe_allow_html=True)

    # --- TAB 6: LIÊN HỆ (ĐÃ CẬP NHẬT CHUẨN XÁC V35) ---
    elif st.session_state.current_tab == "📍 Liên hệ BHXH":
        st.markdown("## 📍 TRUNG TÂM HỖ TRỢ & LIÊN HỆ")
        st.markdown("""
        <div class='crystal-card' style='text-align: center; border-bottom: 8px solid #2563eb; padding: 50px 20px; margin-top: 30px;'>
            <img src='https://cdn-icons-png.flaticon.com/512/8198/8198144.png' width='120' style='margin-bottom: 20px;'>
            <h1 style='color:#1e3a8a; font-size: 2.8rem; margin-bottom: 20px;'>BẢO HIỂM XÃ HỘI CƠ SỞ THUẬN AN</h1>
            <p style='font-size: 1.4rem; color: #475569;'><b>📍 Địa chỉ:</b> Thôn Thuận Sơn, xã Thuận An, tỉnh Lâm Đồng.</p>
            <p style='font-size: 1.4rem; color: #475569;'><b>📞 Điện thoại:</b> <span style='color:#2563eb; font-weight:900;'>02613. 741.255</span></p>
            <p style='font-size: 1.4rem; color: #475569;'><b>📧 Email:</b> thuanan@lamdong.vss.gov.vn</p>
            <hr style='margin: 40px 0; border: 1px dashed #cbd5e1;'>
            <p style='font-size: 1.2rem; color: #64748b; font-style: italic;'>"Luôn đồng hành cùng sự phát triển bền vững của Doanh nghiệp và Người lao động"</p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br><hr><center style='color:#94a3b8; font-size:0.95rem; padding-bottom:60px;'>© 2026 BHXH CƠ SỞ THUẬN AN | v35.0 Cosmic Nexus (Advanced Edition)</center>", unsafe_allow_html=True)
