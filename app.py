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
    page_title="BHXH Thuận An - Cổng Tra cứu Thông minh v7.0",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- KHỞI TẠO TRẠNG THÁI HỆ THỐNG ---
if 'selected_unit' not in st.session_state:
    st.session_state.selected_unit = None
if 'last_query' not in st.session_state:
    st.session_state.last_query = ""
if 'loading_done' not in st.session_state:
    st.session_state.loading_done = False

# --- PHONG CÁCH THIẾT KẾ (CSS NÂNG CAO) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;700;800&display=swap');
    
    :root {
        --primary-color: #2563eb;
        --secondary-color: #1e40af;
        --bg-color: #f8fafc;
        --card-bg: rgba(255, 255, 255, 0.95);
    }

    * { font-family: 'Plus Jakarta Sans', sans-serif; }
    
    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
    }
    
    /* Panel chứa thông tin Dashboard */
    .dashboard-panel {
        background: var(--card-bg);
        border: 1px solid rgba(255, 255, 255, 0.7);
        border-radius: 40px;
        padding: 45px;
        box-shadow: 0 30px 60px -12px rgba(0,0,0,0.1);
        margin-bottom: 25px;
    }

    /* Thanh tìm kiếm trung tâm */
    .stTextInput input {
        border-radius: 50px !important;
        padding: 1.6rem 2.8rem !important;
        border: 2px solid #cbd5e1 !important;
        background: white !important;
        font-size: 1.3rem !important;
        box-shadow: 0 10px 20px rgba(0,0,0,0.03) !important;
        transition: all 0.3s ease;
    }
    
    .stTextInput input:focus {
        border-color: var(--primary-color) !important;
        box-shadow: 0 0 0 5px rgba(37, 99, 235, 0.1) !important;
    }
    
    /* Thẻ kết quả tìm kiếm */
    .unit-selector-card {
        background: white;
        padding: 28px;
        border-radius: 28px;
        border: 1px solid #e2e8f0;
        margin-bottom: 18px;
        border-left: 10px solid #cbd5e1;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer;
    }
    .unit-selector-card:hover {
        transform: translateY(-5px);
        border-left-color: var(--primary-color);
        box-shadow: 0 20px 35px -5px rgba(0,0,0,0.1);
    }

    /* Tiêu đề lớn */
    .main-title {
        background: linear-gradient(90deg, #1e3a8a, #2563eb);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 4.5rem;
        font-weight: 800;
        letter-spacing: -4px;
        margin-bottom: 0px;
        line-height: 1;
    }
    
    .sub-title {
        color: #64748b;
        font-size: 1.3rem;
        font-weight: 500;
        margin-bottom: 4rem;
    }

    /* Card số liệu Metric */
    .metric-container {
        background: #ffffff;
        padding: 24px;
        border-radius: 24px;
        border: 1px solid #f1f5f9;
        text-align: center;
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.02);
    }
    
    [data-testid="stMetricValue"] {
        font-weight: 800 !important;
        color: #1e293b !important;
    }

    /* Button thiết kế riêng */
    .stButton>button {
        border-radius: 50px !important;
        font-weight: 800 !important;
        padding: 12px 30px !important;
        transition: all 0.3s ease !important;
    }

    /* Nội dung nộp tiền chuyên nghiệp */
    .transfer-box {
        background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
        padding: 35px;
        border-radius: 30px;
        border: 2px dashed #2563eb;
        margin-top: 25px;
        position: relative;
    }
    </style>
    """, unsafe_allow_html=True)

# --- HÀM TẢI DỮ LIỆU ---
@st.cache_data
def load_data(uploaded_file=None):
    df = None
    try:
        # Tìm file c12 trong thư mục hiện tại
        current_files = [f for f in os.listdir('.') if f.lower().startswith('c12')]
        
        if uploaded_file is not None:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
        elif current_files:
            target_file = current_files[0]
            if target_file.lower().endswith('.csv'):
                df = pd.read_csv(target_file)
            else:
                df = pd.read_excel(target_file)
        
        if df is not None:
            # Chuẩn hóa tên cột: bỏ dấu, viết thường, thay dấu cách bằng gạch dưới
            # Đây là bước quan trọng để Python đọc được các cột Tiền đầu kỳ, Tỷ lệ nợ...
            df.columns = [unidecode(str(c)).lower().strip().replace(' ', '_') for c in df.columns]
            
            # Đảm bảo cột mã đơn vị là chuỗi
            if 'madvi' in df.columns:
                df['madvi'] = df['madvi'].astype(str).str.strip()
            
            # Tạo chỉ mục tìm kiếm tổng hợp
            df['search_index'] = df.apply(lambda x: unidecode(str(x.get('madvi', '')) + " " + str(x.get('tendvi', ''))).lower(), axis=1)
            return df
    except Exception as e:
        st.error(f"⚠️ Không thể xử lý file dữ liệu. Vui lòng kiểm tra lại định dạng file: {e}")
    return None

# --- GIAO DIỆN HEADER ---
st.markdown("<div style='text-align:center'><h1 class='main-title'>💎 Smart BHXH Hub</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>Hệ thống tra cứu thông báo đóng BHXH dành cho Đơn vị v7.0</p></div>", unsafe_allow_html=True)

df = load_data()

# KIỂM TRA DỮ LIỆU ĐẦU VÀO
if df is None:
    st.info("👋 Chào bạn! Hệ thống chưa nhận được dữ liệu. Vui lòng tải file C12 lên để kích hoạt.")
    uploaded = st.file_uploader("Tải file dữ liệu (.xls, .xlsx, .csv)", type=['xls', 'xlsx', 'csv'])
    if uploaded:
        df = load_data(uploaded)
        if df is not None: 
            st.success("✅ Đã nhận dữ liệu thành công!")
            st.rerun()

# --- XỬ LÝ LOGIC HIỂN THỊ CHÍNH ---
if df is not None:
    # MÀN HÌNH 1: TÌM KIẾM ĐƠN VỊ
    if st.session_state.selected_unit is None:
        st.markdown("### 🏢 Nhập Tên đơn vị hoặc Mã đơn vị để bắt đầu")
        query = st.text_input("Search", placeholder="Ví dụ: gõ 'dak', 'daknoco', 'TC0243'...", label_visibility="collapsed")
        
        if query:
            clean_query = unidecode(query).lower()
            results = df[df['search_index'].str.contains(clean_query, na=False)].head(10)

            if not results.empty:
                st.write(f"🔍 Tìm thấy **{len(results)}** đơn vị phù hợp. Vui lòng nhấn vào đơn vị của bạn:")
                for _, row in results.iterrows():
                    with st.container():
                        c1, c2 = st.columns([5, 1.5])
                        with c1:
                            st.markdown(f"""
                            <div class="unit-selector-card">
                                <span style="color:#2563eb; font-weight:800; font-size:0.95rem;">MÃ ĐƠN VỊ: {row.get('madvi', 'N/A')}</span><br>
                                <b style="font-size:1.35rem; color:#1e293b;">{row.get('tendvi', 'N/A')}</b>
                            </div>
                            """, unsafe_allow_html=True)
                        with c2:
                            st.write("<div style='height:28px'></div>", unsafe_allow_html=True)
                            if st.button(f"Xác nhận đơn vị này ➔", key=f"sel_{row.get('madvi')}_{_}", use_container_width=True):
                                # HIỆU ỨNG LOADING CHUYÊN NGHIỆP TRƯỚC KHI CHUYỂN TRANG
                                with st.empty():
                                    for percent_complete in range(100):
                                        time.sleep(0.01)
                                    st.write("✔️ Đang tải báo cáo...")
                                
                                with st.status("🛠️ Đang xử lý dữ liệu đơn vị...", expanded=True) as status:
                                    st.write("Đang kết nối hệ thống BHXH...")
                                    time.sleep(0.4)
                                    st.write("Đang trích xuất các cột số liệu...")
                                    time.sleep(0.4)
                                    st.write("Đang khởi tạo Dashboard cá nhân...")
                                    time.sleep(0.4)
                                    status.update(label="Vui lòng chờ trong giây lát...", state="complete", expanded=False)
                                
                                st.session_state.selected_unit = row.get('madvi')
                                st.rerun()
            else:
                st.error("😢 Xin lỗi, chúng tôi không tìm thấy đơn vị nào khớp với từ khóa trên.")
        else:
            st.markdown("<br><br><center><img src='https://cdn-icons-png.flaticon.com/512/3772/3772274.png' width='160' style='opacity:0.2'><p style='color:#94a3b8; font-size:1.1rem;'>Dữ liệu được cập nhật mới nhất từ cơ quan BHXH</p></center>", unsafe_allow_html=True)

    # MÀN HÌNH 2: DASHBOARD CHI TIẾT (XÓA BỎ TÌM KIẾM)
    else:
        unit_data = df[df['madvi'] == st.session_state.selected_unit].iloc[0]
        
        # Thanh điều hướng Back
        if st.button("⬅ Tìm đơn vị khác", type="secondary"):
            st.session_state.selected_unit = None
            st.rerun()

        st.markdown(f"""
        <div style='background:white; padding:40px; border-radius:35px; border-left:12px solid #2563eb; margin-top:20px; box-shadow:0 15px 40px rgba(0,0,0,0.06);'>
            <h1 style='margin:0; color:#1e3a8a; font-size:2.8rem;'>🏢 {unit_data.get('tendvi')}</h1>
            <p style='margin:8px 0 0 0; color:#64748b; font-size:1.2rem;'><b>Mã đơn vị:</b> {unit_data.get('madvi')} | <b>Đại diện:</b> {unit_data.get('nguoilh', 'N/A')}</p>
        </div>
        """, unsafe_allow_html=True)
        
        col_main, col_gauge = st.columns([1.8, 1])
        
        with col_main:
            st.markdown("<div class='dashboard-panel'>", unsafe_allow_html=True)
            st.write("### 📊 Chi tiết thông báo kết quả đóng BHXH")
            
            # --- HIỂN THỊ TẤT CẢ SỐ LIỆU TỪ FILE ---
            # Sử dụng các tên cột đã chuẩn hóa
            val_dau = unit_data.get('tien_dau_ky', 0)
            val_phai_dong = unit_data.get('so_phai_dong', 0)
            val_dieu_chinh = unit_data.get('dieu_chinh_ky_truoc', 0)
            val_da_dong = unit_data.get('so_da_dong', 0)
            val_lech = unit_data.get('so_bi_lech', 0)
            val_cuoi = unit_data.get('tien_cuoi_ky', 0)
            val_tyleno = unit_data.get('tyleno', 0)
            
            # Dòng 1: Các chỉ số cơ bản
            m1, m2, m3 = st.columns(3)
            m1.metric("Tiền đầu kỳ", f"{val_dau:,.0f}đ")
            m2.metric("Số phải đóng", f"{val_phai_dong:,.0f}đ")
            m3.metric("Điều chỉnh kỳ trước", f"{val_dieu_chinh:,.0f}đ")
            
            st.write("<br>", unsafe_allow_html=True)
            
            # Dòng 2: Kết quả thực hiện
            m4, m5, m6 = st.columns(3)
            m4.metric("Số đã đóng", f"{val_da_dong:,.0f}đ")
            m5.metric("Số bị lệch", f"{val_lech:,.0f}đ", delta_color="off")
            
            label_cuoi = "Tiền cuối kỳ (Nợ)" if val_cuoi > 0 else "Tiền cuối kỳ (Dư)"
            m6.metric(label_cuoi, f"{abs(val_cuoi):,.0f}đ", delta=-val_cuoi, delta_color="inverse")

            st.write("<br>", unsafe_allow_html=True)
            
            # Dòng 3: Tỷ lệ
            st.markdown(f"**Tỷ lệ nợ hiện tại:** `{val_tyleno}%`")
            st.progress(min(float(val_tyleno / 100), 1.0) if val_tyleno > 0 else 0.0)

            st.markdown("---")
            st.write("📍 **Địa chỉ:**", unit_data.get('diachi', 'N/A'))
            st.write("📞 **Điện thoại:**", unit_data.get('dienthoai', 'N/A'))
            
            # --- CÚ PHÁP NỘP TIỀN CHUẨN THỜI GIAN THỰC ---
            now = datetime.now()
            current_month = now.strftime("%m")
            current_year = now.strftime("%Y")
            
            transfer_text = f"{unit_data.get('madvi')} {unit_data.get('tendvi')} đóng bhxh tháng {current_month} năm {current_year}"
            
            st.markdown(f"""
            <div class="transfer-box">
                <p style='margin:0; font-size: 0.95rem; color: #1e40af; font-weight: 800; text-transform: uppercase;'>Cú pháp chuyển khoản nộp tiền:</p>
                <h2 style='margin:15px 0; color: #1e3a8a; font-family: monospace; line-height:1.4;'>{transfer_text}</h2>
                <p style='margin:0; font-size: 0.85rem; color: #64748b;'><i>(Lưu ý: Đơn vị vui lòng ghi đúng cú pháp trên để hệ thống tự động ghi nhận tiền đóng)</i></p>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with col_gauge:
            # Biểu đồ Gauge hoàn thành
            target_calc = val_phai_dong if val_phai_dong > 0 else 1
            completion_rate = min(round((val_da_dong / target_calc) * 100, 1), 100)
            
            fig = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = completion_rate,
                title = {'text': "Tiến độ hoàn thành đóng BHXH", 'font': {'size': 20, 'color': '#64748b'}},
                number = {'suffix': "%", 'font': {'size': 50, 'color': '#2563eb'}},
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
            fig.update_layout(height=400, margin=dict(l=35, r=35, t=60, b=25), paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)
            
            # QR Code thanh toán nhanh
            qr_data = f"BHXH_THUANAN|{unit_data.get('madvi')}|{val_cuoi}"
            qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=350x350&data={qr_data}&color=1e3a8a"
            st.markdown(f"""
            <center>
                <div style='background:white; padding:20px; border-radius:30px; box-shadow:0 15px 35px rgba(0,0,0,0.1); display:inline-block;'>
                    <img src='{qr_url}' width='200'>
                </div>
                <p style='margin-top:20px; color:#1e3a8a; font-weight:800; font-size:1.1rem;'>QUÉT MÃ NỘP TIỀN NHANH</p>
                <p style='color:#64748b; font-size:0.8rem;'>Tự động tích hợp thông tin nợ và mã đơn vị</p>
            </center>
            """, unsafe_allow_html=True)
            
            if st.button("🌟 Hoàn thành tra cứu", use_container_width=True):
                st.balloons()

# --- FOOTER ---
st.markdown("<br><hr><center style='color:#94a3b8; font-size:0.9rem; padding-bottom:40px;'>© 2026 Hệ thống Dashboard BHXH Thuận An - Phiên bản Platinum v7.0<br>Được phát triển với công nghệ Python & AI thông minh</center>", unsafe_allow_html=True)