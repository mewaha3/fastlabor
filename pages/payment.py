import streamlit as st

# 1) Page Config
st.set_page_config(page_title="Payment", layout="centered")

# 2) Header
st.markdown("### FAST LABOR")
st.markdown("## Payment")

# 3) Payment method selection
payment_method = st.radio(
    "",
    ("Mobile Banking", "Credit card", "QR Code")
)

# 4) Buttons
col1, col2 = st.columns(2)
with col1:
    if st.button("Cancel"):
        st.warning("❌ ยกเลิกการชำระเงิน")
with col2:
    if st.button("Confirm"):
        # Store selected method
        st.session_state["selected_payment_method"] = payment_method
        st.success(f"✅ คุณเลือกวิธีชำระเงิน: {payment_method}")
        # Redirect to Payment Success page
        st.switch_page("pages/payment_success.py")
