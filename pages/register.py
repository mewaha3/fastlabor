import streamlit as st
import gspread
import json
import pandas as pd
import re
from oauth2client.service_account import ServiceAccountCredentials

# ✅ ตั้งค่า Google Sheets API
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

try:
    if "gcp" in st.secrets:
        credentials_dict = json.loads(st.secrets["gcp"]["credentials"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
    else:
        creds = ServiceAccountCredentials.from_json_keyfile_name("pages/credentials.json", scope)

    client = gspread.authorize(creds)
    sheet = client.open("fastlabor").sheet1

except Exception as e:
    st.error(f"❌ ไม่สามารถเชื่อมต่อกับ Google Sheets: {e}")
    st.stop()

# ✅ โหลดข้อมูลจาก GitHub
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

# ✅ ใช้ st.session_state เพื่อให้ UI อัปเดตอัตโนมัติ
if "selected_province" not in st.session_state:
    st.session_state.selected_province = "Select Province"
if "selected_district" not in st.session_state:
    st.session_state.selected_district = "Select District"
if "selected_subdistrict" not in st.session_state:
    st.session_state.selected_subdistrict = "Select Subdistrict"

# ✅ ตั้งค่าหน้า Streamlit
st.set_page_config(page_title="New Member Registration", page_icon="📝", layout="centered")

st.image("image.png", width=150)
st.title("New Member")

with st.form(key="register_form"):
    st.markdown("#### Personal Information")
    first_name = st.text_input("First name", placeholder="Enter your first name")
    last_name = st.text_input("Last name", placeholder="Enter your last name")
    
    national_id = st.text_input("National ID (13 digits)", placeholder="Enter your ID number")
    if national_id and not re.match(r'^\d{13}$', national_id):
        st.error("⚠️ National ID ต้องเป็นตัวเลข 13 หลักเท่านั้น")

    dob = st.date_input("Date of Birth")
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    nationality = st.text_input("Nationality", placeholder="Enter your nationality")

    st.markdown("#### Address Information")

    # ✅ เลือกจังหวัด
    province_list = ["Select Province"] + provinces["name_th"].tolist()
    province = st.selectbox("Province", province_list, key="province")

    # ✅ ถ้าผู้ใช้เปลี่ยนจังหวัด รีเซ็ตค่า District และ Subdistrict
    if province != st.session_state.selected_province:
        st.session_state.selected_province = province
        st.session_state.selected_district = "Select District"
        st.session_state.selected_subdistrict = "Select Subdistrict"
        st.rerun()

    # ✅ ค้นหา Province ID
    province_id = provinces[provinces["name_th"] == province]["id"].iloc[0] if province != "Select Province" else None

    # ✅ โหลดอำเภอที่ตรงกับจังหวัดที่เลือก
    district_list = ["Select District"]
    if province_id:
        district_list += districts[districts["province_id"] == province_id]["name_th"].tolist()

    district = st.selectbox("District", district_list, key="district")

    # ✅ ถ้าผู้ใช้เปลี่ยนอำเภอ รีเซ็ตค่า Subdistrict
    if district != st.session_state.selected_district:
        st.session_state.selected_district = district
        st.session_state.selected_subdistrict = "Select Subdistrict"
        st.rerun()

    # ✅ ค้นหา District ID
    district_id = districts[districts["name_th"] == district]["id"].iloc[0] if district != "Select District" else None

    # ✅ โหลดตำบลที่ตรงกับอำเภอที่เลือก
    subdistrict_list = ["Select Subdistrict"]
    if district_id:
        subdistrict_list += subdistricts[subdistricts["amphure_id"] == district_id]["name_th"].tolist()

    subdistrict = st.selectbox("Subdistrict", subdistrict_list, key="subdistrict")

    # ✅ ดึงรหัสไปรษณีย์อัตโนมัติ
    zip_code = subdistricts[subdistricts["name_th"] == subdistrict]["zip_code"].values
    zip_code_value = zip_code[0] if len(zip_code) > 0 else ""
    zip_code = st.text_input("Zip Code", value=zip_code_value, disabled=True)

    st.markdown("#### Account Information")
    email = st.text_input("Email address", placeholder="Enter your email")
    password = st.text_input("Password", type="password", placeholder="Enter your password")

    submit_button = st.form_submit_button("Submit")

# ✅ เช็คข้อมูลก่อนบันทึก
if submit_button:
    if first_name and last_name and re.match(r'^\d{13}$', national_id) and email and password and province != "Select Province" and district != "Select District" and subdistrict != "Select Subdistrict":
        try:
            sheet.append_row([first_name, last_name, national_id, str(dob), gender, nationality,
                              province, district, subdistrict, zip_code, email, password])
            st.success(f"🎉 Welcome, {first_name}! You have successfully registered.")
        except Exception as e:
            st.error(f"⚠️ Failed to save data: {e}")
    else:
        st.error("⚠️ กรุณากรอกข้อมูลที่มีเครื่องหมาย * ให้ครบ")

# ✅ ปุ่มกลับไปหน้าล็อกอิน
if st.button("⬅️ Back to Login"):
    st.switch_page("app.py")
