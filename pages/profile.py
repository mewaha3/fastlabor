import streamlit as st
import gspread
import json
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

# ✅ ตั้งค่าหน้า Streamlit
st.set_page_config(page_title="Edit Profile", page_icon="📝", layout="centered")
st.title("Edit Profile")

# ✅ กำหนด Scope และโหลด Credentials
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

try:
    if "gcp" in st.secrets and "credentials" in st.secrets["gcp"]:
        credentials_dict = json.loads(st.secrets["gcp"]["credentials"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
    else:
        creds = ServiceAccountCredentials.from_json_keyfile_name("pages/credentials.json", scope)

    client = gspread.authorize(creds)
    sheet = client.open("fastlabor").sheet1
    data = sheet.get_all_records()
    df = pd.DataFrame(data)

except Exception as e:
    st.error(f"❌ ไม่สามารถเชื่อมต่อกับ Google Sheets: {e}")
    st.stop()

# ✅ ตรวจสอบว่า email ของผู้ใช้ login อยู่ใน session หรือให้กรอก
if "user_email" in st.session_state:
    email = st.session_state["user_email"]
else:
    email = st.text_input("Enter your email to edit profile")

if email:
    user_data = df[df["email"] == email]
    
    if not user_data.empty:
        user = user_data.iloc[0]

        # ✅ Personal Info
        st.markdown("### Personal Information")
        first_name = st.text_input("First name *", user["first_name"])
        last_name = st.text_input("Last name *", user["last_name"])
        national_id = st.text_input("National ID *", user["national_id"], disabled=True)
        dob = st.date_input("Date of Birth *", pd.to_datetime(user["dob"], errors='coerce'))
        gender_options = ["Male", "Female", "Other"]
        gender = st.selectbox("Gender *", gender_options, index=gender_options.index(user["gender"]) if user["gender"] in gender_options else 0)
        nationality = st.text_input("Nationality *", user["nationality"])

        # ✅ Address
        st.markdown("### Address")
        address = st.text_area("Address (House Number, Road, Soi.) *", user["address"])
        province = st.text_input("Province *", user["province"])
        district = st.text_input("District *", user["district"])
        subdistrict = st.text_input("Subdistrict *", user["subdistrict"])
        zip_code = st.text_input("Zip Code *", user["zip_code"], disabled=True)

        # ✅ Account Info
        st.markdown("### Account")
        password = st.text_input("Password *", value=user["password"], type="password")

        # ✅ Additional Docs
        st.markdown("### Additional Documents (optional)")
        certificate = st.text_input("Certificate", user.get("certificate", ""))
        passport = st.text_input("Passport", user.get("passport", ""))
        visa = st.text_input("Visa", user.get("visa", ""))
        work_permit = st.text_input("Work Permit", user.get("work_permit", ""))

        # ✅ บันทึกข้อมูล
        if st.button("Save Changes"):
            try:
                row_index = user_data.index[0] + 2  # +2 เพราะ header เริ่มแถว 1 และ df เริ่มที่ index 0
                sheet.update(f"A{row_index}:Q{row_index}", [[
                    first_name, last_name, national_id, str(dob), gender, nationality,
                    address, province, district, subdistrict, zip_code,
                    email, password, certificate, passport, visa, work_permit
                ]])
                st.success("✅ บันทึกข้อมูลเรียบร้อยแล้ว")
            except Exception as e:
                st.error(f"❌ ไม่สามารถบันทึกข้อมูลได้: {e}")

    else:
        st.warning("ไม่พบผู้ใช้งานในระบบ กรุณาตรวจสอบ email")
