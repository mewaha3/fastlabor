import streamlit as st

# 1) Page Config
st.set_page_config(page_title="Payment Success", layout="centered")

# 2) Header
st.markdown("### FAST LABOR")
st.markdown("## ✅ Payment Success")

# 3) Show chosen payment method, if any
if "selected_payment_method" in st.session_state:
    st.write(f"คุณเลือกวิธีชำระเงิน: **{st.session_state['selected_payment_method']}**")

st.markdown("")  # spacing

# 4) Button to return to Job Detail (preserving session_state)
st.markdown("### ไปสรุปผลการจ้างงาน")
if st.button("📄 ดูรายละเอียดการจ้างงาน"):
    # Switch back to job_detail.py within the same session
    st.switch_page("pages/job_detail.py")
