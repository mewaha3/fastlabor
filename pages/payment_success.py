import streamlit as st
from streamlit_extras.switch_page_button import switch_page

# ตั้งชื่อหัวหน้า
st.set_page_config(page_title="Payment Success", page_icon="✅")
st.markdown("### FAST LABOR")

# เว้นระยะห่าง
st.markdown("## ")
st.markdown("## Payment Success", unsafe_allow_html=True)

# แสดงไอคอนผู้ใช้และเครื่องหมายถูก
st.markdown(
    """
    <div style='text-align: center; font-size: 50px;'>
        <span style='display: inline-block;'>👤</span>
        <span style='display: inline-block; margin-left: 20px;'>✅</span>
    </div>
    """,
    unsafe_allow_html=True
)

# ปุ่ม "สรุปผลการจ้างงาน" อยู่ตรงกลาง
st.markdown("")

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("สรุปผลการจ้างงาน"):
        switch_page("job_detail")
