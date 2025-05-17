import streamlit as st

st.set_page_config(page_title="Payment", layout="centered")

st.markdown("### FAST LABOR")
st.markdown("## Payment")

# ตัวเลือกการชำระเงิน
payment_method = st.radio(
    "",
    ("Mobile Banking", "Credit card", "QR Code")
)

# ปุ่ม Cancel/Confirm
col1, col2 = st.columns([1, 1])
with col1:
    if st.button("Cancel"):
        st.warning("❌ ยกเลิกการชำระเงิน")
with col2:
    if st.button("Confirm"):
        # เก็บวิธีชำระเงินใน session
        st.session_state["selected_payment_method"] = payment_method

        # แสดงข้อความยืนยัน
        st.success(f"✅ คุณเลือกวิธีชำระเงิน: {payment_method}")

        # ไปหน้า Payment Success ผ่าน switch_page (session ยังคง selected_job อยู่)
        st.experimental_rerun()  # รีโหลดเพื่อให้ UI อัพเดตก่อนเปลี่ยนหน้า
        st.switch_page("pages/payment_success.py")
