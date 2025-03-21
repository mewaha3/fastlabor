import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ✅ ตั้งค่า Google Sheets API
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("pages/credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open("fastlabor").sheet1  # ใช้ Sheet หลัก

# ✅ ตั้งค่าหน้า
st.set_page_config(page_title="New Member Registration", page_icon="📝", layout="centered")
st.image("image.png", width=150)  
st.title("New Member")

# ✅ ฟอร์มลงทะเบียน
with st.form(key="register_form"):
    first_name = st.text_input("First name *")
    last_name = st.text_input("Last name *")
    dob = st.date_input("Date of Birth *")
    gender = st.selectbox("Gender *", ["Male", "Female", "Other"])
    nationality = st.text_input("Nationality *")
    member_type = st.selectbox("Member Type *", ["Employer", "Worker"])
    address = st.text_area("Address (House Number, Road, Soi.)")
    province = st.text_input("Province *")
    district = st.text_input("District *")
    subdistrict = st.text_input("Subdistrict *")
    zip_code = st.text_input("Zip Code *")
    email = st.text_input("Email address *")
    password = st.text_input("Password *", type="password")

    submit_button = st.form_submit_button("Submit")

if submit_button:
    if first_name and last_name and email and password:
        # ✅ บันทึกข้อมูลลง Google Sheets
        sheet.append_row([first_name, last_name, str(dob), gender, nationality, member_type,
                          address, province, district, subdistrict, zip_code, email, password])
        
        st.success(f"🎉 Welcome, {first_name}! You have successfully registered.")

        # ✅ เก็บอีเมลใน Session State
        st.session_state.user_email = email

        # ✅ นำทางไปหน้า upload.py
        st.switch_page("upload.py")
    else:
        st.error("⚠️ กรุณากรอกข้อมูลให้ครบทุกช่องที่จำเป็น")
