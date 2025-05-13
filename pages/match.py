# pages/match.py

import streamlit as st
import pandas as pd
import json
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials
import gspread

# —————————————————————————————————————————
# 1. Streamlit page config & title
# —————————————————————————————————————————
st.set_page_config(page_title="🔍 Matching by Job Type", layout="wide")
st.title("🔍 Matching Results (by Job Type)")

# —————————————————————————————————————————
# 2. Load GCP credentials
# —————————————————————————————————————————
creds_json = json.loads(st.secrets["gcp"]["credentials"])
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, scope)
gc = gspread.authorize(creds)

# —————————————————————————————————————————
# 3. Open spreadsheet & detect tabs
# —————————————————————————————————————————
SPREADSHEET_NAME = "fastlabor"
sh = gc.open(SPREADSHEET_NAME)
tabs = [ws.title for ws in sh.worksheets()]

# helper: หาแท็บแบบไม่สน case/underscore/space
def find_tab(key):
    nk = key.lower().replace(" ", "").replace("_","")
    for t in tabs:
        if t.lower().replace(" ", "").replace("_","") == nk:
            return t
    return None

jobs_tab    = find_tab("post_job")
seekers_tab = find_tab("find_job")
if not jobs_tab or not seekers_tab:
    st.error(f"Cannot find worksheets: post_job={jobs_tab}, find_job={seekers_tab}")
    st.stop()

# —————————————————————————————————————————
# 4. Load data robustly
# —————————————————————————————————————————
def load_sheet(title):
    ws   = sh.worksheet(title)
    vals = ws.get_all_values()
    if len(vals) < 2:
        return pd.DataFrame()
    df = pd.DataFrame(vals[1:], columns=vals[0])
    # normalize column names
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    return df

jobs_df    = load_sheet(jobs_tab)
seekers_df = load_sheet(seekers_tab)
if jobs_df.empty or seekers_df.empty:
    st.warning("⚠️ post_job or find_job has no data")
    st.stop()

# —————————————————————————————————————————
# 5. Convert job_date to datetime & build start_dt/end_dt
# —————————————————————————————————————————
# แปลงคอลัมน์ job_date ให้เป็น Timestamp
jobs_df["job_date"]    = pd.to_datetime(jobs_df["job_date"], errors="coerce")
seekers_df["job_date"] = pd.to_datetime(seekers_df["job_date"], errors="coerce")

def make_dt(df, date_col, time_col, out_col):
    df[out_col] = pd.to_datetime(
        df[date_col].dt.strftime("%Y-%m-%d") + " " + df[time_col].astype(str),
        errors="coerce"
    )

make_dt(jobs_df,    "job_date",  "start_time",   "start_dt")
make_dt(jobs_df,    "job_date",  "end_time",     "end_dt")
make_dt(seekers_df, "job_date",  "start_time",   "avail_start")
make_dt(seekers_df, "job_date",  "end_time",     "avail_end")

# —————————————————————————————————————————
# 6. Prepare job_type & wages
# —————————————————————————————————————————
# แปลงให้ job_type & salary เป็น string/number
jobs_df["job_type"]       = jobs_df["job_type"].astype(str).str.strip()
seekers_df["job_type"]    = seekers_df["job_type"].astype(str).str.strip()
jobs_df["min_wage"]       = pd.to_numeric(jobs_df.get("start_salary", 0), errors="coerce")
jobs_df["max_wage"]       = pd.to_numeric(jobs_df.get("range_salary", 0), errors="coerce")
seekers_df["expected_wage"] = pd.to_numeric(seekers_df.get("salary", 0), errors="coerce")

# —————————————————————————————————————————
# 7. Scoring functions
# —————————————————————————————————————————
def job_type_score(job, seeker):
    return 1.0 if job.job_type.lower() == seeker.job_type.lower() else 0.0

def datetime_score(job, seeker):
    ov = (min(job.end_dt, seeker.avail_end) - max(job.start_dt, seeker.avail_start)).total_seconds()
    return 1.0 if ov > 0 else 0.0

def location_score(job, seeker):
    return 1.0 if (
        job.province    == seeker.province
        and job.district   == seeker.district
        and job.subdistrict == seeker.subdistrict
    ) else 0.0

def wage_score(job, seeker):
    return 1.0 if job.min_wage <= seeker.expected_wage <= job.max_wage else 0.0

# —————————————————————————————————————————
# 8. Compute match scores
# —————————————————————————————————————————
weights = {"type":0.4, "time":0.2, "loc":0.2, "wage":0.2}
records = []

for i, job in jobs_df.iterrows():
    for j, seeker in seekers_df.iterrows():
        s_type = job_type_score(job, seeker)
        s_time = datetime_score(job, seeker)
        s_loc  = location_score(job, seeker)
        s_wage = wage_score(job, seeker)
        total  = s_type*weights["type"] + s_time*weights["time"] + s_loc*weights["loc"] + s_wage*weights["wage"]
        if total > 0:
            # ใช้ start_dt ในการสร้าง job_id
            jid = job.start_dt.strftime("%Y%m%d_%H%M") + f"_{i}"
            records.append({
                "job_idx":   i,
                "seek_idx":  j,
                "job_id":    jid,
                "seeker_id": seeker.email,
                "score":     total
            })

matches = pd.DataFrame(records)
if matches.empty:
    st.info("⚠️ ยังไม่มีคู่ที่ match ได้")
    st.stop()

top3 = matches.sort_values(["job_idx","score"], ascending=[True,False])\
               .groupby("job_idx")\
               .head(3)

# —————————————————————————————————————————
# 9. Display results
# —————————————————————————————————————————
for _, grp in top3.groupby("job_idx"):
    job = jobs_df.loc[grp.job_idx.iloc[0]]
    st.subheader(f"📄 Job: {job.start_dt.strftime('%Y-%m-%d %H:%M')} ({job.job_type})")
    for _, r in grp.iterrows():
        sk = seekers_df.loc[r.seek_idx]
        st.markdown(
            f"- **{sk.email}** (Score {r.score:.2f})  \n"
            f"  • Job Type: {sk.job_type}  \n"
            f"  • Availability: {sk.avail_start.strftime('%H:%M')}–{sk.avail_end.strftime('%H:%M')}  \n"
            f"  • Location: {sk.province}/{sk.district}/{sk.subdistrict}  \n"
            f"  • Expected Wage: {sk.expected_wage}"
        )
    st.markdown("---")
