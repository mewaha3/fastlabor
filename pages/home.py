import streamlit as st

st.set_page_config(page_title="Home", page_icon="🏠", layout="wide")

st.image("image.png", width=150)  # แสดงโลโก้
st.title("Please Select Activity")

st.markdown("##")

col1, col2 = st.columns([1, 1])
with col1:
    st.page_link("pages/post_job.py", label="Post Job", icon="📝", use_container_width=True)
with col2:
    # ✅ ปุ่มไปหน้า Find Job
    if st.button("Find Job"):
        st.switch_page("pages/find_job.py")

# ✅ ปุ่ม Profile ด้านบน
st.page_link("pages/profile.py", label="Profile", icon="👤")

st.markdown("---")
st.markdown("### FAST LABOR")
st.write("Follow us on:")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown('[Facebook](#)')
with col2:
    st.markdown('[Instagram](#)')
with col3:
    st.markdown('[LinkedIn](#)')
with col4:
    st.markdown('[YouTube](#)')
