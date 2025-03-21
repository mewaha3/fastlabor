import streamlit as st
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials
import datetime

# ✅ ตั้งค่า Google Sheets API
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

try:
    if "gcp" in st.secrets and "credentials" in st.secrets["gcp"]:
        credentials_dict = json.loads(st.secrets["gcp"]["credentials"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
    else:
        creds = ServiceAccountCredentials.from_json_keyfile_name("pages/credentials.json", scope)

    client = gspread.authorize(creds)
    sheet = client.open("fastlabor").sheet1  # ใช้ Sheet เดียวกับ Register

except Exception as e:
    st.error(f"❌ ไม่สามารถเชื่อมต่อกับ Google Sheets: {e}")
    st.stop()

# ✅ ตรวจสอบว่ามีอีเมลใน session_state หรือไม่
if "user_email" not in st.session_state:
    st.error("⚠️ ไม่พบข้อมูลผู้ใช้ กรุณาลงทะเบียนใหม่")
    st.stop()

user_email = st.session_state["user_email"]

# ✅ ตั้งค่าหน้า Streamlit
st.set_page_config(page_title="Upload Documents", page_icon="📂", layout="centered")
st.image("image.png", width=150)
st.title("Upload File")

st.markdown("กรุณาอัปโหลดเอกสารตามที่กำหนดด้านล่าง")

file_types = ["pdf"]

# ✅ ฟอร์มอัปโหลดเอกสาร
certificate = st.file_uploader("หนังสือรับรอง (Certificate) *", type=file_types)
passport = st.file_uploader("หนังสือเดินทาง (Passport) *", type=file_types)
visa = st.file_uploader("หนังสือขอวีซ่า (Visa) *", type=file_types)
work_permit = st.file_uploader("หนังสืออนุญาตทำงาน (Work Permit) *", type=file_types)

# ✅ ตรวจสอบว่าผู้ใช้มีข้อมูลอยู่ใน Google Sheets หรือไม่
try:
    records = sheet.get_all_records()
    user_row = next((i + 2 for i, row in enumerate(records) if row["Email"] == user_email), None)
except Exception as e:
    st.error(f"❌ ไม่สามารถดึงข้อมูลจาก Google Sheets: {e}")
    st.stop()

if not user_row:
    st.error("⚠️ ไม่พบข้อมูลผู้ใช้ กรุณาลงทะเบียนใหม่")
    st.stop()

# ✅ ปุ่มยืนยันเอกสาร
if st.button("Verify"):
    if certificate and passport and visa and work_permit:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # ✅ บันทึกข้อมูลลงในแถวที่ผู้ใช้สมัครไว้
        try:
            sheet.update_cell(user_row, 14, "Certificate.pdf")  # คอลัมน์ที่ 14
            sheet.update_cell(user_row, 15, "Passport.pdf")     # คอลัมน์ที่ 15
            sheet.update_cell(user_row, 16, "Visa.pdf")         # คอลัมน์ที่ 16
            sheet.update_cell(user_row, 17, "Work_permit.pdf")  # คอลัมน์ที่ 17
            sheet.update_cell(user_row, 18, timestamp)          # คอลัมน์ที่ 18 (Timestamp)

            st.success(f"✅ อัปโหลดสำเร็จสำหรับ {user_email}!")
        except Exception as e:
            st.error(f"❌ ไม่สามารถบันทึกข้อมูลได้: {e}")
    else:
        st.error("⚠️ กรุณาอัปโหลดเอกสารให้ครบทุกไฟล์ก่อนกด Verify")
