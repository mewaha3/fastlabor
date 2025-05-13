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
jobs_df["job_date"]    = pd.to_datetime(jobs_df["job_date"], errors="coerce")
seekers_df["job_date"] = pd.to_datetime(seekers_df["job_date"], errors="coerce")

def make_dt(df, date_col, time_col, out_col):
    df[out_col] = pd.to_datetime(
        df[date_col].dt.strftime("%Y-%m-%d") + " " +
        df[time_col].astype(str),
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
    return 1.0 if job.job_type.lower() == seeker.job_type.lower() else 0.0

def datetime_score(job, seeker):
    ov = (min(job.end_dt, seeker.avail_end) -
          max(job.start_dt, seeker.avail_start)).total_seconds()
    return 1.0 if ov > 0 else 0.0

def location_score(job, seeker):
    return 1.0 if (
        job.province   == seeker.province
        and job.district   == seeker.district
        and job.subdistrict== seeker.subdistrict
    ) else 0.0

def wage_score(job, seeker):
    return 1.0 if job.min_wage <= seeker.expected_wage <= job.max_wage else 0.0

# —————————————————————————————————————————
# 5. Compute matching & select Top-5 per job
# —————————————————————————————————————————
weights = {"type":0.4, "time":0.2, "loc":0.2, "wage":0.2}
records = []

for i, job in jobs_df.iterrows():
    for j, seeker in seekers_df.iterrows():
        score = (
            job_type_score(job,seeker)*weights["type"] +
            datetime_score(job,seeker)*weights["time"] +
            location_score(job,seeker)*weights["loc"] +
            wage_score(job,seeker)*weights["wage"]
        )
        if score > 0:
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

top5 = (
    matches
    .sort_values(["job_idx","score"], ascending=[True,False])
    .groupby("job_idx")
    .head(5)           # <-- Top 5
    .reset_index(drop=True)
)

# —————————————————————————————————————————
# 6. Render expanders for Top-5 with default Priority = idx+1
# —————————————————————————————————————————
updated_priorities = {}

for idx, row in top5.iterrows():  # idx = 0..4
    seeker = seekers_df.loc[row.seek_idx]
    with st.expander(f"Employee No.{idx+1}"):
        st.write(f"ทักษะ: {seeker.job_type}")
        priority = st.selectbox(
            "Priority",
            options=[1,2,3,4,5],
            index=idx,                # <-- default is idx (0→1,1→2…)
            key=f"priority_{idx}"
        )
        updated_priorities[seeker.email] = priority

# —————————————————————————————————————————
# 7. Confirm button & navigation
# —————————————————————————————————————————
if st.button("Confirm"):
    st.success("Your matching priorities have been saved!")
    st.write("### Updated priorities")
    st.write(updated_priorities)
    st.experimental_set_query_params(page="status_matching")
    st.experimental_rerun()
