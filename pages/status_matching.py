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
st.markdown("## Status matching")
st.markdown("List of employee who was matching with job")

# Image
st.image("image.png", width=150)

# Sample data
employees = [
    {"name": "Employee No.1", "gender": "ชาย",
        "skill": "ขับรถส่งของ",
        "priority": 1,
        "area": "กรุงเทพฯ",
     "status": "Decline"},
    {"name": "Employee No.2", "gender": "ชาย",
        "skill": "ขับรถตู้",
        "priority": 2,
        "area": "นนทบุรี",
     "status": "Accepted"},
    {"name": "Employee No.3", "gender": "ชาย",
        "skill": "ขับรถผู้บริหาร",
        "priority": 3,
        "area": "สาทร, กรุงเทพฯ",
     "status": "On Queue"},
    {"name": "Employee No.4", "gender": "หญิง",
        "skill": "ขับมอเตอร์ไซค์ส่งของ",
        "priority": 4,
        "area": "ลาดพร้าว, กรุงเทพฯ",
     "status": ""},
    {"name": "Employee No.5", "gender": "ชาย",
        "skill": "ขับรถผู้บริหาร",
        "priority": 2,
        "area": "สาทร, กรุงเทพฯ",
     "status": "Decline"},
]

# Status color helper
def get_status_color(status):
    status = status.lower()
    if status == "accepted":
        return "green"
    elif status == "on queue":
        return "orange"
    elif status == "decline":
        return "red"
    elif status == "":
        return "gray"
    return "black"

# UI for each employee
st.markdown("---")
for i, emp in enumerate(employees):
    with st.container():
        st.markdown(f"**{emp['name']}**")
        st.write(f"เพศ: {emp['gender']}")
        st.write(f"ทักษะ: {emp['skill']}")
        st.write(f"Priority: {emp['priority']}")
        
        color = get_status_color(emp["status"])
        status_text = emp["status"] if emp["status"] else "No Status"
        st.markdown(
            f"<span style='padding: 4px 12px; background-color: {color}; color: white; border-radius: 5px;'>"
            f"{status_text}</span>",
            unsafe_allow_html=True
        )

        # ✅ แสดงปุ่มเฉพาะถ้า status = Accepted
        if emp["status"].lower() == "accepted":
            st.page_link("pages/job_detail.py", label="💳 Job Detail")

        st.markdown("----")
