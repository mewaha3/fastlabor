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

    # ✅ ตรวจสอบว่า Google Sheet มีอยู่หรือไม่
    spreadsheet = client.open("fastlabor")
    try:
        sheet = spreadsheet.worksheet("register")  # ✅ เปิด Sheet "register"
    except gspread.exceptions.WorksheetNotFound:
        sheet = spreadsheet.add_worksheet(title="register", rows="1000", cols="12")  # ✅ สร้างใหม่ถ้าไม่มี

except Exception as e:
    st.error(f"❌ ไม่สามารถเชื่อมต่อกับ Google Sheets: {e}")
    st.stop()

# ✅ ตั้งค่าหน้า Streamlit
st.set_page_config(page_title="New Member Registration", page_icon="📝", layout="centered")

st.image("image.png", width=150)  # แสดงโลโก้
st.title("New Member")

st.markdown("#### Personal Information")
first_name = st.text_input("First name *", placeholder="Enter your first name")
last_name = st.text_input("Last name *", placeholder="Enter your last name")

national_id = st.text_input("National ID *", placeholder="Enter your ID number (13 digits)")
if national_id and (not national_id.isdigit() or len(national_id) != 13):
    st.error("❌ National ID ต้องเป็นตัวเลข 13 หลักเท่านั้น")

dob = st.date_input("Date of Birth *")
gender = st.selectbox("Gender *", ["Male", "Female", "Other"])
nationality = st.text_input("Nationality *", placeholder="Enter your nationality")

st.markdown("#### Address Information")
address = st.text_area("Address (House Number, Road, Soi.) *", placeholder="Enter your address")

province = st.text_input("Province *", placeholder="Enter province")
district = st.text_input("District *", placeholder="Enter district")
subdistrict = st.text_input("Subdistrict *", placeholder="Enter subdistrict")
zip_code = st.text_input("Zip Code *", placeholder="Enter zip code")

st.markdown("#### Account Information")
email = st.text_input("Email address *", placeholder="Enter your email")
password = st.text_input("Password *", type="password", placeholder="Enter your password")

# ✅ เช็คว่าทุกช่องถูกกรอกครบหรือไม่
required_fields = [first_name, last_name, national_id, dob, gender, nationality,
                   address, province, district, subdistrict, zip_code, email, password]

all_fields_filled = all(bool(str(field).strip()) for field in required_fields)

if not all_fields_filled:
    st.warning("⚠️ กรุณากรอกข้อมูลทุกช่องให้ครบถ้วนก่อนกด Submit")

# ✅ ปุ่ม Submit (ปิดใช้งานถ้ายังกรอกไม่ครบ)
submit_button = st.button("Submit", disabled=not all_fields_filled)

# ✅ ถ้ากรอกครบและกด Submit ให้บันทึกข้อมูลลง Google Sheets
if submit_button:
    try:
        sheet.append_row([first_name, last_name, national_id, str(dob), gender, nationality,
                          address, province, district, subdistrict, zip_code, email, password])
        st.success(f"🎉 Welcome, {first_name}! You have successfully registered.")
    except Exception as e:
        st.error(f"❌ ไม่สามารถบันทึกข้อมูลได้: {e}")

# ✅ ปุ่มกลับไปหน้าล็อกอิน
st.page_link("app.py", label="⬅️ Back to Login", icon="🔙")
