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
if 'show_loading' not in st.session_state:
    st.session_state.show_loading = False

# --- TỔNG LỰC CSS (GIAO DIỆN ELITE v11.0.1) ---
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
    
    /* FIX Ô TÌM KIẾM BỊ CHE CHỮ */
    .stTextInput input {
        border-radius: 50px !important;
        padding: 1rem 2.5rem !important; /* Giảm padding dọc để tránh che chữ */
        border: 3px solid #3b82f6 !important;
        font-size: 1.5rem !important;
        line-height: 1.2 !important;
        height: auto !important;
        box-shadow: 0 20px 40px rgba(59, 130, 246, 0.2) !important;
        transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    .stTextInput input:focus {
        transform: scale(1.02);
        border-color: #2563eb !important;
    }

    /* HIỆU ỨNG ĐÈN NEON NHẤP NHÁY CHO CÁN BỘ */
    @keyframes neon-blue-blink {
        0%, 100% { border-color: #00d2ff; box-shadow: 0 0 5px #00d2ff, inset 0 0 5px #00d2ff; }
        50% { border-color: #ffffff; box-shadow: 0 0 20px #00d2ff, inset 0 0 10px #00d2ff; }
    }
    @keyframes neon-gold-blink {
        0%, 100% { border-color: #ffaa00; box-shadow: 0 0 5px #ffaa00, inset 0 0 5px #ffaa00; }
        50% { border-color: #ffffff; box-shadow: 0 0 20px #ffaa00, inset 0 0 10px #ffaa00; }
    }
    @keyframes neon-green-blink {
        0%, 100% { border-color: #39ff14; box-shadow: 0 0 5px #39ff14, inset 0 0 5px #39ff14; }
        50% { border-color: #ffffff; box-shadow: 0 0 20px #39ff14, inset 0 0 10px #39ff14; }
    }

    .officer-card {
        background: white;
        padding: 20px;
        border-radius: 20px;
        border: 4px solid #e2e8f0;
        margin-bottom: 20px;
        text-align: center;
    }
    .card-nhai { animation: neon-blue-blink 2s infinite; }
    .card-dat { animation: neon-gold-blink 2.5s infinite; }
    .card-hai { animation: neon-green-blink 3s infinite; }

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

    /* Premium Design */
    .premium-panel {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 40px;
        padding: 40px;
        box-shadow: 0 25px 50px rgba(0,0,0,0.06);
        border: 1px solid rgba(255,255,255,0.7);
    }

    /* Metric UI */
    .metric-box {
        text-align: center;
        background: #f8fafc;
        padding: 20px;
        border-radius: 25px;
        border: 1px solid #edf2f7;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
    }
    .metric-val { font-size: 1.8rem; font-weight: 800; color: #1e3a8a; }
    .metric-lab { font-size: 0.8rem; color: #64748b; font-weight: 700; text-transform: uppercase; }

    .badge-flash {
        background: #ff3131;
        color: white;
        padding: 4px 12px;
        border-radius: 50px;
        font-size: 0.7rem;
        font-weight: 800;
        animation: pulse 1s infinite;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.7; transform: scale(0.95); }
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
        "areas": ["duc lap", "dak mil", "đức lập", "đắk mil"]
    },
    {
        "name": "Ông BÙI THÀNH ĐẠT",
        "title": "Chuyên viên BHXH",
        "scope": "Xã Đắk Sắk, Xã Đắk Song",
        "phone": "0986.05.30.06",
        "class": "card-dat",
        "areas": ["dak sak", "dak song", "đắk sắk", "đắk song"]
    },
    {
        "name": "Ông HOÀNG SỸ HẢI",
        "title": "Chuyên viên BHXH",
        "scope": "Xã Thuận An",
        "phone": "0919.06.11.53",
        "class": "card-hai",
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
            # Chuẩn hóa tên cột chính xác theo file
            df.columns = [unidecode(str(c)).lower().strip().replace(' ', '_') for c in df.columns]
            if 'madvi' in df.columns: df['madvi'] = df['madvi'].astype(str).str.strip()
            df['search_index'] = df.apply(lambda x: unidecode(str(x.get('madvi', '')) + " " + str(x.get('tendvi', ''))).lower(), axis=1)
            return df
    except Exception as e:
        st.error(f"Lỗi đọc dữ liệu: {e}")
    return None

# --- BANNER TUYÊN TRUYỀN ---
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
st.markdown("<p style='text-align:center; color:#64748b; font-size:1.2rem; font-weight:600; margin-top:-10px;'>Cổng Kết Nối & Tra Cứu Dữ Liệu Chuyên Nghiệp</p>", unsafe_allow_html=True)

# Bảng tin chạy
marquee_text = "🛡️ BHXH Thuận An: Thôn Thuận Sơn, xã Thuận An, Lâm Đồng. | 🏦 BIDV: 63510009867032 | 🏦 Agribank: 5301202919045 | 🏦 Vietinbank: 919035000003. | Vui lòng liên hệ cán bộ chuyên quản để được hỗ trợ tốt nhất."
st.markdown(f"<div class='marquee-wrapper'><marquee scrollamount='9'>{marquee_text}</marquee></div>", unsafe_allow_html=True)

df = load_data()

# --- XỬ LÝ HIỂN THỊ ---
if df is not None:
    # MÀN HÌNH 1: TRANG CHỦ & TÌM KIẾM
    if st.session_state.selected_unit is None:
        # Cửa ngõ tìm kiếm nổi bật
        _, c_search, _ = st.columns([0.1, 0.8, 0.1])
        with c_search:
            st.markdown("<h3 style='text-align:center; color:#1e3a8a; margin-bottom:10px;'>🔍 NHẬP MÃ HOẶC TÊN ĐƠN VỊ</h3>", unsafe_allow_html=True)
            query = st.text_input("Gateway", placeholder="Gõ tìm kiếm tại đây...", label_visibility="collapsed")
        
        st.markdown("<br>", unsafe_allow_html=True)
        col_main, col_officers = st.columns([1.8, 1])

        with col_main:
            if query:
                clean_query = unidecode(query).lower()
                results = df[df['search_index'].str.contains(clean_query, na=False)].head(10)
                if not results.empty:
                    st.write(f"✨ Tìm thấy **{len(results)}** kết quả:")
                    for idx, row in results.iterrows():
                        with st.container():
                            ca, cb = st.columns([4, 1.5])
                            ca.markdown(f"""
                                <div style='background:white; padding:20px; border-radius:25px; border-left:12px solid #e2e8f0; margin-bottom:15px; box-shadow: 0 5px 15px rgba(0,0,0,0.05);'>
                                    <small style='color:#2563eb; font-weight:800;'>MÃ: {row.get('madvi')}</small><br>
                                    <b style='font-size:1.4rem; color:#1e293b;'>{row.get('tendvi')}</b>
                                </div>
                            """, unsafe_allow_html=True)
                            
                            # FIX LỖI XÁC NHẬN: Sử dụng logic state thay vì status trực tiếp trong button
                            if cb.button("Xác nhận tra cứu ➔", key=f"btn_{row.get('madvi')}_{idx}", use_container_width=True):
                                st.session_state.selected_unit = row.get('madvi')
                                st.session_state.show_loading = True
                                st.rerun()
                else:
                    st.error("Không tìm thấy đơn vị. Hãy kiểm tra lại từ khóa.")
            else:
                p = get_rotating_poster()
                st.markdown(f"""
                    <div class="poster-area">
                        <h1 style='color:white; margin:0;'>{p['t']}</h1>
                        <p style='font-size:1.3rem; opacity:0.9; line-height:1.6; margin:20px 0;'>{p['c']}</p>
                        <hr style='border: 0.5px solid rgba(255,255,255,0.3);'>
                        <h2 style='color:#ffaa00; margin:0;'>{p['s']}</h2>
                    </div>
                """, unsafe_allow_html=True)

        with col_officers:
            st.markdown("<h3 style='text-align:center;'>📞 Cán bộ Chuyên quản</h3>", unsafe_allow_html=True)
            for off in OFFICERS:
                st.markdown(f"""
                <div class="officer-card {off['class']}">
                    <span class="badge-flash">ONLINE</span>
                    <h4 style="margin:0; color:#1e3a8a;">{off['name']}</h4>
                    <p style="margin:5px 0; font-size:0.85rem; color:#64748b;"><b>{off['title']}</b></p>
                    <p style="margin:5px 0; font-size:0.8rem;">Phụ trách: {off['scope']}</p>
                    <div style="background:#f0f9ff; padding:10px; border-radius:12px; margin-top:10px; border:1px solid #e2e8f0; text-align:center;">
                        <a href="tel:{off['phone'].replace('.','')}" style="text-decoration:none; color:#2563eb; font-weight:800; font-size:1.2rem;">📱 {off['phone']}</a>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # MÀN HÌNH LOADING KHI XÁC NHẬN
    elif st.session_state.show_loading:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        with st.status("💎 Đang phân tích dữ liệu chuyên sâu...", expanded=True) as status:
            st.write("🔄 Đang kết nối máy chủ dữ liệu...")
            time.sleep(0.5)
            st.write("📊 Đang tổng hợp số liệu C12-TS...")
            time.sleep(0.5)
            st.write("✨ Đang tạo Dashboard báo cáo...")
            time.sleep(0.5)
            status.update(label="Hoàn tất!", state="complete")
        
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
            <div style='background:white; padding:40px; border-radius:40px; border-left:20px solid #1e3a8a; box-shadow: 0 25px 60px rgba(0,0,0,0.08);'>
                <h1 style='margin:0; color:#1e3a8a; font-size:3rem;'>🏢 {unit_data.get('tendvi')}</h1>
                <p style='margin:10px 0 0 0; color:#64748b; font-size:1.2rem;'>Mã đơn vị: <b style='color:#1e3a8a;'>{unit_data.get('madvi')}</b> | Địa chỉ: {unit_data.get('diachi', 'N/A')}</p>
            </div>
        """, unsafe_allow_html=True)

        col_left, col_right = st.columns([1.9, 1])

        with col_left:
            st.markdown("<div class='premium-panel' style='margin-top:30px;'>", unsafe_allow_html=True)
            st.write("### 📈 Phân tích Số liệu C12-TS")
            
            # Metric Grid với đầy đủ các cột yêu cầu
            m1, m2, m3 = st.columns(3)
            with m1: st.markdown(f"<div class='metric-box'><p class='metric-lab'>Tiền đầu kỳ</p><p class='metric-val'>{unit_data.get('tien_dau_ky', 0):,.0f}đ</p></div>", unsafe_allow_html=True)
            with m2: st.markdown(f"<div class='metric-box'><p class='metric-lab'>Số phải đóng</p><p class='metric-val'>{unit_data.get('so_phai_dong', 0):,.0f}đ</p></div>", unsafe_allow_html=True)
            with m3: st.markdown(f"<div class='metric-box'><p class='metric-lab'>Điều chỉnh</p><p class='metric-val'>{unit_data.get('dieu_chinh_ky_truoc', 0):,.0f}đ</p></div>", unsafe_allow_html=True)
            
            st.write("<br>", unsafe_allow_html=True)
            m4, m5, m6 = st.columns(3)
            with m4: st.markdown(f"<div class='metric-box'><p class='metric-lab'>Số đã đóng</p><p class='metric-val' style='color:#10b981;'>{unit_data.get('so_da_dong', 0):,.0f}đ</p></div>", unsafe_allow_html=True)
            with m5: st.markdown(f"<div class='metric-box'><p class='metric-lab'>Số bị lệch</p><p class='metric-val' style='color:#f59e0b;'>{unit_data.get('so_bi_lech', 0):,.0f}đ</p></div>", unsafe_allow_html=True)
            with m6:
                debt = unit_data.get('tien_cuoi_ky', 0)
                color = "#ef4444" if debt > 0 else "#3b82f6"
                st.markdown(f"<div class='metric-box'><p class='metric-lab'>Còn nợ/Dư</p><p class='metric-val' style='color:{color};'>{abs(debt):,.0f}đ</p></div>", unsafe_allow_html=True)
            
            st.write(f"**Tỷ lệ nợ hiện tại:** `{unit_data.get('tyleno', 0)}%`")
            
            # Cú pháp nộp tiền chuẩn
            now = datetime.now()
            transfer_note = f"{unit_data.get('madvi')} {unit_data.get('tendvi')} đóng bhxh tháng {now.month} năm {now.year}"
            st.markdown(f"""
                <div style='background:#f0f9ff; padding:35px; border-radius:30px; border:3px dashed #3b82f6; margin-top:30px;'>
                    <p style='color:#1e40af; font-weight:800; margin:0; font-size:1.1rem; text-transform:uppercase;'>📝 Nội dung nộp tiền chuyển khoản:</p>
                    <h2 style='color:#1e3a8a; font-family:monospace; margin:15px 0; font-size:1.8rem; background:white; padding:15px; border-radius:15px; border:1px solid #e2e8f0;'>{transfer_note}</h2>
                    <p style='margin:0; font-size:0.9rem; color:#64748b;'><i>Vui lòng ghi đúng nội dung để hệ thống ghi nhận tự động.</i></p>
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
                title = {'text': "Tỷ lệ hoàn thành (%)", 'font': {'size': 20}},
                number = {'suffix': "%", 'font': {'color': '#1e40af', 'size': 50}},
                gauge = {
                    'axis': {'range': [0, 100]},
                    'bar': {'color': "#1e40af"},
                    'bgcolor': "white",
                    'steps': [{'range': [0, 50], 'color': '#fee2e2'}, {'range': [50, 90], 'color': '#fef9c3'}, {'range': [90, 100], 'color': '#dcfce7'}]
                }
            ))
            fig.update_layout(height=400, margin=dict(l=35, r=35, t=70, b=35), paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)
            
            # Cán bộ phụ trách
            st.markdown("### 👨‍💼 Cán bộ Chuyên quản phụ trách")
            found_officer = False
            for off in OFFICERS:
                is_assigned = any(area in unit_addr for area in off['areas'])
                blink_class = off['class'] if is_assigned else ""
                badge = '<span class="badge-flash">PHỤ TRÁCH TRỰC TIẾP</span>' if is_assigned else ""
                
                if is_assigned:
                    found_officer = True
                    st.markdown(f"""
                    <div class="officer-card {blink_class}" style="background:#f0f9ff;">
                        {badge}
                        <h4 style="margin:0; color:#1e3a8a;">{off['name']}</h4>
                        <p style="margin:5px 0; font-size:0.85rem;">{off['title']}</p>
                        <div style="background:white; padding:10px; border-radius:12px; margin-top:10px; border:2px solid #3b82f6; text-align:center;">
                            <a href="tel:{off['phone'].replace('.','')}" style="text-decoration:none; color:#2563eb; font-weight:800; font-size:1.4rem;">📱 {off['phone']}</a>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            if not found_officer:
                st.warning("Hệ thống không nhận diện được cán bộ khu vực. Vui lòng liên hệ tổng đài.")

# --- FOOTER ---
st.markdown("<br><hr>", unsafe_allow_html=True)
st.markdown(f"<center style='color:#94a3b8; font-size:0.9rem; padding-bottom:60px;'>© {datetime.now().year} BHXH CƠ SỞ THUẬN AN - LÂM ĐỒNG | Elite Connect v11.0.1</center>", unsafe_allow_html=True)
