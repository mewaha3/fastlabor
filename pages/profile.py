import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

# ✅ ตั้งค่า Google Sheets API
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("pages/credentials.json", scope)
client = gspread.authorize(creds)

# ✅ เปิด Google Sheet
sheet = client.open("fastlabor").sheet1  # เปลี่ยนเป็นชื่อ Google Sheet ของคุณ

# ✅ โหลดข้อมูลทั้งหมดจาก Google Sheets
data = sheet.get_all_records()
df = pd.DataFrame(data)

# ✅ ตรวจสอบว่าผู้ใช้ล็อกอินหรือยัง
if "email" not in st.session_state:
    st.warning("🔒 กรุณาล็อกอินก่อน")
    st.stop()

# ✅ ค้นหาข้อมูลของผู้ใช้ตาม email
email = st.session_state["email"]
user_data = df[df["email"] == email]

if user_data.empty:
    st.error("❌ ไม่พบข้อมูลผู้ใช้")
    st.stop()

user = user_data.iloc[0]  # ดึงข้อมูลแถวแรกของผู้ใช้

# ✅ ตรวจสอบว่ามีคอลัมน์ 'skills', 'password' และ 'additional_skill' หรือไม่
if "skills" not in user:
    user["skills"] = ""
if "password" not in user:
    user["password"] = ""  # ป้องกันข้อมูล password หายไป
if "additional_skill" not in user:
    user["additional_skill"] = ""

# ✅ UI หน้า Profile
st.set_page_config(page_title="Profile", page_icon="👤", layout="centered")
st.title("Profile")

# ✅ ฟอร์มแก้ไขข้อมูล
with st.form("profile_form"):
    first_name = st.text_input("First name *", user["first_name"])
    last_name = st.text_input("Last name *", user["last_name"])
    dob = st.date_input("Date of Birth *", pd.to_datetime(user["dob"]))
    gender = st.selectbox("Gender *", ["Male", "Female", "Other"], index=["Male", "Female", "Other"].index(user["gender"]))
    nationality = st.text_input("Nationality *", user["nationality"])
    member_type = st.selectbox("Member Type *", ["Employer", "Worker"], index=["Employer", "Worker"].index(user["member_type"]))
    address = st.text_area("Address (House Number, Road, Soi.)", user["address"])
    
    province = st.text_input("Province *", user["province"])
    district = st.text_input("District *", user["district"])
    subdistrict = st.text_input("Subdistrict *", user["subdistrict"])
    zip_code = st.text_input("Zip Code *", user["zip_code"])
    
    # ✅ ฟอร์มเลือกทักษะ (Skill)
    skills = ["Skill 1", "Skill 2", "Skill 3", "Skill 4", "Skill 5"]
    selected_skills = st.multiselect("Skill *", skills, user["skills"].split(", ") if user["skills"] else [])

    additional_skill = st.text_area("Additional Skill", user["additional_skill"])
    
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
        sheet.update(f"A{row_index}:O{row_index}", [[
            first_name, last_name, str(dob), gender, nationality, member_type, address,
            province, district, subdistrict, zip_code, email, user["password"], ", ".join(selected_skills), additional_skill
        ]])

        st.success("✅ บันทึกข้อมูลสำเร็จ!")
    except Exception as e:
        st.error(f"❌ เกิดข้อผิดพลาด: {e}")

# ✅ ปุ่มกลับหน้า Home
st.page_link("pages/home.py", label="Go to Homepage", icon="🏠")
