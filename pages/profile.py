import streamlit as st
import gspread
import json
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

# ✅ ตั้งค่า Google Sheets API
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

try:
    # ✅ โหลด Credentials จาก Streamlit Secrets (สำหรับ Cloud)
    if "gcp" in st.secrets:
        credentials_dict = json.loads(st.secrets["gcp"]["credentials"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
    else:
        # ✅ โหลด Credentials จากไฟล์ (สำหรับ Local)
        creds = ServiceAccountCredentials.from_json_keyfile_name("pages/credentials.json", scope)

    # ✅ เชื่อมต่อ Google Sheets
    client = gspread.authorize(creds)
    sheet = client.open("fastlabor").sheet1  # เปลี่ยนเป็นชื่อ Google Sheets ของคุณ

    # ✅ โหลดข้อมูลทั้งหมดจาก Google Sheets
    data = sheet.get_all_records()
    df = pd.DataFrame(data)

except Exception as e:
    st.error(f"❌ ไม่สามารถเชื่อมต่อกับ Google Sheets: {e}")
    st.stop()

# ✅ ตรวจสอบว่าผู้ใช้ล็อกอินหรือยัง
if "email" not in st.session_state or not st.session_state["email"]:
    st.warning("🔒 กรุณาล็อกอินก่อน")
    st.stop()

# ✅ ค้นหาข้อมูลของผู้ใช้ตาม email
email = st.session_state["email"]
user_data = df[df["email"] == email]

if user_data.empty:
    st.error("❌ ไม่พบข้อมูลผู้ใช้")
    st.stop()

user = user_data.iloc[0]  # ดึงข้อมูลแถวแรกของผู้ใช้

# ✅ ตรวจสอบว่ามีคอลัมน์ 'skills' และ 'additional_skill' หรือไม่
skills_value = user.get("skills", "")
additional_skill_value = user.get("additional_skill", "")

# ✅ UI หน้า Profile
st.set_page_config(page_title="Profile", page_icon="👤", layout="centered")
st.title("Profile")

# ✅ ฟอร์มแก้ไขข้อมูล (เหมือน Register)
with st.form("profile_form"):
    st.markdown("#### Personal Information")
    first_name = st.text_input("First name *", user.get("first_name", ""))
    last_name = st.text_input("Last name *", user.get("last_name", ""))
    dob = st.date_input("Date of Birth *", pd.to_datetime(user.get("dob", "2000-01-01")))

    gender_options = ["Male", "Female", "Other"]
    gender = st.selectbox("Gender *", gender_options, index=gender_options.index(user.get("gender", "Male")) if user.get("gender") in gender_options else 0)

    nationality = st.text_input("Nationality *", user.get("nationality", ""))

    st.markdown("#### Address Information")
    address = st.text_area("Address (House Number, Road, Soi.)", user.get("address", ""))
    
    province = st.text_input("Province *", user.get("province", ""))
    district = st.text_input("District *", user.get("district", ""))
    subdistrict = st.text_input("Subdistrict *", user.get("subdistrict", ""))
    zip_code = st.text_input("Zip Code *", user.get("zip_code", ""))

    st.markdown("#### Skill Information")
    skills = ["Skill 1", "Skill 2", "Skill 3", "Skill 4", "Skill 5"]
    selected_skills = st.multiselect("Skill *", skills, skills_value.split(", ") if skills_value else [])

    additional_skill = st.text_area("Additional Skill", additional_skill_value)

    # ✅ แสดง email (อ่านอย่างเดียว)
    st.text_input("Email address", user["email"], disabled=True)

    # ✅ ปุ่ม Save Profile
    submit_button = st.form_submit_button("Save Profile")

# ✅ ถ้ากดปุ่ม Save ให้บันทึกข้อมูลลง Google Sheets
if submit_button:
    try:
        # ค้นหาแถวที่ต้องแก้ไข
        row_index = user_data.index[0] + 2  # แถวใน Google Sheets (index เริ่มที่ 0 + header)
        
        # ✅ อัปเดตข้อมูลใน Google Sheets (แก้ไขลำดับให้ตรง)
        sheet.update(f"A{row_index}:N{row_index}", [[
            first_name, last_name, str(dob), gender, nationality, address,
            province, district, subdistrict, zip_code, email, ", ".join(selected_skills), additional_skill
        ]])

        st.success("✅ บันทึกข้อมูลสำเร็จ!")
    except Exception as e:
        st.error(f"❌ เกิดข้อผิดพลาด: {e}")

# ✅ ปุ่มกลับหน้า Home
st.page_link("pages/home.py", label="Go to Homepage", icon="🏠")
