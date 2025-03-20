import streamlit as st

# ✅ ตั้งค่าหน้าหลัก
st.set_page_config(page_title="Home", page_icon="🏠", layout="wide")

# ✅ CSS ปรับแต่งให้พื้นหลังเป็นรูป และทำให้รูปจางลง
st.markdown("""
    <style>
        /* ตั้งค่าพื้นหลังเป็นรูป */
        .main-container {
            position: relative;
            width: 100%;
            height: 100vh;
            background: url('image.png') no-repeat center center fixed;
            background-size: cover;
        }
        /* เพิ่ม overlay สีขาวจางๆ เพื่อให้รูปจางลง */
        .overlay {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(255, 255, 255, 0.5); /* ปรับค่าความจางของรูป */
        }
        /* จัดปุ่มให้อยู่ตรงกลาง */
        .content {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            text-align: center;
            z-index: 10;
        }
        /* ปรับสไตล์ปุ่มให้เป็นสีขาว */
        .stButton > button {
            background-color: white !important;
            color: black !important;
            padding: 12px 20px;
            border: 2px solid black !important;
            border-radius: 8px;
            font-size: 18px;
            width: 200px;
        }
        /* ปุ่ม Profile อยู่มุมขวาบน */
        .profile-button {
            position: absolute;
            top: 15px;
            right: 20px;
            z-index: 20;
        }
        /* ส่วนท้าย */
        .footer {
            position: absolute;
            bottom: 10px;
            width: 100%;
            text-align: center;
            color: #777;
        }
    </style>
""", unsafe_allow_html=True)

# ✅ ส่วนหลักของหน้า (พื้นหลังเป็นรูป)
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# ✅ Overlay เพื่อทำให้รูปจางลง
st.markdown('<div class="overlay"></div>', unsafe_allow_html=True)

# ✅ ปุ่ม Profile บนขวา
st.markdown('<div class="profile-button">', unsafe_allow_html=True)
if st.button("👤 Profile", use_container_width=False):
    st.switch_page("pages/profile.py")
st.markdown("</div>", unsafe_allow_html=True)

# ✅ ส่วนของปุ่มให้อยู่ตรงกลาง
st.markdown('<div class="content">', unsafe_allow_html=True)
st.markdown('<h1 style="margin-bottom: 15px;">Please Select Activity</h1>', unsafe_allow_html=True)

# ✅ ปุ่ม Post Job & Find Job
col1, col2 = st.columns([1, 1])
with col1:
    if st.button("📝 Post Job"):
        st.switch_page("pages/post_job.py")
with col2:
    if st.button("🔎 Find Job"):
        st.switch_page("pages/find_job.py")

st.markdown("</div>", unsafe_allow_html=True)  # ปิด .content
st.markdown("</div>", unsafe_allow_html=True)  # ปิด .main-container

# ✅ ส่วนท้าย (FAST LABOR + Social Media)
st.markdown('<div class="footer">FAST LABOR | Follow us on:</div>', unsafe_allow_html=True)

# 🔹 Social Media Links
social_links = {
    "Facebook": "#",
    "Instagram": "#",
    "LinkedIn": "#",
    "YouTube": "#"
}

cols = st.columns(len(social_links))
for col, (name, link) in zip(cols, social_links.items()):
    with col:
        st.markdown(f"[{name}]({link})", unsafe_allow_html=True)
