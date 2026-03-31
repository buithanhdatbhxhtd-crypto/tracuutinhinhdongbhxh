import streamlit as st
import pandas as pd
import numpy as np

# --- CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="BHXH Thuận An - Tra cứu C12",
    page_icon="🏥",
    layout="centered"
)

# --- CSS TÙY CHỈNH ĐỂ GIỐNG GIAO DIỆN PREMIUM ---
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
    }
    .qr-container {
        display: flex;
        justify-content: center;
        padding: 20px;
        background: white;
        border-radius: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- HÀM TẢI DỮ LIỆU ---
@st.cache_data
def load_data():
    try:
        # Đọc file CSV bạn đã cung cấp
        df = pd.read_csv('C12_CHI_TIEU 27-3.xls - 06703.csv')
        # Đảm bảo mã đơn vị là chuỗi để tìm kiếm chính xác
        df['madvi'] = df['madvi'].astype(str).str.strip()
        return df
    except Exception as e:
        st.error(f"Không tìm thấy file dữ liệu hoặc lỗi định dạng: {e}")
        return None

df = load_data()

# --- GIAO DIỆN CHÍNH ---
st.title("🏥 Tra cứu kết quả đóng BHXH")
st.markdown("Vui lòng nhập **Mã đơn vị** để xem thông báo kết quả đóng (Mẫu C12-TS).")

# Ô tìm kiếm
search_code = st.text_input("🔍 Nhập mã đơn vị (VD: CC0001C, TC0243C...):", placeholder="Gõ mã vào đây...").strip()

if search_code:
    if df is not None:
        # Tìm kiếm đơn vị
        result = df[df['madvi'].str.upper() == search_code.upper()]
        
        if not result.empty:
            row = result.iloc[0]
            
            st.success(f"Đã tìm thấy dữ liệu cho đơn vị: **{row['tendvi']}**")
            
            # Hiển thị thông tin chung
            with st.container():
                st.markdown(f"""
                <div class="unit-card">
                    <h3 style='color: #1e3a8a; margin-top:0;'>🏢 {row['tendvi']}</h3>
                    <p>📍 <b>Địa chỉ:</b> {row['diachi']}</p>
                    <p>📞 <b>Điện thoại:</b> {row['dienthoai']} | 👤 <b>Liên hệ:</b> {row['nguoilh']}</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Chỉ số tài chính
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Tiền đầu kỳ", f"{row['tiền đầu kỳ']:,.0f} đ")
            with col2:
                st.metric("Số phải đóng", f"{row['số phải đóng']:,.0f} đ")
            with col3:
                st.metric("Số đã đóng", f"{row['số đã đóng']:,.0f} đ", delta=f"{row['số đã đóng'] - row['số phải đóng']:,.0f}")
                
            col4, col5, col6 = st.columns(3)
            with col4:
                # Tiền cuối kỳ (Nợ) - Nếu > 0 là nợ, dùng màu đỏ
                st.metric("Tiền cuối kỳ", f"{row['tiền cuối kỳ']:,.0f} đ", delta_color="inverse")
            with col5:
                st.metric("Số bị lệch", f"{row['số bị lệch']:,.0f} đ")
            with col6:
                st.metric("Tỷ lệ nợ", f"{row['tyleno']}%")

            st.divider()
            
            # Phần QR Code và Thanh toán
            c_left, c_right = st.columns([1, 1])
            
            with c_left:
                st.subheader("💳 Thông tin thanh toán")
                payment_note = f"BHXH {row['madvi']} {row['tendvi']}"
                st.info(f"**Nội dung chuyển khoản:**\n\n`{payment_note}`")
                st.warning("⚠️ Vui lòng kiểm tra kỹ số tiền và nội dung trước khi chuyển khoản.")
                
            with c_right:
                st.subheader("📲 Quét mã QR")
                # Tạo URL QR Code giống bản HTML (sử dụng API QRServer)
                qr_data = f"BHXH:{row['madvi']}|SO_TIEN:{row['tiền cuối kỳ']}"
                qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={qr_data}&color=1e3a8a"
                
                st.markdown(f"""
                <div class="qr-container">
                    <img src="{qr_url}" width="200">
                </div>
                """, unsafe_allow_html=True)
                st.caption("Quét mã để lấy thông tin đơn vị và số tiền nợ.")
                
            if st.button("🎉 Xác nhận hoàn tất tra cứu"):
                st.balloons()
                
        else:
            st.error(f"Không tìm thấy mã đơn vị '{search_code}'. Vui lòng kiểm tra lại.")
    else:
        st.warning("Hệ thống chưa có dữ liệu. Vui lòng kiểm tra file CSV.")

# --- FOOTER ---
st.markdown("---")
st.caption("© 2024 BHXH Thuận An | Hệ thống tra cứu tự động v2.0 (Streamlit)")