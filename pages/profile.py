import streamlit as st
import gspread
import json
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

# ✅ โหลดข้อมูลจังหวัด อำเภอ ตำบล และรหัสไปรษณีย์
@st.cache_data
def load_location_data():
    url_province = "https://raw.githubusercontent.com/kongvut/thai-province-data/master/api_province.json"
    url_district = "https://raw.githubusercontent.com/kongvut/thai-province-data/master/api_amphure.json"
    url_subdistrict = "https://raw.githubusercontent.com/kongvut/thai-province-data/master/api_tambon.json"

    provinces = pd.read_json(url_province)
    districts = pd.read_json(url_district)
    subdistricts = pd.read_json(url_subdistrict)

    return provinces, districts, subdistricts

provinces, districts, subdistricts = load_location_data()

# ✅ ตั้งค่า Google Sheets API
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

try:
    if "gcp" in st.secrets and "credentials" in st.secrets["gcp"]:
        credentials_dict = json.loads(st.secrets["gcp"]["credentials"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
    else:
        creds = ServiceAccountCredentials.from_json_keyfile_name("pages/credentials.json", scope)

    client = gspread.authorize(creds)
    sheet = client.open("fastlabor").sheet1

    # ✅ โหลดข้อมูลทั้งหมดจาก Google Sheets
    data = sheet.get_all_records()
    df = pd.DataFrame(data)

    # ✅ ตรวจสอบโครงสร้างคอลัมน์
    required_columns = [
        "First Name", "Last Name", "National ID", "DOB", "Gender", "Nationality",
        "Address", "Province", "District", "Subdistrict", "Zip Code",
        "Email", "Password", "Skills", "Additional Skill"
    ]

    if df.columns.tolist() != required_columns:
        st.error(f"❌ คอลัมน์ใน Google Sheets ไม่ตรงกับที่ต้องการ!\n\nพบ: {df.columns.tolist()}\n\nต้องการ: {required_columns}")
        st.stop()

except Exception as e:
    st.error(f"❌ ไม่สามารถเชื่อมต่อกับ Google Sheets: {e}")
    st.stop()

# ✅ ตรวจสอบว่าผู้ใช้ล็อกอินหรือยัง
if "email" not in st.session_state or not st.session_state["email"]:
    st.warning("🔒 กรุณาล็อกอินก่อน")
    st.stop()

# ✅ ดึงข้อมูลจาก Google Sheets ตาม email ที่ล็อกอิน
email = st.session_state["email"]
user_data = df[df["Email"] == email]

if user_data.empty:
    st.error("❌ ไม่พบข้อมูลผู้ใช้")
    st.stop()

user = user_data.iloc[0]  # ดึงข้อมูลแถวแรกของผู้ใช้

# ✅ UI หน้า Profile
st.set_page_config(page_title="Profile", page_icon="👤", layout="centered")
st.title("Profile")

st.markdown("#### Personal Information")
first_name = st.text_input("First name *", user.get("First Name", ""))
last_name = st.text_input("Last name *", user.get("Last Name", ""))

national_id = st.text_input("National ID *", user.get("National ID", ""), disabled=True)
dob = st.date_input("Date of Birth *", pd.to_datetime(user.get("DOB", "2000-01-01")))

gender_options = ["Male", "Female", "Other"]
gender = st.selectbox("Gender *", gender_options, index=gender_options.index(user.get("Gender", "Male")) if user.get("Gender") in gender_options else 0)

nationality = st.text_input("Nationality *", user.get("Nationality", ""))

st.markdown("#### Address Information")
address = st.text_area("Address (House Number, Road, Soi.) *", user.get("Address", ""))

province = st.text_input("Province *", user.get("Province", ""))
district = st.text_input("District *", user.get("District", ""))
subdistrict = st.text_input("Subdistrict *", user.get("Subdistrict", ""))
zip_code = st.text_input("Zip Code *", user.get("Zip Code", ""), disabled=True)

st.markdown("#### Skill Information")
skills = ["Skill 1", "Skill 2", "Skill 3", "Skill 4", "Skill 5"]
selected_skills = st.multiselect("Skill *", skills, user.get("Skills", "").split(", ") if user.get("Skills") else [])

additional_skill = st.text_area("Additional Skill", user.get("Additional Skill", ""))

# ✅ แสดง email (อ่านอย่างเดียว)
st.text_input("Email address *", user["Email"], disabled=True)

# ✅ ปุ่ม Submit
if st.button("Save Profile"):
    try:
        row_index = user_data.index[0] + 2  # คำนวณแถวของผู้ใช้ใน Google Sheets

        # ✅ ใช้ลำดับคอลัมน์ที่ถูกต้อง (Skills & Additional Skill ถัดจาก Password)
        updated_values = [
            first_name, last_name, national_id, str(dob), gender, nationality,
            address, province, district, subdistrict, zip_code, email,
            user.get("Password", ""),  # ✅ ค่าของ Password คงเดิม
            ", ".join(selected_skills),  # ✅ Skills คอลัมน์นี้
            additional_skill  # ✅ Additional Skill คอลัมน์นี้
        ]

        # ✅ อัปเดตข้อมูลใน Google Sheets
        sheet.update(f"A{row_index}:O{row_index}", [updated_values])

        st.success("✅ บันทึกข้อมูลสำเร็จ!")
    except Exception as e:
        st.error(f"❌ เกิดข้อผิดพลาด: {e}")

# ✅ ปุ่มกลับไปหน้า Home
st.page_link("pages/home.py", label="Go to Homepage", icon="🏠")
