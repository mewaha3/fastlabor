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

    # ✅ ตรวจสอบว่ามี Sheet `post_job` หรือยัง ถ้าไม่มีให้สร้างใหม่
    try:
        sheet = spreadsheet.worksheet("post_job")  # ดึง sheet ที่ชื่อ post_job
    except gspread.exceptions.WorksheetNotFound:
        sheet = spreadsheet.add_worksheet(title="post_job", rows="1000", cols="14")  # สร้างใหม่ถ้าไม่มี

    # ✅ เพิ่ม Header ใน Sheet `post_job` ถ้ายังไม่มี
    expected_headers = ["email", "job_type", "job_detail", "salary", "job_date", "start_time", "end_time",
                        "job_address", "province", "district", "subdistrict", "zip_code",
                        "start_salary", "range_salary"]

    existing_headers = sheet.row_values(1)

    if not existing_headers:
        sheet.append_row(expected_headers)  # ✅ เพิ่ม Header ในแถวแรก

except Exception as e:
    st.error(f"❌ ไม่สามารถเชื่อมต่อกับ Google Sheets: {e}")
    st.stop()

# ✅ ตรวจสอบว่า user ล็อกอินอยู่หรือไม่
if "email" not in st.session_state or not st.session_state["email"]:
    st.warning("🔒 กรุณาล็อกอินก่อนโพสต์งาน")
    st.stop()

# ✅ ตั้งค่าหน้า Streamlit
st.set_page_config(page_title="Post Job", page_icon="📌", layout="centered")

# ✅ ปุ่ม Profile ด้านบน
st.page_link("pages/profile.py", label="Profile", icon="👤")

st.title("Post Job")
st.write("For generate list of employees who match with the job.")

st.image("image.png", width=400)  # ใส่ภาพ Header

# ✅ ฟอร์มสำหรับเพิ่มงานใหม่
with st.form("job_form"):
    job_type = st.text_input("Job Type *", placeholder="Enter job type")
    job_detail = st.text_input("Job Detail *", placeholder="Enter job details")
    salary = st.text_input("Salary *", placeholder="Enter salary range")
    job_date = st.date_input("Date of Schedule *")
    
    start_time = st.text_input("Start Time *", placeholder="Enter start time (e.g. 08:00 AM)")
    end_time = st.text_input("End Time *", placeholder="Enter end time (e.g. 05:00 PM)")
    
    job_address = st.text_area("Job Address (House Number, Road, Soi.)", placeholder="Enter address details")
    
    province = st.selectbox("Province *", ["Select", "Bangkok", "Chiang Mai", "Phuket", "Other"])
    district = st.selectbox("District *", ["Select", "District 1", "District 2", "District 3"])
    subdistrict = st.selectbox("Subdistrict *", ["Select", "Subdistrict 1", "Subdistrict 2", "Subdistrict 3"])
    zip_code = st.text_input("Zip Code *", placeholder="Enter zip code")

    start_salary = st.number_input("Start Salary*", min_value=0, step=100, value=3000)
    range_salary = st.number_input("Range Salary*", min_value=0, step=100, value=6000)

    submit_button = st.form_submit_button("Match Employee")

# ✅ ถ้ากดปุ่ม ให้บันทึกข้อมูลงานลง Google Sheets
if submit_button:
    try:
        # ✅ ดึง email ของผู้ใช้ที่ล็อกอิน
        email = st.session_state["email"]

        # ✅ บันทึกข้อมูลลง Sheet
        sheet.append_row([
            email, job_type, job_detail, salary, str(job_date), start_time, end_time, job_address,
            province, district, subdistrict, zip_code, start_salary, range_salary
        ])
        st.success("✅ Job posted successfully!")
    except Exception as e:
        st.error(f"❌ Error: {e}")

# ✅ ปุ่มกลับหน้า Home
st.page_link("pages/home.py", label="Go to Homepage", icon="🏠")
