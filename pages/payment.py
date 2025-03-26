import streamlit as st

# ตั้งค่าหน้าหลัก
st.set_page_config(page_title="Payment", layout="centered")

st.markdown("### FAST LABOR")
st.markdown("## ")
st.markdown("## Payment")

# ✅ หากมีการสั่ง redirect ไป payment_success แล้ว
if st.session_state.get("go_payment_success", False):
    st.session_state.pop("go_payment_success")  # เคลียร์ flag
    st.markdown("## ✅ Payment Successful! Redirecting...")
    st.markdown("[คลิกที่นี่หากระบบไม่เปลี่ยนหน้าอัตโนมัติ](./payment_success)")
    st.stop()  # หยุดการรันหน้าอื่นต่อ

# ✅ ตัวเลือกการชำระเงิน
payment_method = st.radio(
    "",
    ("Mobile Banking", "Credit card", "QR Code")
)

# ✅ ปุ่มกด
col1, col2 = st.columns([1, 1])
with col1:
    cancel = st.button("Cancel")
with col2:
    confirm = st.button("Confirm")

# ✅ เมื่อกด Confirm
if confirm:
    st.session_state["selected_payment_method"] = payment_method
    st.session_state["go_payment_success"] = True
    st.rerun()

# ✅ เมื่อกด Cancel
if cancel:
    st.warning("❌ Payment cancelled.")
