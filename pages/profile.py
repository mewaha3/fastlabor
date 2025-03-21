import streamlit as st
import gspread
import json
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

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

    # ✅ โหลดข้อมูลทั้งหมดจาก Google Sheets
    values = sheet.get_all_values()

    if not values or len(values) < 2:
        st.error("❌ ไม่พบข้อมูลใน Google Sheets (Sheet ว่าง)")
        st.stop()

    # ✅ แปลง header เป็นพิมพ์เล็กและตัดช่องว่าง
    headers = [h.strip().lower() for h in values[0]]  # ✅ เปลี่ยนเป็นพิมพ์เล็กทั้งหมด
    rows = values[1:]
    df = pd.DataFrame(rows, columns=headers).fillna("")  # ✅ ป้องกัน NaN

    # ✅ Debug: ตรวจสอบ headers
    st.write("📌 Headers from Google Sheets:", df.columns.tolist())

    # ✅ ตรวจสอบว่ามีคอลัมน์ email หรือไม่
    if "email" not in df.columns:
        st.error("❌ ไม่พบคอลัมน์ 'email' ใน Google Sheets")
        st.stop()

except Exception as e:
    st.error(f"❌ ไม่สามารถเชื่อมต่อกับ Google Sheets: {e}")
    st.stop()

# ✅ ตรวจสอบว่าผู้ใช้ล็อกอินหรือยัง
if "email" not in st.session_state or not st.session_state["email"]:
    st.warning("🔒 กรุณาล็อกอินก่อน")
    st.stop()

# ✅ ดึงข้อมูลจาก Google Sheets ตามอีเมลที่ล็อกอิน
email = st.session_state["email"]
user_data = df[df["email"].str.strip().str.lower() == email.strip().lower()]

if user_data.empty:
    st.error("❌ ไม่พบข้อมูลผู้ใช้")
    st.stop()

user = user_data.iloc[0]  # ดึงข้อมูลแถวแรกของผู้ใช้

# ✅ ตั้งค่าหน้าโปรไฟล์
st.set_page_config(page_title="Profile", page_icon="👤", layout="centered")
st.title("Profile")

st.markdown("#### Personal Information")

# ✅ Debug: ตรวจสอบว่าคีย์ `first_name` มีอยู่จริงหรือไม่
st.write("📌 Available keys in user data:", user.keys())

# ✅ ใช้ชื่อคอลัมน์ที่ถูกต้อง
first_name = st.text_input("First name *", user.get("first_name", ""))  # ✅ ใช้ `.get()` ป้องกัน KeyError
last_name = st.text_input("Last name *", user.get("last_name", ""))

national_id = st.text_input("National ID *", user.get("national_id", ""), disabled=True)
dob = st.date_input("Date of Birth *", pd.to_datetime(user.get("dob", ""), errors='coerce'))

gender_options = ["Male", "Female", "Other"]
gender = st.selectbox("Gender *", gender_options, index=gender_options.index(user.get("gender", "")) if user.get("gender", "") in gender_options else 0)

nationality = st.text_input("Nationality *", user.get("nationality", ""))

st.markdown("#### Address Information")
address = st.text_area("Address (House Number, Road, Soi.) *", user.get("address", ""))

province = st.text_input("Province *", user.get("province", ""))
district = st.text_input("District *", user.get("district", ""))
subdistrict = st.text_input("Subdistrict *", user.get("subdistrict", ""))
zip_code = st.text_input("Zip Code *", user.get("zip_code", ""), disabled=True)

# ✅ แสดง email (อ่านอย่างเดียว)
st.text_input("Email address *", user.get("email", ""), disabled=True)

# ✅ ปุ่ม Submit (บันทึกการเปลี่ยนแปลง)
if st.button("Save Profile"):
    try:
        row_index = user_data.index[0] + 2  # คำนวณแถวของผู้ใช้ใน Google Sheets

        # ✅ ใช้ลำดับคอลัมน์ที่ถูกต้อง
        updated_values = [
            first_name, last_name, national_id, str(dob.date()), gender, nationality,
            address, province, district, subdistrict, zip_code, email,
            user.get("password", ""),  # ✅ คงค่า Password เดิมไว้
        ]

        # ✅ อัปเดตข้อมูลใน Google Sheets
        sheet.update(f"A{row_index}:L{row_index}", [updated_values])

        st.success("✅ บันทึกข้อมูลสำเร็จ!")
    except Exception as e:
        st.error(f"❌ เกิดข้อผิดพลาด: {e}")

# ✅ ปุ่มกลับไปหน้า Home
st.page_link("pages/home.py", label="Go to Homepage", icon="🏠")
