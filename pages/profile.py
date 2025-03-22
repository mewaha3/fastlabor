import streamlit as st
import gspread
import json
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(page_title="My Profile", page_icon="👤", layout="centered")
st.title("👤 My Full Profile")

# ✅ ตรวจสอบ Login
if "user_email" not in st.session_state or not st.session_state["user_email"]:
    st.warning("⚠️ กรุณาเข้าสู่ระบบก่อนดูข้อมูล")
    st.page_link("app.py", label="⬅️ กลับหน้า Login", icon="🔙")
    st.stop()

email = st.session_state["user_email"]

# ✅ เชื่อมต่อ Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
try:
    if "gcp" in st.secrets:
        credentials_dict = json.loads(st.secrets["gcp"]["credentials"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
    else:
        creds = ServiceAccountCredentials.from_json_keyfile_name("pages/credentials.json", scope)

    client = gspread.authorize(creds)
    sheet = client.open("fastlabor").sheet1
    records = sheet.get_all_records()
    df = pd.DataFrame(records)
except Exception as e:
    st.error(f"❌ ไม่สามารถเชื่อมต่อ Google Sheets: {e}")
    st.stop()

# ✅ ดึงข้อมูลของผู้ใช้จากอีเมล
user_data = df[df["email"] == email]
if user_data.empty:
    st.error("❌ ไม่พบข้อมูลผู้ใช้งานในระบบ")
    st.stop()

user = user_data.iloc[0]
row_index = user_data.index[0] + 2  # +2 เพราะ header อยู่ที่แถว 1

# ✅ แสดงข้อมูลแบบแก้ไขได้ (ยกเว้น email, national_id)
st.markdown("### 🧍 Personal Info")
first_name = st.text_input("First Name", user.get("first_name", ""))
last_name = st.text_input("Last Name", user.get("last_name", ""))
national_id = st.text_input("National ID", user.get("national_id", ""), disabled=True)
dob = st.text_input("Date of Birth", user.get("dob", ""))
gender = st.selectbox("Gender", ["Male", "Female", "Other"], index=["Male", "Female", "Other"].index(user.get("gender", "Male")))
nationality = st.text_input("Nationality", user.get("nationality", ""))

st.markdown("### 🏡 Address")
address = st.text_area("Address", user.get("address", ""))
province = st.text_input("Province", user.get("province", ""))
district = st.text_input("District", user.get("district", ""))
subdistrict = st.text_input("Subdistrict", user.get("subdistrict", ""))
zip_code = st.text_input("Zip Code", user.get("zip_code", ""))

st.markdown("### 📧 Account")
st.text_input("Email", user.get("email", ""), disabled=True)

st.markdown("### 📎 Documents (from upload.py)")
certificate = st.text_input("Certificate", user.get("certificate", ""))
passport = st.text_input("Passport", user.get("passport", ""))
visa = st.text_input("Visa", user.get("visa", ""))
work_permit = st.text_input("Work Permit", user.get("work_permit", ""))

# ✅ บันทึกการแก้ไข
if st.button("💾 Save Changes"):
    try:
        sheet.update(f"A{row_index}:Q{row_index}", [[
            first_name, last_name, national_id, dob, gender, nationality,
            address, province, district, subdistrict, zip_code,
            email, user.get("password", ""), certificate, passport, visa, work_permit
        ]])
        st.success("✅ ข้อมูลถูกบันทึกแล้วเรียบร้อย")
    except Exception as e:
        st.error(f"❌ บันทึกข้อมูลไม่สำเร็จ: {e}")

# ✅ ปุ่มกลับหน้า Home
st.page_link("pages/home.py", label="🏠 Go to Home", icon="🏡")
