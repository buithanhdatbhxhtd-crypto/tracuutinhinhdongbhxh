import streamlit as st
import pandas as pd
import numpy as np
import os
import plotly.graph_objects as go
from unidecode import unidecode
import time
from datetime import datetime

# --- CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="BHXH Thuận An - v16.0 Beyond Digital",
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

# --- TỔNG LỰC CSS (GIAO DIỆN BEYOND DIGITAL v16.0) ---
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
        --glass: rgba(255, 255, 255, 0.92);
    }

    * { font-family: 'Plus Jakarta Sans', sans-serif; }
    
    .stApp {
        background: radial-gradient(circle at 50% 50%, #f8fafc 0%, #e2e8f0 100%);
    }

    /* HIỆU ỨNG CHUYỂN TRANG MƯỢT MÀ */
    .stApp > section {
        animation: fadeIn 0.8s ease-in-out;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* BẢNG LED RGB CAO CẤP */
    .led-marquee {
        background: linear-gradient(90deg, #000, #1a1a1a, #000);
        color: #00ff00;
        padding: 12px 0;
        font-weight: 700;
        border-radius: 15px;
        box-shadow: 0 0 25px rgba(0, 255, 0, 0.4);
        border: 2px solid #444;
        margin-bottom: 30px;
        font-family: 'Courier New', Courier, monospace;
        font-size: 1.2rem;
        text-shadow: 0 0 10px #00ff00;
        border-left: 5px solid #00ff00;
        border-right: 5px solid #00ff00;
    }

    /* SIÊU Ô TÌM KIẾM TRUNG TÂM (FIXED & BEYOND) */
    .mega-search-wrapper {
        max-width: 1100px;
        margin: 0 auto 3.5rem auto;
        text-align: center;
        position: relative;
    }

    div[data-testid="stTextInput"] > div {
        height: auto !important;
        background: transparent !important;
    }

    .stTextInput input {
        border-radius: 30px !important;
        padding: 20px 60px !important; 
        border: 10px solid var(--secondary) !important;
        font-size: 3rem !important; 
        font-weight: 900 !important;
        height: 150px !important; 
        background: white !important;
        color: var(--primary) !important;
        box-shadow: 0 40px 90px rgba(59, 130, 246, 0.5) !important;
        transition: all 0.6s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        text-align: center !important;
        line-height: normal !important;
    }
    
    .stTextInput input:focus {
        border-color: var(--neon-blue) !important;
        transform: scale(1.03) translateY(-5px);
        box-shadow: 0 50px 120px rgba(0, 210, 255, 0.6) !important;
    }

    /* THẺ CÁN BỘ MATRIX NEON */
    .officer-matrix-card {
        background: #080808;
        padding: 25px;
        border-radius: 30px;
        border: 4px solid #1a1a1a;
        margin-bottom: 25px;
        text-align: center;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
    }
    .officer-matrix-card:hover { 
        transform: translateY(-12px) rotate(1deg);
        border-color: #555;
        box-shadow: 0 20px 40px rgba(0,0,0,0.6);
    }

    @keyframes neon-pulse-blue { 0%, 100% { box-shadow: 0 0 15px #00d2ff; } 50% { box-shadow: 0 0 35px #00d2ff; } }
    @keyframes neon-pulse-gold { 0%, 100% { box-shadow: 0 0 15px #ffaa00; } 50% { box-shadow: 0 0 35px #ffaa00; } }
    @keyframes neon-pulse-green { 0%, 100% { box-shadow: 0 0 15px #39ff14; } 50% { box-shadow: 0 0 35px #39ff14; } }

    .card-nhai { animation: neon-pulse-blue 2s infinite; border-color: #00d2ff !important; }
    .card-dat { animation: neon-pulse-gold 2.5s infinite; border-color: #ffaa00 !important; }
    .card-hai { animation: neon-pulse-green 3s infinite; border-color: #39ff14 !important; }

    /* NÚT ZALO & LIÊN HỆ */
    .contact-badge {
        background: #0068ff;
        color: white !important;
        padding: 10px 20px;
        border-radius: 50px;
        text-decoration: none !important;
        font-weight: 800;
        font-size: 1rem;
        display: inline-block;
        margin-top: 15px;
        box-shadow: 0 5px 15px rgba(0, 104, 255, 0.4);
        transition: all 0.3s;
    }
    .contact-badge:hover { background: white; color: #0068ff !important; transform: scale(1.1); }

    /* DASHBOARD */
    .glass-dashboard {
        background: var(--glass);
        backdrop-filter: blur(25px);
        border-radius: 50px;
        padding: 50px;
        box-shadow: 0 40px 120px rgba(0,0,0,0.1);
        border: 1px solid rgba(255,255,255,0.8);
    }

    /* TIỆN ÍCH SIDEBAR DARK MODE */
    [data-testid="stSidebar"] { background-color: #020617; }
    .sidebar-title { color: #fff; font-weight: 900; text-align: center; margin-bottom: 2rem; font-size: 1.5rem; letter-spacing: 2px; }

    /* INDICATORS */
    .status-live {
        height: 12px; width: 12px; background-color: #ff3131; border-radius: 50%;
        display: inline-block; margin-right: 8px; animation: heartbeat 1.2s infinite;
    }
    @keyframes heartbeat { 0% { transform: scale(1); opacity: 1; } 50% { transform: scale(1.5); opacity: 0.4; } 100% { transform: scale(1); opacity: 1; } }
    </style>
    """, unsafe_allow_html=True)

# --- DATA HUB: CÁN BỘ & NGÂN HÀNG ---
OFFICERS = [
    {
        "name": "Bà NGUYỄN THỊ NHÀI", "scope": "Xã Đức Lập, Xã Đắk Mil", 
        "phone": "0846.39.29.29", "zalo": "https://zalo.me/0846392929",
        "class": "card-nhai", "color": "#00d2ff", "areas": ["duc lap", "dak mil", "đức lập", "đắk mil"]
    },
    {
        "name": "Ông BÙI THÀNH ĐẠT", "scope": "Xã Đắk Sắk, Xã Đắk Song", 
        "phone": "0986.05.30.06", "zalo": "https://zalo.me/0986053006",
        "class": "card-dat", "color": "#ffaa00", "areas": ["dak sak", "dak song", "đắk sắk", "đắk song"]
    },
    {
        "name": "Ông HOÀNG SỸ HẢI", "scope": "Xã Thuận An", 
        "phone": "0919.06.11.53", "zalo": "https://zalo.me/0919061153",
        "class": "card-hai", "color": "#39ff14", "areas": ["thuan an", "thuận an"]
    }
]

BANKS = [
    {"name": "BIDV", "number": "63510009867032"},
    {"name": "AGRIBANK", "number": "5301202919045"},
    {"name": "VIETINBANK", "number": "919035000003"}
]

# --- HÀM TẢI DỮ LIỆU ---
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

# --- MENU SIDEBAR v16.0 ---
with st.sidebar:
    st.markdown("<div class='sidebar-title'>🛡️ BEYOND BHXH</div>", unsafe_allow_html=True)
    st.divider()
    
    tabs = {
        "📊 Tra cứu C12-TS": "Báo cáo đóng BHXH mới nhất",
        "🤖 Trợ lý AI (Beyond)": "Giải đáp chính sách thông minh",
        "📰 Tin tức & Văn bản": "Cập nhật Nghị định, Thông tư",
        "📑 Cẩm nang Thủ tục": "Hướng dẫn các bước hồ sơ",
        "🧮 Máy tính BHXH 2026": "Công cụ tính mức đóng nhanh",
        "💬 Góp ý trực tuyến": "Cải thiện dịch vụ công",
        "📍 Bản đồ cơ sở": "Chỉ đường đến cơ quan"
    }
    
    for t_name, t_desc in tabs.items():
        if st.button(t_name, use_container_width=True, key=f"tab_{t_name}"):
            st.session_state.current_tab = t_name
            st.rerun()
            
    st.divider()
    st.markdown("### 🏦 THUẬN AN HUB")
    st.info("Phiên bản v16.0 - Tối ưu 2026")

# --- HEADER (LED MARQUEE RGB) ---
marquee_msg = "💎 CHÀO MỪNG QUÝ ĐƠN VỊ ĐẾN VỚI HỆ THỐNG TRA CỨU BHXH THUẬN AN PHIÊN BẢN v16.0 BEYOND DIGITAL • TÍCH HỢP TRÍ TUỆ NHÂN TẠO VÀ KẾT NỐI ZALO TRỰC TIẾP • ĐỊA CHỈ: THÔN THUẬN SƠN, XÃ THUẬN AN, TỈNH LÂM ĐỒNG •"
st.markdown(f"<div class='led-marquee'><marquee scrollamount='10'>{marquee_msg}</marquee></div>", unsafe_allow_html=True)

df = load_data()

if df is not None:
    
    # --- TAB 1: TRA CỨU C12-TS ---
    if st.session_state.current_tab == "📊 Tra cứu C12-TS":
        if st.session_state.selected_unit is None:
            # SIÊU Ô TÌM KIẾM TRUNG TÂM
            st.markdown("<div class='mega-search-wrapper'>", unsafe_allow_html=True)
            st.markdown("<h1 style='color:#1e3a8a; font-size:4rem; font-weight:900; margin-bottom:10px;'>🛡️ HỆ THỐNG TRA CỨU</h1>", unsafe_allow_html=True)
            st.markdown("<p style='color:#64748b; font-size:1.8rem; margin-bottom:45px; font-weight:700;'>NHẬP MÃ ĐƠN VỊ HOẶC TÊN CÔNG TY</p>", unsafe_allow_html=True)
            query = st.text_input("Gateway", placeholder="🔍 Nhập tại đây để xem số liệu...", label_visibility="collapsed")
            st.markdown("</div>", unsafe_allow_html=True)

            col_post, col_res, col_info = st.columns([0.85, 1.4, 1.1])

            with col_post:
                st.markdown("##### 📢 TIN TỨC MỚI")
                posters = [
                    {"t": "🛡️ AN SINH 2026", "c": "Các quy định mới về đóng BHXH bắt đầu có hiệu lực từ tháng này."},
                    {"t": "🏥 PHÁT HÀNH THẺ", "c": "Cấp thẻ BHYT điện tử ngay trên ứng dụng VssID cực kỳ nhanh chóng."},
                    {"t": "🤰 THAI SẢN MỚI", "c": "Thời gian giải quyết hồ sơ thai sản rút ngắn còn 5 ngày làm việc."}
                ]
                p = posters[datetime.now().minute % len(posters)]
                st.markdown(f"""
                    <div style='background:white; padding:40px; border-radius:40px; border:2.5px solid #e2e8f0; text-align:center; min-height:350px; display:flex; flex-direction:column; justify-content:center; box-shadow: 0 20px 40px rgba(0,0,0,0.06);'>
                        <h3 style='color:#1e3a8a; margin:0;'>{p['t']}</h3>
                        <p style='font-size:1.15rem; color:#64748b; margin:20px 0; line-height:1.7;'>{p['c']}</p>
                        <hr style='border: 0.5px solid #eee;'>
                        <small style='color:#ffaa00; font-weight:800;'>BHXH THUẬN AN ĐỒNG HÀNH</small>
                    </div>
                """, unsafe_allow_html=True)

            with col_res:
                if query:
                    clean_query = unidecode(query).lower()
                    results = df[df['search_index'].str.contains(clean_query, na=False)].head(8)
                    if not results.empty:
                        st.write(f"✨ Tìm thấy **{len(results)}** kết quả phù hợp:")
                        for idx, row in results.iterrows():
                            with st.container():
                                ca, cb = st.columns([3.2, 1.3])
                                ca.markdown(f"""
                                    <div style='background:white; padding:25px; border-radius:25px; border-left:12px solid #2563eb; margin-bottom:15px; box-shadow:0 8px 20px rgba(0,0,0,0.04);'>
                                        <small style='color:#2563eb; font-weight:800; text-transform:uppercase;'>Mã: {row.get('madvi')}</small><br>
                                        <b style='font-size:1.4rem; color:#1e293b;'>{row.get('tendvi')}</b>
                                    </div>
                                """, unsafe_allow_html=True)
                                if cb.button("XÁC NHẬN ➔", key=f"sel_{row.get('madvi')}_{idx}", use_container_width=True):
                                    st.session_state.selected_unit = row.get('madvi')
                                    st.session_state.show_loading = True
                                    st.rerun()
                else:
                    st.markdown("<br><center><img src='https://cdn-icons-png.flaticon.com/512/3772/3772274.png' width='180' style='opacity:0.25'><h3 style='color:#94a3b8;'>Hệ thống Digital v16.0 sẵn sàng</h3></center>", unsafe_allow_html=True)

            with col_info:
                st.markdown("##### 👨‍💼 CÁN BỘ CHUYÊN QUẢN (LIVE)")
                for off in OFFICERS:
                    st.markdown(f"""
                    <div class="officer-matrix-card {off['class']}">
                        <div class="status-live"></div><small style="color:white; font-weight:800;">TRỰC TUYẾN</small>
                        <div style="color:{off['color']}; font-weight:900; font-size:1.25rem; margin-top:10px;">{off['name']}</div>
                        <div style="color:#aaa; font-size:0.9rem; margin:8px 0;">Phụ trách: {off['scope']}</div>
                        <a href="tel:{off['phone'].replace('.','')}" style="text-decoration:none; color:white; font-weight:800; font-size:1.3rem;">📱 {off['phone']}</a><br>
                        <a href="{off['zalo']}" target="_blank" class="contact-badge">💬 CHAT ZALO NGAY</a>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("##### 🏦 SỐ TÀI KHOẢN CỦA BHXH CƠ SỞ THUẬN AN")
                for bank in BANKS:
                    st.markdown(f"""
                    <div style="background:linear-gradient(135deg, #0f172a 0%, #1e293b 100%); padding:18px; border-radius:18px; border-left:8px solid #00d2ff; margin-bottom:10px;">
                        <div style="color:#00d2ff; font-weight:900; font-size:0.9rem; text-transform:uppercase;">{bank['name']}</div>
                        <div style="color:#fff; font-size:1.3rem; font-family:monospace; font-weight:800; letter-spacing:1px;">{bank['number']}</div>
                    </div>
                    """, unsafe_allow_html=True)

        # MÀN HÌNH LOADING CAO CẤP
        elif st.session_state.show_loading:
            st.markdown("<br><br><br>", unsafe_allow_html=True)
            with st.status("💎 ĐANG KẾT NỐI BEYOND DIGITAL...", expanded=True) as status:
                st.write("📡 Truy xuất Database trung tâm...")
                time.sleep(0.6)
                st.write("⚡ Đồng bộ số liệu C12-TS theo thời gian thực...")
                time.sleep(0.6)
                st.write("🎨 Khởi tạo Holographic Dashboard...")
                time.sleep(0.5)
                status.update(label="TẢI DỮ LIỆU THÀNH CÔNG!", state="complete")
            st.session_state.show_loading = False
            st.balloons()
            st.rerun()

        # DASHBOARD CHI TIẾT
        else:
            unit_data = df[df['madvi'] == st.session_state.selected_unit].iloc[0]
            unit_addr = unidecode(str(unit_data.get('diachi', ''))).lower()
            
            if st.button("⬅ QUAY LẠI TRANG TÌM KIẾM"):
                st.session_state.selected_unit = None
                st.rerun()

            st.markdown(f"""
                <div style='background:white; padding:50px; border-radius:50px; border-left:25px solid #1e3a8a; box-shadow: 0 30px 80px rgba(0,0,0,0.08); margin-top:20px;'>
                    <h1 style='margin:0; color:#1e3a8a; font-size:3.5rem;'>🏢 {unit_data.get('tendvi')}</h1>
                    <p style='margin:12px 0 0 0; color:#64748b; font-size:1.3rem;'>Mã đơn vị: <b>{unit_data.get('madvi')}</b> | Địa chỉ: {unit_data.get('diachi', 'N/A')}</p>
                </div>
            """, unsafe_allow_html=True)

            col_l, col_r = st.columns([1.8, 1])
            with col_l:
                st.markdown("<div class='glass-dashboard' style='margin-top:30px;'>", unsafe_allow_html=True)
                st.write("### 📉 PHÂN TÍCH TÀI CHÍNH TỔNG QUAN")
                
                # Metric Grid với hiệu ứng chữ rõ ràng
                m1, m2, m3 = st.columns(3)
                m1.metric("Tiền đầu kỳ", f"{unit_data.get('tien_dau_ky', 0):,.0f}đ")
                m2.metric("Số phải đóng", f"{unit_data.get('so_phai_dong', 0):,.0f}đ")
                m3.metric("Điều chỉnh", f"{unit_data.get('dieu_chinh_ky_truoc', 0):,.0f}đ")
                
                st.write("<br>", unsafe_allow_html=True)
                m4, m5, m6 = st.columns(3)
                m4.metric("Số đã đóng", f"{unit_data.get('so_da_dong', 0):,.0f}đ")
                m5.metric("Số bị lệch", f"{unit_data.get('so_bi_lech', 0):,.0f}đ")
                debt = unit_data.get('tien_cuoi_ky', 0)
                m6.metric("CÒN NỢ" if debt > 0 else "DƯ CÓ", f"{abs(debt):,.0f}đ", delta=-debt, delta_color="inverse")
                
                now = datetime.now()
                transfer_note = f"{unit_data.get('madvi')} {unit_data.get('tendvi')} đóng bhxh tháng {now.month} năm {now.year}"
                st.markdown(f"""
                    <div style='background:#eff6ff; padding:35px; border-radius:35px; border:4px dashed #2563eb; margin-top:35px; text-align:center;'>
                        <p style='color:#1e40af; font-weight:800; font-size:1.2rem; text-transform:uppercase;'>📝 CÚ PHÁP CHUYỂN KHOẢN CHUẨN:</p>
                        <h3 style='color:#1e3a8a; font-family:monospace; font-size:2.2rem; background:white; padding:20px; border-radius:20px; border:1px solid #dbeafe; margin:20px 0;'>{transfer_note}</h3>
                        <p style='color:#64748b; font-size:1rem;'><i>(Vui lòng ghi đúng nội dung để hệ thống tự động gạch nợ chính xác trong 24h)</i></p>
                    </div>
                """, unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

            with col_r:
                phai_dong = unit_data.get('so_phai_dong', 1)
                da_dong = unit_data.get('so_da_dong', 0)
                rate = min(round((da_dong / phai_dong) * 100, 1), 100) if phai_dong > 0 else 0
                fig = go.Figure(go.Indicator(
                    mode = "gauge+number", value = rate,
                    title = {'text': "TỶ LỆ HOÀN THÀNH (%)", 'font': {'size': 26, 'color': '#1e3a8a', 'weight': 'bold'}},
                    number = {'suffix': "%", 'font': {'color': '#1e40af', 'size': 70}},
                    gauge = {
                        'axis': {'range': [0, 100], 'tickwidth': 1},
                        'bar': {'color': "#1e40af"},
                        'bgcolor': "white",
                        'borderwidth': 3,
                        'steps': [{'range': [0, 50], 'color': '#fee2e2'}, {'range': [90, 100], 'color': '#dcfce7'}]
                    }
                ))
                fig.update_layout(height=480, margin=dict(l=40, r=40, t=80, b=40), paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig, use_container_width=True)
                
                # Highlight Cán bộ phụ trách xã (Neon Matrix)
                for off in OFFICERS:
                    if any(area in unit_addr for area in off['areas']):
                        st.markdown(f"""
                        <div class="officer-matrix-card {off['class']}" style="background:#000;">
                            <div class="status-live"></div><small style="color:#39ff14; font-weight:900; letter-spacing:1px;">PHỤ TRÁCH TRỰC TIẾP</small>
                            <h4 style="margin:10px 0; color:{off['color']}; font-size:1.7rem;">{off['name']}</h4>
                            <a href="tel:{off['phone'].replace('.','')}" style="text-decoration:none; color:white; font-weight:800; font-size:1.6rem;">📱 {off['phone']}</a><br>
                            <a href="{off['zalo']}" target="_blank" class="contact-badge" style="width:100%; text-align:center;">GỬI TIN NHẮN ZALO</a>
                        </div>
                        """, unsafe_allow_html=True)

    # --- TAB 2: AI ASSISTANT (BEYOND DIGITAL) ---
    elif st.session_state.current_tab == "🤖 Trợ lý AI (Beyond)":
        st.markdown("## 🤖 TRỢ LÝ ẢO BEYOND DIGITAL")
        st.chat_input("Hãy hỏi tôi về chính sách BHXH 2026...")
        st.info("Hệ thống AI đang được huấn luyện dữ liệu theo Nghị định mới nhất.")

    # --- TAB 3: TIN TỨC ---
    elif st.session_state.current_tab == "📰 Tin tức & Văn bản":
        st.markdown("## 📰 TIN TỨC & VĂN BẢN PHÁP QUY")
        st.info("📑 Nghị định số 75/2023/NĐ-CP sửa đổi mức đóng BHYT...")
        st.info("📑 Quyết định 595/QĐ-BHXH về quy trình thu BHXH, BHYT...")

    # --- TAB 4: CẨM NANG ---
    elif st.session_state.current_tab == "📑 Cẩm nang Thủ tục":
        st.markdown("## 📑 CẨM NANG HƯỚNG DẪN NGHIỆP VỤ")
        with st.expander("Quy trình báo tăng/giảm lao động"):
            st.write("Sử dụng hồ sơ điện tử mẫu D02-LT qua phần mềm IVAN...")
        with st.expander("Hướng dẫn cài đặt VssID - BHXH số"):
            st.write("Tải ứng dụng trên AppStore hoặc CH Play...")

    # --- TAB 5: TÍNH TOÁN ---
    elif st.session_state.current_tab == "🧮 Máy tính BHXH 2026":
        st.markdown("## 🧮 CÔNG CỤ TÍNH MỨC ĐÓNG NHANH")
        sal = st.number_input("Mức lương đóng BHXH (VNĐ):", value=5000000, step=100000)
        st.success(f"Dự toán tổng số tiền nộp (Đơn vị + NLĐ): **{(sal*0.32):,.0f}đ**")

    # --- TAB 6: GÓP Ý ---
    elif st.session_state.current_tab == "💬 Góp ý trực tuyến":
        st.markdown("## 💬 GỬI Ý KIẾN GÓP Ý")
        st.text_area("Nội dung góp ý của Quý đơn vị:")
        st.button("Gửi phản hồi")

    # --- TAB 7: BẢN ĐỒ ---
    elif st.session_state.current_tab == "📍 Bản đồ cơ sở":
        st.markdown("## 📍 VỊ TRÍ CƠ QUAN BHXH THUẬN AN")
        st.write("🏠 Thôn Thuận Sơn, xã Thuận An, tỉnh Lâm Đồng.")

st.markdown("<br><hr><center style='color:#94a3b8; font-size:0.95rem; padding-bottom:60px;'>© 2026 BHXH CƠ SỞ THUẬN AN | Elite Digital Hub v16.0 Beyond Digital</center>", unsafe_allow_html=True)
