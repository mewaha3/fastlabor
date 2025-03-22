import streamlit as st
import gspread
import json
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(page_title="Edit Profile", page_icon="📝", layout="centered")
st.title("Edit Your Profile")

# ✅ ตรวจสอบว่าเข้าสู่ระบบหรือไม่
if "user_email" not in st.session_state or not st.session_state["user_email"]:
    st.warning("⚠️ กรุณาเข้าสู่ระบบก่อนแก้ไขข้อมูล")
    st.page_link("app.py", label="⬅️ Go to Login")
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
    data = sheet.get_all_records()
    df = pd.DataFrame(data)

except Exception as e:
    st.error(f"❌ ไม่สามารถเชื่อมต่อ Google Sheets: {e}")
    st.stop()

# ✅ ดึงข้อมูลของผู้ใช้
user_data = df[df["email"] == email]
if user_data.empty:
    st.error("❌ ไม่พบข้อมูลผู้ใช้งาน")
    st.stop()

user = user_data.iloc[0]

# ✅ แสดงฟอร์มแก้ไข (ไม่รวม password และ email read-only)
st.markdown("### Personal Information")
first_name = st.text_input("First name *", user["first_name"])
last_name = st.text_input("Last name *", user["last_name"])
national_id = st.text_input("National ID *", user["national_id"], disabled=True)
dob = st.date_input("Date of Birth *", pd.to_datetime(user["dob"], errors="coerce"))
gender = st.selectbox("Gender *", ["Male", "Female", "Other"], index=["Male", "Female", "Other"].index(user["gender"]) if user["gender"] in ["Male", "Female", "Other"] else 0)
nationality = st.text_input("Nationality *", user["nationality"])

st.markdown("### Address")
address = st.text_area("Address *", user["address"])
province = st.text_input("Province *", user["province"])
district = st.text_input("District *", user["district"])
subdistrict = st.text_input("Subdistrict *", user["subdistrict"])
zip_code = st.text_input("Zip Code", user["zip_code"], disabled=True)

st.markdown("### Email")
st.text_input("Email", user["email"], disabled=True)

st.markdown("### Documents")
certificate = st.text_input("Certificate", user.get("certificate", ""))
passport = st.text_input("Passport", user.get("passport", ""))
visa = st.text_input("Visa", user.get("visa", ""))
work_permit = st.text_input("Work Permit", user.get("work_permit", ""))

# ✅ ปุ่มบันทึก
if st.button("💾 Save Changes"):
    try:
        row_index = user_data.index[0] + 2  # +2 เพราะ header เริ่มที่แถว 1
        sheet.update(f"A{row_index}:Q{row_index}", [[
            first_name, last_name, national_id, str(dob), gender, nationality,
            address, province, district, subdistrict, zip_code,
            email, user["password"], certificate, passport, visa, work_permit
        ]])
        st.success("✅ ข้อมูลถูกบันทึกเรียบร้อยแล้ว!")

    except Exception as e:
        st.error(f"❌ เกิดข้อผิดพลาด: {e}")
