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
    page_title="BHXH cơ sở Thuận An - Digital Hub v10.0",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- KHỞI TẠO STATE ---
if 'selected_unit' not in st.session_state:
    st.session_state.selected_unit = None
if 'last_query' not in st.session_state:
    st.session_state.last_query = ""

# --- TỔNG LỰC CSS (GIAO DIỆN PREMIUM v10.0) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    :root {
        --primary: #1e3a8a;
        --secondary: #3b82f6;
        --accent: #0ea5e9;
        --bg: #f8fafc;
        --card-bg: rgba(255, 255, 255, 0.9);
    }

    * { font-family: 'Plus Jakarta Sans', sans-serif; }
    
    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
    }
    
    /* Hero Title Section */
    .hero-container {
        text-align: center;
        padding: 2rem 0;
        background: transparent;
    }
    
    .hero-title {
        background: linear-gradient(90deg, #1e3a8a, #2563eb, #0ea5e9);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 5rem;
        font-weight: 800;
        letter-spacing: -4px;
        margin-bottom: 0px;
        line-height: 1.1;
    }

    /* Marquee Styling */
    .marquee-wrapper {
        background: #1e3a8a;
        color: white;
        padding: 15px 0;
        font-weight: 600;
        border-radius: 15px;
        box-shadow: 0 10px 20px -5px rgba(30, 58, 138, 0.3);
        margin-bottom: 30px;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    /* Premium Cards */
    .premium-card {
        background: var(--card-bg);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.7);
        border-radius: 35px;
        padding: 40px;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.05);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    
    .premium-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 35px 70px rgba(0, 0, 0, 0.1);
    }

    /* Info Banner / Poster */
    .poster-area {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        color: white;
        padding: 40px;
        border-radius: 35px;
        box-shadow: 0 20px 40px rgba(30, 58, 138, 0.3);
        text-align: center;
        min-height: 350px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        border: 1px solid rgba(255,255,255,0.2);
    }

    /* Search Box */
    .stTextInput input {
        border-radius: 25px !important;
        padding: 1.8rem 3rem !important;
        border: 2px solid #e2e8f0 !important;
        background: white !important;
        font-size: 1.4rem !important;
        box-shadow: 0 15px 35px rgba(0,0,0,0.05) !important;
        transition: all 0.3s ease;
    }
    .stTextInput input:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 6px rgba(59, 130, 246, 0.15) !important;
    }

    /* Bank Account Display */
    .bank-grid {
        display: grid;
        gap: 15px;
        margin-top: 20px;
    }
    .bank-item {
        background: white;
        padding: 15px 25px;
        border-radius: 20px;
        border: 1px solid #f1f5f9;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-weight: 700;
        color: #1e293b;
    }
    .bank-item span { color: #2563eb; font-family: monospace; font-size: 1.1rem; }

    /* Custom Metric */
    .metric-title { font-size: 0.85rem; color: #64748b; font-weight: 700; text-transform: uppercase; margin-bottom: 5px; }
    .metric-value { font-size: 2.2rem; font-weight: 800; color: #1e3a8a; }

    /* Transfer Code Box */
    .transfer-code-box {
        background: #f0f9ff;
        padding: 35px;
        border-radius: 30px;
        border: 3px dashed #3b82f6;
        margin-top: 30px;
    }
    </style>
    """, unsafe_allow_html=True)

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

# --- NỘI DUNG BANNER TUYÊN TRUYỀN (AUTO-ROTATE) ---
def get_current_poster():
    posters = [
        {
            "title": "🛡️ QUYỀN LỢI HÔM NAY",
            "content": "Tham gia BHXH là hình thức tiết kiệm tích lũy cho tương lai. Người lao động được hưởng lương hưu hàng tháng khi về già, đảm bảo cuộc sống an nhàn.",
            "sub": "Đóng bảo hiểm - Hưởng an vui"
        },
        {
            "title": "🏥 CHĂM SÓC SỨC KHỎE",
            "content": "BHYT chi trả phần lớn chi phí khám chữa bệnh. Giảm bớt gánh nặng tài chính cho gia đình khi không may gặp rủi ro sức khỏe.",
            "sub": "Có thẻ BHYT - Cả nhà yên tâm"
        },
        {
            "title": "🤰 CHẾ ĐỘ THAI SẢN",
            "content": "Lao động nữ được nghỉ hưởng trợ cấp thai sản bằng 100% mức bình quân tiền lương tháng đóng BHXH. Hỗ trợ mẹ và bé trong những ngày đầu đời.",
            "sub": "Đồng hành cùng hạnh phúc gia đình"
        },
        {
            "title": "💼 BẢO HIỂM THẤT NGHIỆP",
            "content": "Hỗ trợ thu nhập cho người lao động khi mất việc làm. Đồng thời hỗ trợ học nghề và tìm kiếm việc làm mới nhanh chóng.",
            "sub": "Điểm tựa khi gặp khó khăn"
        },
        {
            "title": "⚖️ TRÁCH NHIỆM ĐƠN VỊ",
            "content": "Đơn vị có nghĩa vụ đóng BHXH, BHYT đầy đủ và đúng hạn cho người lao động. Đây là hành động tuân thủ pháp luật và nâng cao uy tín doanh nghiệp.",
            "sub": "Doanh nghiệp vững mạnh - Xã hội phồn vinh"
        }
    ]
    # Chọn poster dựa trên phút hiện tại (xoay vòng mỗi phút)
    current_minute = datetime.now().minute
    idx = current_minute % len(posters)
    return posters[idx]

# --- HEADER SECTION ---
st.markdown("<div class='hero-container'><h1 class='hero-title'>BHXH cơ sở Thuận An</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#64748b; font-size:1.4rem; font-weight:600; margin-top:-10px;'>Cổng Tra cứu & Quản lý Thông tin BHXH Kỹ thuật số</p></div>", unsafe_allow_html=True)

# Marquee Information
bank_info = "BIDV: 63510009867032 - Agribank: 5301202919045 - Vietinbank: 919035000003"
marquee_text = f"🛡️ BHXH Thuận An - Thôn Thuận Sơn, xã Thuận An, Lâm Đồng. | 🏦 STK: {bank_info} | Luôn đồng hành cùng quyền lợi của người lao động và đơn vị. | Cập nhật số liệu nộp tiền định kỳ hàng tháng."
st.markdown(f"""
    <div class="marquee-wrapper">
        <marquee scrollamount="9" behavior="scroll" direction="left">{marquee_text}</marquee>
    </div>
    """, unsafe_allow_html=True)

df = load_data()

# --- GIAO DIỆN CHÍNH ---
if df is not None:
    # MÀN HÌNH 1: TRANG CHỦ & TÌM KIẾM
    if st.session_state.selected_unit is None:
        col_main, col_side = st.columns([1.7, 1])
        
        with col_main:
            st.markdown("### 🔍 Tra cứu thông báo kết quả đóng")
            query = st.text_input("SearchQuery", placeholder="Nhập tên đơn vị hoặc mã số đơn vị (vd: TC0243)...", label_visibility="collapsed")
            
            if query:
                clean_query = unidecode(query).lower()
                results = df[df['search_index'].str.contains(clean_query, na=False)].head(12)
                
                if not results.empty:
                    st.write(f"Tìm thấy **{len(results)}** kết quả phù hợp:")
                    for _, row in results.iterrows():
                        with st.container():
                            c_a, c_b = st.columns([4, 1.5])
                            c_a.markdown(f"""
                                <div style='background:white; padding:25px; border-radius:25px; border-left:12px solid #e2e8f0; margin-bottom:15px; box-shadow: 0 5px 15px rgba(0,0,0,0.05);'>
                                    <small style='color:#3b82f6; font-weight:800; text-transform:uppercase;'>Mã: {row.get('madvi')}</small><br>
                                    <b style='font-size:1.4rem; color:#1e293b;'>{row.get('tendvi')}</b>
                                </div>
                            """, unsafe_allow_html=True)
                            if c_b.button("Xem chi tiết ➔", key=f"sel_{row.get('madvi')}_{_}", use_container_width=True):
                                # Hiệu ứng chúc mừng & Loading
                                st.balloons()
                                with st.status("💎 Đang tổng hợp số liệu vàng...", expanded=False):
                                    time.sleep(0.7)
                                st.session_state.selected_unit = row.get('madvi')
                                st.rerun()
                else:
                    st.error("Không tìm thấy đơn vị nào phù hợp. Vui lòng kiểm tra lại từ khóa.")
            else:
                st.markdown("<br><br><center><img src='https://cdn-icons-png.flaticon.com/512/3772/3772274.png' width='160' style='opacity:0.2'></center>", unsafe_allow_html=True)

        with col_side:
            # Banner tự động xoay vòng
            poster_data = get_current_poster()
            st.markdown(f"""
                <div class="poster-area">
                    <h1 style='color:white; margin-top:0;'>{poster_data['title']}</h1>
                    <p style='font-size:1.25rem; opacity:0.95; line-height:1.6;'>{poster_data['content']}</p>
                    <hr style='border: 0.5px solid rgba(255,255,255,0.3); margin: 25px 0;'>
                    <h3 style='color:#fbbf24; margin:0;'>{poster_data['sub']}</h3>
                </div>
            """, unsafe_allow_html=True)
            st.caption(f"🕒 Banner tự động cập nhật nội dung mỗi phút. (Hiện tại: {datetime.now().strftime('%H:%M')})")

    # MÀN HÌNH 2: DASHBOARD CHI TIẾT
    else:
        unit_data = df[df['madvi'] == st.session_state.selected_unit].iloc[0]
        
        if st.button("⬅ Quay lại trang tra cứu", use_container_width=False):
            st.session_state.selected_unit = None
            st.rerun()

        st.markdown(f"""
            <div style='background:white; padding:45px; border-radius:40px; border-left:18px solid #1e3a8a; box-shadow: 0 25px 55px rgba(0,0,0,0.07);'>
                <h1 style='margin:0; color:#1e3a8a; font-size:3.5rem;'>🏢 {unit_data.get('tendvi')}</h1>
                <p style='margin:12px 0 0 0; color:#64748b; font-size:1.3rem;'>Mã đơn vị: <b style='color:#1e3a8a;'>{unit_data.get('madvi')}</b> | Đại diện: {unit_data.get('nguoilh', 'N/A')}</p>
                <p style='margin:5px 0 0 0; color:#94a3b8;'>📍 Địa chỉ: {unit_data.get('diachi', 'Chưa có thông tin')}</p>
            </div>
        """, unsafe_allow_html=True)

        c_dash1, c_dash2 = st.columns([1.9, 1])

        with c_dash1:
            st.markdown("<div class='premium-card' style='margin-top:30px;'>", unsafe_allow_html=True)
            st.write("### 📉 Phân tích số liệu đóng BHXH")
            
            # Metric Grid v10.0
            m1, m2, m3 = st.columns(3)
            with m1:
                st.markdown("<p class='metric-title'>Tiền đầu kỳ</p>", unsafe_allow_html=True)
                st.markdown(f"<p class='metric-value'>{unit_data.get('tien_dau_ky', 0):,.0f}đ</p>", unsafe_allow_html=True)
            with m2:
                st.markdown("<p class='metric-title'>Số phải đóng</p>", unsafe_allow_html=True)
                st.markdown(f"<p class='metric-value'>{unit_data.get('so_phai_dong', 0):,.0f}đ</p>", unsafe_allow_html=True)
            with m3:
                st.markdown("<p class='metric-title'>Điều chỉnh</p>", unsafe_allow_html=True)
                st.markdown(f"<p class='metric-value'>{unit_data.get('dieu_chinh_ky_truoc', 0):,.0f}đ</p>", unsafe_allow_html=True)
            
            st.write("<br>", unsafe_allow_html=True)
            
            m4, m5, m6 = st.columns(3)
            with m4:
                st.markdown("<p class='metric-title'>Số đã đóng</p>", unsafe_allow_html=True)
                st.markdown(f"<p class='metric-value' style='color:#10b981;'>{unit_data.get('so_da_dong', 0):,.0f}đ</p>", unsafe_allow_html=True)
            with m5:
                st.markdown("<p class='metric-title'>Số bị lệch</p>", unsafe_allow_html=True)
                st.markdown(f"<p class='metric-value' style='color:#f59e0b;'>{unit_data.get('so_bi_lech', 0):,.0f}đ</p>", unsafe_allow_html=True)
            with m6:
                debt = unit_data.get('tien_cuoi_ky', 0)
                label_txt = "Tiền còn nợ" if debt > 0 else "Tiền dư có"
                color_txt = "#ef4444" if debt > 0 else "#3b82f6"
                st.markdown(f"<p class='metric-title'>{label_txt}</p>", unsafe_allow_html=True)
                st.markdown(f"<p class='metric-value' style='color:{color_txt};'>{abs(debt):,.0f}đ</p>", unsafe_allow_html=True)
            
            # Cú pháp nộp tiền chuẩn theo tháng/năm hiện tại
            now = datetime.now()
            transfer_note = f"{unit_data.get('madvi')} {unit_data.get('tendvi')} đóng bhxh tháng {now.month} năm {now.year}"
            
            st.markdown(f"""
                <div class="transfer-code-box">
                    <p style='color:#1e40af; font-weight:800; margin:0; font-size:1.1rem; text-transform:uppercase;'>📝 Cú pháp nộp tiền (Duy nhất):</p>
                    <h2 style='color:#1e3a8a; font-family:monospace; margin:15px 0; font-size:1.8rem; background:white; padding:15px; border-radius:15px; border:1px solid #e2e8f0;'>{transfer_note}</h2>
                    <p style='margin:0; font-size:0.9rem; color:#64748b;'><i>Vui lòng ghi đúng nội dung để phần mềm gạch nợ tự động trong 24h.</i></p>
                </div>
            """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with c_dash2:
            # Interactive Gauge Chart
            phai_dong = unit_data.get('so_phai_dong', 1)
            da_dong = unit_data.get('so_da_dong', 0)
            rate = min(round((da_dong / phai_dong) * 100, 1), 100) if phai_dong > 0 else 0
            
            fig = go.Figure(go.Indicator(
                mode = "gauge+number", value = rate,
                title = {'text': "Tỷ lệ nộp tiền hoàn thành", 'font': {'size': 22, 'color': '#64748b'}},
                number = {'suffix': "%", 'font': {'color': '#1e40af', 'size': 60}},
                gauge = {
                    'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#cbd5e1"},
                    'bar': {'color': "#1e40af"},
                    'bgcolor': "white",
                    'borderwidth': 3,
                    'bordercolor': "#f1f5f9",
                    'steps': [
                        {'range': [0, 50], 'color': '#fee2e2'},
                        {'range': [50, 90], 'color': '#fef9c3'},
                        {'range': [90, 100], 'color': '#dcfce7'}
                    ]
                }
            ))
            fig.update_layout(height=450, margin=dict(l=35, r=35, t=70, b=35), paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)
            
            # Tài khoản Ngân hàng
            st.markdown("### 🏦 Danh sách tài khoản thụ hưởng")
            st.markdown("""
                <div class="bank-grid">
                    <div class='bank-item'><b>BIDV</b> <span>63510009867032</span></div>
                    <div class='bank-item'><b>Agribank</b> <span>5301202919045</span></div>
                    <div class='bank-item'><b>Vietinbank</b> <span>919035000003</span></div>
                </div>
            """, unsafe_allow_html=True)
            
            # QR Pay Integration
            qr_data = f"BHXH|{unit_data.get('madvi')}|{debt}"
            st.markdown(f"""
                <center>
                    <div style='background:white; padding:20px; border-radius:30px; box-shadow: 0 15px 35px rgba(0,0,0,0.06); display:inline-block; margin-top:25px; border:1px solid #f1f5f9;'>
                        <img src='https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={qr_data}' width='200'>
                    </div>
                    <p style='color:#1e3a8a; font-weight:800; font-size:1.1rem; margin-top:15px;'>QUÉT MÃ NỘP TIỀN NHANH</p>
                </center>
            """, unsafe_allow_html=True)

# --- FOOTER SECTION ---
st.markdown("<br><br><hr>", unsafe_allow_html=True)
st.markdown(f"""
    <center style='color:#94a3b8; font-size:0.95rem; padding-bottom:60px; line-height:1.6;'>
        © {datetime.now().year} BHXH CƠ SỞ THUẬN AN - THÔN THUẬN SƠN, XÃ THUẬN AN, LÂM ĐỒNG<br>
        🛡️ Kiến tạo tương lai - Bảo vệ an sinh. Hệ thống tra cứu tự động hóa v10.0
    </center>
""", unsafe_allow_html=True)
