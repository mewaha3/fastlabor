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
st.image("https://i.ibb.co/7NFFZBK/passport-image.png", use_column_width=True)

# Sample data
employees = [
    {"name": "Employee No.1", "gender": "ชาย", "skill": "Weld", "priority": 1, "status": "Decline"},
    {"name": "Employee No.2", "gender": "หญิง", "skill": "Paint", "priority": 3, "status": "Accepted"},
    {"name": "Employee No.3", "gender": "ชาย", "skill": "Weld", "priority": 4, "status": "On Queue"},
    {"name": "Employee No.4", "gender": "หญิง", "skill": "Sew", "priority": 5, "status": ""},
    {"name": "Employee No.5", "gender": "หญิง", "skill": "Solid", "priority": 2, "status": "Decline"},
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
for emp in employees:
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
        st.markdown("----")

