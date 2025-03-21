import streamlit as st
import gspread
import json
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

# ✅ ตั้งค่า Google Sheets API
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

try:
    if "gcp" in st.secrets and "credentials" in st.secrets["gcp"]:
        credentials_dict = json.loads(st.secrets["gcp"]["credentials"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
    else:
        creds = ServiceAccountCredentials.from_json_keyfile_name("pages/credentials.json", scope)

    client = gspread.authorize(creds)
    sheet = client.open("fastlabor").sheet1  # เปลี่ยนเป็นชื่อ Google Sheets ของคุณ

    # ✅ โหลดข้อมูลทั้งหมดจาก Google Sheets
    values = sheet.get_all_values()
    headers = values[0]
    df = pd.DataFrame(values[1:], columns=headers)

except Exception as e:
    st.error(f"❌ ไม่สามารถเชื่อมต่อกับ Google Sheets: {e}")
    st.stop()

# ✅ ตรวจสอบว่าผู้ใช้ล็อกอินหรือยัง
if "email" not in st.session_state or not st.session_state["email"]:
    st.warning("🔒 กรุณาล็อกอินก่อน")
    st.stop()

# ✅ ดึงข้อมูลจาก Google Sheets ตามอีเมลที่ล็อกอิน
email = st.session_state["email"]
user_data = df[df["email"] == email]

if user_data.empty:
    st.error("❌ ไม่พบข้อมูลผู้ใช้")
    st.stop()

user = user_data.iloc[0]  # ดึงข้อมูลแถวแรกของผู้ใช้

# ✅ ตั้งค่าหน้าโปรไฟล์
st.set_page_config(page_title="Profile", page_icon="👤", layout="centered")
st.title("Profile")

st.markdown("#### Personal Information")
first_name = st.text_input("First name *", user["First Name"])
last_name = st.text_input("Last name *", user["Last Name"])

national_id = st.text_input("National ID *", user["National ID"], disabled=True)
dob = st.date_input("Date of Birth *", pd.to_datetime(user["DOB"], errors='coerce'))

gender_options = ["Male", "Female", "Other"]
gender = st.selectbox("Gender *", gender_options, index=gender_options.index(user["Gender"]) if user["Gender"] in gender_options else 0)

nationality = st.text_input("Nationality *", user["Nationality"])

st.markdown("#### Address Information")
address = st.text_area("Address (House Number, Road, Soi.) *", user["Address"])

province = st.text_input("Province *", user["Province"])
district = st.text_input("District *", user["District"])
subdistrict = st.text_input("Subdistrict *", user["Subdistrict"])
zip_code = st.text_input("Zip Code *", user["Zip Code"], disabled=True)

st.markdown("#### Skill Information")
skills = ["Skill 1", "Skill 2", "Skill 3", "Skill 4", "Skill 5"]
selected_skills = st.multiselect("Skill *", skills, user["Skills"].split(", ") if user["Skills"] else [])

additional_skill = st.text_area("Additional Skill", user["Additional Skill"])

# ✅ แสดง email (อ่านอย่างเดียว)
st.text_input("Email address *", user["email"], disabled=True)

# ✅ ปุ่ม Submit (บันทึกการเปลี่ยนแปลง)
if st.button("Save Profile"):
    try:
        row_index = user_data.index[0] + 2  # คำนวณแถวของผู้ใช้ใน Google Sheets

        # ✅ ใช้ลำดับคอลัมน์ที่ถูกต้อง
        updated_values = [
            first_name, last_name, national_id, str(dob.date()), gender, nationality,
            address, province, district, subdistrict, zip_code, email,
            user["password"],  # ✅ คงค่า Password เดิมไว้
            ", ".join(selected_skills),  # ✅ Skills
            additional_skill  # ✅ Additional Skill
        ]

        # ✅ อัปเดตข้อมูลใน Google Sheets
        sheet.update(f"A{row_index}:O{row_index}", [updated_values])

        st.success("✅ บันทึกข้อมูลสำเร็จ!")
    except Exception as e:
        st.error(f"❌ เกิดข้อผิดพลาด: {e}")

# ✅ ปุ่มกลับไปหน้า Home
st.page_link("pages/home.py", label="Go to Homepage", icon="🏠")
