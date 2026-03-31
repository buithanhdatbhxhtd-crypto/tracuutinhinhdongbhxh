import streamlit as st
import pandas as pd
import numpy as np
import os
import plotly.graph_objects as go
from unidecode import unidecode
import time

# --- CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="BHXH Thuận An - Cổng Tra cứu Thông minh",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- KHỞI TẠO TRẠNG THÁI HỆ THỐNG ---
if 'selected_unit' not in st.session_state:
    st.session_state.selected_unit = None
if 'last_query' not in st.session_state:
    st.session_state.last_query = ""

# --- PHONG CÁCH THIẾT KẾ (CSS NÂNG CAO) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;700;800&display=swap');
    
    :root {
        --primary-color: #2563eb;
        --secondary-color: #1e40af;
        --bg-color: #f1f5f9;
    }

    * { font-family: 'Plus Jakarta Sans', sans-serif; }
    
    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
    }
    
    /* Panel chứa thông tin */
    .glass-panel {
        background: rgba(255, 255, 255, 0.98);
        border: 1px solid rgba(255, 255, 255, 0.6);
        border-radius: 32px;
        padding: 40px;
        box-shadow: 0 25px 50px -12px rgba(0,0,0,0.08);
        margin-bottom: 20px;
    }

    /* Thanh tìm kiếm */
    .stTextInput input {
        border-radius: 50px !important;
        padding: 1.5rem 2.5rem !important;
        border: 2px solid #cbd5e1 !important;
        background: white !important;
        font-size: 1.25rem !important;
        transition: all 0.3s ease;
    }
    
    /* Nút bấm chuyên nghiệp */
    .stButton>button {
        border-radius: 50px !important;
        font-weight: 700 !important;
        text-transform: none !important;
        padding: 10px 25px !important;
        transition: all 0.2s ease;
    }
    
    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
    }

    /* Thẻ kết quả */
    .search-result-card {
        background: white;
        padding: 25px;
        border-radius: 25px;
        border: 1px solid #e2e8f0;
        margin-bottom: 15px;
        border-left: 8px solid #cbd5e1;
    }

    .main-title {
        background: linear-gradient(90deg, #1e3a8a, #2563eb);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 4rem;
        font-weight: 800;
        letter-spacing: -3px;
        margin-bottom: 0px;
    }
    
    .sub-title {
        color: #64748b;
        font-size: 1.2rem;
        margin-bottom: 3rem;
    }

    /* Bảng số liệu */
    .metric-card {
        background: #ffffff;
        padding: 20px;
        border-radius: 24px;
        border: 1px solid #f1f5f9;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
    }
    </style>
    """, unsafe_allow_html=True)

# --- HÀM TẢI DỮ LIỆU ---
@st.cache_data
def load_data(uploaded_file=None):
    df = None
    try:
        if uploaded_file is not None:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
        else:
            files = [f for f in os.listdir('.') if f.lower().startswith('c12')]
            if files:
                target_file = files[0]
                if target_file.lower().endswith('.csv'):
                    df = pd.read_csv(target_file)
                else:
                    df = pd.read_excel(target_file)
        
        if df is not None:
            df.columns = [unidecode(str(c)).lower().strip().replace(' ', '_') for c in df.columns]
            if 'madvi' in df.columns:
                df['madvi'] = df['madvi'].astype(str).str.strip()
            df['search_index'] = df.apply(lambda x: unidecode(str(x.get('madvi', '')) + " " + str(x.get('tendvi', ''))).lower(), axis=1)
            return df
    except Exception as e:
        st.error(f"Lỗi dữ liệu: {e}")
    return None

# --- GIAO DIỆN CHÍNH ---
st.markdown("<div style='text-align:center'><h1 class='main-title'>💎 BHXH Smart Hub</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>Hệ thống tra cứu thông tin đóng BHXH tự động</p></div>", unsafe_allow_html=True)

df = load_data()

# KIỂM TRA DỮ LIỆU
if df is None:
    st.info("👋 Chào bạn! Hãy tải file dữ liệu lên để bắt đầu.")
    uploaded = st.file_uploader("Tải file (C12... .xls, .xlsx, .csv)", type=['xls', 'xlsx', 'csv'])
    if uploaded:
        df = load_data(uploaded)
        if df is not None: 
            st.success("✅ Đã nhận dữ liệu!")
            st.rerun()

# --- XỬ LÝ LOGIC HIỂN THỊ ---
if df is not None:
    # NẾU CHƯA CHỌN ĐƠN VỊ: HIỆN Ô TÌM KIẾM
    if st.session_state.selected_unit is None:
        st.markdown("### 🔍 Nhập tên hoặc mã đơn vị để tìm")
        query = st.text_input("Tìm kiếm", placeholder="Ví dụ: gõ 'dak' hoặc 'ten cong ty'...", label_visibility="collapsed")
        
        if query:
            clean_query = unidecode(query).lower()
            results = df[df['search_index'].str.contains(clean_query, na=False)].head(10)

            if not results.empty:
                st.write(f"Tìm thấy **{len(results)}** kết quả phù hợp. Hãy chọn đơn vị của bạn bên dưới:")
                for _, row in results.iterrows():
                    with st.container():
                        c1, c2 = st.columns([5, 1.2])
                        with c1:
                            st.markdown(f"""
                            <div class="search-result-card">
                                <span style="color:#2563eb; font-weight:800; font-size:0.9rem;">MÃ: {row.get('madvi', 'N/A')}</span><br>
                                <b style="font-size:1.2rem; color:#1e293b;">{row.get('tendvi', 'N/A')}</b>
                            </div>
                            """, unsafe_allow_html=True)
                        with c2:
                            st.write("<div style='height:20px'></div>", unsafe_allow_html=True)
                            if st.button(f"Xem thông báo ➔", key=f"sel_{row.get('madvi')}_{_}", use_container_width=True):
                                # HIỆU ỨNG LOADING CHUYÊN NGHIỆP
                                with st.status("🚀 Đang truy xuất dữ liệu, vui lòng đợi giây lát...", expanded=True) as status:
                                    st.write("Đang kết nối cơ sở dữ liệu...")
                                    time.sleep(0.5)
                                    st.write("Đang tính toán số dư...")
                                    time.sleep(0.5)
                                    st.write("Đang tạo báo cáo trực quan...")
                                    time.sleep(0.3)
                                    status.update(label="Tải dữ liệu hoàn tất!", state="complete", expanded=False)
                                
                                st.session_state.selected_unit = row.get('madvi')
                                st.rerun()
            else:
                st.error("😢 Không tìm thấy đơn vị nào. Bạn hãy thử gõ tên khác nhé!")
        else:
            # Trang chủ khi chưa gõ gì
            st.markdown("<br><br><center><img src='https://cdn-icons-png.flaticon.com/512/3772/3772274.png' width='150' style='opacity:0.2'><p style='color:#94a3b8; font-size:1.1rem;'>Hệ thống tra cứu dành riêng cho các đơn vị tại Thuận An</p></center>", unsafe_allow_html=True)

    # NẾU ĐÃ CHỌN ĐƠN VỊ: XÓA HẾT VÀ CHỈ HIỆN DASHBOARD
    else:
        unit_data = df[df['madvi'] == st.session_state.selected_unit].iloc[0]
        
        # Nút quay lại nổi bật
        if st.button("⬅ Quay lại tìm kiếm đơn vị khác", type="secondary"):
            st.session_state.selected_unit = None
            st.rerun()

        st.markdown(f"""
        <div style='background:white; padding:30px; border-radius:30px; border-left:10px solid #2563eb; margin-top:20px; box-shadow:0 10px 30px rgba(0,0,0,0.05);'>
            <h1 style='margin:0; color:#1e3a8a;'>🏢 {unit_data.get('tendvi')}</h1>
            <p style='margin:5px 0 0 0; color:#64748b; font-size:1.1rem;'><b>Mã đơn vị:</b> {unit_data.get('madvi')}</p>
        </div>
        """, unsafe_allow_html=True)
        
        col_left, col_right = st.columns([1.7, 1])
        
        with col_left:
            st.markdown("<div class='glass-panel'>", unsafe_allow_html=True)
            st.write("### 📊 Thông báo kết quả đóng BHXH")
            
            # Chỉ số tài chính
            phai_dong = unit_data.get('so_phai_dong', 0)
            da_dong = unit_data.get('so_da_dong', 0)
            debt = unit_data.get('tien_cuoi_ky', 0)
            
            m1, m2, m3 = st.columns(3)
            with m1:
                st.metric("Số phải đóng", f"{phai_dong:,.0f}đ")
            with m2:
                st.metric("Số đã đóng", f"{da_dong:,.0f}đ")
            with m3:
                label_status = "Số tiền nợ" if debt > 0 else "Số tiền dư"
                st.metric(label_status, f"{abs(debt):,.0f}đ", delta=-debt, delta_color="inverse")
            
            st.markdown("---")
            st.write("📍 **Địa chỉ:**", unit_data.get('diachi', 'N/A'))
            st.write("📞 **Thông tin liên hệ:**", f"{unit_data.get('nguoilh', 'N/A')} - {unit_data.get('dienthoai', 'N/A')}")
            
            # Hướng dẫn nộp tiền siêu rõ ràng
            st.markdown(f"""
            <div style='background: #f0f7ff; padding: 25px; border-radius: 20px; border: 2px solid #2563eb; margin-top: 20px;'>
                <p style='margin:0; font-size: 0.9rem; color: #1e40af; font-weight: 700;'>HƯỚNG DẪN NỘP TIỀN QUA NGÂN HÀNG:</p>
                <p style='margin:10px 0; font-size: 1.3rem; color: #1e3a8a; font-weight: 800; font-family: monospace;'>BHXH {unit_data.get('madvi')} {unit_data.get('tendvi')}</p>
                <p style='margin:0; font-size: 0.8rem; color: #64748b;'><i>(Vui lòng sao chép chính xác nội dung trên khi chuyển khoản)</i></p>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with col_right:
            # Biểu đồ Gauge
            target = phai_dong if phai_dong > 0 else 1
            percent = min(round((da_dong / target) * 100, 1), 100)
            
            fig = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = percent,
                title = {'text': "Tiến độ hoàn thành", 'font': {'size': 20, 'color': '#64748b'}},
                number = {'suffix': "%", 'font': {'size': 40, 'color': '#2563eb'}},
                gauge = {
                    'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#cbd5e1"},
                    'bar': {'color': "#2563eb"},
                    'bgcolor': "white",
                    'borderwidth': 2,
                    'bordercolor': "#e2e8f0",
                    'steps': [
                        {'range': [0, 50], 'color': "#fee2e2"},
                        {'range': [50, 90], 'color': "#fef9c3"},
                        {'range': [90, 100], 'color': "#dcfce7"}]
                }
            ))
            fig.update_layout(height=350, margin=dict(l=30, r=30, t=50, b=20), paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)
            
            # QR Code
            qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=BHXH_PAY_{unit_data.get('madvi')}_{debt}"
            st.markdown(f"""
            <center>
                <div style='background:white; padding:15px; border-radius:25px; box-shadow:0 10px 25px rgba(0,0,0,0.1); display:inline-block;'>
                    <img src='{qr_url}' width='180'>
                </div>
                <p style='margin-top:15px; color:#64748b; font-weight:600;'>Quét mã để nộp tiền nhanh</p>
            </center>
            """, unsafe_allow_html=True)
            
            if st.button("🎉 Hoàn tất tra cứu", use_container_width=True):
                st.balloons()

# --- FOOTER ---
st.markdown("<br><hr><center style='color:#94a3b8; font-size:0.85rem; padding-bottom:30px;'>© 2024 Cổng Thông tin BHXH Thuận An Dashboard v6.0<br>Hệ thống tự động vận hành bởi Python AI</center>", unsafe_allow_html=True)