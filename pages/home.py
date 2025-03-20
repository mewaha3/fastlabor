import streamlit as st

# ✅ ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="Home", page_icon="🏠", layout="wide")

# ✅ CSS ปรับแต่งให้หน้าเว็บดูดีขึ้น
st.markdown("""
    <style>
        /* กำหนดพื้นหลังเต็มจอ */
        .main-container {
            position: relative;
            width: 100%;
            height: 100vh;
            background: url('image.png') no-repeat center center fixed;
            background-size: cover;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }
        
        /* กล่องข้อความตรงกลาง */
        .content-box {
            background: rgba(255, 255, 255, 0.8);
            padding: 30px;
            border-radius: 10px;
            text-align: center;
        }

        /* ปุ่มดำสวยงาม */
        .stButton > button {
            background-color: black !important;
            color: white !important;
            padding: 10px 20px;
            border-radius: 8px;
            font-size: 18px;
            width: 100%;
        }

        /* ส่วนท้าย */
        .footer {
            margin-top: 40px;
            text-align: center;
            font-size: 16px;
            color: #777;
        }

        /* Social Icons */
        .social-icons {
            display: flex;
            justify-content: center;
            gap: 15px;
            margin-top: 10px;
        }
        .social-icons a {
            font-size: 20px;
            color: black;
            text-decoration: none;
        }
    </style>
""", unsafe_allow_html=True)

# ✅ ส่วนหัวของหน้า
st.markdown('<div class="main-container">', unsafe_allow_html=True)
st.markdown('<div class="content-box">', unsafe_allow_html=True)
st.markdown('<h1 style="margin-bottom: 10px;">Please Select Activity</h1>', unsafe_allow_html=True)

# ✅ ปุ่ม Post Job & Find Job
col1, col2 = st.columns([1, 1])
with col1:
    st.page_link("pages/post_job.py", label="Post Job", use_container_width=True)
with col2:
    if st.button("Find Job", use_container_width=True):
        st.switch_page("pages/find_job.py")

st.markdown("</div>", unsafe_allow_html=True)  # ปิด content-box
st.markdown("</div>", unsafe_allow_html=True)  # ปิด main-container

# ✅ ส่วนท้าย (FAST LABOR + Social Media + Footer Menu)
st.markdown('<div class="footer">FAST LABOR</div>', unsafe_allow_html=True)

# 🔹 Social Media Icons
social_links = {
    "🌐 Facebook": "#",
    "📸 Instagram": "#",
    "💼 LinkedIn": "#",
    "▶️ YouTube": "#"
}

st.markdown('<div class="social-icons">', unsafe_allow_html=True)
for name, link in social_links.items():
    st.markdown(f'<a href="{link}" target="_blank">{name}</a>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# 🔹 Footer Menu
cols = st.columns(4)
for col in cols:
    with col:
        st.markdown("**Topic**")
        st.markdown("[Page](#)")
        st.markdown("[Page](#)")
        st.markdown("[Page](#)")
