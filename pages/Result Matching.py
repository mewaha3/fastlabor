import streamlit as st

st.set_page_config(layout="centered")

# Header
st.markdown("### FAST LABOR")
st.markdown("""
<style>
.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30px;
}
.nav-right a {
    margin-left: 20px;
    text-decoration: none;
    font-weight: bold;
}
</style>
<div class="header">
    <div><strong>FAST LABOR</strong></div>
    <div class="nav-right">
        <a href="#">Find Job</a>
        <a href="#">My Job</a>
        <a href="#" style="background: black; color: white; padding: 4px 10px; border-radius: 4px;">Profile</a>
    </div>
</div>
""", unsafe_allow_html=True)

# Title & Subtitle
st.markdown("## Result matching")
st.markdown("List of employee who was matching with job")

# Image (ใช้ภาพประกอบผลลัพธ์การอนุมัติ)
st.image("https://i.ibb.co/7NFFZBK/passport-image.png", use_column_width=True)

# ข้อมูลพนักงานจำลอง
employees = [
    {"name": "Employee No.1", "gender": "ชาย", "skill": "Weld", "priority": 1},
    {"name": "Employee No.2", "gender": "หญิง", "skill": "Paint", "priority": 3},
    {"name": "Employee No.3", "gender": "ชาย", "skill": "Weld", "priority": 4},
    {"name": "Employee No.4", "gender": "หญิง", "skill": "Sew", "priority": 5},
    {"name": "Employee No.5", "gender": "หญิง", "skill": "Solid", "priority": 2},
]

st.markdown("---")

# Form
updated_priorities = {}

for emp in employees:
    with st.expander(emp["name"]):
        st.write(f"เพศ: {emp['gender']}")
        st.write(f"ทักษะ: {emp['skill']}")
        priority = st.selectbox(
            f"Priority", 
            options=[1, 2, 3, 4, 5],
            index=emp["priority"] - 1,
            key=emp["name"]
        )
        updated_priorities[emp["name"]] = priority

# Confirm Button
if st.button("Confirm"):
    st.success("Your matching priorities have been saved!")
    st.write("### Updated Priorities")
    st.write(updated_priorities)
