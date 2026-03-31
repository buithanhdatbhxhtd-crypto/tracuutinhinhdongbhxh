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

# --- KHỞI TẠO STATE (Để tránh lỗi KeyError) ---
if 'selected_unit' not in st.session_state:
    st.session_state.selected_unit = None
if 'last_query' not in st.session_state:
    st.session_state.last_query = ""

# --- TỔNG LỰC CSS (UI/UX TRẢI NGHIỆM NGƯỜI DÙNG) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');
    
    * { font-family: 'Plus Jakarta Sans', sans-serif; }
    
    .stApp { background-color: #f8fafc; }
    
    /* Thanh tìm kiếm trung tâm */
    .stTextInput input {
        border-radius: 20px !important;
        padding: 1.5rem 2rem !important;
        border: 2px solid #e2e8f0 !important;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1) !important;
        font-size: 1.2rem !important;
        transition: all 0.3s ease;
    }
    .stTextInput input:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.15) !important;
    }
    
    /* Thẻ gợi ý (Suggestion Cards) */
    .suggestion-card {
        background: white;
        padding: 20px;
        border-radius: 20px;
        border: 1px solid #f1f5f9;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        margin-bottom: 15px;
        border-left: 6px solid #e2e8f0;
    }
    .suggestion-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
        border-left-color: #3b82f6;
    }

    /* Thẻ nội dung chính */
    .main-card {
        background: white;
        padding: 40px;
        border-radius: 32px;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.05);
        border: 1px solid #f1f5f9;
        margin-top: 2rem;
    }

    /* Metric Styling */
    .metric-container {
        background: #f1f5f9;
        padding: 24px;
        border-radius: 24px;
        text-align: center;
        border: 1px solid #e2e8f0;
    }
    
    .stMetric label { font-weight: 700 !important; color: #64748b !important; }
    
    h1, h2, h3 { color: #0f172a; font-weight: 800; letter-spacing: -0.02em; }
    </style>
    """, unsafe_allow_html=True)

# --- HÀM XỬ LÝ DỮ LIỆU ---
@st.cache_data
def load_data():
    file_path = 'c12.xls'
    if not os.path.exists(file_path):
        if os.path.exists('c12.xlsx'): file_path = 'c12.xlsx'
        else: return None
    try:
        df = pd.read_excel(file_path)
        df.columns = df.columns.astype(str).str.strip()
        # Chuẩn hóa tìm kiếm: Mã + Tên (Bỏ dấu)
        df['search_no_accent'] = (df['madvi'].astype(str) + " " + df['tendvi'].astype(str)).apply(lambda x: unidecode(str(x)).lower())
        return df
    except: return None

df = load_data()

# --- GIAO DIỆN HEADER ---
st.markdown("<h1 style='text-align: center; font-size: 3.5rem; margin-top: 2rem;'>💎 Smart BHXH Hub</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #64748b; font-size: 1.2rem; margin-bottom: 3rem;'>Tìm kiếm thông minh & Phân tích số liệu đóng bảo hiểm xã hội</p>", unsafe_allow_html=True)

# --- CÔNG CỤ TÌM KIẾM ---
c_search, _ = st.columns([2, 1])
with c_search:
    query = st.text_input("Tìm kiếm", placeholder="Gõ từ khóa (vd: 'dak', 'ket noi', 'TC024'...) để tìm nhanh", label_visibility="collapsed")

# Logic: Nếu gõ từ khóa mới, reset đơn vị đã chọn
if query != st.session_state.last_query:
    st.session_state.selected_unit = None
    st.session_state.last_query = query

if df is not None:
    if query:
        processed_query = unidecode(query).lower()
        results = df[df['search_no_accent'].str.contains(processed_query, na=False)].head(6)

        if not results.empty:
            st.markdown(f"🔍 Tìm thấy **{len(results)}** đơn vị phù hợp:")
            
            # Hiển thị Suggestions Grid
            cols = st.columns(3)
            for idx, (i, row) in enumerate(results.iterrows()):
                with cols[idx % 3]:
                    st.markdown(f"""
                    <div class="suggestion-card">
                        <span style="color: #3b82f6; font-weight: 800; font-size: 0.8rem;">{row['madvi']}</span>
                        <div style="font-weight: 700; color: #1e293b; margin: 8px 0;">{row['tendvi'][:45]}...</div>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"Chọn {row['madvi']}", key=f"btn_{row['madvi']}"):
                        st.session_state.selected_unit = row['madvi']
                        st.rerun()

            # Hiển thị thông tin chi tiết
            selected_unit_code = st.session_state.get('selected_unit')
            if selected_unit_code:
                final_data = df[df['madvi'] == selected_unit_code].iloc[0]
                
                st.markdown("<div class='main-card'>", unsafe_allow_html=True)
                col_left, col_right = st.columns([1.5, 1])
                
                with col_left:
                    st.markdown(f"<h2 style='color: #2563eb;'>🏢 {final_data['tendvi']}</h2>", unsafe_allow_html=True)
                    st.markdown(f"📍 **Địa chỉ:** {final_data.get('diachi', 'N/A')}")
                    st.markdown(f"👤 **Người liên hệ:** {final_data.get('nguoilh', 'N/A')} | 📞 {final_data.get('dienthoai', 'N/A')}")
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    m1, m2 = st.columns(2)
                    with m1:
                        st.metric("Số phải đóng", f"{final_data.get('số phải đóng', 0):,.0f} đ")
                    with m2:
                        st.metric("Số đã đóng", f"{final_data.get('số đã đóng', 0):,.0f} đ")
                    
                    m3, m4 = st.columns(2)
                    with m3:
                        debt = final_data.get('tiền cuối kỳ', 0)
                        st.metric("Nợ / Dư cuối kỳ", f"{debt:,.0f} đ", delta=-debt, delta_color="inverse")
                    with m4:
                        st.metric("Tỷ lệ nợ", f"{final_data.get('tyleno', 0)}%")

                    # Nội dung chuyển khoản
                    st.markdown(f"""
                    <div style='background: #eff6ff; padding: 25px; border-radius: 20px; border: 1px dashed #3b82f6; margin-top: 2rem;'>
                        <p style='margin:0; font-size: 0.9rem; color: #1e40af; font-weight: 600;'>CÚ PHÁP CHUYỂN KHOẢN:</p>
                        <code style='font-size: 1.3rem; color: #1e3a8a; font-weight: 800;'>BHXH {final_data['madvi']} {final_data['tendvi']}</code>
                    </div>
                    """, unsafe_allow_html=True)

                with col_right:
                    # Gauge Chart
                    phai_dong = final_data.get('số phải đóng', 0)
                    da_dong = final_data.get('số đã đóng', 0)
                    progress = (da_dong / phai_dong * 100) if phai_dong > 0 else 0
                    
                    fig = go.Figure(go.Indicator(
                        mode = "gauge+number",
                        value = progress,
                        title = {'text': "Tiến độ hoàn thành (%)", 'font': {'size': 20}},
                        gauge = {
                            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                            'bar': {'color': "#2563eb"},
                            'bgcolor': "white",
                            'borderwidth': 2,
                            'bordercolor': "#e2e8f0",
                            'steps': [
                                {'range': [0, 50], 'color': '#fee2e2'},
                                {'range': [50, 90], 'color': '#fef9c3'},
                                {'range': [90, 100], 'color': '#dcfce7'}],
                        }
                    ))
                    fig.update_layout(height=350, margin=dict(l=30, r=30, t=50, b=20))
                    st.plotly_chart(fig, use_container_width=True)
                    
                    st.download_button(
                        label="📥 Tải báo cáo PDF (CSV)",
                        data=final_data.to_csv().encode('utf-8-sig'),
                        file_name=f"Report_{final_data['madvi']}.csv",
                        mime='text/csv',
                        use_container_width=True
                    )
                
                st.markdown("</div>", unsafe_allow_html=True)
                st.balloons()
        else:
            st.error("😢 Không tìm thấy đơn vị nào phù hợp với từ khóa.")
    else:
        st.markdown("<br><br><center><img src='https://cdn-icons-png.flaticon.com/512/3772/3772274.png' width='120'><p style='color:#64748b; font-size: 1.1rem; margin-top: 10px;'>Vui lòng nhập tên đơn vị để bắt đầu</p></center>", unsafe_allow_html=True)
else:
    st.error("Cảnh báo: Không tìm thấy dữ liệu nguồn c12.xls.")

# --- FOOTER ---
st.markdown("<br><br><br><hr>", unsafe_allow_html=True)
st.caption("<center>Hệ thống Tra cứu Thông minh v4.0 | Power by Python & AI</center>", unsafe_allow_html=True)
