import streamlit as st

# ตั้งชื่อหัวหน้า
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

# เว้นระยะห่าง
st.markdown("")

# ปุ่ม "สรุปผลการจ้างงาน"
center_button = """
<div style='display: flex; justify-content: center; margin-top: 20px;'>
    <form action='/summary'>
        <button style='background-color: black; color: white; padding: 8px 20px; border: none; border-radius: 5px;'>
            สรุปผลการจ้างงาน
        </button>
    </form>
</div>
"""

st.markdown(center_button, unsafe_allow_html=True)
