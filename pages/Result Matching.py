# pages/result_matching.py

import streamlit as st
import pandas as pd
import json
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials
import gspread

# 1) Page config + guard
st.set_page_config(page_title="Result Matching | FAST LABOR", layout="wide")
if not st.session_state.get("logged_in", False):
    st.experimental_set_query_params(page="login")
    st.stop()

# 2) Header / nav
st.markdown("### FAST LABOR")
st.markdown("""
<style>
.header { display:flex; justify-content:space-between; align-items:center; margin-bottom:30px; }
.nav-right a { margin-left:20px; text-decoration:none; font-weight:bold; }
</style>
<div class="header">
  <div><strong>FAST LABOR</strong></div>
  <div class="nav-right">
    <a href="/?page=find_job">Find Job</a>
    <a href="/?page=list_job">My Jobs</a>
    <a href="/?page=profile" style="background:black;color:white;padding:4px 10px;border-radius:4px">Profile</a>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("## Result Matching")
st.markdown("List of employees matching this job")
st.markdown("---")

# 3) Read query params
params = st.experimental_get_query_params()
job_idx    = params.get("job_idx", [None])[0]
seeker_idx = params.get("seeker_idx", [None])[0]

# 4) Google Sheets setup
creds_json = json.loads(st.secrets["gcp"]["credentials"])
scope = ["https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, scope)
gc    = gspread.authorize(creds)
sh    = gc.open("fastlabor")

def load_df(sheet):
    ws   = sh.worksheet(sheet)
    vals = ws.get_all_values()
    df   = pd.DataFrame(vals[1:], columns=vals[0])
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    return df

jobs    = load_df("post_job")
seekers = load_df("find_job")

# 5) Prepare datetime & numeric
for df in (jobs, seekers):
    df["job_date"] = pd.to_datetime(df["job_date"], errors="coerce")
    for tcol in ("start_time","end_time"):
        df[tcol] = pd.to_datetime(df[tcol], format="%H:%M:%S", errors="coerce").dt.time
    for wage in ("start_salary","range_salary","salary"):
        if wage in df.columns:
            df[wage] = pd.to_numeric(df[wage], errors="coerce").fillna(0)

def make_dt(df, date_col, time_col, out_col):
    df[out_col] = df.apply(lambda r: datetime.combine(r[date_col], r[time_col]), axis=1)

make_dt(jobs,    "job_date","start_time","job_start_dt")
make_dt(jobs,    "job_date","end_time",  "job_end_dt")
make_dt(seekers, "job_date","start_time","avail_start_dt")
make_dt(seekers, "job_date","end_time",  "avail_end_dt")

jobs["min_wage"] = jobs["start_salary"]
jobs["max_wage"] = jobs["range_salary"]
seekers["exp_wage"] = seekers["start_salary"]

# 6) Scoring
def s_type(j,s): return 1 if j.job_type.lower()==s.job_type.lower() else 0
def s_time(j,s): return 1 if (min(j.job_end_dt, s.avail_end_dt) - max(j.job_start_dt, s.avail_start_dt)).total_seconds()>0 else 0
def s_loc(j,s):  return 1 if (j.province, j.district, j.subdistrict)==(s.province, s.district, s.subdistrict) else 0
def s_wage(j,s): return 1 if j.min_wage <= s.exp_wage <= j.max_wage else 0

w = {"type":0.4, "time":0.2, "loc":0.2, "wage":0.2}
records = []

for i, job in jobs.iterrows():
    # filter by job_idx if provided
    if job_idx is not None and str(i) != str(job_idx):
        continue
    for j, seeker in seekers.iterrows():
        if seeker_idx is not None and str(j) != str(seeker_idx):
            continue
        score = (
            s_type(job,seeker)*w["type"] +
            s_time(job,seeker)*w["time"] +
            s_loc(job,seeker)*w["loc"] +
            s_wage(job,seeker)*w["wage"]
        )
        if score > 0:
            records.append({"job_idx":i, "seek_idx":j, "score":score})

matches = pd.DataFrame(records)
if matches.empty:
    st.info("⚠️ ยังไม่มีคู่ที่ match ได้")
    st.stop()

# Top-5 per job
top5 = (
    matches
    .sort_values(["job_idx","score"], ascending=[True,False])
    .groupby("job_idx")
    .head(5)
    .reset_index(drop=True)
)

# 7) Show expanders
updated_priorities = {}
for rank, row in enumerate(top5.itertuples(), start=1):
    seeker = seekers.loc[row.seek_idx]
    with st.expander(f"Employee No.{rank}"):
        st.write(f"- Email: {seeker.email}")
        st.write(f"- Skill: {seeker.job_type}")
        priority = st.selectbox(
            "Priority",
            options=[1,2,3,4,5],
            index=rank-1,
            key=f"prio_{rank}"
        )
        updated_priorities[seeker.email] = priority

# 8) Confirm
if st.button("Confirm"):
    st.success("Your matching priorities have been saved!")
    st.write(updated_priorities)
    st.experimental_set_query_params(page="status_matching")
    st.experimental_rerun()
