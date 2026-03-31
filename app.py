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
    page_title="BHXH cơ sở Thuận An - Elite Digital v12.1",
    page_icon="🛡️",
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

# --- TỔNG LỰC CSS (GIAO DIỆN ELITE v12.1 - FIXED) ---
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

    /* BANNER HERO SECTION */
    .hero-banner {
        text-align: center;
        padding: 1.5rem 0;
        margin-bottom: 1rem;
    }

    .hero-title {
        background: linear-gradient(90deg, #1e3a8a, #2563eb, #0ea5e9);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 4.5rem;
        font-weight: 800;
        letter-spacing: -3px;
        margin-bottom: 0px;
        line-height: 1.1;
    }

    /* BẢNG LED CHẠY CHỮ (CYBER MARQUEE) */
    .led-marquee {
        background: #000;
        color: #00ff00;
        padding: 8px 0;
        font-weight: 700;
        border-radius: 8px;
        box-shadow: 0 0 15px rgba(0, 255, 0, 0.4);
        border: 2px solid #333;
        margin-bottom: 25px;
        font-family: 'Courier New', Courier, monospace;
    }

    /* Ô TÌM KIẾM CỬA NGÕ (FIXED HEIGHT) */
    .gateway-container {
        max-width: 800px;
        margin: 0 auto 2rem auto;
        text-align: center;
        background: rgba(255, 255, 255, 0.6);
        padding: 30px;
        border-radius: 40px;
        box-shadow: 0 20px 40px rgba(0,0,0,0.05);
        border: 1px solid rgba(255,255,255,1);
    }

    .stTextInput input {
        border-radius: 50px !important;
        padding: 0.8rem 2.5rem !important; /* Fixed padding to prevent clipping */
        border: 4px solid #3b82f6 !important;
        font-size: 1.4rem !important;
        height: 65px !important; /* Fixed height for better display */
        background: white !important;
        box-shadow: 0 10px 25px rgba(59, 130, 246, 0.1) !important;
        transition: all 0.3s ease;
    }
    
    .stTextInput input:hover {
        border-color: #2563eb !important;
        box-shadow: 0 15px 35px rgba(59, 130, 246, 0.2) !important;
    }

    /* THẺ CÁN BỘ NEON */
    .officer-card {
        background: #0a0a0a;
        padding: 22px;
        border-radius: 25px;
        border: 3px solid #222;
        margin-bottom: 20px;
        text-align: center;
        transition: all 0.4s ease;
    }
    
    .officer-card:hover {
        transform: translateY(-8px);
    }

    @keyframes blink-blue { 0%, 100% { border-color: #00d2ff; box-shadow: 0 0 10px #00d2ff; } 50% { border-color: #111; } }
    @keyframes blink-gold { 0%, 100% { border-color: #ffaa00; box-shadow: 0 0 10px #ffaa00; } 50% { border-color: #111; } }
    @keyframes blink-green { 0%, 100% { border-color: #39ff14; box-shadow: 0 0 10px #39ff14; } 50% { border-color: #111; } }

    .card-nhai { animation: blink-blue 2s infinite; }
    .card-dat { animation: blink-gold 2.5s infinite; }
    .card-hai { animation: blink-green 3s infinite; }

    /* DASHBOARD PANEL */
    .dashboard-panel {
        background: rgba(255, 255, 255, 0.98);
        border-radius: 35px;
        padding: 40px;
        box-shadow: 0 30px 60px rgba(0,0,0,0.06);
        border: 1px solid #fff;
    }

    .metric-card {
        background: #f8fafc;
        padding: 20px;
        border-radius: 20px;
        border: 1px solid #edf2f7;
        text-align: center;
    }

    /* TÀI KHOẢN NGÂN HÀNG (NEON STYLE) */
    .bank-account-card {
        background: #111;
        padding: 20px;
        border-radius: 20px;
        border: 2px solid #333;
        margin-bottom: 12px;
        transition: all 0.3s;
    }
    .bank-account-card:hover {
        border-color: #00d2ff;
        box-shadow: 0 0 15px rgba(0, 210, 255, 0.2);
    }
    .bank-name { color: #00d2ff; font-weight: 800; font-size: 0.9rem; }
    .bank-number { color: #fff; font-size: 1.3rem; font-family: 'Courier New', Courier, monospace; letter-spacing: 1px; }

    /* BUTTONS */
    .stButton>button {
        border-radius: 50px !important;
        font-weight: 800 !important;
        transition: all 0.2s ease !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- DỮ LIỆU CÁN BỘ CHUYÊN QUẢN ---
OFFICERS = [
    {
        "name": "Bà NGUYỄN THỊ NHÀI",
        "title": "Chuyên viên BHXH",
        "scope": "Xã Đức Lập, Xã Đắk Mil",
        "phone": "0846.39.29.29",
        "class": "card-nhai",
        "color": "#00d2ff",
        "areas": ["duc lap", "dak mil", "đức lập", "đắk mil"]
    },
    {
        "name": "Ông BÙI THÀNH ĐẠT",
        "title": "Chuyên viên BHXH",
        "scope": "Xã Đắk Sắk, Xã Đắk Song",
        "phone": "0986.05.30.06",
        "class": "card-dat",
        "color": "#ffaa00",
        "areas": ["dak sak", "dak song", "đắk sắk", "đắk song"]
    },
    {
        "name": "Ông HOÀNG SỸ HẢI",
        "title": "Chuyên viên BHXH",
        "scope": "Xã Thuận An",
        "phone": "0919.06.11.53",
        "class": "card-hai",
        "color": "#39ff14",
        "areas": ["thuan an", "thuận an"]
    }
]

# --- DỮ LIỆU NGÂN HÀNG ---
BANKS = [
    {"name": "BIDV", "number": "63510009867032", "owner": "BHXH cơ sở Thuận An"},
    {"name": "AGRIBANK", "number": "5301202919045", "owner": "BHXH cơ sở Thuận An"},
    {"name": "VIETINBANK", "number": "919035000003", "owner": "BHXH cơ sở Thuận An"}
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
    except Exception as e:
        st.error(f"Lỗi: {e}")
    return None

# --- BANNER TUYÊN TRUYỀN TỰ ĐỘNG ---
def get_dynamic_poster():
    posters = [
        {"t": "🛡️ AN SINH HÀNG ĐẦU", "c": "Tham gia BHXH là hình thức tích lũy tài chính an toàn nhất cho tuổi già của bạn.", "s": "Vững bước tương lai"},
        {"t": "🏥 BẢO HIỂM Y TẾ", "c": "Thẻ BHYT chi trả tới 80-100% chi phí khám chữa bệnh. Giảm bớt nỗi lo tài chính.", "s": "Chăm sóc sức khỏe vàng"},
        {"t": "🤰 QUYỀN LỢI THAI SẢN", "c": "Hỗ trợ 100% lương bình quân đóng BHXH giúp các mẹ an tâm chăm sóc bé yêu.", "s": "Đồng hành cùng gia đình"},
        {"t": "💼 TRỢ CẤP THẤT NGHIỆP", "c": "Hỗ trợ thu nhập và đào tạo nghề mới giúp bạn sớm quay lại thị trường lao động.", "s": "Điểm tựa khi khó khăn"}
    ]
    return posters[datetime.now().minute % len(posters)]

# --- HEADER & LED MARQUEE ---
st.markdown("<div class='hero-banner'><h1 class='hero-title'>BHXH cơ sở Thuận An</h1></div>", unsafe_allow_html=True)

marquee_msg = "📍 ĐỊA CHỈ: THÔN THUẬN SƠN, XÃ THUẬN AN, TỈNH LÂM ĐỒNG • CHÚC QUÝ ĐƠN VỊ SỨC KHỎE VÀ THÀNH CÔNG! • TRA CỨU NHANH - NỘP TIỀN ĐÚNG - QUYỀN LỢI VỮNG BỀN •"
st.markdown(f"<div class='led-marquee'><marquee scrollamount='10'>{marquee_msg}</marquee></div>", unsafe_allow_html=True)

df = load_data()

# --- GIAO DIỆN CHÍNH ---
if df is not None:
    # MÀN HÌNH 1: CỬA NGÕ TÌM KIẾM
    if st.session_state.selected_unit is None:
        st.markdown("<div class='gateway-container'>", unsafe_allow_html=True)
        st.markdown("<h2 style='color:#1e3a8a; margin-top:0;'>🔍 BẮT ĐẦU TRA CỨU</h2>", unsafe_allow_html=True)
        query = st.text_input("Gateway", placeholder="Gõ tên hoặc mã đơn vị để tìm kiếm...", label_visibility="collapsed")
        st.markdown("</div>", unsafe_allow_html=True)

        col_main, col_info = st.columns([1.8, 1])

        with col_main:
            if query:
                clean_query = unidecode(query).lower()
                results = df[df['search_index'].str.contains(clean_query, na=False)].head(10)
                if not results.empty:
                    st.write(f"✨ Tìm thấy **{len(results)}** đơn vị phù hợp:")
                    for idx, row in results.iterrows():
                        with st.container():
                            ca, cb = st.columns([4, 1.5])
                            ca.markdown(f"""
                                <div style='background:white; padding:25px; border-radius:30px; border-left:12px solid #e2e8f0; margin-bottom:15px; box-shadow:0 10px 20px rgba(0,0,0,0.05);'>
                                    <small style='color:#2563eb; font-weight:800;'>MÃ: {row.get('madvi')}</small><br>
                                    <b style='font-size:1.4rem; color:#1e293b;'>{row.get('tendvi')}</b>
                                </div>
                            """, unsafe_allow_html=True)
                            if cb.button("Xác nhận tra cứu ➔", key=f"sel_{row.get('madvi')}_{idx}", use_container_width=True):
                                st.session_state.selected_unit = row.get('madvi')
                                st.session_state.show_loading = True
                                st.rerun()
                else:
                    st.error("Không tìm thấy đơn vị. Hãy kiểm tra lại từ khóa.")
            else:
                p = get_dynamic_poster()
                st.markdown(f"""
                    <div class="poster-box">
                        <h1 style='color:white; margin:0;'>{p['t']}</h1>
                        <p style='font-size:1.5rem; opacity:0.9; line-height:1.7; margin:25px 0;'>{p['c']}</p>
                        <hr style='border: 0.5px solid rgba(255,255,255,0.3);'>
                        <h2 style='color:#ffaa00; margin:0;'>{p['s']}</h2>
                    </div>
                """, unsafe_allow_html=True)

        with col_info:
            st.markdown("### 🏦 Số tài khoản nộp tiền")
            for bank in BANKS:
                st.markdown(f"""
                <div class="bank-account-card">
                    <div class="bank-name">{bank['name']}</div>
                    <div class="bank-number">{bank['number']}</div>
                    <div style="color: #888; font-size: 0.75rem;">{bank['owner']}</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("### 👨‍💼 Cán bộ Chuyên quản")
            for off in OFFICERS:
                st.markdown(f"""
                <div class="officer-card {off['class']}">
                    <h4 style="margin:0; color:{off['color']}; text-shadow: 0 0 5px {off['color']};">{off['name']}</h4>
                    <p style="margin:5px 0; font-size:0.85rem; color:#aaa;">{off['title']}</p>
                    <p style="margin:5px 0; font-size:0.8rem; color:#fff;">{off['scope']}</p>
                    <div style="background:rgba(255,255,255,0.1); padding:8px; border-radius:12px; margin-top:10px; border:1px solid #444;">
                        <a href="tel:{off['phone'].replace('.','')}" style="text-decoration:none; color:white; font-weight:800; font-size:1.2rem;">📱 {off['phone']}</a>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # MÀN HÌNH LOADING
    elif st.session_state.show_loading:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        with st.status("💎 Đang phân tích dữ liệu chuyên sâu...", expanded=True) as status:
            st.write("🔄 Đang kết nối máy chủ BHXH...")
            time.sleep(0.5)
            st.write("📊 Đang tổng hợp số liệu C12-TS mới nhất...")
            time.sleep(0.5)
            st.write("✨ Đang khởi tạo Dashboard cá nhân...")
            time.sleep(0.5)
            status.update(label="Tải dữ liệu hoàn tất!", state="complete")
        
        st.session_state.show_loading = False
        st.balloons()
        time.sleep(0.5)
        st.rerun()

    # MÀN HÌNH 2: DASHBOARD CHI TIẾT
    else:
        unit_data = df[df['madvi'] == st.session_state.selected_unit].iloc[0]
        unit_addr = unidecode(str(unit_data.get('diachi', ''))).lower()
        
        if st.button("⬅ QUAY LẠI TÌM KIẾM"):
            st.session_state.selected_unit = None
            st.rerun()

        st.markdown(f"""
            <div style='background:white; padding:45px; border-radius:45px; border-left:25px solid #1e3a8a; box-shadow: 0 30px 70px rgba(0,0,0,0.1); margin-top:15px;'>
                <h1 style='margin:0; color:#1e3a8a; font-size:3.5rem;'>🏢 {unit_data.get('tendvi')}</h1>
                <p style='margin:12px 0 0 0; color:#64748b; font-size:1.4rem;'>Mã: <b style='color:#1e3a8a;'>{unit_data.get('madvi')}</b> | Địa chỉ: {unit_data.get('diachi', 'N/A')}</p>
            </div>
        """, unsafe_allow_html=True)

        col_left, col_right = st.columns([1.9, 1])

        with col_left:
            st.markdown("<div class='dashboard-panel' style='margin-top:30px;'>", unsafe_allow_html=True)
            st.write("### 📉 Phân tích Số liệu đóng BHXH")
            
            # Metric Grid
            m1, m2, m3 = st.columns(3)
            with m1: st.markdown(f"<div class='metric-card'><small>TIỀN ĐẦU KỲ</small><div style='font-size:1.8rem; font-weight:800;'>{unit_data.get('tien_dau_ky', 0):,.0f}đ</div></div>", unsafe_allow_html=True)
            with m2: st.markdown(f"<div class='metric-card'><small>SỐ PHẢI ĐÓNG</small><div style='font-size:1.8rem; font-weight:800;'>{unit_data.get('so_phai_dong', 0):,.0f}đ</div></div>", unsafe_allow_html=True)
            with m3: st.markdown(f"<div class='metric-card'><small>ĐIỀU CHỈNH</small><div style='font-size:1.8rem; font-weight:800;'>{unit_data.get('dieu_chinh_ky_truoc', 0):,.0f}đ</div></div>", unsafe_allow_html=True)
            
            st.write("<br>", unsafe_allow_html=True)
            m4, m5, m6 = st.columns(3)
            with m4: st.markdown(f"<div class='metric-card'><small>SỐ ĐÃ ĐÓNG</small><div style='font-size:1.8rem; font-weight:800; color:#10b981;'>{unit_data.get('so_da_dong', 0):,.0f}đ</div></div>", unsafe_allow_html=True)
            with m5: st.markdown(f"<div class='metric-card'><small>SỐ BỊ LỆCH</small><div style='font-size:1.8rem; font-weight:800; color:#f59e0b;'>{unit_data.get('so_bi_lech', 0):,.0f}đ</div></div>", unsafe_allow_html=True)
            with m6:
                debt = unit_data.get('tien_cuoi_ky', 0)
                color = "#ef4444" if debt > 0 else "#3b82f6"
                label = "CÒN NỢ" if debt > 0 else "DƯ CÓ"
                st.markdown(f"<div class='metric-card'><small>{label}</small><div style='font-size:1.8rem; font-weight:800; color:{color};'>{abs(debt):,.0f}đ</div></div>", unsafe_allow_html=True)
            
            # Cú pháp nộp tiền chuẩn
            now = datetime.now()
            transfer_note = f"{unit_data.get('madvi')} {unit_data.get('tendvi')} đóng bhxh tháng {now.month} năm {now.year}"
            st.markdown(f"""
                <div style='background:#f0f9ff; padding:35px; border-radius:35px; border:3px dashed #3b82f6; margin-top:35px;'>
                    <p style='color:#1e40af; font-weight:800; margin:0; font-size:1.1rem; text-transform:uppercase;'>📝 Nội dung nộp tiền chuyển khoản:</p>
                    <h2 style='color:#1e3a8a; font-family:monospace; margin:15px 0; font-size:1.9rem; background:white; padding:15px; border-radius:15px; border:1px solid #e2e8f0;'>{transfer_note}</h2>
                    <p style='margin:0; font-size:0.9rem; color:#64748b;'><i>Vui lòng sao chép đúng nội dung để hệ thống ghi nhận chính xác.</i></p>
                </div>
            """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with col_right:
            # Gauge Chart
            phai_dong = unit_data.get('so_phai_dong', 1)
            da_dong = unit_data.get('so_da_dong', 0)
            rate = min(round((da_dong / phai_dong) * 100, 1), 100) if phai_dong > 0 else 0
            fig = go.Figure(go.Indicator(
                mode = "gauge+number", value = rate,
                title = {'text': "Tỷ lệ hoàn thành (%)", 'font': {'size': 22, 'color': '#64748b'}},
                number = {'suffix': "%", 'font': {'color': '#1e40af', 'size': 60}},
                gauge = {
                    'axis': {'range': [0, 100]},
                    'bar': {'color': "#1e40af"},
                    'bgcolor': "white",
                    'steps': [{'range': [0, 50], 'color': '#fee2e2'}, {'range': [50, 90], 'color': '#fef9c3'}, {'range': [90, 100], 'color': '#dcfce7'}]
                }
            ))
            fig.update_layout(height=450, margin=dict(l=35, r=35, t=70, b=35), paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)
            
            # Cán bộ phụ trách (Highlight nhấp nháy)
            st.markdown("### 👨‍💼 Cán bộ Phụ trách Xã")
            found_officer = False
            for off in OFFICERS:
                is_assigned = any(area in unit_addr for area in off['areas'])
                blink_class = off['class'] if is_assigned else ""
                
                if is_assigned:
                    found_officer = True
                    st.markdown(f"""
                    <div class="officer-card {blink_class}">
                        <span style="color:#39ff14; font-weight:800; font-size:0.7rem; border:1px solid #39ff14; padding:2px 8px; border-radius:50px;">PHỤ TRÁCH TRỰC TIẾP</span>
                        <h4 style="margin:10px 0; color:{off['color']}; text-shadow: 0 0 10px {off['color']};">{off['name']}</h4>
                        <p style="margin:5px 0; font-size:0.85rem; color:#fff;">{off['title']}</p>
                        <div style="background:#222; padding:8px; border-radius:15px; margin-top:10px; border:1px solid #444;">
                            <a href="tel:{off['phone'].replace('.','')}" style="text-decoration:none; color:white; font-weight:800; font-size:1.3rem;">📱 {off['phone']}</a>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            if not found_officer:
                st.warning("Hệ thống không nhận diện được xã quản lý. Vui lòng liên hệ bất kỳ cán bộ nào.")

# --- FOOTER ---
st.markdown("<br><hr>", unsafe_allow_html=True)
st.markdown(f"<center style='color:#94a3b8; font-size:0.9rem; padding-bottom:60px;'>© {datetime.now().year} BHXH CƠ SỞ THUẬN AN - LÂM ĐỒNG | Elite Digital Hub v12.1</center>", unsafe_allow_html=True)
