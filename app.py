import streamlit as st
import pandas as pd
import numpy as np
import os

# --- CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="BHXH Thuận An - Tra cứu C12",
    page_icon="🏥",
    layout="centered"
)

# --- CSS TÙY CHỈNH CHO GIAO DIỆN HIỆN ĐẠI ---
st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .unit-card {
        background-color: white;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        border-left: 10px solid #1e3a8a;
    }
    .qr-container {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 20px;
        background: white;
        border-radius: 20px;
        border: 2px dashed #1e3a8a;
    }
    .stButton>button {
        background-color: #1e3a8a;
        color: white;
        border-radius: 10px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- HÀM TẢI DỮ LIỆU TỪ EXCEL (XLS/XLSX) ---
@st.cache_data
def load_data():
    # Tên file mặc định theo yêu cầu của bạn
    file_path = 'c12.xls'
    
    # Kiểm tra file tồn tại
    if not os.path.exists(file_path):
        if os.path.exists('c12.xlsx'):
            file_path = 'c12.xlsx'
        else:
            st.warning("⚠️ Đang chờ file dữ liệu 'c12.xls'...")
            return None
    
    try:
        # Đọc file Excel
        df = pd.read_excel(file_path)
        
        # Làm sạch tên cột
        df.columns = df.columns.astype(str).str.strip()
        
        # Chuyển mã đơn vị về dạng chuỗi để tìm kiếm chính xác
        if 'madvi' in df.columns:
            df['madvi'] = df['madvi'].astype(str).str.strip()
            
        return df
    except Exception as e:
        st.error(f"❌ Lỗi khi đọc file: {e}")
        return None

df = load_data()

# --- GIAO DIỆN NGƯỜI DÙNG ---
st.title("🏥 Tra cứu kết quả đóng BHXH")
st.info("Hệ thống hỗ trợ đơn vị tra cứu thông báo kết quả đóng bảo hiểm (Mẫu C12-TS).")

# Ô nhập liệu tìm kiếm
search_code = st.text_input("🔍 Nhập Mã đơn vị cần tra cứu:", placeholder="Ví dụ: TC0243C...").strip()

if search_code:
    if df is not None:
        # Tìm kiếm không phân biệt hoa thường
        result = df[df['madvi'].str.upper() == search_code.upper()]
        
        if not result.empty:
            row = result.iloc[0]
            st.balloons()
            
            # 1. Thẻ thông tin đơn vị
            st.markdown(f"""
            <div class="unit-card">
                <h2 style='color: #1e3a8a; margin-top:0;'>🏢 {row.get('tendvi', 'N/A')}</h2>
                <p style='font-size: 1.1em;'>📍 <b>Địa chỉ:</b> {row.get('diachi', 'N/A')}</p>
                <p>📞 <b>Điện thoại:</b> {row.get('dienthoai', 'N/A')} | 👤 <b>Người liên hệ:</b> {row.get('nguoilh', 'N/A')}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # 2. Các chỉ số tài chính (Metrics)
            st.subheader("📊 Số liệu đóng BHXH")
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("Tiền đầu kỳ", f"{row.get('tiền đầu kỳ', 0):,.0f} đ")
            with c2:
                st.metric("Số phải đóng", f"{row.get('số phải đóng', 0):,.0f} đ")
            with c3:
                da_dong = row.get('số đã đóng', 0)
                phai_dong = row.get('số phải đóng', 0)
                st.metric("Số đã đóng", f"{da_dong:,.0f} đ", delta=f"{da_dong - phai_dong:,.0f}")
            
            c4, c5, c6 = st.columns(3)
            with c4:
                cuoi_ky = row.get('tiền cuối kỳ', 0)
                label = "Tiền cuối kỳ (Nợ)" if cuoi_ky > 0 else "Tiền cuối kỳ (Dư)"
                st.metric(label, f"{abs(cuoi_ky):,.0f} đ", delta_color="inverse")
            with c5:
                st.metric("Số bị lệch", f"{row.get('số bị lệch', 0):,.0f} đ")
            with c6:
                st.metric("Tỷ lệ nợ", f"{row.get('tyleno', 0)}%")
                
            st.divider()
            
            # 3. QR Code và Hướng dẫn thanh toán
            col_left, col_right = st.columns([1, 1])
            
            with col_left:
                st.subheader("💳 Hướng dẫn nộp tiền")
                noi_dung = f"BHXH {row['madvi']} {row.get('tendvi', '')}"
                st.code(noi_dung, language="text")
                st.caption("Sao chép nội dung trên để thực hiện chuyển khoản chính xác.")
                st.warning("Ghi chú: Đơn vị vui lòng nộp tiền trước ngày 25 hàng tháng.")
                
            with col_right:
                st.subheader("📲 Quét mã nhanh")
                # Tạo mã QR chứa thông tin đơn vị và số tiền nợ
                qr_info = f"BHXH_THUANAN|DVI:{row['madvi']}|TIEN:{row.get('tiền cuối kỳ', 0)}"
                qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={qr_info}&color=1e3a8a"
                
                st.markdown(f"""
                <div class="qr-container">
                    <img src="{qr_url}" width="180" title="Quét mã để tra cứu nhanh">
                </div>
                """, unsafe_allow_html=True)

        else:
            st.error(f"❌ Không tìm thấy thông tin cho mã đơn vị: **{search_code}**")
    else:
        st.warning("Dữ liệu đang được cập nhật, vui lòng quay lại sau.")

# --- FOOTER ---
st.markdown("<br><hr>", unsafe_allow_html=True)
st.markdown("<center style='color: #666;'>© 2024 BHXH Thuận An - Hệ thống tra cứu trực tuyến thông minh</center>", unsafe_allow_html=True)
