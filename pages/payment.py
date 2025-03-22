import streamlit as st

# ตั้งชื่อหัวข้อด้านบน
st.markdown("### FAST LABOR")

# เว้นระยะห่างเล็กน้อย
st.markdown("## ")

# กล่อง Payment
st.markdown("## Payment")

# ตัวเลือกการชำระเงิน
payment_method = st.radio(
    "",
    ("Mobile Banking", "Credit card", "QR Code")
)

# ปุ่มด้านล่าง
col1, col2 = st.columns([1, 1])

with col1:
    cancel = st.button("Cancel", type="secondary")
with col2:
    confirm = st.button("Confirm")

# ถ้ากด Confirm
if confirm:
    st.success(f"You selected: {payment_method}")

# ถ้ากด Cancel
if cancel:
    st.warning("Payment cancelled.")
