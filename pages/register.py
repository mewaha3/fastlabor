import streamlit as st
import gspread
import json
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

# ✅ โหลดข้อมูลจังหวัด อำเภอ ตำบล และรหัสไปรษณีย์
import requests

url = "https://raw.githubusercontent.com/kongvut/thai-province-data/master/api_province.json"
province_data = requests.get(url).json()

# ✅ สร้าง Dictionary ของจังหวัด -> อำเภอ -> ตำบล -> รหัสไปรษณีย์
province_dict = {p["name_th"]: {} for p in province_data}

for p in province_data:
    province_name = p["name_th"]
    for a in p["amphure"]:
        district_name = a["name_th"]
        province_dict[province_name][district_name] = {}
        for t in a["tambon"]:
            subdistrict_name = t["name_th"]
            zip_code = t["zip_code"]
            province_dict[province_name][district_name][subdistrict_name] = zip_code

# ✅ ตั้งค่า Google Sheets API
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

try:
    if "gcp" in st.secrets:
        credentials_dict = json.loads(st.secrets["gcp"]["credentials"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
    else:
        creds = ServiceAccountCredentials.from_json_keyfile_name("pages/credentials.json", scope)

    client = gspread.authorize(creds)
    spreadsheet = client.open("fastlabor")
    try:
        sheet = spreadsheet.worksheet("register")
    except gspread.exceptions.WorksheetNotFound:
        sheet = spreadsheet.add_worksheet(title="register", rows="1000", cols="12")

except Exception as e:
    st.error(f"❌ ไม่สามารถเชื่อมต่อกับ Google Sheets: {e}")
    st.stop()

# ✅ ตั้งค่าหน้า Streamlit
st.set_page_config(page_title="New Member Registration", page_icon="📝", layout="centered")

st.image("image.png", width=150)
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

# ✅ เลือกจังหวัด
province_list = list(province_dict.keys())
province = st.selectbox("Province *", ["Select Province"] + province_list)

# ✅ อัปเดต District เมื่อ Province เปลี่ยน
district_list = ["Select District"]
if province != "Select Province":
    district_list += list(province_dict[province].keys())

district = st.selectbox("District *", district_list)

# ✅ อัปเดต Subdistrict เมื่อ District เปลี่ยน
subdistrict_list = ["Select Subdistrict"]
zip_code = ""

if district != "Select District":
    subdistrict_list += list(province_dict[province][district].keys())

subdistrict = st.selectbox("Subdistrict *", subdistrict_list)

# ✅ อัปเดต Zip Code เมื่อ Subdistrict เปลี่ยน
if subdistrict != "Select Subdistrict":
    zip_code = province_dict[province][district][subdistrict]

st.text_input("Zip Code *", zip_code, disabled=True)

st.markdown("#### Account Information")
email = st.text_input("Email address *", placeholder="Enter your email")
password = st.text_input("Password *", type="password", placeholder="Enter your password")

# ✅ ตรวจสอบว่าทุกช่องถูกกรอกครบ
required_fields = [first_name, last_name, national_id, dob, gender, nationality,
                   address, province, district, subdistrict, zip_code, email, password]

all_fields_filled = all(bool(str(field).strip()) for field in required_fields) and province != "Select Province" and district != "Select District" and subdistrict != "Select Subdistrict"

if not all_fields_filled:
    st.warning("⚠️ กรุณากรอกข้อมูลทุกช่องให้ครบถ้วนก่อนกด Submit")

# ✅ ปิดปุ่ม Submit ถ้ายังกรอกไม่ครบ
submit_button = st.button("Submit", disabled=not all_fields_filled)

# ✅ ถ้ากรอกครบและกด Submit ให้บันทึกข้อมูลลง Google Sheets
if submit_button:
    try:
        sheet.append_row([first_name, last_name, national_id, str(dob), gender, nationality,
                          address, province, district, subdistrict, zip_code, email, password])
        st.success(f"🎉 Welcome, {first_name}! You have successfully registered.")
    except Exception as e:
        st.error(f"❌ ไม่สามารถบันทึกข้อมูลได้: {e}")

st.page_link("app.py", label="⬅️ Back to Login", icon="🔙")
