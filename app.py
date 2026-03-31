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
    page_title="BHXH cơ sở Thuận An - Elite Connect v11.0",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- KHỞI TẠO STATE ---
if 'selected_unit' not in st.session_state:
    st.session_state.selected_unit = None
if 'last_query' not in st.session_state:
    st.session_state.last_query = ""

# --- TỔNG LỰC CSS (GIAO DIỆN ELITE v11.0) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    :root {
        --primary: #1e3a8a;
        --secondary: #2563eb;
        --accent: #0ea5e9;
        --neon-blue: #00d2ff;
        --neon-gold: #ffaa00;
        --neon-red: #ff3131;
    }

    * { font-family: 'Plus Jakarta Sans', sans-serif; }
    
    .stApp {
        background: linear-gradient(135deg, #f0f4f8 0%, #d9e2ec 100%);
    }
    
    /* Hiệu ứng nhấp nháy đèn Neon cho Cán bộ */
    @keyframes neon-blink {
        0%, 100% { border-color: var(--secondary); box-shadow: 0 0 10px var(--secondary); }
        50% { border-color: var(--neon-blue); box-shadow: 0 0 25px var(--neon-blue); }
    }
    
    @keyframes gold-blink {
        0%, 100% { border-color: #d97706; box-shadow: 0 0 10px #d97706; }
        50% { border-color: var(--neon-gold); box-shadow: 0 0 25px var(--neon-gold); }
    }

    .officer-card {
        background: white;
        padding: 25px;
        border-radius: 25px;
        border: 3px solid #e2e8f0;
        margin-bottom: 20px;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .blink-active {
        animation: neon-blink 1.5s infinite;
        background: linear-gradient(to bottom right, #ffffff, #f0f9ff);
    }
    
    .blink-gold {
        animation: gold-blink 2s infinite;
    }

    /* Hero Title */
    .hero-title {
        background: linear-gradient(90deg, #1e3a8a, #2563eb, #0ea5e9);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 5rem;
        font-weight: 800;
        letter-spacing: -4px;
        text-align: center;
        margin-bottom: 10px;
    }

    /* Marquee */
    .marquee-wrapper {
        background: #1e3a8a;
        color: white;
        padding: 12px 0;
        border-radius: 12px;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        margin-bottom: 30px;
    }

    /* Premium Card Design */
    .premium-panel {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 40px;
        padding: 40px;
        box-shadow: 0 25px 50px rgba(0,0,0,0.06);
        border: 1px solid rgba(255,255,255,0.7);
    }

    /* Gateway Search nổi bật */
    .stTextInput input {
        border-radius: 50px !important;
        padding: 2.2rem 3.5rem !important;
        border: 3px solid #3b82f6 !important;
        font-size: 1.6rem !important;
        box-shadow: 0 20px 40px rgba(59, 130, 246, 0.2) !important;
        transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    .stTextInput input:focus {
        transform: scale(1.02);
        border-color: #2563eb !important;
    }

    /* Poster Auto-rotate */
    .poster-area {
        background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%);
        color: white;
        padding: 40px;
        border-radius: 35px;
        text-align: center;
        min-height: 400px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        box-shadow: 0 20px 40px rgba(0,0,0,0.1);
    }

    /* Metric UI */
    .metric-box {
        text-align: center;
        background: #f8fafc;
        padding: 20px;
        border-radius: 25px;
        border: 1px solid #edf2f7;
    }
    .metric-val { font-size: 2.2rem; font-weight: 800; color: #1e3a8a; }
    .metric-lab { font-size: 0.9rem; color: #64748b; font-weight: 700; text-transform: uppercase; }

    /* Flashy Badge */
    .badge-flash {
        background: #ff3131;
        color: white;
        padding: 4px 12px;
        border-radius: 50px;
        font-size: 0.7rem;
        font-weight: 800;
        position: absolute;
        top: 15px;
        right: 15px;
        animation: pulse 1s infinite;
    }
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    </style>
    """, unsafe_allow_html=True)

# --- DỮ LIỆU CÁN BỘ CHUYÊN QUẢN ---
OFFICERS = [
    {
        "name": "Bà Nguyễn Thị Nhài",
        "title": "Chuyên viên BHXH",
        "scope": "Xã Đức Lập, Xã Đắk Mil",
        "phone": "0846.39.29.29",
        "areas": ["duc lap", "dak mil", "đức lập", "đắk mil"]
    },
    {
        "name": "Ông Bùi Thành Đạt",
        "title": "Chuyên viên BHXH",
        "scope": "Xã Đắk Sắk, Xã Đắk Song",
        "phone": "0986.05.30.06",
        "areas": ["dak sak", "dak song", "đắk sắk", "đắk song"]
    },
    {
        "name": "Ông Hoàng Sỹ Hải",
        "title": "Chuyên viên BHXH",
        "scope": "Xã Thuận An",
        "phone": "0919.06.11.53",
        "areas": ["thuan an", "thuận an"]
    }
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
def get_rotating_poster():
    posters = [
        {"t": "🛡️ AN SINH HÔM NAY", "c": "Tham gia BHXH là hình thức đầu tư an toàn nhất cho tuổi già. Lương hưu giúp bạn tự chủ tài chính khi về già.", "s": "Vững bước tương lai"},
        {"t": "🏥 SỨC KHỎE VÀNG", "c": "Thẻ BHYT là 'bùa hộ mệnh' giúp chi trả viện phí khi ốm đau. Đừng để bệnh tật làm khánh kiệt gia đình.", "s": "BHYT - Lá chắn y tế"},
        {"t": "🤰 HẠNH PHÚC LÀM MẸ", "c": "Chế độ thai sản hỗ trợ 100% lương giúp các mẹ an tâm chăm sóc bé yêu trong những tháng đầu đời.", "s": "Đồng hành cùng gia đình"},
        {"t": "⚖️ TRÁCH NHIỆM DOANH NGHIỆP", "c": "Đóng BHXH đầy đủ là bảo vệ quyền lợi hợp pháp của NLĐ và xây dựng uy tín bền vững cho doanh nghiệp.", "s": "Doanh nghiệp nhân văn"}
    ]
    return posters[datetime.now().minute % len(posters)]

# --- HEADER ---
st.markdown("<h1 class='hero-title'>BHXH cơ sở Thuận An</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#64748b; font-size:1.4rem; font-weight:600; margin-top:-10px;'>Cổng Kết Nối & Tra Cứu Dữ Liệu Chuyên Nghiệp</p>", unsafe_allow_html=True)

# Bảng tin chạy
marquee_text = "🛡️ BHXH Thuận An: Thôn Thuận Sơn, xã Thuận An, Lâm Đồng. | 🏦 BIDV: 63510009867032 | 🏦 Agribank: 5301202919045 | 🏦 Vietinbank: 919035000003. | Quý đơn vị vui lòng liên hệ cán bộ chuyên quản để được hỗ trợ tốt nhất."
st.markdown(f"<div class='marquee-wrapper'><marquee scrollamount='9'>{marquee_text}</marquee></div>", unsafe_allow_html=True)

df = load_data()

# --- GIAO DIỆN CHÍNH ---
if df is not None:
    # MÀN HÌNH 1: TRANG CHỦ & TÌM KIẾM
    if st.session_state.selected_unit is None:
        # Cửa ngõ tìm kiếm nổi bật
        _, c_search, _ = st.columns([0.15, 0.7, 0.15])
        with c_search:
            st.markdown("<h3 style='text-align:center; color:#1e3a8a;'>🔍 NHẬP MÃ HOẶC TÊN ĐƠN VỊ ĐỂ TRA CỨU</h3>", unsafe_allow_html=True)
            query = st.text_input("Gateway", placeholder="Ví dụ: TC0243, Daknoco...", label_visibility="collapsed")
        
        st.markdown("<br>", unsafe_allow_html=True)
        col_main, col_officers = st.columns([1.8, 1])

        with col_main:
            if query:
                clean_query = unidecode(query).lower()
                results = df[df['search_index'].str.contains(clean_query, na=False)].head(12)
                if not results.empty:
                    st.write(f"✨ Tìm thấy **{len(results)}** đơn vị phù hợp:")
                    for _, row in results.iterrows():
                        with st.container():
                            ca, cb = st.columns([4, 1.5])
                            ca.markdown(f"""
                                <div style='background:white; padding:25px; border-radius:25px; border-left:12px solid #e2e8f0; margin-bottom:15px; box-shadow: 0 5px 15px rgba(0,0,0,0.05);'>
                                    <small style='color:#2563eb; font-weight:800;'>MÃ: {row.get('madvi')}</small><br>
                                    <b style='font-size:1.5rem; color:#1e293b;'>{row.get('tendvi')}</b>
                                </div>
                            """, unsafe_allow_html=True)
                            if cb.button("Tra cứu ngay ➔", key=f"sel_{row.get('madvi')}_{_}", use_container_width=True):
                                st.balloons()
                                with st.status("💎 Đang phân tích dữ liệu chuyên sâu...", expanded=False):
                                    time.sleep(0.6)
                                st.session_state.selected_unit = row.get('madvi')
                                st.rerun()
                else:
                    st.error("Không tìm thấy đơn vị. Hãy kiểm tra lại từ khóa.")
            else:
                # Banner Poster Tự động
                p = get_rotating_poster()
                st.markdown(f"""
                    <div class="poster-area">
                        <h1 style='color:white; margin:0;'>{p['t']}</h1>
                        <p style='font-size:1.4rem; opacity:0.9; line-height:1.6; margin:20px 0;'>{p['c']}</p>
                        <hr style='border: 0.5px solid rgba(255,255,255,0.3);'>
                        <h2 style='color:#ffaa00; margin:0;'>{p['s']}</h2>
                    </div>
                """, unsafe_allow_html=True)

        with col_officers:
            st.markdown("### 📞 Cán bộ Chuyên quản")
            for off in OFFICERS:
                st.markdown(f"""
                <div class="officer-card">
                    <span class="badge-flash">TRỰC TUYẾN</span>
                    <h4 style="margin:0; color:#1e3a8a;">{off['name']}</h4>
                    <p style="margin:5px 0; font-size:0.9rem; color:#64748b;"><b>{off['title']}</b></p>
                    <p style="margin:5px 0; font-size:0.85rem;">Phụ trách: {off['scope']}</p>
                    <div style="background:#f0f9ff; padding:10px; border-radius:12px; margin-top:10px; border:1px solid #e2e8f0; text-align:center;">
                        <a href="tel:{off['phone'].replace('.','')}" style="text-decoration:none; color:#2563eb; font-weight:800; font-size:1.2rem;">📱 {off['phone']}</a>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # MÀN HÌNH 2: DASHBOARD CHI TIẾT
    else:
        unit_data = df[df['madvi'] == st.session_state.selected_unit].iloc[0]
        unit_addr = unidecode(str(unit_data.get('diachi', ''))).lower()
        
        if st.button("⬅ QUAY LẠI TÌM KIẾM"):
            st.session_state.selected_unit = None
            st.rerun()

        st.markdown(f"""
            <div style='background:white; padding:45px; border-radius:40px; border-left:20px solid #1e3a8a; box-shadow: 0 25px 60px rgba(0,0,0,0.08);'>
                <h1 style='margin:0; color:#1e3a8a; font-size:3.8rem;'>🏢 {unit_data.get('tendvi')}</h1>
                <p style='margin:10px 0 0 0; color:#64748b; font-size:1.4rem;'>Mã đơn vị: <b style='color:#1e3a8a;'>{unit_data.get('madvi')}</b> | Địa chỉ: {unit_data.get('diachi', 'N/A')}</p>
            </div>
        """, unsafe_allow_html=True)

        col_left, col_right = st.columns([1.9, 1])

        with col_left:
            st.markdown("<div class='premium-panel' style='margin-top:30px;'>", unsafe_allow_html=True)
            st.write("### 📉 Phân tích Số liệu C12-TS")
            
            m1, m2, m3 = st.columns(3)
            with m1: st.markdown(f"<div class='metric-box'><p class='metric-lab'>Đầu kỳ</p><p class='metric-val'>{unit_data.get('tien_dau_ky', 0):,.0f}đ</p></div>", unsafe_allow_html=True)
            with m2: st.markdown(f"<div class='metric-box'><p class='metric-lab'>Phải đóng</p><p class='metric-val'>{unit_data.get('so_phai_dong', 0):,.0f}đ</p></div>", unsafe_allow_html=True)
            with m3: st.markdown(f"<div class='metric-box'><p class='metric-lab'>Điều chỉnh</p><p class='metric-val'>{unit_data.get('dieu_chinh_ky_truoc', 0):,.0f}đ</p></div>", unsafe_allow_html=True)
            
            st.write("<br>", unsafe_allow_html=True)
            m4, m5, m6 = st.columns(3)
            with m4: st.markdown(f"<div class='metric-box'><p class='metric-lab'>Đã đóng</p><p class='metric-val' style='color:#10b981;'>{unit_data.get('so_da_dong', 0):,.0f}đ</p></div>", unsafe_allow_html=True)
            with m5: st.markdown(f"<div class='metric-box'><p class='metric-lab'>Bị lệch</p><p class='metric-val' style='color:#f59e0b;'>{unit_data.get('so_bi_lech', 0):,.0f}đ</p></div>", unsafe_allow_html=True)
            with m6:
                debt = unit_data.get('tien_cuoi_ky', 0)
                color = "#ef4444" if debt > 0 else "#3b82f6"
                st.markdown(f"<div class='metric-box'><p class='metric-lab'>Còn nợ/Dư</p><p class='metric-val' style='color:{color};'>{abs(debt):,.0f}đ</p></div>", unsafe_allow_html=True)
            
            # Cú pháp nộp tiền chuẩn
            now = datetime.now()
            transfer_note = f"{unit_data.get('madvi')} {unit_data.get('tendvi')} đóng bhxh tháng {now.month} năm {now.year}"
            st.markdown(f"""
                <div style='background:#f0f9ff; padding:35px; border-radius:30px; border:3px dashed #3b82f6; margin-top:30px;'>
                    <p style='color:#1e40af; font-weight:800; margin:0; font-size:1.1rem; text-transform:uppercase;'>📝 Nội dung nộp tiền chuyển khoản:</p>
                    <h2 style='color:#1e3a8a; font-family:monospace; margin:15px 0; font-size:2rem; background:white; padding:15px; border-radius:15px;'>{transfer_note}</h2>
                    <p style='margin:0; font-size:0.9rem; color:#64748b;'><i>Vui lòng ghi đúng nội dung để hệ thống ghi nhận kịp thời.</i></p>
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
                title = {'text': "Tỷ lệ hoàn thành", 'font': {'size': 22}},
                number = {'suffix': "%", 'font': {'color': '#1e40af', 'size': 60}},
                gauge = {
                    'axis': {'range': [0, 100]},
                    'bar': {'color': "#1e40af"},
                    'bgcolor': "white",
                    'steps': [{'range': [0, 50], 'color': '#fee2e2'}, {'range': [50, 90], 'color': '#fef9c3'}, {'range': [90, 100], 'color': '#dcfce7'}]
                }
            ))
            fig.update_layout(height=400, margin=dict(l=35, r=35, t=70, b=35), paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)
            
            # Cán bộ phụ trách đơn vị (NỔI BẬT NHẤP NHÁY)
            st.markdown("### 👩‍💼 Cán bộ Chuyên quản phụ trách")
            found_officer = False
            for off in OFFICERS:
                # Kiểm tra nếu địa chỉ đơn vị chứa từ khóa của cán bộ phụ trách
                is_assigned = any(area in unit_addr for area in off['areas'])
                blink_class = "blink-active" if is_assigned else ""
                badge = '<span class="badge-flash">PHỤ TRÁCH TRỰC TIẾP</span>' if is_assigned else ""
                
                if is_assigned: found_officer = True
                
                # Nếu tìm thấy cán bộ phụ trách, chỉ hiện cán bộ đó nổi bật, hoặc hiện hết nhưng highlight
                st.markdown(f"""
                <div class="officer-card {blink_class}">
                    {badge}
                    <h4 style="margin:0; color:#1e3a8a;">{off['name']}</h4>
                    <p style="margin:5px 0; font-size:0.85rem;">{off['title']}</p>
                    <p style="margin:5px 0; font-size:0.8rem; color:#64748b;">Vùng quản lý: {off['scope']}</p>
                    <div style="background:white; padding:10px; border-radius:12px; margin-top:10px; border:1px solid #e2e8f0; text-align:center;">
                        <a href="tel:{off['phone'].replace('.','')}" style="text-decoration:none; color:#2563eb; font-weight:800; font-size:1.3rem;">📱 {off['phone']}</a>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            if not found_officer:
                st.warning("Hệ thống không tự động nhận diện được cán bộ phụ trách khu vực này. Vui lòng liên hệ bất kỳ cán bộ nào ở trên.")

# --- FOOTER ---
st.markdown("<br><hr>", unsafe_allow_html=True)
st.markdown(f"<center style='color:#94a3b8; font-size:0.9rem; padding-bottom:60px;'>© {datetime.now().year} BHXH CƠ SỞ THUẬN AN - LÂM ĐỒNG | Elite Connect v11.0</center>", unsafe_allow_html=True)
