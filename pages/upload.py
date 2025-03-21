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
    sheet = client.open("fastlabor").sheet1

except Exception as e:
    st.error(f"❌ ไม่สามารถเชื่อมต่อกับ Google Sheets: {e}")
    st.stop()

# ✅ ตรวจสอบ session
if "user_email" not in st.session_state:
    st.error("⚠️ ไม่พบข้อมูลผู้ใช้ กรุณาลงทะเบียนใหม่")
    st.stop()

user_email = st.session_state["user_email"]

# ✅ ดึงข้อมูลผู้ใช้จาก Google Sheets
try:
    values = sheet.get_all_values()
    raw_headers = values[0]
    headers = [h.strip().lower() for h in raw_headers]

    if "email" not in headers:
        st.error("❌ ไม่พบคอลัมน์ 'email' ใน Google Sheets กรุณาตรวจสอบแถวหัวตาราง")
        st.stop()

    email_col = headers.index("email")
    user_row = next((i + 2 for i, row in enumerate(values[1:]) if len(row) > email_col and row[email_col] == user_email), None)

    if not user_row:
        st.error(f"⚠️ ไม่พบข้อมูลผู้ใช้ {user_email} ใน Google Sheets")
        st.stop()

except Exception as e:
    st.error(f"❌ ไม่สามารถดึงข้อมูลจาก Google Sheets: {e}")
    st.stop()

# ✅ ตั้งค่าหน้า
st.set_page_config(page_title="Upload Documents", page_icon="📂", layout="centered")
st.image("image.png", width=150)
st.title("Upload File")

st.markdown("กรุณาอัปโหลดเอกสารที่คุณมี (รองรับ .pdf และ .png)")

file_types = ["pdf", "png"]

# ✅ แบบฟอร์มอัปโหลด
certificate = st.file_uploader("หนังสือรับรอง (Certificate)", type=file_types)
passport = st.file_uploader("หนังสือเดินทาง (Passport)", type=file_types)
visa = st.file_uploader("หนังสือขอวีซ่า (Visa)", type=file_types)
work_permit = st.file_uploader("หนังสืออนุญาตทำงาน (Work Permit)", type=file_types)

# ✅ ปุ่มอัปโหลด
if st.button("Upload"):
    try:
        updates = []
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # ✅ เริ่มบันทึกไฟล์ที่อัปโหลดเท่านั้น
        if certificate:
            updates.append((email_col + 2, certificate.name))
        if passport:
            updates.append((email_col + 3, passport.name))
        if visa:
            updates.append((email_col + 4, visa.name))
        if work_permit:
            updates.append((email_col + 5, work_permit.name))

        # ✅ ถ้ามีการอัปโหลดใด ๆ จึงบันทึก
        if updates:
            for col, filename in updates:
                sheet.update_cell(user_row, col, filename)
            sheet.update_cell(user_row, email_col + 6, timestamp)
            st.success(f"✅ อัปโหลดสำเร็จสำหรับ {user_email}!")
        else:
            st.warning("⚠️ กรุณาเลือกไฟล์อย่างน้อย 1 รายการเพื่ออัปโหลด")

    except Exception as e:
        st.error(f"❌ ไม่สามารถบันทึกข้อมูลได้: {e}")
