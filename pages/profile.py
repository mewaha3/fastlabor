import streamlit as st
import gspread
import json
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

# ✅ ตั้งค่า Streamlit
st.set_page_config(page_title="User Profile", page_icon="👤", layout="centered")
st.title("👤 My Profile")

# ✅ ตรวจสอบการ login
if "user_email" not in st.session_state or not st.session_state["user_email"]:
    st.warning("⚠️ กรุณาเข้าสู่ระบบก่อนดูข้อมูล")
    st.page_link("app.py", label="⬅️ กลับไปหน้า Login", icon="🔙")
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

# ✅ ค้นหาข้อมูลผู้ใช้
user_data = df[df["email"] == email]
if user_data.empty:
    st.error("❌ ไม่พบข้อมูลผู้ใช้งาน")
    st.stop()

user = user_data.iloc[0]  # ดึง row แรกของผู้ใช้

# ✅ แสดงข้อมูลในรูปแบบ Read-Only
st.markdown("### 🧍 Personal Info")
st.text_input("First Name", user["first_name"], disabled=True)
st.text_input("Last Name", user["last_name"], disabled=True)
st.text_input("National ID", user["national_id"], disabled=True)
st.text_input("Date of Birth", user["dob"], disabled=True)
st.text_input("Gender", user["gender"], disabled=True)
st.text_input("Nationality", user["nationality"], disabled=True)

st.markdown("### 🏡 Address")
st.text_area("Address", user["address"], disabled=True)
st.text_input("Province", user["province"], disabled=True)
st.text_input("District", user["district"], disabled=True)
st.text_input("Subdistrict", user["subdistrict"], disabled=True)
st.text_input("Zip Code", user["zip_code"], disabled=True)

st.markdown("### 📧 Account")
st.text_input("Email", user["email"], disabled=True)

st.markdown("### 📄 Documents")
st.text_input("Certificate", user.get("certificate", ""), disabled=True)
st.text_input("Passport", user.get("passport", ""), disabled=True)
st.text_input("Visa", user.get("visa", ""), disabled=True)
st.text_input("Work Permit", user.get("work_permit", ""), disabled=True)

# ✅ ปุ่มย้อนกลับหรือ logout
col1, col2 = st.columns(2)
with col1:
    st.page_link("pages/edit_profile.py", label="✏️ Edit Profile")
with col2:
    if st.button("🚪 Logout"):
        st.session_state["logged_in"] = False
        st.session_state["user_email"] = None
        st.experimental_rerun()
