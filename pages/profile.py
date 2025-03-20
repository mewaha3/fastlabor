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

# ✅ ตั้งค่า session_state เพื่ออัปเดตค่าอัตโนมัติ
if "selected_province" not in st.session_state:
    st.session_state.selected_province = "Select Province"
if "selected_district" not in st.session_state:
    st.session_state.selected_district = "Select District"
if "selected_subdistrict" not in st.session_state:
    st.session_state.selected_subdistrict = "Select Subdistrict"
if "zip_code" not in st.session_state:
    st.session_state.zip_code = ""

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

# ✅ Province (เลือกแล้วอัปเดต District)
province_names = ["Select Province"] + provinces["name_th"].tolist()
selected_province = st.selectbox("Province *", province_names, index=province_names.index(st.session_state.selected_province))

# 🔹 ถ้า Province เปลี่ยนค่า ให้รีเซ็ต District และ Subdistrict
if selected_province != st.session_state.selected_province:
    st.session_state.selected_province = selected_province
    st.session_state.selected_district = "Select District"
    st.session_state.selected_subdistrict = "Select Subdistrict"
    st.session_state.zip_code = ""
    st.rerun()

# ✅ District (กรองตามจังหวัดที่เลือก)
if selected_province != "Select Province":
    province_id = provinces[provinces["name_th"] == selected_province]["id"].values[0]
    filtered_districts = ["Select District"] + districts[districts["province_id"] == province_id]["name_th"].tolist()
else:
    filtered_districts = ["Select District"]

selected_district = st.selectbox("District *", filtered_districts, index=filtered_districts.index(st.session_state.selected_district))

# 🔹 ถ้า District เปลี่ยนค่า ให้รีเซ็ต Subdistrict
if selected_district != st.session_state.selected_district:
    st.session_state.selected_district = selected_district
    st.session_state.selected_subdistrict = "Select Subdistrict"
    st.session_state.zip_code = ""
    st.rerun()

# ✅ Subdistrict & Zip Code (กรองตามอำเภอที่เลือก)
if selected_district != "Select District":
    district_id = districts[districts["name_th"] == selected_district]["id"].values[0]
    filtered_subdistricts = subdistricts[subdistricts["amphure_id"] == district_id]

    subdistrict_names = ["Select Subdistrict"] + filtered_subdistricts["name_th"].tolist()
    zip_codes = filtered_subdistricts.set_index("name_th")["zip_code"].to_dict()
else:
    subdistrict_names = ["Select Subdistrict"]
    zip_codes = {}

selected_subdistrict = st.selectbox("Subdistrict *", subdistrict_names, index=subdistrict_names.index(st.session_state.selected_subdistrict))

# 🔹 ถ้า Subdistrict เปลี่ยนค่า ให้ Zip Code อัปเดต
if selected_subdistrict != st.session_state.selected_subdistrict:
    st.session_state.selected_subdistrict = selected_subdistrict
    st.session_state.zip_code = zip_codes.get(selected_subdistrict, "")
    st.rerun()

zip_code = st.text_input("Zip Code *", st.session_state.zip_code, disabled=True)

st.markdown("#### Skill Information")
skills = ["Skill 1", "Skill 2", "Skill 3", "Skill 4", "Skill 5"]
selected_skills = st.multiselect("Skill *", skills, [])

additional_skill = st.text_area("Additional Skill", placeholder="Enter additional skills")

# ✅ แสดง email (อ่านอย่างเดียว)
email = st.text_input("Email address *", st.session_state.get("email", ""), disabled=True)

# ✅ **เช็คว่าทุกช่องกรอกครบหรือไม่**
required_fields = [first_name, last_name, national_id, dob, gender, nationality,
                   address, selected_province, selected_district, selected_subdistrict, st.session_state.zip_code, email]

all_fields_filled = all(bool(str(field).strip()) for field in required_fields)

if not all_fields_filled:
    st.warning("⚠️ กรุณากรอกข้อมูลทุกช่องให้ครบถ้วนก่อนกด Submit")

# ✅ ปุ่ม Submit (ปิดใช้งานถ้ายังกรอกไม่ครบ)
submit_button = st.button("Submit", disabled=not all_fields_filled)

# ✅ ถ้ากรอกครบและกด Submit ให้บันทึกข้อมูลลง Google Sheets
if submit_button:
    try:
        sheet.append_row([first_name, last_name, national_id, str(dob), gender, nationality,
                          address, selected_province, selected_district, selected_subdistrict, st.session_state.zip_code, email, ", ".join(selected_skills), additional_skill])
        st.success(f"🎉 Welcome, {first_name}! You have successfully registered.")
    except Exception as e:
        st.error(f"❌ ไม่สามารถบันทึกข้อมูลได้: {e}")

# ✅ ปุ่มกลับไปหน้าล็อกอิน
st.page_link("app.py", label="⬅️ Back to Login", icon="🔙")
