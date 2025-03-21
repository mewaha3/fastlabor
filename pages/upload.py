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

# ✅ ดึงข้อมูลทั้งหมดจาก Google Sheets
try:
    values = sheet.get_all_values()  # ✅ ใช้ get_all_values() เพื่อให้แน่ใจว่าไม่มีคอลัมน์หายไป
    headers = [h.lower() for h in values[0]]  # ✅ แปลงชื่อคอลัมน์เป็นตัวพิมพ์เล็กทั้งหมด

    if "email" not in headers:
        st.error("❌ ไม่พบคอลัมน์ 'email' ใน Google Sheets กรุณาตรวจสอบไฟล์ของคุณ")
        st.stop()

    email_col = headers.index("email")  # ✅ หา index ของคอลัมน์ 'email'

    # ✅ หาแถวของ user_email
    user_row = next((i + 1 for i, row in enumerate(values[1:], start=2) if row[email_col] == user_email), None)

    if not user_row:
        st.error(f"⚠️ ไม่พบข้อมูลผู้ใช้ {user_email} ใน Google Sheets กรุณาลงทะเบียนใหม่")
        st.stop()

except Exception as e:
    st.error(f"❌ ไม่สามารถดึงข้อมูลจาก Google Sheets: {e}")
    st.stop()

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

# ✅ ปุ่มยืนยันเอกสาร
if st.button("Verify"):
    if certificate and passport and visa and work_permit:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # ✅ บันทึกข้อมูลลงในแถวที่ผู้ใช้สมัครไว้
        try:
            sheet.update_cell(user_row, email_col + 2, "Certificate.pdf")  # ✅ อัปเดตหลังคอลัมน์ email
            sheet.update_cell(user_row, email_col + 3, "Passport.pdf")  
            sheet.update_cell(user_row, email_col + 4, "Visa.pdf")         
            sheet.update_cell(user_row, email_col + 5, "Work_permit.pdf")  
            sheet.update_cell(user_row, email_col + 6, timestamp)  # ✅ Timestamp

            st.success(f"✅ อัปโหลดสำเร็จสำหรับ {user_email}!")
        except Exception as e:
            st.error(f"❌ ไม่สามารถบันทึกข้อมูลได้: {e}")
    else:
        st.error("⚠️ กรุณาอัปโหลดเอกสารให้ครบทุกไฟล์ก่อนกด Verify")
