import streamlit as st
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials

# ✅ ตั้งค่า Google Sheets API
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

try:
    # ✅ โหลด Credentials จาก Streamlit Secrets (สำหรับ Cloud)
    if "gcp" in st.secrets:
        credentials_dict = json.loads(st.secrets["gcp"]["credentials"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
    else:
        # ✅ โหลด Credentials จากไฟล์ (สำหรับ Local)
        creds = ServiceAccountCredentials.from_json_keyfile_name("pages/credentials.json", scope)

    # ✅ เชื่อมต่อ Google Sheets
    client = gspread.authorize(creds)
    spreadsheet = client.open("fastlabor")  # เปลี่ยนเป็นชื่อ Google Sheets ของคุณ

    # ✅ ตรวจสอบว่ามี Sheet `find_job` หรือยัง ถ้าไม่มีให้สร้างใหม่
    try:
        sheet = spreadsheet.worksheet("find_job")  # ดึง sheet ที่ชื่อ find_job
    except gspread.exceptions.WorksheetNotFound:
        sheet = spreadsheet.add_worksheet(title="find_job", rows="1000", cols="10")  # สร้างใหม่ถ้าไม่มี

    # ✅ เพิ่ม Header ใน Sheet `find_job` ถ้ายังไม่มี
    expected_headers = ["email", "job_type", "skills", "job_date", "start_time", "end_time",
                        "province", "district", "subdistrict", "start_salary", "range_salary"]

    existing_headers = sheet.row_values(1)

    if not existing_headers:
        sheet.append_row(expected_headers)  # ✅ เพิ่ม Header ในแถวแรก

except Exception as e:
    st.error(f"❌ ไม่สามารถเชื่อมต่อกับ Google Sheets: {e}")
    st.stop()

# ✅ ตรวจสอบว่า user ล็อกอินอยู่หรือไม่
if "email" not in st.session_state or not st.session_state["email"]:
    st.warning("🔒 กรุณาล็อกอินก่อนค้นหางาน")
    st.stop()

# ✅ ตั้งค่าหน้า Streamlit
st.set_page_config(page_title="Find Job", page_icon="🔍", layout="centered")

# ✅ ปุ่ม Profile ด้านบน
st.page_link("pages/profile.py", label="Profile", icon="👤")

st.title("Find Job")
st.write("For generate list of employees who match with the job.")

st.image("image.png", width=400)  # ใส่ภาพ Header

# ✅ ฟอร์มสำหรับค้นหางาน
with st.form("find_job_form"):
    job_type = st.text_input("Job Type *", placeholder="Enter job type")
    skills = st.text_input("Skills *", placeholder="Enter skills required (comma separated)")
    job_date = st.date_input("Date of Schedule *")

    start_time = st.text_input("Start Time *", placeholder="Enter start time (e.g. 08:00 AM)")
    end_time = st.text_input("End Time *", placeholder="Enter end time (e.g. 05:00 PM)")

    province = st.selectbox("Province *", ["Select", "Bangkok", "Chiang Mai", "Phuket", "Other"])
    district = st.selectbox("District *", ["Select", "District 1", "District 2", "District 3"])
    subdistrict = st.selectbox("Subdistrict *", ["Select", "Subdistrict 1", "Subdistrict 2", "Subdistrict 3"])

    start_salary = st.number_input("Start Salary*", min_value=0, step=100, value=3000)
    range_salary = st.number_input("Range Salary*", min_value=0, step=100, value=6000)

    submit_button = st.form_submit_button("Find Job")

# ✅ ถ้ากดปุ่ม Find Job
if submit_button:
    try:
        # ✅ ดึง email ของผู้ใช้ที่ล็อกอิน
        email = st.session_state["email"]

        # ✅ บันทึกข้อมูลลง Sheet
        sheet.append_row([
            email, job_type, skills, str(job_date), start_time, end_time,
            province, district, subdistrict, start_salary, range_salary
        ])
        st.success("✅ Job search saved successfully!")
    except Exception as e:
        st.error(f"❌ Error: {e}")

# ✅ ปุ่มกลับหน้า Home
st.page_link("pages/home.py", label="Go to Homepage", icon="🏠")
