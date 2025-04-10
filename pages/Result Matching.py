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
st.image("image.png", width=150)

# ข้อมูลพนักงานจำลอง
employees = [
    {"name": "Employee No.1", "gender": "ชาย",
        "skill": "ขับรถส่งของ",
        "priority": 1,
        "area": "กรุงเทพฯ"
    },
    {"name": "Employee No.2", "gender": "ชาย",
        "skill": "ขับรถตู้",
        "priority": 2,
        "area": "นนทบุรี"
    },
    {"name": "Employee No.3", "gender": "ชาย",
        "skill": "ขับรถผู้บริหาร",
        "priority": 3,
        "area": "สาทร, กรุงเทพฯ"
    },
    {"name": "Employee No.4", "gender": "หญิง",
        "skill": "ขับมอเตอร์ไซค์ส่งของ",
        "priority": 4,
        "area": "ลาดพร้าว, กรุงเทพฯ"
    },
    {"name": "Employee No.5", "gender": "ชาย",
        "skill": "ขับรถผู้บริหาร",
        "priority": 2,
        "area": "สาทร, กรุงเทพฯ"
    },

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
    st.switch_page("pages/status_matching.py
")
