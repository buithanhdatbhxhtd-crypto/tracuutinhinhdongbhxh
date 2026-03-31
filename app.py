import streamlit as st
import pandas as pd
import numpy as np
import os
from unidecode import unidecode

# --- CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="BHXH Thuận An - Smart Lookup",
    page_icon="⚡",
    layout="wide"
)

# --- CSS TÙY CHỈNH: Giao diện Modern & Clean ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif;
    }
    
    .main {
        background: #f8fafc;
    }
    
    /* Hiệu ứng Glassmorphism cho Card */
    .glass-card {
        background: white;
        padding: 30px;
        border-radius: 24px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -2px rgba(0, 0, 0, 0.02);
        border: 1px solid #f1f5f9;
        margin-bottom: 25px;
        border-left: 8px solid #3b82f6;
    }
    
    .status-badge {
        padding: 6px 12px;
        border-radius: 99px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 10px;
    }
    
    .status-ok { background: #dcfce7; color: #166534; }
    .status-debt { background: #fee2e2; color: #991b1b; }
    
    /* Tùy chỉnh Metrics */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
        font-weight: 800 !important;
        color: #1e293b;
    }
    
    /* Search Bar Input */
    .stTextInput input {
        border-radius: 15px !important;
        padding: 12px 20px !important;
        border: 2px solid #e2e8f0 !important;
        transition: all 0.3s ease;
        font-size: 1.1rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- HÀM TẢI DỮ LIỆU ---
@st.cache_data
def load_data():
    file_path = 'c12.xls'
    if not os.path.exists(file_path):
        if os.path.exists('c12.xlsx'):
            file_path = 'c12.xlsx'
        else:
            return None
    
    try:
        # Đọc file Excel
        df = pd.read_excel(file_path)
        df.columns = df.columns.astype(str).str.strip()
        
        # Tiền xử lý dữ liệu để tìm kiếm nhanh
        if 'madvi' in df.columns and 'tendvi' in df.columns:
            # Tạo cột tìm kiếm tổng hợp: Mã + Tên
            df['search_content'] = df['madvi'].astype(str) + " " + df['tendvi'].astype(str)
            # Tạo cột không dấu để tìm kiếm thông minh kiểu Google
            df['search_no_accent'] = df['search_content'].apply(lambda x: unidecode(str(x)).lower())
            
        return df
    except Exception:
        return None

df = load_data()

# --- GIAO DIỆN CHÍNH ---
col_head1, col_head2 = st.columns([2, 1])

with col_head1:
    st.title("🚀 BHXH Smart Search v3.0")
    st.markdown("Nhập tên hoặc mã đơn vị để tra cứu kết quả đóng BHXH.")

with col_head2:
    st.info("💡 **Mẹo:** Bạn có thể gõ tiếng Việt không dấu (vd: 'cong ty thuan an')")

# --- Ô TÌM KIẾM THÔNG MINH ---
search_query = st.text_input("", placeholder="🔍 Nhập tên đơn vị hoặc mã số...", label_visibility="collapsed")

if df is not None:
    if search_query:
        # Chuẩn hóa từ khóa tìm kiếm (bỏ dấu, viết thường)
        query_processed = unidecode(search_query).lower()
        
        # Lọc dữ liệu ngay lập tức (Search-as-you-type)
        filtered_df = df[df['search_no_accent'].str.contains(query_processed, na=False)]
        
        if not filtered_df.empty:
            # Nếu có nhiều kết quả, cho người dùng chọn
            if len(filtered_df) > 1:
                st.write(f"✨ Tìm thấy **{len(filtered_df)}** kết quả phù hợp:")
                list_options = filtered_df['madvi'] + " - " + filtered_df['tendvi']
                selection = st.selectbox("Chọn chính xác đơn vị của bạn:", list_options)
                selected_code = selection.split(" - ")[0]
                final_data = filtered_df[filtered_df['madvi'] == selected_code].iloc[0]
            else:
                final_data = filtered_df.iloc[0]
            
            st.divider()
            
            # --- HIỂN THỊ THÔNG TIN CHI TIẾT ---
            col_info, col_data = st.columns([1.2, 2])
            
            with col_info:
                debt_val = final_data.get('tiền cuối kỳ', 0)
                status_class = "status-debt" if debt_val > 0 else "status-ok"
                status_text = "⚠️ Còn nợ" if debt_val > 0 else "✅ Đã đóng đủ"
                
                st.markdown(f"""
                <div class="glass-card">
                    <span class="status-badge {status_class}">{status_text}</span>
                    <h2 style='color: #1e293b; margin: 10px 0;'>{final_data.get('tendvi', 'N/A')}</h2>
                    <p style='color: #64748b;'>Mã đơn vị: <b>{final_data.get('madvi', 'N/A')}</b></p>
                    <hr style='border: 0.5px solid #f1f5f9; margin: 20px 0;'>
                    <p>📍 {final_data.get('diachi', 'N/A')}</p>
                    <p>📞 {final_data.get('dienthoai', 'N/A')}</p>
                    <p>👤 LH: {final_data.get('nguoilh', 'N/A')}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # QR Code
                qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=BHXH_{final_data.get('madvi')}_{debt_val}&color=1e3a8a"
                st.markdown(f"""
                <div style='text-align: center; background: white; padding: 20px; border-radius: 20px; border: 1px solid #f1f5f9;'>
                    <img src="{qr_url}" width="160">
                    <p style='margin-top:10px; font-size: 0.8rem; color: #64748b;'>Quét mã nộp tiền nhanh</p>
                </div>
                """, unsafe_allow_html=True)

            with col_data:
                # Metrics tài chính
                c1, c2 = st.columns(2)
                with c1:
                    st.metric("Tiền đầu kỳ", f"{final_data.get('tiền đầu kỳ', 0):,.0f} đ")
                with c2:
                    st.metric("Số phải đóng", f"{final_data.get('số phải đóng', 0):,.0f} đ")
                
                c3, c4 = st.columns(2)
                with c3:
                    da_dong = final_data.get('số đã đóng', 0)
                    phai_dong = final_data.get('số phải đóng', 0)
                    st.metric("Số đã đóng", f"{da_dong:,.0f} đ", delta=f"{da_dong - phai_dong:,.0f}")
                with c4:
                    st.metric("Dư nợ cuối kỳ", f"{debt_val:,.0f} đ", delta_color="inverse")
                
                # Thanh tiến độ
                st.write("---")
                progress_val = 0
                if phai_dong > 0:
                    progress_val = min(float(da_dong / phai_dong), 1.0)
                st.write(f"**Tỷ lệ hoàn thành: {progress_val*100:.1f}%**")
                st.progress(progress_val)
                
                # Nội dung chuyển khoản
                st.markdown(f"""
                <div style='background: #f1f5f9; padding: 20px; border-radius: 15px; margin-top: 20px; border-left: 5px solid #3b82f6;'>
                    <p style='margin:0; font-size: 0.8rem; color: #64748b;'>NỘI DUNG CHUYỂN KHOẢN MẪU:</p>
                    <code style='font-size: 1.1rem; color: #1e3a8a;'>BHXH {final_data.get('madvi')} {final_data.get('tendvi')}</code>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("🎊 Xác nhận thông tin"):
                    st.balloons()
                    st.success("Thông tin đã được đơn vị ghi nhận!")

        else:
            st.error("😢 Không tìm thấy đơn vị nào khớp với từ khóa.")
    else:
        st.write("---")
        st.info("👋 Chào bạn! Hãy nhập tên hoặc mã số của đơn vị để bắt đầu tra cứu.")
else:
    st.error("❌ Không tìm thấy file dữ liệu 'c12.xls' trên server GitHub.")

st.markdown("---")
st.caption("<center>© 2026 BHXH Thuận An - Công cụ hỗ trợ chuyển đổi số</center>", unsafe_allow_html=True)
