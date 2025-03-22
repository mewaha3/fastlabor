import streamlit as st
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# ✅ ตั้งค่า Streamlit
st.set_page_config(page_title="My Full Profile", page_icon="🙍", layout="centered")
st.image("image.png", width=150)
st.title("👤 My Full Profile")

# ✅ ตรวจสอบ Session
user_email = st.session_state.get("user_email") or st.session_state.get("email")

if not user_email:
    st.warning("⚠️ กรุณาเข้าสู่ระบบก่อนดูข้อมูล")
    st.page_link("app.py", label="⬅️ กลับหน้า Login", icon="⬅️")
    st.stop()

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
    values = sheet.get_all_values()
    headers = [h.strip().lower() for h in values[0]]

except Exception as e:
    st.error(f"❌ ไม่สามารถเชื่อมต่อกับ Google Sheets: {e}")
    st.stop()

# ✅ หาตำแหน่งแถวของผู้ใช้
if "email" not in headers:
    st.error("❌ ไม่มีคอลัมน์ email ใน Google Sheets")
    st.stop()

email_col = headers.index("email")
user_row = next(
    (i + 2 for i, row in enumerate(values[1:]) if len(row) > email_col and row[email_col] == user_email),
    None
)

if not user_row:
    st.error(f"⚠️ ไม่พบข้อมูลของ {user_email}")
    st.stop()

user_data = sheet.row_values(user_row)
profile_data = dict(zip(headers, user_data))

# ✅ แปลงวันเกิดจาก string → datetime.date
dob_str = profile_data.get("date of birth", "")
try:
    dob_default = datetime.strptime(dob_str, "%Y-%m-%d").date() if dob_str else datetime.today().date()
except Exception:
    dob_default = datetime.today().date()

# ✅ ฟอร์มแก้ไขข้อมูล
with st.form("edit_profile"):
    st.markdown("### ✏️ แก้ไขข้อมูลส่วนตัว")

    first_name = st.text_input("First Name", value=profile_data.get("first name", ""))
    last_name = st.text_input("Last Name", value=profile_data.get("last name", ""))
    national_id = st.text_input("National ID", value=profile_data.get("national id", ""))
    dob = st.date_input("Date of Birth", value=dob_default)
    gender = st.selectbox("Gender", ["Male", "Female", "Other"],
                          index=["Male", "Female", "Other"].index(profile_data.get("gender", "Male")))
    nationality = st.text_input("Nationality", value=profile_data.get("nationality", ""))
    address = st.text_area("Address", value=profile_data.get("address", ""))
    province = st.text_input("Province", value=profile_data.get("province", ""))
    district = st.text_input("District", value=profile_data.get("district", ""))
    subdistrict = st.text_input("Subdistrict", value=profile_data.get("subdistrict", ""))
    zip_code = st.text_input("Zip Code", value=profile_data.get("zip code", ""))
    email = st.text_input("Email (ไม่สามารถแก้ไขได้)", value=user_email, disabled=True)

    submitted = st.form_submit_button("💾 Save")

# ✅ บันทึกข้อมูลกลับเข้า Google Sheets
if submitted:
    try:
        update_values = [
            first_name, last_name, national_id, str(dob), gender, nationality,
            address, province, district, subdistrict, zip_code, user_email
        ]

        for i, val in enumerate(update_values):
            sheet.update_cell(user_row, i + 1, val)

        st.success("✅ บันทึกข้อมูลเรียบร้อยแล้ว!")

    except Exception as e:
        st.error(f"❌ เกิดข้อผิดพลาดในการอัปเดตข้อมูล: {e}")
