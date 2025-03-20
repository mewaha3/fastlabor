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

# ✅ ตั้งค่า Session State สำหรับ Address
if "selected_province" not in st.session_state:
    st.session_state.selected_province = "Select Province"
if "selected_district" not in st.session_state:
    st.session_state.selected_district = "Select District"
if "selected_subdistrict" not in st.session_state:
    st.session_state.selected_subdistrict = "Select Subdistrict"
if "zip_code" not in st.session_state:
    st.session_state.zip_code = ""

# ✅ ตั้งค่าหน้า Streamlit
st.set_page_config(page_title="Post Job", page_icon="📌", layout="centered")

st.title("Post Job")
st.image("image.png", width=400)

st.markdown("#### Address Information")
job_address = st.text_area("Address (House Number, Road, Soi.) *", placeholder="Enter your address")

# ✅ เลือกจังหวัด > อำเภอ > ตำบล (อัปเดตอัตโนมัติ)
province_names = ["Select Province"] + provinces["name_th"].tolist()
selected_province = st.selectbox("Province *", province_names, index=province_names.index(st.session_state.selected_province))

if selected_province != st.session_state.selected_province:
    st.session_state.selected_province = selected_province
    st.session_state.selected_district = "Select District"
    st.session_state.selected_subdistrict = "Select Subdistrict"
    st.session_state.zip_code = ""
    st.rerun()

# ✅ กรองอำเภอจากจังหวัด
if selected_province != "Select Province":
    province_id = provinces[provinces["name_th"] == selected_province]["id"].values[0]
    filtered_districts = ["Select District"] + districts[districts["province_id"] == province_id]["name_th"].tolist()
else:
    filtered_districts = ["Select District"]

selected_district = st.selectbox("District *", filtered_districts, index=filtered_districts.index(st.session_state.selected_district))

if selected_district != st.session_state.selected_district:
    st.session_state.selected_district = selected_district
    st.session_state.selected_subdistrict = "Select Subdistrict"
    st.session_state.zip_code = ""
    st.rerun()

# ✅ กรองตำบลจากอำเภอ
if selected_district != "Select District":
    district_id = districts[districts["name_th"] == selected_district]["id"].values[0]
    filtered_subdistricts = subdistricts[subdistricts["amphure_id"] == district_id]
    subdistrict_names = ["Select Subdistrict"] + filtered_subdistricts["name_th"].tolist()
    zip_codes = filtered_subdistricts.set_index("name_th")["zip_code"].to_dict()
else:
    subdistrict_names = ["Select Subdistrict"]
    zip_codes = {}

selected_subdistrict = st.selectbox("Subdistrict *", subdistrict_names, index=subdistrict_names.index(st.session_state.selected_subdistrict))

if selected_subdistrict != st.session_state.selected_subdistrict:
    st.session_state.selected_subdistrict = selected_subdistrict
    st.session_state.zip_code = zip_codes.get(selected_subdistrict, "")
    st.rerun()

zip_code = st.text_input("Zip Code *", st.session_state.zip_code, disabled=True)

# ✅ ปุ่ม Submit
if st.button("Submit Job"):
    st.success(f"✅ Job with Address: {job_address}, {selected_subdistrict}, {selected_district}, {selected_province} saved successfully!")

# ✅ ปุ่มกลับหน้า Home
st.page_link("pages/home.py", label="Go to Homepage", icon="🏠")
