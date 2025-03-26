import streamlit as st
from datetime import datetime

st.set_page_config(layout="centered")

# Header & Navigation
st.markdown("""
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
    <div><strong>FAST LABOR</strong></div>
    <div>
        <a href="#" style="margin-right: 20px;">Find Job</a>
        <a href="#" style="margin-right: 20px;">My Job</a>
        <a href="#" style="background-color: black; color: white; padding: 5px 10px; border-radius: 4px;">Profile</a>
    </div>
</div>
""", unsafe_allow_html=True)

# Title
st.markdown("## Job Detail")
st.image("https://i.ibb.co/kq4bnfK/handshake.png", width=200)

# Job status dropdown
job_status = st.selectbox("Job Status", ["In-Progress", "Job Done"])

# Input fields
col1, col2 = st.columns(2)
with col1:
    job_type = st.text_input("Job Type")
with col2:
    job_title = st.text_input("Job Short")

col3, col4 = st.columns(2)
with col3:
    start_date = st.date_input("Start Date", format="DD/MM/YYYY")
with col4:
    end_date = st.date_input("End Date", format="DD/MM/YYYY")

col5, col6 = st.columns(2)
with col5:
    start_time = st.time_input("Start Time", value=datetime.strptime("08:00", "%H:%M").time())
with col6:
    end_time = st.time_input("End Time", value=datetime.strptime("17:00", "%H:%M").time())

job_address = st.text_area("Job Address (House No, Road, District)", placeholder="Enter job location or message")

col7, col8 = st.columns(2)
with col7:
    province = st.selectbox("Province", ["Bangkok", "Chiang Mai", "Khon Kaen"])
with col8:
    district = st.selectbox("District", ["District A", "District B", "District C"])

col9, col10 = st.columns(2)
with col9:
    subdistrict = st.selectbox("Subdistrict", ["Sub A", "Sub B", "Sub C"])
with col10:
    gender = st.selectbox("Gender", ["Any", "Male", "Female"])

col11, col12 = st.columns(2)
with col11:
    job_salary = st.text_input("Job Salary", "500 THB")
with col12:
    salary_range = st.text_input("Range Salary", "500 - 700 THB")

# Selected Employees
st.markdown("#### Employee")
st.write("👤 Employee No.1")
st.write("👤 Employee No.2")

# ปุ่มชำระเงิน
st.page_link("pages/payment.py", label="💳 ชำระเงิน", icon="💰")

# ✅ ปุ่ม Job Done (นายจ้าง และ ลูกจ้าง)
col_done1, col_done2 = st.columns(2)

with col_done1:
    if st.button("✅ Job Done นายจ้าง"):
        st.success("✅ Job details saved by employer!")
        st.markdown("""
            <meta http-equiv="refresh" content="0; url=./review_employee" />
        """, unsafe_allow_html=True)

with col_done2:
    if st.button("🧑‍🔧 Job Done ลูกจ้าง"):
        st.success("🎉 Job details saved by employee!")
        st.markdown("""
            <meta http-equiv="refresh" content="0; url=./waiting_payment" />
        """, unsafe_allow_html=True)

# ปุ่มกลับหน้าแรก
st.page_link("pages/home.py", label="Go to Homepage", icon="🏠")
