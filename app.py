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
    page_title="BHXH cơ sở Thuận An - Ultimate AI v13.0",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- KHỞI TẠO STATE ---
if 'selected_unit' not in st.session_state:
    st.session_state.selected_unit = None
if 'last_query' not in st.session_state:
    st.session_state.last_query = ""
if 'show_loading' not in st.session_state:
    st.session_state.show_loading = False
if 'current_tab' not in st.session_state:
    st.session_state.current_tab = "Tra cứu"

# --- TỔNG LỰC CSS (GIAO DIỆN ULTIMATE v13.0) ---
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
        background: linear-gradient(135deg, #f0f4f8 0%, #d9e2ec 100%);
    }

    /* NỀN ĐỘNG GRADIENT */
    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* BẢNG LED CHẠY CHỮ CHUYÊN NGHIỆP */
    .led-marquee {
        background: #000;
        color: #00ff00;
        padding: 10px 0;
        font-weight: 700;
        border-radius: 12px;
        box-shadow: 0 0 20px rgba(0, 255, 0, 0.4);
        border: 2px solid #333;
        margin-bottom: 25px;
        font-family: 'Courier New', Courier, monospace;
        font-size: 1.1rem;
        text-shadow: 0 0 5px #00ff00;
    }

    /* SIÊU KHUNG XANH TÌM KIẾM (ULTRA SEARCH ZONE) */
    .search-zone {
        background: linear-gradient(-45deg, #1e3a8a, #2563eb, #3b82f6, #0ea5e9);
        background-size: 400% 400%;
        animation: gradientBG 10s ease infinite;
        padding: 55px 40px;
        border-radius: 40px;
        box-shadow: 0 30px 70px rgba(30, 58, 138, 0.4);
        margin-bottom: 40px;
        text-align: center;
        border: 2px solid rgba(255,255,255,0.4);
    }

    /* SIÊU Ô INPUT TÌM KIẾM */
    .stTextInput input {
        border-radius: 20px !important;
        padding: 0 40px !important; 
        border: 5px solid #fff !important;
        font-size: 2.2rem !important; 
        font-weight: 800 !important;
        height: 100px !important; 
        line-height: 100px !important; 
        background: white !important;
        color: #1e3a8a !important;
        box-shadow: 0 15px 45px rgba(0, 0, 0, 0.2) !important;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    
    .stTextInput input:focus {
        border-color: #00d2ff !important;
        transform: scale(1.02);
        box-shadow: 0 20px 60px rgba(0, 210, 255, 0.4) !important;
    }

    /* THẺ CÁN BỘ & TÀI KHOẢN (GLOW STYLE) */
    .officer-card {
        background: #080808;
        padding: 22px;
        border-radius: 25px;
        border: 2px solid #222;
        margin-bottom: 15px;
        text-align: center;
        transition: all 0.4s ease;
    }
    .officer-card:hover { transform: translateY(-8px); border-color: #444; box-shadow: 0 10px 25px rgba(0,0,0,0.5); }

    @keyframes blink-blue { 0%, 100% { border-color: #00d2ff; box-shadow: 0 0 15px #00d2ff; } 50% { border-color: #111; } }
    @keyframes blink-gold { 0%, 100% { border-color: #ffaa00; box-shadow: 0 0 15px #ffaa00; } 50% { border-color: #111; } }
    @keyframes blink-green { 0%, 100% { border-color: #39ff14; box-shadow: 0 0 15px #39ff14; } 50% { border-color: #111; } }

    .card-nhai { animation: blink-blue 2s infinite; }
    .card-dat { animation: blink-gold 2.5s infinite; }
    .card-hai { animation: blink-green 3s infinite; }

    /* TIỆN ÍCH SIDEBAR */
    [data-testid="stSidebar"] {
        background-color: #1e3a8a;
        color: white;
    }
    
    .stButton>button {
        border-radius: 50px !important;
        font-weight: 800 !important;
        transition: all 0.3s ease !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* DASHBOARD */
    .dashboard-panel {
        background: white;
        border-radius: 45px;
        padding: 45px;
        box-shadow: 0 40px 80px rgba(0,0,0,0.1);
        border: 1px solid #fff;
    }
    
    .ai-assistant-box {
        background: white;
        padding: 25px;
        border-radius: 30px;
        border-left: 10px solid #8b5cf6;
        box-shadow: 0 10px 30px rgba(139, 92, 246, 0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# --- DỮ LIỆU CÁN BỘ & NGÂN HÀNG ---
OFFICERS = [
    {"name": "Bà NGUYỄN THỊ NHÀI", "scope": "Xã Đức Lập, Xã Đắk Mil", "phone": "0846.39.29.29", "class": "card-nhai", "color": "#00d2ff", "areas": ["duc lap", "dak mil", "đức lập", "đắk mil"]},
    {"name": "Ông BÙI THÀNH ĐẠT", "scope": "Xã Đắk Sắk, Xã Đắk Song", "phone": "0986.05.30.06", "class": "card-dat", "color": "#ffaa00", "areas": ["dak sak", "dak song", "đắk sắk", "đắk song"]},
    {"name": "Ông HOÀNG SỸ HẢI", "scope": "Xã Thuận An", "phone": "0919.06.11.53", "class": "card-hai", "color": "#39ff14", "areas": ["thuan an", "thuận an"]}
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

# --- SIDEBAR: TIỆN ÍCH KHÁC ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3772/3772274.png", width=100)
    st.markdown("## TIỆN ÍCH MỞ RỘNG")
    st.divider()
    
    if st.button("📊 Tra cứu C12-TS", use_container_width=True):
        st.session_state.current_tab = "Tra cứu"
        st.rerun()
    if st.button("🤖 Trợ lý AI (Gemini)", use_container_width=True):
        st.session_state.current_tab = "AI"
        st.rerun()
    if st.button("📖 Cẩm nang Thủ tục", use_container_width=True):
        st.session_state.current_tab = "Cẩm nang"
        st.rerun()
    if st.button("🧮 Tính mức đóng BHXH", use_container_width=True):
        st.session_state.current_tab = "Tính toán"
        st.rerun()
        
    st.divider()
    st.caption("Phiên bản v13.0 Ultimate AI")

# --- HEADER (LED MARQUEE) ---
st.markdown(f"<div class='led-marquee'><marquee scrollamount='10'>📍 ĐỊA CHỈ: THÔN THUẬN SƠN, XÃ THUẬN AN, TỈNH LÂM ĐỒNG • HỆ THỐNG TRA CỨU BHXH THÔNG MINH TÍCH HỢP TRÍ TUỆ NHÂN TẠO • HÀNH CHÍNH CÔNG HIỆN ĐẠI •</marquee></div>", unsafe_allow_html=True)

df = load_data()

if df is not None:
    
    # --- TAB 1: TRA CỨU ---
    if st.session_state.current_tab == "Tra cứu":
        if st.session_state.selected_unit is None:
            # SIÊU KHUNG XANH TÌM KIẾM
            st.markdown("<div class='search-zone'>", unsafe_allow_html=True)
            st.markdown("<h1 style='color:white; margin-top:0; font-size:2.8rem; font-weight:800; text-shadow: 2px 2px 8px rgba(0,0,0,0.5);'>🛡️ CỔNG TRA CỨU BHXH THUẬN AN</h1>", unsafe_allow_html=True)
            st.markdown("<p style='color:rgba(255,255,255,0.95); font-size:1.3rem; margin-bottom:30px; font-weight:600;'>Mời Quý đơn vị nhập Mã đơn vị hoặc Tên công ty để trích xuất số liệu</p>", unsafe_allow_html=True)
            query = st.text_input("Gateway", placeholder="Ví dụ: TC0243, Daknoco...", label_visibility="collapsed")
            st.markdown("</div>", unsafe_allow_html=True)

            col_post, col_res, col_info = st.columns([0.8, 1.4, 1])

            with col_post:
                st.markdown("##### 📢 Thông báo từ cơ quan")
                posters = [
                    {"t": "🛡️ AN SINH TUỔI GIÀ", "c": "Hưởng lương hưu hàng tháng khi về già là quyền lợi bền vững nhất."},
                    {"t": "🏥 LÁ CHẮN SỨC KHỎE", "c": "BHYT chi trả viện phí, giúp gia đình bạn vượt qua sóng gió bệnh tật."},
                    {"t": "🤰 ĐỒNG HÀNH LÀM MẸ", "c": "Chế độ thai sản hỗ trợ tài chính tối đa trong thời gian nghỉ sinh con."}
                ]
                p = posters[datetime.now().minute % len(posters)]
                st.markdown(f"""
                    <div style='background:white; padding:25px; border-radius:30px; border:2px solid #e2e8f0; text-align:center; min-height:300px; display:flex; flex-direction:column; justify-content:center; box-shadow: 0 10px 20px rgba(0,0,0,0.05);'>
                        <h4 style='color:#1e3a8a; margin:0;'>{p['t']}</h4>
                        <p style='font-size:1.1rem; color:#64748b; margin:15px 0; line-height:1.6;'>{p['c']}</p>
                        <hr style='border: 0.5px solid #eee;'>
                        <small style='color:#ffaa00; font-weight:800;'>BHXH THUẬN AN ĐỒNG HÀNH</small>
                    </div>
                """, unsafe_allow_html=True)

            with col_res:
                if query:
                    clean_query = unidecode(query).lower()
                    results = df[df['search_index'].str.contains(clean_query, na=False)].head(8)
                    if not results.empty:
                        st.write(f"✨ Tìm thấy **{len(results)}** đơn vị phù hợp:")
                        for idx, row in results.iterrows():
                            with st.container():
                                ca, cb = st.columns([3, 1.2])
                                ca.markdown(f"""
                                    <div style='background:white; padding:20px; border-radius:25px; border-left:8px solid #2563eb; margin-bottom:12px; box-shadow:0 4px 6px rgba(0,0,0,0.03);'>
                                        <small style='color:#2563eb; font-weight:800;'>MÃ: {row.get('madvi')}</small><br>
                                        <b style='font-size:1.2rem; color:#1e293b;'>{row.get('tendvi')}</b>
                                    </div>
                                """, unsafe_allow_html=True)
                                if cb.button("Tra cứu ➔", key=f"sel_{row.get('madvi')}_{idx}", use_container_width=True):
                                    st.session_state.selected_unit = row.get('madvi')
                                    st.session_state.show_loading = True
                                    st.rerun()
                    else:
                        st.error("Không tìm thấy dữ liệu phù hợp.")
                else:
                    st.markdown("<br><center><img src='https://cdn-icons-png.flaticon.com/512/3772/3772274.png' width='140' style='opacity:0.2'><h4 style='color:#94a3b8;'>Hệ thống đang sẵn sàng tra cứu dữ liệu C12-TS</h4></center>", unsafe_allow_html=True)

            with col_info:
                st.markdown("##### 👩‍💼 Cán bộ Chuyên quản")
                for off in OFFICERS:
                    st.markdown(f"""
                    <div class="officer-card {off['class']}">
                        <div style="color:{off['color']}; font-weight:800; font-size:1.1rem; text-shadow: 0 0 5px rgba(0,0,0,0.5);">{off['name']}</div>
                        <div style="color:#aaa; font-size:0.8rem; margin:5px 0;">Xã phụ trách: {off['scope']}</div>
                        <a href="tel:{off['phone'].replace('.','')}" style="text-decoration:none; color:white; font-weight:800; font-size:1.2rem;">📱 {off['phone']}</a>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("##### 🏦 Số tài khoản nộp tiền")
                for bank in BANKS:
                    st.markdown(f"""
                    <div class="bank-account-card">
                        <div class="bank-name">{bank['name']}</div>
                        <div class="bank-number">{bank['number']}</div>
                    </div>
                    """, unsafe_allow_html=True)

        # MÀN HÌNH LOADING
        elif st.session_state.show_loading:
            st.markdown("<br><br><br>", unsafe_allow_html=True)
            with st.status("💎 ĐANG TRÍCH XUẤT DỮ LIỆU VÀNG...", expanded=True) as status:
                st.write("🔄 Đang kết nối máy chủ BHXH...")
                time.sleep(0.5)
                st.write("📊 Đang phân tích số liệu C12-TS tháng hiện hành...")
                time.sleep(0.5)
                status.update(label="Tải dữ liệu hoàn tất!", state="complete")
            st.session_state.show_loading = False
            st.balloons()
            st.rerun()

        # MÀN HÌNH 2: DASHBOARD CHI TIẾT
        else:
            unit_data = df[df['madvi'] == st.session_state.selected_unit].iloc[0]
            unit_addr = unidecode(str(unit_data.get('diachi', ''))).lower()
            
            if st.button("⬅ QUAY LẠI TRANG CHỦ"):
                st.session_state.selected_unit = None
                st.rerun()

            st.markdown(f"""
                <div style='background:white; padding:40px; border-radius:40px; border-left:20px solid #1e3a8a; box-shadow: 0 25px 60px rgba(0,0,0,0.08); margin-top:20px;'>
                    <h2 style='margin:0; color:#1e3a8a;'>🏢 {unit_data.get('tendvi')}</h2>
                    <p style='margin:8px 0 0 0; color:#64748b;'>Mã đơn vị: <b>{unit_data.get('madvi')}</b> | Địa chỉ: {unit_data.get('diachi', 'N/A')}</p>
                </div>
            """, unsafe_allow_html=True)

            col_l, col_r = st.columns([1.8, 1])
            with col_l:
                st.markdown("<div class='dashboard-panel' style='margin-top:25px;'>", unsafe_allow_html=True)
                st.write("#### 📉 Phân tích số liệu tài chính chi tiết")
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
                    <div style='background:#f0f9ff; padding:30px; border-radius:30px; border:3px dashed #3b82f6; margin-top:30px; text-align:center;'>
                        <p style='color:#1e40af; font-weight:800; font-size:1.1rem; text-transform:uppercase;'>📝 NỘI DUNG CHUYỂN KHOẢN CHUẨN:</p>
                        <h3 style='color:#1e3a8a; font-family:monospace; font-size:2rem; background:white; padding:15px; border-radius:15px; margin:15px 0;'>{transfer_note}</h3>
                        <p style='color:#64748b; font-size:0.9rem;'><i>(Lưu ý: Đơn vị vui lòng ghi đúng nội dung để hệ thống tự động gạch nợ)</i></p>
                    </div>
                """, unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

            with col_r:
                phai_dong = unit_data.get('so_phai_dong', 1)
                da_dong = unit_data.get('so_da_dong', 0)
                rate = min(round((da_dong / phai_dong) * 100, 1), 100) if phai_dong > 0 else 0
                fig = go.Figure(go.Indicator(
                    mode = "gauge+number", value = rate,
                    title = {'text': "Tỷ lệ hoàn thành (%)", 'font': {'size': 24, 'color': '#64748b'}},
                    number = {'suffix': "%", 'font': {'color': '#1e40af', 'size': 65}},
                    gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': "#1e40af"}, 'steps': [{'range': [0, 50], 'color': '#fee2e2'}, {'range': [90, 100], 'color': '#dcfce7'}]}
                ))
                fig.update_layout(height=450, margin=dict(l=35, r=35, t=70, b=35), paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig, use_container_width=True)
                
                # Highlight Cán bộ phụ trách xã
                for off in OFFICERS:
                    if any(area in unit_addr for area in off['areas']):
                        st.markdown(f"""
                        <div class="officer-card {off['class']}" style="background:#000;">
                            <small style="color:#39ff14; font-weight:800; border:1px solid #39ff14; padding:2px 8px; border-radius:50px;">PHỤ TRÁCH TRỰC TIẾP</small>
                            <h4 style="margin:10px 0; color:{off['color']}; font-size:1.6rem;">{off['name']}</h4>
                            <a href="tel:{off['phone'].replace('.','')}" style="text-decoration:none; color:white; font-weight:800; font-size:1.5rem;">📱 {off['phone']}</a>
                        </div>
                        """, unsafe_allow_html=True)

    # --- TAB 2: AI ASSISTANT ---
    elif st.session_state.current_tab == "AI":
        st.markdown("## 🤖 TRỢ LÝ ẢO BHXH THUẬN AN (AI)")
        st.markdown("<p style='color:#64748b;'>Hỏi AI về chính sách BHXH, BHYT, BHTN hoặc các thủ tục hành chính.</p>", unsafe_allow_html=True)
        
        st.markdown("<div class='ai-assistant-box'>", unsafe_allow_html=True)
        user_msg = st.text_input("Gửi câu hỏi của bạn:", placeholder="Ví dụ: Làm sao để chốt sổ BHXH? Chế độ thai sản cần những gì?...")
        if user_msg:
            with st.spinner("AI đang suy nghĩ..."):
                time.sleep(2)
                st.success("🤖 Trợ lý AI trả lời:")
                st.write("Chào Quý đơn vị, hiện tại tính năng kết nối trực tiếp với API đang được thiết lập. Về thắc mắc của bạn, vui lòng liên hệ cán bộ chuyên quản hoặc tổng đài 1900 9068 để được hướng dẫn chi tiết nhất về hồ sơ theo quy định mới nhất.")
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.info("💡 Mẹo: Bạn có thể hỏi về Mức lương cơ sở mới, Tỷ lệ đóng BHXH 2026...")

    # --- TAB 3: CẨM NANG ---
    elif st.session_state.current_tab == "Cẩm nang":
        st.markdown("## 📖 CẨM NANG THỦ TỤC ĐIỆN TỬ")
        col1, col2 = st.columns(2)
        with col1:
            with st.expander("🏢 Dành cho Doanh nghiệp"):
                st.write("1. Đăng ký tham gia BHXH lần đầu.")
                st.write("2. Báo tăng, báo giảm lao động.")
                st.write("3. Cấp thẻ BHYT điện tử.")
        with col2:
            with st.expander("👤 Dành cho Người lao động"):
                st.write("1. Tra cứu quá trình đóng trên VssID.")
                st.write("2. Thủ tục hưởng BHXH một lần.")
                st.write("3. Đăng ký khám chữa bệnh bằng CCCD gắn chíp.")

    # --- TAB 4: TÍNH TOÁN ---
    elif st.session_state.current_tab == "Tính toán":
        st.markdown("## 🧮 BỘ CÔNG CỤ TÍNH MỨC ĐÓNG BHXH")
        salary = st.number_input("Nhập mức lương đóng BHXH (VNĐ):", min_value=0, value=5000000, step=500000)
        
        c1, c2 = st.columns(2)
        with c1:
            st.info("🏢 Doanh nghiệp đóng (21.5%)")
            st.write(f"- BHXH: {salary * 0.175:,.0f}đ")
            st.write(f"- BHYT: {salary * 0.03:,.0f}đ")
            st.write(f"- BHTN: {salary * 0.01:,.0f}đ")
            st.markdown(f"**Tổng: {salary * 0.215:,.0f}đ**")
        with c2:
            st.success("👤 Người lao động đóng (10.5%)")
            st.write(f"- BHXH: {salary * 0.08:,.0f}đ")
            st.write(f"- BHYT: {salary * 0.015:,.0f}đ")
            st.write(f"- BHTN: {salary * 0.01:,.0f}đ")
            st.markdown(f"**Tổng: {salary * 0.105:,.0f}đ**")

st.markdown("<br><hr><center style='color:#94a3b8; font-size:0.9rem; padding-bottom:60px;'>© 2026 BHXH CƠ SỞ THUẬN AN | Ultimate AI Digital Hub v13.0</center>", unsafe_allow_html=True)
