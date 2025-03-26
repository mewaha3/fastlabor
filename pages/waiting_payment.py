import streamlit as st

st.set_page_config(page_title="รอนายจ้างชำระเงิน", layout="centered")

# Header
st.markdown("### FAST LABOR")
st.markdown("## 💸 กำลังรอการชำระเงินจากนายจ้าง")

# ภาพประกอบ
st.image("https://i.ibb.co/HV1rC3f/loading.gif", width=150)

# ข้อความแสดงสถานะ
st.markdown("""
<div style="text-align: center; font-size: 18px; margin-top: 20px;">
    โปรดรอให้นายจ้างดำเนินการชำระเงิน<br>
    ระบบจะอัปเดตสถานะโดยอัตโนมัติหลังจากได้รับการชำระเงิน
</div>
""", unsafe_allow_html=True)

# ปุ่มกลับหน้าแรก
st.page_link("pages/home.py", label="🏠 กลับหน้าแรก", icon="🏠")
