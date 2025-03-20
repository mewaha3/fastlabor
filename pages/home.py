import streamlit as st

# ✅ ตั้งค่าหน้าหลัก
st.set_page_config(page_title="Home", page_icon="🏠", layout="centered")

# ✅ CSS ปรับแต่งให้ดูดีขึ้น
st.markdown("""
    <style>
        .main {
            background-color: #f7f9fc;
            text-align: center;
        }
        .title {
            font-size: 36px;
            font-weight: bold;
            text-align: center;
            margin-bottom: 10px;
        }
        .subtext {
            font-size: 18px;
            color: #555;
            margin-bottom: 30px;
        }
        .stButton > button {
            background-color: black !important;
            color: white !important;
            padding: 10px 15px;
            border-radius: 8px;
            font-size: 18px;
            width: 100%;
        }
        .footer {
            text-align: center;
            margin-top: 40px;
            color: #777;
        }
    </style>
""", unsafe_allow_html=True)

# ✅ แสดงโลโก้
st.image("image.png", width=150)

# ✅ ส่วนหัว
st.markdown('<div class="title">Please Select Activity</div>', unsafe_allow_html=True)
st.markdown('<div class="subtext">Choose an option to continue</div>', unsafe_allow_html=True)

# ✅ ปุ่มกิจกรรม (Post Job & Find Job)
col1, col2 = st.columns([1, 1])
with col1:
    if st.button("📝 Post Job", use_container_width=True):
        st.switch_page("pages/post_job.py")
with col2:
    if st.button("🔎 Find Job", use_container_width=True):
        st.switch_page("pages/find_job.py")

# ✅ ปุ่ม Profile (ให้อยู่ตรงกลาง)
st.markdown("<br>", unsafe_allow_html=True)  # เพิ่มระยะห่าง
if st.button("👤 Profile", use_container_width=True):
    st.switch_page("pages/profile.py")

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
