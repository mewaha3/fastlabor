import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime

# ✅ ตั้งค่า Google Sheets API
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("pages/credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open("fastlabor").worksheet("Uploads")  # ใช้ Sheet "Uploads"

# ✅ ตรวจสอบว่า Session State มีอีเมลหรือไม่
if "user_email" not in st.session_state:
    st.error("⚠️ ไม่พบข้อมูลผู้ใช้ กรุณาลงทะเบียนใหม่")
    st.stop()

user_email = st.session_state.user_email  # ดึงอีเมลจาก Session State

# ✅ ตั้งค่าหน้า
st.set_page_config(page_title="Upload Documents", page_icon="📂", layout="centered")
st.title("Upload File")

file_types = ["pdf"]

# ✅ ฟอร์มอัปโหลดไฟล์
certificate = st.file_uploader("หนังสือรับรอง (Certificate) *", type=file_types)
passport = st.file_uploader("หนังสือเดินทาง (Passport) *", type=file_types)
visa = st.file_uploader("หนังสือขอวีซ่า (Visa) *", type=file_types)
work_permit = st.file_uploader("หนังสืออนุญาตทำงาน (Work Permit) *", type=file_types)

if st.button("Verify"):
    if certificate and passport and visa and work_permit:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # ✅ บันทึกข้อมูลไฟล์ลง Google Sheets พร้อมอีเมล
        sheet.append_row([user_email, timestamp, "Certificate.pdf", "Passport.pdf", "Visa.pdf", "Work_permit.pdf"])

        st.success(f"✅ เอกสารถูกอัปโหลดและบันทึกเรียบร้อยแล้วสำหรับ {user_email}!")
    else:
        st.error("⚠️ กรุณาอัปโหลดเอกสารให้ครบทุกไฟล์ก่อนกด Verify")
