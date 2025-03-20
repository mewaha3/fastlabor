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

# ✅ ตั้งค่า Google Sheets API (ใช้ st.secrets)
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

try:
    # ✅ โหลด Credentials จาก Streamlit Secrets (สำหรับ Cloud)
    if "gcp" in st.secrets and "credentials" in st.secrets["gcp"]:
        credentials_dict = json.loads(st.secrets["gcp"]["credentials"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
    else:
        # ✅ โหลด Credentials จากไฟล์ (สำหรับ Local)
        creds = ServiceAccountCredentials.from_json_keyfile_name("pages/credentials.json", scope)

    # ✅ เชื่อมต่อ Google Sheets
    client = gspread.authorize(creds)
    sheet = client.open("fastlabor").sheet1

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

# ✅ ดึงข้อมูลจาก Google Sheets ตาม email ที่ล็อกอิน
email = st.session_state["email"]
user_data = df[df["email"] == email]

if user_data.empty:
    st.error("❌ ไม่พบข้อมูลผู้ใช้")
    st.stop()

user = user_data.iloc[0]  # ดึงข้อมูลแถวแรกของผู้ใช้

# ✅ UI หน้า Profile
st.set_page_config(page_title="Profile", page_icon="👤", layout="centered")
st.title("Profile")

st.markdown("#### Personal Information")
first_name = st.text_input("First name *", user.get("first_name", ""))
last_name = st.text_input("Last name *", user.get("last_name", ""))

national_id = st.text_input("National ID *", user.get("national_id", ""), disabled=True)
dob = st.date_input("Date of Birth *", pd.to_datetime(user.get("dob", "2000-01-01")))

gender_options = ["Male", "Female", "Other"]
gender = st.selectbox("Gender *", gender_options, index=gender_options.index(user.get("gender", "Male")) if user.get("gender") in gender_options else 0)

nationality = st.text_input("Nationality *", user.get("nationality", ""))

st.markdown("#### Address Information")
address = st.text_area("Address (House Number, Road, Soi.) *", user.get("address", ""))

# ✅ Province (เลือกแล้วอัปเดต District)
province_names = ["Select Province"] + provinces["name_th"].tolist()
selected_province = st.selectbox("Province *", province_names, index=province_names.index(user.get("province", "Select Province")) if user.get("province") in province_names else 0)

# ✅ District (กรองตามจังหวัดที่เลือก)
if selected_province != "Select Province":
    province_id = provinces[provinces["name_th"] == selected_province]["id"].values[0]
    filtered_districts = ["Select District"] + districts[districts["province_id"] == province_id]["name_th"].tolist()
else:
    filtered_districts = ["Select District"]

selected_district = st.selectbox("District *", filtered_districts, index=filtered_districts.index(user.get("district", "Select District")) if user.get("district") in filtered_districts else 0)

# ✅ Subdistrict & Zip Code (กรองตามอำเภอที่เลือก)
if selected_district != "Select District":
    district_id = districts[districts["name_th"] == selected_district]["id"].values[0]
    filtered_subdistricts = subdistricts[subdistricts["amphure_id"] == district_id]

    subdistrict_names = ["Select Subdistrict"] + filtered_subdistricts["name_th"].tolist()
    zip_codes = filtered_subdistricts.set_index("name_th")["zip_code"].to_dict()
else:
    subdistrict_names = ["Select Subdistrict"]
    zip_codes = {}

selected_subdistrict = st.selectbox("Subdistrict *", subdistrict_names, index=subdistrict_names.index(user.get("subdistrict", "Select Subdistrict")) if user.get("subdistrict") in subdistrict_names else 0)

zip_code = st.text_input("Zip Code *", user.get("zip_code", ""), disabled=True)

st.markdown("#### Skill Information")
skills = ["Skill 1", "Skill 2", "Skill 3", "Skill 4", "Skill 5"]
selected_skills = st.multiselect("Skill *", skills, user.get("skills", "").split(", ") if user.get("skills") else [])

additional_skill = st.text_area("Additional Skill", user.get("additional_skill", ""))

# ✅ แสดง email (อ่านอย่างเดียว)
st.text_input("Email address *", user["email"], disabled=True)

# ✅ ปุ่ม Submit
if st.button("Save Profile"):
    try:
        # ค้นหาแถวที่ต้องแก้ไข
        row_index = user_data.index[0] + 2  # แถวใน Google Sheets (index เริ่มที่ 0 + header)
        
        # ✅ อัปเดตข้อมูลใน Google Sheets
        sheet.update(f"A{row_index}:N{row_index}", [[
            first_name, last_name, national_id, str(dob), gender, nationality,
            address, selected_province, selected_district, selected_subdistrict, zip_code, email, ", ".join(selected_skills), additional_skill
        ]])

        st.success("✅ บันทึกข้อมูลสำเร็จ!")
    except Exception as e:
        st.error(f"❌ เกิดข้อผิดพลาด: {e}")

# ✅ ปุ่มกลับไปหน้า Home
st.page_link("pages/home.py", label="Go to Homepage", icon="🏠")
