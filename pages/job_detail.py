import streamlit as st
from datetime import datetime
import pandas as pd
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials

# 1) Page Config
st.set_page_config(layout="centered")

# Header & Navigation
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

# Title
st.markdown("## Job Detail")
st.image("image.png", width=150)

# 2) Connect to Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(
    json.loads(st.secrets["gcp"]["credentials"]), scope
)
gc = gspread.authorize(creds)
sh = gc.open("fastlabor")

# 3) Load match_results sheet
ws_match = sh.worksheet("match_results")
match_results_df = pd.DataFrame(ws_match.get_all_records())

# 4) Load post_job sheet for employer info
ws_post = sh.worksheet("post_job")
post_df = pd.DataFrame(ws_post.get_all_records())

# Get selected match from session
selected = st.session_state.get("selected_job")
if not selected:
    st.info("Please select a job from the previous page.")
    st.stop()

# Extract job_id and find corresponding employer
job_id = selected.get("job_id")
employer_row = post_df[post_df["job_id"] == job_id]
if not employer_row.empty:
    emp = employer_row.iloc[0]
    employer_name = f"{emp.get('first_name','').strip()} {emp.get('last_name','').strip()}".strip()
else:
    employer_name = "N/A"

# --- Display Job & Employer ---
st.markdown(f"**Employer:** {employer_name}")
st.text_input("Job Type", value=selected.get('job_type',''), disabled=True)
st.text_input("Job Status", value="In-Progress", disabled=True)

# Date / Time
job_date = selected.get('job_date','')
start_date, end_date = (job_date.split(' to ') + [job_date])[:2]
st.date_input("Start Date", datetime.fromisoformat(start_date) if start_date else None, disabled=True)
st.date_input("End Date",   datetime.fromisoformat(end_date)   if end_date   else None, disabled=True)

start_time = selected.get('start_time','08:00:00')
end_time   = selected.get('end_time','17:00:00')
st.time_input("Start Time", datetime.fromisoformat(f"1970-01-01T{start_time}").time(), disabled=True)
st.time_input("End Time",   datetime.fromisoformat(f"1970-01-01T{end_time}").time(),   disabled=True)

# Address / Location
address = selected.get('job_address') or f"{selected.get('subdistrict','')}, {selected.get('district','')}, {selected.get('province','')}"
st.text_area("Job Address (House No, Road, District)", value=address, disabled=True)
st.text_input("Province",    selected.get('province',''),    disabled=True)
st.text_input("District",    selected.get('district',''),    disabled=True)
st.text_input("Subdistrict", selected.get('subdistrict',''), disabled=True)

# Gender (of employee)
st.text_input("Gender", selected.get('gender',''), disabled=True)

# Salary
st.text_input("Job Salary", selected.get('job_salary',''), disabled=True)

# --- Employees List ---
st.markdown("#### Employee")
# filter match_results by this findjob_id
emps = match_results_df[match_results_df['findjob_id'] == selected.get('findjob_id')]
if not emps.empty:
    for _, e in emps.iterrows():
        name = f"{e.get('first_name','')} {e.get('last_name','')}"
        st.write(f"👤 {name}")
else:
    st.write("No employees selected for this job.")

# --- Actions ---
col1, col2 = st.columns(2)
def update_job_done(fid, who):
    # write "Job Done" to status column
    df = match_results_df
    idx = df.index[df["findjob_id"] == fid][0] + 2
    ws_match.update_acell(f"O{idx}", "Job Done")
    st.success(f"{who} saved Job Done!")
    st.experimental_rerun()

with col1:
    if st.button("✅ Job Done นายจ้าง"):
        update_job_done(selected.get('findjob_id'), "Employer")
with col2:
    if st.button("🧑‍🔧 Job Done ลูกจ้าง"):
        update_job_done(selected.get('findjob_id'), "Employee")

# Payment and Back
st.markdown("---")
st.page_link("pages/payment.py", label="💳 ชำระเงิน")
if st.button("🔙 กลับหน้า My Jobs"):
    st.switch_page("pages/list_job.py")
