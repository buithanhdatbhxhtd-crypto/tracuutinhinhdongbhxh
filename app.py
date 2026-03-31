import streamlit as st
import pandas as pd
import numpy as np
import os
import plotly.graph_objects as go
from unidecode import unidecode

# --- CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="BHXH Thuận An - Digital Dashboard",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- KHỞI TẠO STATE (Để tránh lỗi KeyError và lưu trạng thái tìm kiếm) ---
if 'selected_unit' not in st.session_state:
    st.session_state.selected_unit = None
if 'search_query' not in st.session_state:
    st.session_state.search_query = ""

# --- TỔNG LỰC CSS (UI/UX TRẢI NGHIỆM NGƯỜI DÙNG) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');
    
    * { font-family: 'Plus Jakarta Sans', sans-serif; }
    
    .stApp { background-color: #f4f7fa; }
    
    /* Thanh tìm kiếm trung tâm */
    .stTextInput input {
        border-radius: 24px !important;
        padding: 1.5rem 2.5rem !important;
        border: 2px solid #e2e8f0 !important;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05) !important;
        font-size: 1.25rem !important;
        transition: all 0.3s ease;
    }
    .stTextInput input:focus {
        border-color: #2563eb !important;
        box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.1) !important;
    }
    
    /* Thẻ gợi ý (Suggestion Cards) */
    .suggestion-card {
        background: white;
        padding: 24px;
        border-radius: 24px;
        border: 1px solid #e2e8f0;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        margin-bottom: 15px;
        position: relative;
        overflow: hidden;
    }
    .suggestion-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 20px 30px -10px rgba(0, 0, 0, 0.1);
        border-color: #2563eb;
    }

    /* Thẻ nội dung chính */
    .main-card {
        background: white;
        padding: 45px;
        border-radius: 35px;
        box-shadow: 0 30px 60px -12px rgba(0, 0, 0, 0.08);
        border: 1px solid #ffffff;
        margin-top: 2.5rem;
    }

    /* Chữ tiêu đề */
    .main-title {
        background: linear-gradient(90deg, #1e3a8a, #2563eb);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 3.5rem;
    }
    
    h1, h2, h3 { color: #0f172a; letter-spacing: -0.03em; }

    /* Button Styling */
    .stButton>button {
        border-radius: 15px;
        font-weight: 600;
        text-transform: none;
        padding: 0.5rem 1rem;
        transition: all 0.2s;
    }
    </style>
    """, unsafe_allow_html=True)

# --- HÀM XỬ LÝ DỮ LIỆU ---
@st.cache_data
def load_data():
    file_path = 'c12.xls'
    # Ưu tiên kiểm tra file .xls sau đó đến .xlsx
    if not os.path.exists(file_path):
        if os.path.exists('c12.xlsx'):
            file_path = 'c12.xlsx'
        else:
            return None
    try:
        df = pd.read_excel(file_path)
        df.columns = df.columns.astype(str).str.strip()
        # Chuẩn hóa cột tìm kiếm (không dấu, viết thường)
        df['search_index'] = (df['madvi'].astype(str) + " " + df['tendvi'].astype(str)).apply(lambda x: unidecode(str(x)).lower())
        return df
    except Exception as e:
        st.error(f"Lỗi đọc file: {e}")
        return None

df = load_data()

# --- GIAO DIỆN HEADER ---
st.markdown("<div style='text-align: center; margin-bottom: 2rem;'><h1 class='main-title'>💎 Smart BHXH Hub</h1></div>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #64748b; font-size: 1.2rem; margin-top: -1.5rem; margin-bottom: 3rem;'>Hệ thống tra cứu thông báo đóng bảo hiểm thế hệ mới</p>", unsafe_allow_html=True)

# --- CÔNG CỤ TÌM KIẾM ---
c_search_box, _ = st.columns([2, 1])
with c_search_box:
    query = st.text_input("Tìm kiếm", placeholder="🔍 Nhập tên công ty hoặc mã đơn vị (VD: dak, TC02...)", label_visibility="collapsed")

# Logic xử lý: Khi thay đổi từ khóa thì reset đơn vị đã chọn
if query != st.session_state.search_query:
    st.session_state.selected_unit = None
    st.session_state.search_query = query

if df is not None:
    if query:
        # Chuẩn hóa từ khóa
        clean_query = unidecode(query).lower()
        # Lọc dữ liệu
        results = df[df['search_index'].str.contains(clean_query, na=False)].head(6)

        if not results.empty:
            st.markdown(f"✨ Tìm thấy **{len(results)}** đơn vị phù hợp:")
            
            # Hiển thị Suggestions Grid
            cols = st.columns(3)
            for idx, (original_idx, row) in enumerate(results.iterrows()):
                with cols[idx % 3]:
                    # Card gợi ý
                    st.markdown(f"""
                    <div class="suggestion-card">
                        <div style="color: #2563eb; font-weight: 800; font-size: 0.85rem; margin-bottom: 5px;">{row['madvi']}</div>
                        <div style="font-weight: 700; color: #1e293b; font-size: 1rem; line-height: 1.4;">{row['tendvi'][:50]}...</div>
                    </div>
                    """, unsafe_allow_html=True)
                    # Nút chọn đơn vị
                    if st.button(f"🔎 Xem chi tiết {row['madvi']}", key=f"btn_{row['madvi']}", use_container_width=True):
                        st.session_state.selected_unit = row['madvi']
                        st.rerun()

            # Hiển thị thông tin chi tiết
            active_unit = st.session_state.get('selected_unit')
            if active_unit:
                unit_data = df[df['madvi'] == active_unit].iloc[0]
                
                st.markdown("<div class='main-card'>", unsafe_allow_html=True)
                col_left, col_right = st.columns([1.6, 1])
                
                with col_left:
                    st.markdown(f"<h2 style='color: #1e3a8a; margin-top:0;'>🏢 {unit_data['tendvi']}</h2>", unsafe_allow_html=True)
                    st.markdown(f"📍 **Địa chỉ:** {unit_data.get('diachi', 'Chưa cập nhật')}")
                    st.markdown(f"👤 **Đại diện:** {unit_data.get('nguoilh', 'N/A')} | 📞 **SĐT:** {unit_data.get('dienthoai', 'N/A')}")
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    # Metrics
                    m_col1, m_col2 = st.columns(2)
                    with m_col1:
                        st.metric("Tiền đầu kỳ", f"{unit_data.get('tiền đầu kỳ', 0):,.0f} đ")
                        st.metric("Số phải đóng", f"{unit_data.get('số phải đóng', 0):,.0f} đ")
                    with m_col2:
                        da_dong = unit_data.get('số đã đóng', 0)
                        phai_dong = unit_data.get('số phải đóng', 0)
                        st.metric("Số đã đóng", f"{da_dong:,.0f} đ", delta=f"{da_dong - phai_dong:,.0f}")
                        
                        debt_val = unit_data.get('tiền cuối kỳ', 0)
                        label_debt = "Còn nợ (Cuối kỳ)" if debt_val > 0 else "Dư có (Cuối kỳ)"
                        st.metric(label_debt, f"{abs(debt_val):,.0f} đ", delta=-debt_val, delta_color="inverse")

                    # Nội dung chuyển khoản
                    st.markdown(f"""
                    <div style='background: #f0f7ff; padding: 30px; border-radius: 25px; border: 2px dashed #2563eb; margin-top: 1.5rem;'>
                        <p style='margin:0; font-size: 0.9rem; color: #1e40af; font-weight: 700; text-transform: uppercase;'>Nội dung chuyển khoản mẫu:</p>
                        <code style='font-size: 1.3rem; color: #1e3a8a; font-weight: 800; background: transparent;'>BHXH {unit_data['madvi']} {unit_data['tendvi']}</code>
                    </div>
                    """, unsafe_allow_html=True)

                with col_right:
                    # Biểu đồ Gauge
                    comp_rate = (da_dong / phai_dong * 100) if phai_dong > 0 else 0
                    
                    fig = go.Figure(go.Indicator(
                        mode = "gauge+number",
                        value = comp_rate,
                        title = {'text': "Tỷ lệ hoàn thành", 'font': {'size': 20, 'color': '#64748b'}},
                        number = {'suffix': "%", 'font': {'color': '#1e293b'}},
                        gauge = {
                            'axis': {'range': [0, 100], 'tickwidth': 1},
                            'bar': {'color': "#2563eb"},
                            'bgcolor': "#f1f5f9",
                            'steps': [
                                {'range': [0, 50], 'color': '#fee2e2'},
                                {'range': [50, 90], 'color': '#fef9c3'},
                                {'range': [90, 100], 'color': '#dcfce7'}],
                        }
                    ))
                    fig.update_layout(height=350, margin=dict(l=30, r=30, t=50, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Nút tải báo cáo
                    st.download_button(
                        label="📥 Tải thông tin đơn vị (CSV)",
                        data=unit_data.to_csv().encode('utf-8-sig'),
                        file_name=f"BHXH_{unit_data['madvi']}.csv",
                        mime='text/csv',
                        use_container_width=True
                    )
                    
                    if st.button("🎉 Hoàn tất tra cứu", use_container_width=True):
                        st.balloons() # Đã sửa từ st.confetti() sang st.balloons()
                
                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.error("😢 Không tìm thấy đơn vị nào phù hợp. Thử từ khóa khác nhé!")
    else:
        # Giao diện khi chưa tìm kiếm
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown("<center><img src='https://cdn-icons-png.flaticon.com/512/3772/3772274.png' width='140' style='opacity: 0.5;'><p style='color:#94a3b8; font-size: 1.2rem; margin-top: 1.5rem;'>Bắt đầu bằng cách nhập thông tin vào ô tìm kiếm ở trên</p></center>", unsafe_allow_html=True)
else:
    st.error("Lỗi hệ thống: Không tìm thấy tệp dữ liệu c12.xls hoặc c12.xlsx.")

# --- FOOTER ---
st.markdown("<br><br><br><br><hr>", unsafe_allow_html=True)
st.caption("<center style='color: #94a3b8;'>Hệ thống Dashboard BHXH Thông minh v4.0 • Phát triển với Python & Streamlit</center>", unsafe_allow_html=True)
