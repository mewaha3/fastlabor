# pages/result_matching.py

import streamlit as st
import pandas as pd
import json
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials
import gspread

# —————————————————————————————————————————
# 1. Page config & header/navbar
# —————————————————————————————————————————
st.set_page_config(page_title="Result matching | FAST LABOR", layout="centered")
st.markdown("### FAST LABOR")
st.markdown("""
<style>
.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30px;
}
.nav-right a {
    margin-left: 20px;
    text-decoration: none;
    font-weight: bold;
}
</style>
<div class="header">
    <div><strong>FAST LABOR</strong></div>
    <div class="nav-right">
        <a href="/?page=find_job">Find Job</a>
        <a href="/?page=list_job">My Job</a>
        <a href="/?page=profile" style="background: black; color: white; padding: 4px 10px; border-radius: 4px;">Profile</a>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("## Result matching")
st.markdown("List of employee who was matching with job")
st.markdown("---")

# —————————————————————————————————————————
# 2. Connect to Google Sheets and load data
# —————————————————————————————————————————
creds_json = json.loads(st.secrets["gcp"]["credentials"])
scope = ["https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, scope)
gc = gspread.authorize(creds)
sh = gc.open("fastlabor")

def load_df(sheet_name):
    ws = sh.worksheet(sheet_name)
    vals = ws.get_all_values()
    df = pd.DataFrame(vals[1:], columns=vals[0])
    df.columns = (
        df.columns
          .str.strip()
          .str.lower()
          .str.replace(" ", "_")
    )
    return df

jobs_df    = load_df("post_job")
seekers_df = load_df("find_job")

# —————————————————————————————————————————
# 3. Prepare data for matching
# —————————————————————————————————————————
# Convert types
jobs_df["job_date"]    = pd.to_datetime(jobs_df["job_date"], errors="coerce")
seekers_df["job_date"] = pd.to_datetime(seekers_df["job_date"], errors="coerce")

def make_dt(df, dcol, tcol, outcol):
    df[outcol] = pd.to_datetime(
        df[dcol].dt.strftime("%Y-%m-%d") + " " + df[tcol].astype(str),
        errors="coerce"
    )

make_dt(jobs_df,    "job_date","start_time","start_dt")
make_dt(jobs_df,    "job_date","end_time","end_dt")
make_dt(seekers_df, "job_date","start_time","avail_start")
make_dt(seekers_df, "job_date","end_time","avail_end")

jobs_df["min_wage"]         = pd.to_numeric(jobs_df.get("start_salary",0), errors="coerce")
jobs_df["max_wage"]         = pd.to_numeric(jobs_df.get("range_salary",0), errors="coerce")
seekers_df["expected_wage"] = pd.to_numeric(seekers_df.get("salary",0), errors="coerce")

jobs_df["job_type"]    = jobs_df["job_type"].astype(str).str.strip()
seekers_df["job_type"] = seekers_df["job_type"].astype(str).str.strip()

# —————————————————————————————————————————
# 4. Define scoring functions
# —————————————————————————————————————————
def job_type_score(job, seeker):
    return 1.0 if job.job_type.lower()==seeker.job_type.lower() else 0.0

def datetime_score(job, seeker):
    overlap = (min(job.end_dt, seeker.avail_end) - max(job.start_dt, seeker.avail_start)).total_seconds()
    return 1.0 if overlap>0 else 0.0

def location_score(job, seeker):
    return 1.0 if (
        job.province==seeker.province
        and job.district==seeker.district
        and job.subdistrict==seeker.subdistrict
    ) else 0.0

def wage_score(job, seeker):
    return 1.0 if job.min_wage <= seeker.expected_wage <= job.max_wage else 0.0

# —————————————————————————————————————————
# 5. Compute matching and build top3
# —————————————————————————————————————————
weights = {"type":0.4, "time":0.2, "loc":0.2, "wage":0.2}
records = []

for i, job in jobs_df.iterrows():
    for j, seeker in seekers_df.iterrows():
        s1 = job_type_score(job, seeker)
        s2 = datetime_score(job, seeker)
        s3 = location_score(job, seeker)
        s4 = wage_score(job, seeker)
        score = s1*weights["type"] + s2*weights["time"] + s3*weights["loc"] + s4*weights["wage"]
        if score>0:
            records.append({
                "job_idx":   i,
                "seek_idx":  j,
                "seeker_id": seeker.email,
                "score":     score
            })

matches = pd.DataFrame(records)
if matches.empty:
    st.info("⚠️ ยังไม่มีคู่ที่ match ได้")
    st.stop()

# Top-3 per job
top3 = (
    matches
    .sort_values(["job_idx","score"], ascending=[True,False])
    .groupby("job_idx")
    .head(3)
    .reset_index(drop=True)
)

# —————————————————————————————————————————
# 6. Render expanders for each matched employee
# —————————————————————————————————————————
updated_priorities = {}
for idx, row in top3.iterrows():
    seeker = seekers_df.loc[row.seek_idx]
    with st.expander(f"Employee No.{idx+1}"):
        st.write(f"เพศ: {seeker.gender}")
        st.write(f"ทักษะ: {seeker.job_type}")
        priority = st.selectbox(
            "Priority",
            options=[1,2,3,4,5],
            index=idx if idx<5 else 0,
            key=f"priority_{idx}"
        )
        updated_priorities[seeker.email] = priority

# —————————————————————————————————————————
# 7. Confirm button
# —————————————————————————————————————————
if st.button("Confirm"):
    # (ที่นี่คุณอาจจะเขียน updated_priorities ลง Google Sheet หรือ DB)
    st.success("Your matching priorities have been saved!")
    st.write("### Updated priorities")
    st.write(updated_priorities)
    # navigate to status_matching page
    st.experimental_set_query_params(page="status_matching")
    st.experimental_rerun()
