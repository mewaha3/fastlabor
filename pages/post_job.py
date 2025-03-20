import streamlit as st
import gspread
import json
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

# ✅ โหลดข้อมูลจังหวัด อำเภอ ตำบล และรหัสไปรษณีย์
@st.cache_data
def load_location_data():
    url_province = "https://raw.githubusercontent.com/kongvut/thai-province-data/master/api_province.json"
    url_district = "https://raw.githubusercontent.com/kongvut/thai-province-data/master/api_amphure.json"
    url_subdistrict = "https://raw.githubusercontent.com/kongvut/thai-province-data/master/api_tambon.json"

    provinces = pd.read_json(url_province)
    districts = pd.read_json(url_district)
    subdistricts = pd.read_json(url_subdistrict)

    return provinces, districts, subdistricts

provinces, districts, subdistricts = load_location_data()

# ✅ ตั้งค่า Google Sheets API
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

try:
    if "gcp" in st.secrets and "credentials" in st.secrets["gcp"]:
        credentials_dict = json.loads(st.secrets["gcp"]["credentials"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
    else:
        creds = ServiceAccountCredentials.from_json_keyfile_name("pages/credentials.json", scope)

    client = gspread.authorize(creds)
    spreadsheet = client.open("fastlabor")

    # ✅ ตรวจสอบว่ามี Sheet `post_job` หรือยัง ถ้าไม่มีให้สร้างใหม่
    try:
        sheet = spreadsheet.worksheet("post_job")
    except gspread.exceptions.WorksheetNotFound:
        sheet = spreadsheet.add_worksheet(title="post_job", rows="1000", cols="12")

    # ✅ เพิ่ม Header ใน Sheet `post_job` ถ้ายังไม่มี
    expected_headers = ["email", "job_type", "job_detail", "salary", "job_date", "start_time", "end_time",
                        "job_address", "province", "district", "subdistrict", "zip_code"]

    existing_headers = sheet.row_values(1)
    if not existing_headers:
        sheet.append_row(expected_headers)

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
st.write("For generating a list of employees who match the job.")

st.image("image.png", width=400)

# ✅ ตั้งค่า Session State สำหรับ Address
if "selected_province" not in st.session_state:
    st.session_state.selected_province = "Select Province"
if "selected_district" not in st.session_state:
    st.session_state.selected_district = "Select District"
if "selected_subdistrict" not in st.session_state:
    st.session_state.selected_subdistrict = "Select Subdistrict"
if "zip_code" not in st.session_state:
    st.session_state.zip_code = ""

# ✅ ฟอร์มสำหรับเพิ่มงานใหม่
with st.form("job_form"):
    job_type = st.text_input("Job Type *", placeholder="Enter job type")
    job_detail = st.text_area("Job Detail *", placeholder="Enter job details")
    salary = st.text_input("Salary *", placeholder="Enter salary range")
    job_date = st.date_input("Date of Schedule *")

    # ✅ เปลี่ยนเป็นตัวเลือกเวลา
    start_time = st.time_input("Start Time *")
    end_time = st.time_input("End Time *")

    st.markdown("#### Address Information")
    job_address = st.text_area("Address (House Number, Road, Soi.) *", placeholder="Enter your address")

    # ✅ เลือกจังหวัด > อำเภอ > ตำบล (อัปเดตอัตโนมัติ)
    province_names = ["Select Province"] + provinces["name_th"].tolist()
    selected_province = st.selectbox("Province *", province_names, index=province_names.index(st.session_state.selected_province) if st.session_state.selected_province in province_names else 0)

    if selected_province != st.session_state.selected_province:
        st.session_state.selected_province = selected_province
        st.session_state.selected_district = "Select District"
        st.session_state.selected_subdistrict = "Select Subdistrict"
        st.session_state.zip_code = ""
        st.experimental_rerun()

    # ✅ กรองอำเภอจากจังหวัด
    if selected_province != "Select Province":
        province_id = provinces[provinces["name_th"] == selected_province]["id"].values[0]
        filtered_districts = ["Select District"] + districts[districts["province_id"] == province_id]["name_th"].tolist()
    else:
        filtered_districts = ["Select District"]

    selected_district = st.selectbox("District *", filtered_districts, index=filtered_districts.index(st.session_state.selected_district) if st.session_state.selected_district in filtered_districts else 0)

    if selected_district != st.session_state.selected_district:
        st.session_state.selected_district = selected_district
        st.session_state.selected_subdistrict = "Select Subdistrict"
        st.session_state.zip_code = ""
        st.experimental_rerun()

    # ✅ กรองตำบลจากอำเภอ
    if selected_district != "Select District":
        district_id = districts[districts["name_th"] == selected_district]["id"].values[0]
        filtered_subdistricts = subdistricts[subdistricts["amphure_id"] == district_id]
        subdistrict_names = ["Select Subdistrict"] + filtered_subdistricts["name_th"].tolist()
        zip_codes = filtered_subdistricts.set_index("name_th")["zip_code"].to_dict()
    else:
        subdistrict_names = ["Select Subdistrict"]
        zip_codes = {}

    selected_subdistrict = st.selectbox("Subdistrict *", subdistrict_names, index=subdistrict_names.index(st.session_state.selected_subdistrict) if st.session_state.selected_subdistrict in subdistrict_names else 0)

    if selected_subdistrict != st.session_state.selected_subdistrict:
        st.session_state.selected_subdistrict = selected_subdistrict
        st.session_state.zip_code = zip_codes.get(selected_subdistrict, "")
        st.experimental_rerun()

    zip_code = st.text_input("Zip Code *", st.session_state.zip_code, disabled=True)

    submit_button = st.form_submit_button("Match Employee")

# ✅ ถ้ากดปุ่ม ให้บันทึกข้อมูลงานลง Google Sheets
if submit_button:
    try:
        email = st.session_state["email"]
        sheet.append_row([
            email, job_type, job_detail, salary, str(job_date), str(start_time), str(end_time),
            job_address, selected_province, selected_district, selected_subdistrict, st.session_state.zip_code
        ])
        st.success("✅ Job posted successfully!")
    except Exception as e:
        st.error(f"❌ Error: {e}")

# ✅ ปุ่มกลับหน้า Home
st.page_link("pages/home.py", label="Go to Homepage", icon="🏠")
