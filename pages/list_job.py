# pages/list_job.py

import streamlit as st
import pandas as pd
import json
from oauth2client.service_account import ServiceAccountCredentials
import gspread

st.set_page_config(page_title="My Jobs | FAST LABOR", layout="wide")
st.title("📄 My Jobs")

# —————————————————————————————————————————
# 1. โหลดข้อมูล PostJob จาก Google Sheets
# —————————————————————————————————————————
creds_json = json.loads(st.secrets["gcp"]["credentials"])
scope = ["https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, scope)
gc = gspread.authorize(creds)
sh = gc.open("fastlabor")

# โหลด sheet
ws = sh.worksheet("post_job")
vals = ws.get_all_values()
jobs_df = pd.DataFrame(vals[1:], columns=vals[0])
# normalize columns
jobs_df.columns = jobs_df.columns.str.strip().str.lower().str.replace(" ", "_")

# —————————————————————————————————————————
# 2. แปลงชนิดข้อมูล (ตามที่ต้องการ)
# —————————————————————————————————————————
jobs_df["job_date"] = pd.to_datetime(jobs_df["job_date"], errors="coerce")
# ถ้ามี start_time/end_time ก็แปลง datetime ต่อได้

# —————————————————————————————————————————
# 3. แสดงตารางงาน พร้อมปุ่ม View Matching
# —————————————————————————————————————————
st.write("Select a job to view its matching results:")

for idx, job in jobs_df.iterrows():
    st.markdown(f"---\n**Job #{idx+1}**: {job.job_type} on {job.job_date.date()}")
    cols = st.columns([3,1])
    with cols[0]:
        st.write(f"- **Detail:** {job.get('job_detail', '-')}")
        st.write(f"- **Address:** {job.job_address or job.province+'/'+job.district+'/'+job.subdistrict}")
        st.write(f"- **Salary:** {job.start_salary} – {job.range_salary}")
    with cols[1]:
        # เมื่อกดจะไปหน้า result_matching พร้อมส่ง job_idx
        if st.button("View Matching", key=f"view_{idx}"):
            st.experimental_set_query_params(page="result_matching", job_idx=idx)
            st.experimental_rerun()

# ถ้าไม่มีงานเลย
if jobs_df.empty:
    st.info("You have not posted any job yet.")

# —————————————————————————————————————————
# 4. ลิงก์กลับหน้า Home
# —————————————————————————————————————————
st.markdown("---")
if st.button("🏠 Go to Homepage"):
    st.experimental_set_query_params(page="home")
    st.experimental_rerun()
