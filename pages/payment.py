import streamlit as st

st.set_page_config(page_title="Payment", layout="centered")
st.markdown("### FAST LABOR")
st.markdown("## ")
st.markdown("## Payment")

# ถ้ากด Confirm แล้ว ให้เปลี่ยนหน้า
if st.session_state.get("go_payment_success", False):
    st.session_state.pop("go_payment_success")  # เคลียร์ state หลังเปลี่ยนหน้า
    st.switch_page("pages/payment_success.py")  # ← ใช้ได้ถ้าเขียนเป็น multi-page structure

# ตัวเลือกการชำระเงิน
payment_method = st.radio(
    "",
    ("Mobile Banking", "Credit card", "QR Code")
)

# ปุ่ม
col1, col2 = st.columns([1, 1])
with col1:
    cancel = st.button("Cancel")
with col2:
    confirm = st.button("Confirm")

# เมื่อกด Confirm ให้เซ็ต state แล้ว rerun
if confirm:
    st.session_state["selected_payment_method"] = payment_method
    st.session_state["go_payment_success"] = True
    st.experimental_rerun()

# เมื่อกด Cancel
if cancel:
    st.warning("❌ Payment cancelled.")
