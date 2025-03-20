import streamlit as st

# ✅ ตั้งค่าหน้าหลัก
st.set_page_config(page_title="Home", page_icon="🏠", layout="wide")

# ✅ CSS ปรับแต่งให้ดูดีขึ้น
st.markdown("""
    <style>
        /* ปรับสไตล์ปุ่มให้เป็นสีขาว */
        .stButton > button {
            background-color: white !important;
            color: black !important;
            padding: 10px 15px;
            border: 2px solid black !important;
            border-radius: 8px;
            font-size: 18px;
            width: 100%;
        }
        /* จัดปุ่ม Profile ไปที่มุมขวาบน */
        .profile-button {
            position: absolute;
            top: 15px;
            right: 20px;
            z-index: 100;
        }
        /* ตำแหน่งตรงกลาง */
        .center-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 80vh;
        }
        /* ส่วนท้าย */
        .footer {
            text-align: center;
            margin-top: 40px;
            color: #777;
        }
    </style>
""", unsafe_allow_html=True)

# ✅ ปุ่ม Profile บนขวา
st.markdown('<div class="profile-button">', unsafe_allow_html=True)
if st.button("👤 Profile", use_container_width=False):
    st.switch_page("pages/profile.py")
st.markdown("</div>", unsafe_allow_html=True)

# ✅ แสดงโลโก้
st.image("image.png", width=150)

# ✅ ส่วนหัว
st.markdown('<div class="center-container">', unsafe_allow_html=True)
st.markdown('<h1 style="margin-bottom: 10px;">Please Select Activity</h1>', unsafe_allow_html=True)

# ✅ ปุ่มกิจกรรม (Post Job & Find Job)
col1, col2 = st.columns([1, 1])
with col1:
    if st.button("📝 Post Job", use_container_width=True):
        st.switch_page("pages/post_job.py")
with col2:
    if st.button("🔎 Find Job", use_container_width=True):
        st.switch_page("pages/find_job.py")

st.markdown("</div>", unsafe_allow_html=True)  # ปิด center-container

# ✅ เส้นแบ่ง
st.divider()

# ✅ ส่วนท้าย (FAST LABOR + Social Media)
st.markdown('<div class="footer">FAST LABOR</div>', unsafe_allow_html=True)
st.markdown('<div class="footer">Follow us on:</div>', unsafe_allow_html=True)

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
