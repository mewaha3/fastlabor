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
    if "gcp" in st.secrets:
        credentials_dict = json.loads(st.secrets["gcp"]["credentials"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
    else:
        creds = ServiceAccountCredentials.from_json_keyfile_name("pages/credentials.json", scope)

    client = gspread.authorize(creds)
    spreadsheet = client.open("fastlabor")

    try:
        sheet = spreadsheet.worksheet("find_job")
    except gspread.exceptions.WorksheetNotFound:
        sheet = spreadsheet.add_worksheet(title="find_job", rows="1000", cols="15")

    expected_headers = [
        "email", "job_type", "skills", "job_date", "start_time", "end_time",
        "job_address", "province", "district", "subdistrict", "zip_code", "start_salary", "range_salary"
    ]
    existing_headers = sheet.row_values(1)
    if not existing_headers:
        sheet.append_row(expected_headers)

except Exception as e:
    st.error(f"❌ ไม่สามารถเชื่อมต่อกับ Google Sheets: {e}")
    st.stop()

# ✅ ตรวจสอบว่า user ล็อกอินอยู่หรือไม่
if "email" not in st.session_state or not st.session_state["email"]:
    st.warning("🔒 กรุณาล็อกอินก่อนค้นหางาน")
    st.stop()

# ✅ ตั้งค่าหน้า Streamlit
st.set_page_config(page_title="Find Job", page_icon="🔍", layout="centered")
st.page_link("pages/profile.py", label="Profile", icon="👤")

st.title("Find Job")
st.write("For generate list of employees who match with the job.")
st.image("image.png", width=400)

# ✅ Address Session State
if "selected_province" not in st.session_state:
    st.session_state.selected_province = "Select Province"
if "selected_district" not in st.session_state:
    st.session_state.selected_district = "Select District"
if "selected_subdistrict" not in st.session_state:
    st.session_state.selected_subdistrict = "Select Subdistrict"
if "zip_code" not in st.session_state:
    st.session_state.zip_code = ""

# ✅ ฟอร์มสำหรับค้นหางาน
with st.form("find_job_form"):
    job_type = st.text_input("Job Type *", placeholder="Enter job type")
    skills = st.text_input("Skills *", placeholder="Enter skills required (comma separated)")

    # 🔁 Start Date / End Date
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date *")
    with col2:
        end_date = st.date_input("End Date *")

    # 🔁 เปลี่ยน Time เป็น time_input
    start_time = st.time_input("Start Time *")
    end_time = st.time_input("End Time *")

    st.markdown("#### Address Information")
    job_address = st.text_area("Address (House Number, Road, Soi.) *", placeholder="Enter your address")

    province_names = ["Select Province"] + provinces["name_th"].tolist()
    selected_province = st.selectbox("Province *", province_names, index=province_names.index(st.session_state.selected_province) if st.session_state.selected_province in province_names else 0)

    if selected_province != st.session_state.selected_province:
        st.session_state.selected_province = selected_province
        st.session_state.selected_district = "Select District"
        st.session_state.selected_subdistrict = "Select Subdistrict"
        st.session_state.zip_code = ""
        st.experimental_rerun()

    filtered_districts = ["Select District"]
    if selected_province != "Select Province":
        province_id = provinces.loc[provinces["name_th"] == selected_province, "id"].values
        if len(province_id) > 0:
            province_id = province_id[0]
            filtered_districts += districts.loc[districts["province_id"] == province_id, "name_th"].tolist()

    selected_district = st.selectbox("District *", filtered_districts, index=filtered_districts.index(st.session_state.selected_district) if st.session_state.selected_district in filtered_districts else 0)

    if selected_district != st.session_state.selected_district:
        st.session_state.selected_district = selected_district
        st.session_state.selected_subdistrict = "Select Subdistrict"
        st.session_state.zip_code = ""
        st.experimental_rerun()

    filtered_subdistricts = ["Select Subdistrict"]
    zip_codes = {}
    if selected_district != "Select District":
        district_id = districts.loc[districts["name_th"] == selected_district, "id"].values
        if len(district_id) > 0:
            district_id = district_id[0]
            subdistrict_list = subdistricts[subdistricts["amphure_id"] == district_id]
            filtered_subdistricts += subdistrict_list["name_th"].tolist()
            zip_codes = subdistrict_list.set_index("name_th")["zip_code"].to_dict()

    selected_subdistrict = st.selectbox("Subdistrict *", filtered_subdistricts, index=filtered_subdistricts.index(st.session_state.selected_subdistrict) if st.session_state.selected_subdistrict in filtered_subdistricts else 0)

    if selected_subdistrict != st.session_state.selected_subdistrict:
        st.session_state.selected_subdistrict = selected_subdistrict
        st.session_state.zip_code = zip_codes.get(selected_subdistrict, "")
        st.experimental_rerun()

    zip_code = st.text_input("Zip Code *", st.session_state.zip_code, disabled=True)

    start_salary = st.number_input("Start Salary*", min_value=0, step=100, value=3000)
    range_salary = st.number_input("Range Salary*", min_value=0, step=100, value=6000)

    submit_button = st.form_submit_button("Find Job")

# ✅ บันทึกลง Google Sheets
if submit_button:
    try:
        email = st.session_state["email"]
        job_date = f"{start_date} to {end_date}"
        sheet.append_row([
            email, job_type, skills, job_date, str(start_time), str(end_time),
            job_address, selected_province, selected_district, selected_subdistrict,
            st.session_state.zip_code, start_salary, range_salary
        ])
        st.success("✅ Job search saved successfully!")
    except Exception as e:
        st.error(f"❌ Error: {e}")

# ✅ กลับหน้า Home
st.page_link("pages/home.py", label="Go to Homepage", icon="🏠")
