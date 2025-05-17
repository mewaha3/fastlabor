import streamlit as st
from datetime import datetime, date, time
import pandas as pd
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials

# 1) Page Config
st.set_page_config(layout="centered")

# Header & Navigation (เหมือนเดิม) …
st.markdown("""
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
    <div><strong>FAST LABOR</strong></div>
    <div>
        <a href="#" style="margin-right: 20px;">Find Job</a>
        <a href="#" style="margin-right: 20px;">My Job</a>
        <a href="#" style="background-color: black; color: white; padding: 5px 10px; border-radius: 4px;">Profile</a>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("## Job Detail")
st.image("image.png", width=150)

# 2) Connect to Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(
    json.loads(st.secrets["gcp"]["credentials"]), scope
)
gc = gspread.authorize(creds)
sh = gc.open("fastlabor")

# 3) Load sheets
ws_match = sh.worksheet("match_results")
match_results_df = pd.DataFrame(ws_match.get_all_records())

ws_post = sh.worksheet("post_job")
post_df = pd.DataFrame(ws_post.get_all_records())

# 4) Get selected match
selected = st.session_state.get("selected_job")
if not selected:
    st.info("Please select a job from the previous page.")
    st.stop()

# 5) Find employer
job_id = selected.get("job_id")
emp_row = post_df[post_df["job_id"] == job_id]
if not emp_row.empty:
    emp = emp_row.iloc[0]
    employer_name = f"{emp.get('first_name','')} {emp.get('last_name','')}".strip()
else:
    employer_name = "N/A"

st.markdown(f"**Employer:** {employer_name}")

# 6) Job fields
st.text_input("Job Type", value=selected.get('job_type',''), disabled=True)
st.text_input("Job Status", value="In-Progress", disabled=True)

# helper for parsing date/time
def parse_date(ds: str) -> date | None:
    for fmt in ("%Y-%m-%d","%Y/%m/%d"):
        try:
            return datetime.strptime(ds, fmt).date()
        except:
            continue
    return None

def parse_time(ts: str) -> time | None:
    for fmt in ("%H:%M:%S","%H:%M"):
        try:
            return datetime.strptime(ts, fmt).time()
        except:
            continue
    return None

# Date
job_date = selected.get("job_date","")
if " to " in job_date:
    d1, d2 = job_date.split(" to ",1)
else:
    d1 = d2 = job_date

start_date = parse_date(d1) or date.today()
end_date   = parse_date(d2) or start_date
col_d1, col_d2 = st.columns(2)
with col_d1:
    st.date_input("Start Date", start_date, disabled=True)
with col_d2:
    st.date_input("End Date", end_date,   disabled=True)

# Time
st_tm = selected.get("start_time","08:00")
en_tm = selected.get("end_time","17:00")
start_tm = parse_time(st_tm) or time(8,0)
end_tm   = parse_time(en_tm) or time(17,0)
col_t1, col_t2 = st.columns(2)
with col_t1:
    st.time_input("Start Time", start_tm, disabled=True)
with col_t2:
    st.time_input("End Time", end_tm,   disabled=True)

# Address
address = selected.get("job_address") or \
    f"{selected.get('subdistrict','')}, {selected.get('district','')}, {selected.get('province','')}"
st.text_area("Job Address (House No, Road, District)", address, disabled=True)

col_p, col_d = st.columns(2)
with col_p:
    st.text_input("Province", selected.get('province',''), disabled=True)
with col_d:
    st.text_input("District", selected.get('district',''), disabled=True)

col_s, col_g = st.columns(2)
with col_s:
    st.text_input("Subdistrict", selected.get('subdistrict',''), disabled=True)
with col_g:
    st.text_input("Gender", selected.get('gender',''), disabled=True)

st.text_input("Job Salary", selected.get('job_salary',''), disabled=True)

# 7) Employees
st.markdown("#### Employee")
emps = match_results_df[match_results_df['findjob_id'] == selected.get('findjob_id')]
if not emps.empty:
    names = emps.drop_duplicates(subset=["email"])[["first_name","last_name"]]
    for _, e in names.iterrows():
        st.write(f"👤 {e['first_name']} {e['last_name']}")
else:
    st.write("No employees selected for this job.")

# 8) Actions
col1, col2 = st.columns(2)
def update_done(status_label: str):
    df = match_results_df
    try:
        idx = df.index[df["findjob_id"] == selected.get("findjob_id")][0] + 2
        ws_match.update_acell(f"O{idx}", "Job Done")
        st.success(f"{status_label} saved Job Done!")
    except:
        st.error("Cannot update status.")

with col1:
    if st.button("✅ Job Done นายจ้าง"):
        update_done("Employer")
        st.switch_page("pages/review_employee.py")

with col2:
    if st.button("🧑‍🔧 Job Done ลูกจ้าง"):
        update_done("Employee")
        st.switch_page("pages/review_employer.py")
st.markdown("---")
st.page_link("pages/payment.py", label="💳 ชำระเงิน")
if st.button("🔙 กลับหน้า My Jobs"):
    st.switch_page("pages/list_job.py")
