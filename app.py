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

# --- TỔNG LỰC CSS (UI/UX TRẢI NGHIỆM NGƯỜI DÙNG) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');
    
    * { font-family: 'Plus Jakarta Sans', sans-serif; }
    
    .main { background-color: #f0f2f6; }
    
    /* Thiết kế thanh tìm kiếm kiểu Google */
    .stTextInput input {
        border-radius: 50px !important;
        padding: 25px 30px !important;
        border: none !important;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05) !important;
        font-size: 1.2rem !important;
    }
    
    /* Thẻ kết quả gợi ý */
    .suggestion-card {
        background: white;
        padding: 15px;
        border-radius: 15px;
        border: 1px solid #eef2f6;
        cursor: pointer;
        transition: all 0.3s ease;
        margin-bottom: 10px;
    }
    .suggestion-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 20px rgba(0,0,0,0.08);
        border-left: 5px solid #0061ff;
    }
    
    /* Thẻ nội dung chính (Glassmorphism) */
    .main-card {
        background: white;
        padding: 35px;
        border-radius: 30px;
        box-shadow: 0 20px 40px rgba(0,0,0,0.04);
        border: 1px solid rgba(255,255,255,0.7);
    }
    
    /* Chỉ số Metric tinh tế */
    .metric-box {
        background: #f8fafc;
        padding: 20px;
        border-radius: 20px;
        border: 1px solid #edf2f7;
    }
    
    h1, h2, h3 { color: #1e293b; font-weight: 800; }
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
        # Chuẩn hóa tìm kiếm
        df['search_no_accent'] = (df['madvi'].astype(str) + " " + df['tendvi'].astype(str)).apply(lambda x: unidecode(str(x)).lower())
        return df
    except: return None

df = load_data()

# --- GIAO DIỆN HEADER ---
st.markdown("<h1 style='text-align: center; font-size: 3rem; margin-bottom: 0;'>💎 BHXH DIGITAL HUB</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #64748b; font-size: 1.1rem;'>Hệ thống tra cứu và quản lý số liệu đóng BHXH thông minh</p>", unsafe_allow_html=True)

# --- CÔNG CỤ TÌM KIẾM THỜI GIAN THỰC ---
st.markdown("<br>", unsafe_allow_html=True)
c_search, _ = st.columns([2, 1])
with c_search:
    query = st.text_input("Tìm kiếm", placeholder="Gõ tên đơn vị (vd: 'dak', 'thuan an'...) hoặc mã số", label_visibility="collapsed")

if df is not None:
    if query:
        processed_query = unidecode(query).lower()
        results = df[df['search_no_accent'].str.contains(processed_query, na=False)].head(6) # Lấy 6 kết quả đầu tiên

        if not results.empty:
            st.markdown(f"🔍 Đang hiển thị các kết quả liên quan đến: **{query}**")
            
            # Tạo danh sách gợi ý dạng lưới (Grid)
            cols = st.columns(3)
            selected_unit_idx = -1
            
            for idx, row in results.iterrows():
                with cols[idx % 3]:
                    st.markdown(f"""
                    <div class="suggestion-card">
                        <small style='color: #3b82f6; font-weight: bold;'>{row['madvi']}</small>
                        <div style='font-weight: 600; font-size: 0.95rem; margin-top: 5px;'>{row['tendvi'][:40]}...</div>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"Xem chi tiết {row['madvi']}", key=row['madvi']):
                        st.session_state.selected_unit = row['madvi']
            
            # Hiển thị thông tin chi tiết khi đã chọn
            if 'selected_unit' in st.session_state:
                final_data = df[df['madvi'] == st.session_state.selected_unit].iloc[0]
                
                st.markdown("<br><div class='main-card'>", unsafe_allow_html=True)
                
                col_left, col_right = st.columns([1.5, 1])
                
                with col_left:
                    st.markdown(f"<h3>🏢 {final_data['tendvi']}</h3>", unsafe_allow_html=True)
                    st.markdown(f"📌 **Địa chỉ:** {final_data.get('diachi', 'N/A')}")
                    
                    # Metrics Grid
                    m1, m2 = st.columns(2)
                    with m1:
                        st.markdown("<div class='metric-box'>", unsafe_allow_html=True)
                        st.metric("Số phải đóng", f"{final_data.get('số phải đóng', 0):,.0f} đ")
                        st.markdown("</div>", unsafe_allow_html=True)
                    with m2:
                        st.markdown("<div class='metric-box'>", unsafe_allow_html=True)
                        st.metric("Số đã đóng", f"{final_data.get('số đã đóng', 0):,.0f} đ")
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    m3, m4 = st.columns(2)
                    with m3:
                        st.markdown("<div class='metric-box'>", unsafe_allow_html=True)
                        debt = final_data.get('tiền cuối kỳ', 0)
                        st.metric("Dư nợ / Thừa", f"{debt:,.0f} đ", delta=-debt, delta_color="inverse")
                        st.markdown("</div>", unsafe_allow_html=True)
                    with m4:
                        st.markdown("<div class='metric-box'>", unsafe_allow_html=True)
                        st.metric("Tỷ lệ nợ", f"{final_data.get('tyleno', 0)}%")
                        st.markdown("</div>", unsafe_allow_html=True)

                with col_right:
                    # TÍNH NĂNG XỊN: Biểu đồ Health Score
                    progress = 0
                    if final_data['số phải đóng'] > 0:
                        progress = (final_data['số đã đóng'] / final_data['số phải đóng']) * 100
                    
                    fig = go.Figure(go.Indicator(
                        mode = "gauge+number",
                        value = progress,
                        title = {'text': "Độ hoàn thành (%)"},
                        gauge = {
                            'axis': {'range': [0, 100]},
                            'bar': {'color': "#0061ff"},
                            'steps': [
                                {'range': [0, 50], 'color': "#fee2e2"},
                                {'range': [50, 90], 'color': "#fef9c3"},
                                {'range': [90, 100], 'color': "#dcfce7"}
                            ],
                        }
                    ))
                    fig.update_layout(height=300, margin=dict(l=20, r=20, t=50, b=20))
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Nút tải báo cáo
                    st.download_button(
                        label="📥 Tải báo cáo chi tiết (CSV)",
                        data=final_data.to_csv().encode('utf-8-sig'),
                        file_name=f"Bao_cao_{final_data['madvi']}.csv",
                        mime='text/csv',
                    )
                
                st.markdown("</div>", unsafe_allow_html=True)
                st.balloons()
        else:
            st.error("Không tìm thấy đơn vị nào phù hợp.")
    else:
        st.markdown("<br><br><center><img src='https://cdn-icons-png.flaticon.com/512/5069/5069162.png' width='100'><p style='color:#94a3b8;'>Hãy nhập từ khóa để khám phá dữ liệu</p></center>", unsafe_allow_html=True)
else:
    st.error("Lỗi: Không tìm thấy file c12.xls. Hãy đảm bảo bạn đã upload file lên GitHub.")

# --- FOOTER ---
st.markdown("<br><br><hr>", unsafe_allow_html=True)
st.caption("<center>Hệ thống được vận hành bởi AI & Streamlit Engine | 2026</center>", unsafe_allow_html=True)
```

### Cập nhật file `requirements.txt`:
Để biểu đồ hoạt động, bạn cần thêm thư viện `plotly`. Hãy copy nội dung này vào file `requirements.txt` của bạn:

```text
streamlit
pandas
numpy
xlrd
openpyxl
unidecode
plotly
