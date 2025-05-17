import streamlit as st
import pandas as pd
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ————————————————————————————————
# 1) Page config & guard
# ————————————————————————————————
st.set_page_config(page_title="Job Detail | FAST LABOR", layout="centered")
if not st.session_state.get("logged_in", False):
    st.error("❌ กรุณาล็อกอินก่อนเข้าหน้านี้")
    st.stop()

# เราคาดว่าเมื่อกด Accept ที่หน้า find_job_matching.py
# จะเซฟข้อมูล match row ไว้ใน session_state["selected_match"]
# และ job_detail.py จะอ่าน session_state["selected_match"]
match_row = st.session_state.get("selected_job")
if match_row is None:
    st.error("❌ ไม่พบข้อมูลงาน กรุณากด Accept จากหน้าจับคู่ก่อน")
    st.stop()

# ————————————————————————————————
# 2) Helper: load any sheet
# ————————————————————————————————
def _sheet_df(name: str) -> pd.DataFrame:
    scope = ["https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        json.loads(st.secrets["gcp"]["credentials"]), scope
    )
    client = gspread.authorize(creds)
    ws = client.open("fastlabor").worksheet(name)
    vals = ws.get_all_values()
    df = pd.DataFrame(vals[1:], columns=vals[0])
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    return df

# ————————————————————————————————
# 3) Load employer info from post_job sheet
# ————————————————————————————————
post_df = _sheet_df("post_job")
# column ใน post_job ควรมี job_id + ชื่อ employer ใน first_name,last_name
# assume match_row ควรมี job_id ด้วย (ถ้าไม่มีก็ต้องส่งมาจากหน้า matching)
job_id = match_row.get("job_id")
if job_id is None:
    st.error("❌ ไม่พบ job_id ในข้อมูล match")
    st.stop()

employer_row = post_df[post_df["job_id"] == job_id]
if employer_row.empty:
    st.error(f"❌ ไม่พบงาน ID={job_id} ใน post_job")
    st.stop()
employer = employer_row.iloc[0]
employer_name = f"{employer.get('first_name','').strip()} {employer.get('last_name','').strip()}".strip()

# ————————————————————————————————
# 4) Render header & job summary
# ————————————————————————————————
st.header("Job Detail")
st.markdown(f"**Employer:** {employer_name}")
st.markdown(f"**Job Type:** {match_row.get('job_type','-')}")

date = match_row.get("job_date","-")
start, end = match_row.get("start_time","-"), match_row.get("end_time","-")
st.markdown(f"**Date:** {date}")
st.markdown(f"**Time:** {start} – {end}")

address = match_row.get("job_address") or \
    f\"{match_row.get('province','')}/{match_row.get('district','')}/{match_row.get('subdistrict','')}\"
st.markdown(f"**Location:** {address}")

st.markdown(f"**Salary:** {match_row.get('job_salary','-')} THB/day")
st.markdown("---")

# ————————————————————————————————
# 5) Show Employees (could be multiple rows for same job in match_results)
# ————————————————————————————————
# ถ้าใน session_state["matched_employees"] เก็บ list ของ match_row หรือดึงใหม่ได้
# สมมติเก็บรายการเดียว ให้แสดงชื่อคนเดียว
# ถ้าต้องการแสดงหลายคน ให้เก็บ list ลงถัดไป

# ในที่นี้เราจะดึง match_results ทั้งหมดที่มี job_id เดียวกัน
match_df = _sheet_df("match_results")
emps = match_df[match_df["job_id"] == job_id].drop_duplicates(subset="email")

st.subheader("Employees")
for _, emp in emps.iterrows():
    name = f"{emp.get('first_name','').strip()} {emp.get('last_name','').strip()}".strip()
    st.markdown(f"- 👤 {name}")

# ————————————————————————————————
# 6) ปุ่มย้อนกลับ
# ————————————————————————————————
st.divider()
if st.button("🔙 กลับหน้า My Jobs"):
    st.switch_page("pages/list_job.py")
