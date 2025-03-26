import streamlit as st

# ตั้งชื่อหัวข้อด้านบน
st.set_page_config(page_title="Payment", layout="centered")
st.markdown("### FAST LABOR")

# เว้นระยะห่างเล็กน้อย
st.markdown("## ")
st.markdown("## Payment")

# ตัวเลือกการชำระเงิน
payment_method = st.radio(
    "",
    ("Mobile Banking", "Credit card", "QR Code")
)

# ปุ่มด้านล่าง
col1, col2 = st.columns([1, 1])

with col1:
    cancel = st.button("Cancel")
with col2:
    confirm = st.button("Confirm")

# ถ้ากด Confirm
if confirm:
    st.session_state["selected_payment_method"] = payment_method
    st.success(f"✅ You selected: {payment_method}")
    st.markdown("คลิกเพื่อดำเนินการต่อไปยังหน้า Payment Success 👇")
    st.page_link("pages/payment_success.py", label="➡️ ไปยัง Payment Success", icon="💳")

# ถ้ากด Cancel
if cancel:
    st.warning("❌ Payment cancelled.")
