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

except Exception as e:
    st.error(f"❌ ไม่สามารถเชื่อมต่อกับ Google Sheets: {e}")
    st.stop()

# ✅ โหลดข้อมูลจังหวัด อำเภอ ตำบล และรหัสไปรษณีย์
@st.cache_data
def load_location_data():
    url = "https://raw.githubusercontent.com/kongvut/thai-province-data/master/api_province.json"
    provinces = pd.read_json(url)

    url_amphur = "https://raw.githubusercontent.com/kongvut/thai-province-data/master/api_amphure.json"
    districts = pd.read_json(url_amphur)

    url_tambon = "https://raw.githubusercontent.com/kongvut/thai-province-data/master/api_tambon.json"
    subdistricts = pd.read_json(url_tambon)

    return provinces, districts, subdistricts

provinces, districts, subdistricts = load_location_data()

# ✅ ตั้งค่าหน้า Streamlit
st.set_page_config(page_title="New Member Registration", page_icon="📝", layout="centered")

st.image("image.png", width=150)  # แสดงโลโก้
st.title("New Member")

# ✅ ฟอร์มลงทะเบียน
with st.form(key="register_form"):
    st.markdown("#### Personal Information")
    first_name = st.text_input("First name *", placeholder="Enter your first name")
    last_name = st.text_input("Last name *", placeholder="Enter your last name")
    
    # ✅ National ID (รับเฉพาะตัวเลข 13 หลัก)
    national_id = st.text_input("National ID *", placeholder="Enter your ID number")
    if national_id and (not national_id.isdigit() or len(national_id) != 13):
        st.error("❌ National ID ต้องเป็นตัวเลข 13 หลักเท่านั้น")

    dob = st.date_input("Date of Birth *")
    gender = st.selectbox("Gender *", ["Male", "Female", "Other"])
    nationality = st.text_input("Nationality *", placeholder="Enter your nationality")

    st.markdown("#### Address Information")
    address = st.text_area("Address (House Number, Road, Soi.) *", placeholder="Enter your address")

    # ✅ Province
    province_names = provinces["name_th"].tolist()
    province = st.selectbox("Province *", ["Select Province"] + province_names)

    # ✅ District (กรองตามจังหวัดที่เลือก)
    if province != "Select Province":
        province_id = provinces[provinces["name_th"] == province]["id"].values[0]
        district_names = districts[districts["province_id"] == province_id]["name_th"].tolist()
        district = st.selectbox("District *", ["Select District"] + district_names)
    else:
        district = st.selectbox("District *", ["Select District"])

    # ✅ Subdistrict & Zip Code (กรองตามอำเภอที่เลือก)
    if district != "Select District":
        district_id = districts[districts["name_th"] == district]["id"].values[0]
        subdistrict_data = subdistricts[subdistricts["amphure_id"] == district_id]
        subdistrict_names = subdistrict_data["name_th"].tolist()
        zip_codes = subdistrict_data["zip_code"].tolist()
        subdistrict = st.selectbox("Subdistrict *", ["Select Subdistrict"] + subdistrict_names)

        # ✅ ดึงรหัสไปรษณีย์อัตโนมัติจากตำบล
        if subdistrict != "Select Subdistrict":
            subdistrict_index = subdistrict_names.index(subdistrict)
            zip_code = zip_codes[subdistrict_index]
        else:
            zip_code = ""
    else:
        subdistrict = st.selectbox("Subdistrict *", ["Select Subdistrict"])
        zip_code = ""

    st.text_input("Zip Code *", zip_code, disabled=True)  # รหัสไปรษณีย์แสดงเฉพาะค่าที่เลือก

    st.markdown("#### Account Information")
    email = st.text_input("Email address *", placeholder="Enter your email")
    password = st.text_input("Password *", type="password", placeholder="Enter your password")

    # ✅ ตรวจสอบว่าทุกช่องกรอกครบหรือไม่
    required_fields = [first_name, last_name, national_id, str(dob), gender, nationality,
                       address, province, district, subdistrict, zip_code, email, password]

    all_fields_filled = all(bool(field) and field.strip() != "" for field in required_fields)

    if not all_fields_filled:
        st.warning("⚠️ กรุณากรอกข้อมูลทุกช่องให้ครบถ้วนก่อนกด Submit")

    # ✅ ปุ่ม Submit (ปิดใช้งานถ้ายังกรอกไม่ครบ)
    submit_button = st.form_submit_button("Submit", disabled=not all_fields_filled)

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
