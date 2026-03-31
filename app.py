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
    page_title="BHXH Thuận An - Ultimate Digital Hub v15.0",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- KHỞI TẠO STATE ---
if 'selected_unit' not in st.session_state:
    st.session_state.selected_unit = None
if 'last_query' not in st.session_state:
    st.session_state.last_query = ""
if 'show_loading' not in st.session_state:
    st.session_state.show_loading = False
if 'current_tab' not in st.session_state:
    st.session_state.current_tab = "📊 Tra cứu C12-TS"
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- TỔNG LỰC CSS (GIAO DIỆN ULTIMATE v15.0) ---
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
        --neon-red: #ff3131;
    }

    * { font-family: 'Plus Jakarta Sans', sans-serif; }
    
    .stApp {
        background: linear-gradient(135deg, #f0f4f8 0%, #d9e2ec 100%);
    }

    /* BẢNG LED CHẠY CHỮ RGB CAO CẤP */
    .led-marquee {
        background: #000;
        color: #00ff00;
        padding: 12px 0;
        font-weight: 700;
        border-radius: 12px;
        box-shadow: 0 0 25px rgba(0, 255, 0, 0.4);
        border: 2px solid #333;
        margin-bottom: 25px;
        font-family: 'Courier New', Courier, monospace;
        font-size: 1.15rem;
        text-shadow: 0 0 10px #00ff00, 0 0 20px #00ff00;
    }

    /* SIÊU Ô TÌM KIẾM - FIX CLIPPING TUYỆT ĐỐI */
    .mega-search-container {
        max-width: 1100px;
        margin: 0 auto 3rem auto;
        text-align: center;
    }

    div[data-testid="stTextInput"] > div {
        height: auto !important;
        background: transparent !important;
    }

    .stTextInput input {
        border-radius: 30px !important;
        padding: 15px 50px !important; 
        border: 8px solid var(--secondary) !important;
        font-size: 2.8rem !important; 
        font-weight: 900 !important;
        height: 140px !important; 
        background: white !important;
        color: var(--primary) !important;
        box-shadow: 0 35px 80px rgba(59, 130, 246, 0.4) !important;
        transition: all 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        text-align: center !important;
        line-height: normal !important;
    }
    
    .stTextInput input:focus {
        border-color: var(--neon-blue) !important;
        transform: scale(1.02);
        box-shadow: 0 45px 110px rgba(0, 210, 255, 0.5) !important;
    }

    /* THẺ CÁN BỘ NEON VỚI HIỆU ỨNG ZALO */
    .officer-card {
        background: #080808;
        padding: 22px;
        border-radius: 25px;
        border: 4px solid #1a1a1a;
        margin-bottom: 20px;
        text-align: center;
        transition: all 0.4s ease;
    }
    .officer-card:hover { transform: translateY(-10px); border-color: #444; }

    @keyframes blink-blue { 0%, 100% { border-color: #00d2ff; box-shadow: 0 0 15px #00d2ff; } 50% { border-color: #111; } }
    @keyframes blink-gold { 0%, 100% { border-color: #ffaa00; box-shadow: 0 0 15px #ffaa00; } 50% { border-color: #111; } }
    @keyframes blink-green { 0%, 100% { border-color: #39ff14; box-shadow: 0 0 15px #39ff14; } 50% { border-color: #111; } }

    .card-nhai { animation: blink-blue 2s infinite; }
    .card-dat { animation: blink-gold 2.5s infinite; }
    .card-hai { animation: blink-green 3s infinite; }

    /* NÚT ZALO ĐỘNG */
    .zalo-btn {
        background: #0068ff;
        color: white !important;
        padding: 8px 15px;
        border-radius: 50px;
        text-decoration: none !important;
        font-weight: 800;
        font-size: 0.9rem;
        display: inline-block;
        margin-top: 10px;
        box-shadow: 0 4px 10px rgba(0, 104, 255, 0.3);
        transition: all 0.3s;
    }
    .zalo-btn:hover { background: white; color: #0068ff !important; transform: scale(1.1); }

    /* MENU SIDEBAR SANG TRỌNG */
    [data-testid="stSidebar"] {
        background-color: #0f172a;
    }
    .sidebar-header {
        color: white;
        text-align: center;
        font-weight: 800;
        margin-bottom: 20px;
    }

    /* DASHBOARD */
    .dashboard-panel {
        background: white;
        border-radius: 40px;
        padding: 40px;
        box-shadow: 0 35px 80px rgba(0,0,0,0.08);
        border: 1px solid #fff;
    }

    /* HIỆU ỨNG LIVE INDICATOR */
    .live-dot {
        height: 10px; width: 10px; background-color: #ff3131; border-radius: 50%;
        display: inline-block; margin-right: 5px; animation: pulse-red 1s infinite;
    }
    @keyframes pulse-red { 0% { opacity: 1; transform: scale(1); } 50% { opacity: 0.3; transform: scale(1.5); } 100% { opacity: 1; transform: scale(1); } }
    </style>
    """, unsafe_allow_html=True)

# --- DỮ LIỆU CÁN BỘ & ZALO ---
OFFICERS = [
    {
        "name": "Bà NGUYỄN THỊ NHÀI", 
        "scope": "Xã Đức Lập, Xã Đắk Mil", 
        "phone": "0846.39.29.29", 
        "zalo": "https://zalo.me/0846392929",
        "class": "card-nhai", "color": "#00d2ff", 
        "areas": ["duc lap", "dak mil", "đức lập", "đắk mil"]
    },
    {
        "name": "Ông BÙI THÀNH ĐẠT", 
        "scope": "Xã Đắk Sắk, Xã Đắk Song", 
        "phone": "0986.05.30.06", 
        "zalo": "https://zalo.me/0986053006",
        "class": "card-dat", "color": "#ffaa00", 
        "areas": ["dak sak", "dak song", "đắk sắk", "đắk song"]
    },
    {
        "name": "Ông HOÀNG SỸ HẢI", 
        "scope": "Xã Thuận An", 
        "phone": "0919.06.11.53", 
        "zalo": "https://zalo.me/0919061153",
        "class": "card-hai", "color": "#39ff14", 
        "areas": ["thuan an", "thuận an"]
    }
]

# --- DỮ LIỆU NGÂN HÀNG ---
BANKS = [
    {"name": "BIDV", "number": "63510009867032"},
    {"name": "AGRIBANK", "number": "5301202919045"},
    {"name": "VIETINBANK", "number": "919035000003"}
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
            df.columns = [unidecode(str(c)).lower().strip().replace(' ', '_') for c in df.columns]
            if 'madvi' in df.columns: df['madvi'] = df['madvi'].astype(str).str.strip()
            df['search_index'] = df.apply(lambda x: unidecode(str(x.get('madvi', '')) + " " + str(x.get('tendvi', ''))).lower(), axis=1)
            return df
    except: return None

# --- MENU SIDEBAR ---
with st.sidebar:
    st.markdown("<div class='sidebar-header'><h1>🛡️ SMART BHXH</h1><p>THUẬN AN HUB</p></div>", unsafe_allow_html=True)
    st.divider()
    
    tabs = ["📊 Tra cứu C12-TS", "🤖 Trợ lý AI (Q&A)", "📑 Cẩm nang & Văn bản", "🧮 Tiện ích Tính toán", "📍 Chỉ đường & Liên hệ"]
    for t in tabs:
        if st.button(t, use_container_width=True, key=f"tab_{t}"):
            st.session_state.current_tab = t
            st.rerun()
            
    st.divider()
    st.markdown("### 📞 HỖ TRỢ KHẨN CẤP")
    st.info("Tổng đài BHXH: 1900 9068")
    st.caption("Phiên bản Platinum v15.0")

# --- HEADER (LED MARQUEE RGB) ---
marquee_msg = "💎 CHÀO MỪNG QUÝ ĐƠN VỊ ĐẾN VỚI HỆ THỐNG TRA CỨU BHXH THUẬN AN THẾ HỆ MỚI • TÍCH HỢP AI VÀ KẾT NỐI ZALO TRỰC TUYẾN • ĐỊA CHỈ: THÔN THUẬN SƠN, XÃ THUẬN AN, TỈNH LÂM ĐỒNG •"
st.markdown(f"<div class='led-marquee'><marquee scrollamount='10'>{marquee_msg}</marquee></div>", unsafe_allow_html=True)

df = load_data()

if df is not None:
    
    # --- TAB 1: TRA CỨU C12-TS (CHỨC NĂNG CHÍNH) ---
    if st.session_state.current_tab == "📊 Tra cứu C12-TS":
        if st.session_state.selected_unit is None:
            # SIÊU Ô TÌM KIẾM TRUNG TÂM
            st.markdown("<div class='mega-search-container'>", unsafe_allow_html=True)
            st.markdown("<h1 style='color:#1e3a8a; font-size:3.5rem; font-weight:900; margin-bottom:10px;'>🛡️ TRA CỨU BHXH THUẬN AN</h1>", unsafe_allow_html=True)
            st.markdown("<p style='color:#64748b; font-size:1.5rem; margin-bottom:40px; font-weight:700;'>NHẬP MÃ ĐƠN VỊ HOẶC TÊN CÔNG TY ĐỂ XEM SỐ LIỆU</p>", unsafe_allow_html=True)
            query = st.text_input("Gateway", placeholder="🔍 Gõ tìm kiếm tại đây...", label_visibility="collapsed")
            st.markdown("</div>", unsafe_allow_html=True)

            col_post, col_res, col_info = st.columns([0.8, 1.4, 1.1])

            with col_post:
                st.markdown("##### 📢 Thông tin an sinh")
                posters = [
                    {"t": "🛡️ AN SINH TUỔI GIÀ", "c": "BHXH là điểm tựa tài chính bền vững nhất cho bạn."},
                    {"t": "🏥 LÁ CHẮN SỨC KHỎE", "c": "Thẻ BHYT bảo vệ bạn trước rủi ro bệnh tật."},
                    {"t": "🤰 THAI SẢN AN TÂM", "c": "Đồng hành cùng gia đình trong ngày vui đón bé."}
                ]
                p = posters[datetime.now().minute % len(posters)]
                st.markdown(f"""
                    <div style='background:white; padding:35px; border-radius:35px; border:2px solid #e2e8f0; text-align:center; min-height:330px; display:flex; flex-direction:column; justify-content:center; box-shadow: 0 15px 30px rgba(0,0,0,0.05);'>
                        <h4 style='color:#1e3a8a; margin:0;'>{p['t']}</h4>
                        <p style='font-size:1.1rem; color:#64748b; margin:15px 0;'>{p['c']}</p>
                        <hr style='border: 0.5px solid #eee;'>
                        <small style='color:#ffaa00; font-weight:800;'>VÌ LỢI ÍCH CỘNG ĐỒNG</small>
                    </div>
                """, unsafe_allow_html=True)

            with col_res:
                if query:
                    clean_query = unidecode(query).lower()
                    results = df[df['search_index'].str.contains(clean_query, na=False)].head(8)
                    if not results.empty:
                        st.write(f"✨ Tìm thấy **{len(results)}** đơn vị phù hợp:")
                        for idx, row in results.iterrows():
                            with st.container():
                                ca, cb = st.columns([3.5, 1.5])
                                ca.markdown(f"""
                                    <div style='background:white; padding:22px; border-radius:25px; border-left:10px solid #2563eb; margin-bottom:12px; box-shadow:0 5px 15px rgba(0,0,0,0.05);'>
                                        <small style='color:#2563eb; font-weight:800;'>MÃ: {row.get('madvi')}</small><br>
                                        <b style='font-size:1.3rem; color:#1e293b;'>{row.get('tendvi')}</b>
                                    </div>
                                """, unsafe_allow_html=True)
                                if cb.button("Xác nhận ➔", key=f"sel_{row.get('madvi')}_{idx}", use_container_width=True):
                                    st.session_state.selected_unit = row.get('madvi')
                                    st.session_state.show_loading = True
                                    st.rerun()
                else:
                    st.markdown("<br><center><img src='https://cdn-icons-png.flaticon.com/512/3772/3772274.png' width='160' style='opacity:0.2'><h4 style='color:#94a3b8;'>Sẵn sàng kết nối dữ liệu</h4></center>", unsafe_allow_html=True)

            with col_info:
                st.markdown("##### 👨‍💼 Cán bộ Chuyên quản & Zalo")
                for off in OFFICERS:
                    st.markdown(f"""
                    <div class="officer-card {off['class']}">
                        <div class="live-dot"></div><small style="color:white; font-weight:800;">ONLINE</small>
                        <div style="color:{off['color']}; font-weight:800; font-size:1.1rem; margin-top:5px;">{off['name']}</div>
                        <div style="color:#aaa; font-size:0.85rem; margin:5px 0;">Phụ trách: {off['scope']}</div>
                        <a href="tel:{off['phone'].replace('.','')}" style="text-decoration:none; color:white; font-weight:800; font-size:1.2rem;">📱 {off['phone']}</a><br>
                        <a href="{off['zalo']}" target="_blank" class="zalo-btn">💬 Chat Zalo</a>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("##### 🏦 Số tài khoản của BHXH cơ sở Thuận An")
                for bank in BANKS:
                    st.markdown(f"""
                    <div style="background:linear-gradient(135deg, #111 0%, #222 100%); padding:15px; border-radius:15px; border-left:8px solid #00d2ff; margin-bottom:8px;">
                        <div style="color:#00d2ff; font-weight:800; font-size:0.85rem;">NH: {bank['name']}</div>
                        <div style="color:#fff; font-size:1.2rem; font-family:monospace; font-weight:700;">{bank['number']}</div>
                    </div>
                    """, unsafe_allow_html=True)

        # MÀN HÌNH LOADING
        elif st.session_state.show_loading:
            st.markdown("<br><br><br>", unsafe_allow_html=True)
            with st.status("💎 ĐANG PHÂN TÍCH DỮ LIỆU C12-TS...", expanded=True) as status:
                st.write("🔄 Kết nối máy chủ dữ liệu BHXH Lâm Đồng...")
                time.sleep(0.7)
                st.write("📊 Đang tổng hợp số dư cuối kỳ...")
                time.sleep(0.5)
                status.update(label="Tải dữ liệu thành công!", state="complete")
            st.session_state.show_loading = False
            st.balloons()
            st.rerun()

        # DASHBOARD CHI TIẾT
        else:
            unit_data = df[df['madvi'] == st.session_state.selected_unit].iloc[0]
            unit_addr = unidecode(str(unit_data.get('diachi', ''))).lower()
            
            if st.button("⬅ QUAY LẠI TRANG CHỦ"):
                st.session_state.selected_unit = None
                st.rerun()

            st.markdown(f"""
                <div style='background:white; padding:45px; border-radius:45px; border-left:25px solid #1e3a8a; box-shadow: 0 25px 60px rgba(0,0,0,0.08); margin-top:20px;'>
                    <h2 style='margin:0; color:#1e3a8a;'>🏢 {unit_data.get('tendvi')}</h2>
                    <p style='margin:10px 0 0 0; color:#64748b;'>Mã đơn vị: <b>{unit_data.get('madvi')}</b> | Địa chỉ: {unit_data.get('diachi', 'N/A')}</p>
                </div>
            """, unsafe_allow_html=True)

            col_l, col_r = st.columns([1.8, 1])
            with col_l:
                st.markdown("<div class='dashboard-panel' style='margin-top:25px;'>", unsafe_allow_html=True)
                st.write("#### 📈 Phân tích tài chính chi tiết")
                m1, m2, m3 = st.columns(3)
                m1.metric("Tiền đầu kỳ", f"{unit_data.get('tien_dau_ky', 0):,.0f}đ")
                m2.metric("Số phải đóng", f"{unit_data.get('so_phai_dong', 0):,.0f}đ")
                m3.metric("Điều chỉnh", f"{unit_data.get('dieu_chinh_ky_truoc', 0):,.0f}đ")
                
                st.write("<br>", unsafe_allow_html=True)
                m4, m5, m6 = st.columns(3)
                m4.metric("Số đã đóng", f"{unit_data.get('so_da_dong', 0):,.0f}đ")
                m5.metric("Số bị lệch", f"{unit_data.get('so_bi_lech', 0):,.0f}đ")
                debt = unit_data.get('tien_cuoi_ky', 0)
                m6.metric("CÒN NỢ" if debt > 0 else "DƯ CÓ", f"{abs(debt):,.0f}đ", delta=-debt, delta_color="inverse")
                
                now = datetime.now()
                transfer_note = f"{unit_data.get('madvi')} {unit_data.get('tendvi')} đóng bhxh tháng {now.month} năm {now.year}"
                st.markdown(f"""
                    <div style='background:#f0f9ff; padding:35px; border-radius:35px; border:3px dashed #3b82f6; margin-top:30px; text-align:center;'>
                        <p style='color:#1e40af; font-weight:800; font-size:1.1rem; text-transform:uppercase;'>📝 NỘI DUNG CHUYỂN KHOẢN CHUẨN:</p>
                        <h3 style='color:#1e3a8a; font-family:monospace; font-size:2rem; background:white; padding:15px; border-radius:15px; margin:15px 0;'>{transfer_note}</h3>
                        <p style='color:#64748b; font-size:0.9rem;'><i>(Vui lòng sao chép chính xác nội dung để hệ thống tự động gạch nợ)</i></p>
                    </div>
                """, unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

            with col_r:
                phai_dong = unit_data.get('so_phai_dong', 1)
                da_dong = unit_data.get('so_da_dong', 0)
                rate = min(round((da_dong / phai_dong) * 100, 1), 100) if phai_dong > 0 else 0
                fig = go.Figure(go.Indicator(
                    mode = "gauge+number", value = rate,
                    title = {'text': "Tỷ lệ hoàn thành (%)", 'font': {'size': 24, 'color': '#64748b'}},
                    number = {'suffix': "%", 'font': {'color': '#1e40af', 'size': 65}},
                    gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': "#1e40af"}, 'steps': [{'range': [0, 50], 'color': '#fee2e2'}, {'range': [90, 100], 'color': '#dcfce7'}]}
                ))
                fig.update_layout(height=450, margin=dict(l=35, r=35, t=70, b=35), paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig, use_container_width=True)
                
                # Highlight Cán bộ phụ trách xã
                for off in OFFICERS:
                    if any(area in unit_addr for area in off['areas']):
                        st.markdown(f"""
                        <div class="officer-card {off['class']}" style="background:#000;">
                            <small style="color:#39ff14; font-weight:800; border:1px solid #39ff14; padding:4px 12px; border-radius:50px;">PHỤ TRÁCH TRỰC TIẾP</small>
                            <h4 style="margin:10px 0; color:{off['color']}; font-size:1.6rem;">{off['name']}</h4>
                            <a href="tel:{off['phone'].replace('.','')}" style="text-decoration:none; color:white; font-weight:800; font-size:1.5rem;">📱 {off['phone']}</a><br>
                            <a href="{off['zalo']}" target="_blank" class="zalo-btn">💬 Chat Zalo</a>
                        </div>
                        """, unsafe_allow_html=True)

    # --- TAB 2: TRỢ LÝ AI (CHATBOT) ---
    elif st.session_state.current_tab == "🤖 Trợ lý AI (Q&A)":
        st.markdown("## 🤖 Trợ lý ảo BHXH Thuận An (AI Assistant)")
        st.write("Hỏi tôi về chính sách, thủ tục hoặc tỷ lệ đóng BHXH mới nhất.")
        
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("Hỏi tôi bất cứ điều gì..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                response = f"Chào bạn! Tôi là trợ lý ảo của BHXH Thuận An. Về câu hỏi '{prompt}', hệ thống đang được huấn luyện dữ liệu. Tuy nhiên, theo quy định chung, bạn nên tham khảo Nghị định 115/2015/NĐ-CP hoặc liên hệ trực tiếp cán bộ chuyên quản để có câu trả lời chính xác nhất cho trường hợp của mình."
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})

    # --- TAB 3: CẨM NANG & VĂN BẢN ---
    elif st.session_state.current_tab == "📑 Cẩm nang & Văn bản":
        st.markdown("## 📚 Thư viện Văn bản & Cẩm nang Nghiệp vụ")
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### 🏢 Nghiệp vụ Doanh nghiệp")
            with st.expander("Quy trình báo tăng lao động (D02-LT)"):
                st.write("1. Hồ sơ bao gồm Tờ khai TK1-TS và Danh sách D02-LT.")
                st.write("2. Nộp qua phần mềm BHXH điện tử (IVAN).")
            with st.expander("Chế độ ốm đau, thai sản"):
                st.write("Hồ sơ mẫu 01B-HSB, nộp trong vòng 45 ngày kể từ ngày đi làm lại.")
        
        with c2:
            st.markdown("### ⚖️ Văn bản Pháp quy")
            st.info("📑 Luật Bảo hiểm xã hội 2014 (Sắp sửa đổi 2024)")
            st.info("📑 Nghị định 146/2018/NĐ-CP về Bảo hiểm y tế")
            st.info("📑 Quyết định 595/QĐ-BHXH quy định về quản lý thu")

    # --- TAB 4: TÍNH TOÁN ---
    elif st.session_state.current_tab == "🧮 Tiện ích Tính toán":
        st.markdown("## 🧮 Công cụ tính toán mức đóng BHXH 2026")
        salary = st.number_input("Nhập mức lương đóng BHXH (VNĐ):", value=5000000, step=100000)
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### 🏢 Đơn vị đóng (21.5%)")
            st.write(f"- Hưu trí: {salary*0.14:,.0f}đ")
            st.write(f"- BHYT: {salary*0.03:,.0f}đ")
            st.write(f"- BHTN: {salary*0.01:,.0f}đ")
            st.markdown(f"**=> Tổng đơn vị: {salary*0.215:,.0f}đ**")
        with c2:
            st.markdown("#### 👤 Người lao động đóng (10.5%)")
            st.write(f"- Hưu trí: {salary*0.08:,.0f}đ")
            st.write(f"- BHYT: {salary*0.015:,.0f}đ")
            st.write(f"- BHTN: {salary*0.01:,.0f}đ")
            st.markdown(f"**=> Tổng NLĐ: {salary*0.105:,.0f}đ**")

    # --- TAB 5: BẢN ĐỒ ---
    elif st.session_state.current_tab == "📍 Chỉ đường & Liên hệ":
        st.markdown("## 📍 Thông tin Cơ quan BHXH cơ sở Thuận An")
        st.write("🏠 Địa chỉ: Thôn Thuận Sơn, xã Thuận An, tỉnh Lâm Đồng.")
        st.warning("Ứng dụng đang phát triển tính năng tích hợp Google Maps API.")

st.markdown("<br><hr><center style='color:#94a3b8; font-size:0.9rem; padding-bottom:60px;'>© 2026 BHXH CƠ SỞ THUẬN AN | Elite Digital Hub v15.0</center>", unsafe_allow_html=True)
