import streamlit as st

st.set_page_config(layout="centered")

# Header & Navigation
st.markdown("""
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
    <div><strong>FAST LABOR</strong></div>
    <div>
        <a href="#" style="margin-right: 20px;">Find Job</a>
        <a href="#" style="margin-right: 20px;">My Job</a>
        <a href="#" style="background-color: black; color: white; padding: 5px 10px; border-radius: 4px;">Profile</a>
    </div>
</div>
""", unsafe_allow_html=True)

# Title
st.markdown("## Find Job")
st.markdown("For generate list of employee who was matching with job")

# Image
st.image("image.png", width=150)

# Sample job list
jobs = [
    {
        "title": "List Job",
        "type": "พนักงานขับรถ",
        "detail": "ขับรถตู้รับส่งคน",
        "date": "11/04/2025",
        "time": "08:00 - 17:00",
        "address": "Nonthaburi",
        "salary": "500 - 600 THB/day",
        "status": ""
    },
    {
        "title": "List Job",
        "type": "พนักงานขับรถส่งของ",
        "detail": "ขับรถส่งสินค้าในเขตกรุงเทพและปริมณฑล",
        "date": "11/04/2025",
        "time": "09:00 - 18:00",
        "address": "Bangkok",
        "salary": "550 - 650 THB/day",
        "status": "Accepted"
    },
    {
        "title": "List Job",
        "type": "พนักงานขับรถผู้บริหาร",
        "detail": "ขับรถรับ-ส่งผู้บริหารตามเวลานัดหมาย",
        "date": "12/04/2025",
        "time": "10:00 - 15:00",
        "address": "Pathumthani",
        "salary": "400 - 500 THB/day",
        "status": ""
    }
]

# Display job cards
for i, job in enumerate(jobs):
    with st.container():
        st.markdown(f"### {job['title']}")
        st.write(f"ประเภทงาน: {job['type']}")
        st.write(f"รายละเอียด: {job['detail']}")
        st.write(f"วันเวลา: {job['date']} | {job['time']}")
        st.write(f"สถานที่: {job['address']}")
        st.write(f"ช่วงรายได้: {job['salary']}")

        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Decline", key=f"decline_{i}"):
                jobs[i]["status"] = "Decline"
        with col2:
            if st.button("Accept", key=f"accept_{i}"):
                jobs[i]["status"] = "Accepted"
                st.session_state["selected_job"] = job  # 👉 ส่งข้อมูลงานไปหน้าใหม่
                st.switch_page("pages/job_detail.py")  # 👉 ไปหน้า job_detail.py

        if job["status"] == "Accepted":
            st.success("✅ Accepted")
        elif job["status"] == "Decline":
            st.error("❌ Declined")

        st.markdown("---")

# Refresh Button
st.markdown(
    """
    <div style='text-align: center; margin-top: 30px;'>
        <button style='background-color: black; color: white; padding: 10px 30px; border-radius: 5px; font-weight: bold;'>
            Refresh Find Job
        </button>
    </div>
    """,
    unsafe_allow_html=True
)
