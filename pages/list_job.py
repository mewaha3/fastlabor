# pages/list_job.py

import streamlit as st
import pandas as pd
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# 1. Read query parameters
params   = st.experimental_get_query_params()
job_idx  = params.get("job_idx", [None])[0]
seek_idx = params.get("seeker_idx", [None])[0]

# 2. Authenticate & connect to Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
if "gcp" in st.secrets:
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        json.loads(st.secrets["gcp"]["credentials"]), scope
    )
else:
    creds = ServiceAccountCredentials.from_json_keyfile_name("pages/credentials.json", scope)
gc    = gspread.authorize(creds)
sh    = gc.open("fastlabor")

# 3. Loader using get_all_values()
def load_df(name: str) -> pd.DataFrame:
    ws   = sh.worksheet(name)
    vals = ws.get_all_values()
    df   = pd.DataFrame(vals[1:], columns=vals[0])
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    return df

jobs_df    = load_df("post_job")
seekers_df = load_df("find_job")

# 4. Prepare datetime and wages
jobs_df["job_date"]    = pd.to_datetime(jobs_df["job_date"], errors="coerce")
seekers_df["job_date"] = pd.to_datetime(seekers_df["job_date"], errors="coerce")

def make_dt(df, dcol, tcol, out_col):
    df[out_col] = pd.to_datetime(
        df[dcol].dt.strftime("%Y-%m-%d") + " " + df[tcol].astype(str),
        errors="coerce"
    )

make_dt(jobs_df,    "job_date", "start_time", "start_dt")
make_dt(jobs_df,    "job_date", "end_time",   "end_dt")
make_dt(seekers_df, "job_date", "start_time", "avail_start")
make_dt(seekers_df, "job_date", "end_time",   "avail_end")

for df in (jobs_df, seekers_df):
    for col in ("start_salary", "range_salary"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

# 5. Scoring functions
def job_type_score(j, s):
    return 1.0 if j.job_type.lower() == s.job_type.lower() else 0.0

def datetime_score(j, s):
    ov = (min(j.end_dt, s.avail_end) - max(j.start_dt, s.avail_start)).total_seconds()
    return 1.0 if ov > 0 else 0.0

def location_score(j, s):
    return 1.0 if (j.province, j.district, j.subdistrict) == (s.province, s.district, s.subdistrict) else 0.0

def wage_score(j, s):
    return 1.0 if j.start_salary <= s.start_salary <= j.range_salary else 0.0

weights = {"type":0.4, "time":0.2, "loc":0.2, "wage":0.2}

# 6. Page layout
st.set_page_config(layout="wide")
st.markdown("<h1>📄 My Jobs</h1>", unsafe_allow_html=True)

# 7. If params present, show matching results
if job_idx is not None or seek_idx is not None:
    st.subheader("🔍 Matching Results")
    records = []
    for i, job in jobs_df.iterrows():
        if job_idx is not None and str(i) != job_idx: 
            continue
        for j, seeker in seekers_df.iterrows():
            if seek_idx is not None and str(j) != seek_idx: 
                continue
            s1 = job_type_score(job, seeker)
            s2 = datetime_score(job, seeker)
            s3 = location_score(job, seeker)
            s4 = wage_score(job, seeker)
            total = s1*weights["type"] + s2*weights["time"] + s3*weights["loc"] + s4*weights["wage"]
            if total > 0:
                records.append((i, j, total))
    if not records:
        st.info("❌ No matches found")
    else:
        records.sort(key=lambda x: -x[2])
        for rank, (i, j, sc) in enumerate(records, start=1):
            job = jobs_df.loc[i]
            seeker = seekers_df.loc[j]
            st.markdown(f"### Rank {rank} — Score: {sc:.2f}")
            st.markdown(f"""
- **Job**: {job.job_type} on {job.job_date.date()} ({job.start_time}–{job.end_time})  
- **Seeker**: {seeker.email}  
- **Skill**: {seeker.skill if 'skill' in seeker else seeker.job_type if 'job_type' in seeker else ''}  
- **Available**: {seeker.job_date.date()} {seeker.start_time}–{seeker.end_time}  
- **Location**: {seeker.province}/{seeker.district}/{seeker.subdistrict}  
- **Expected Wage**: {seeker.start_salary}–{seeker.range_salary}
""")
    if st.button("🔙 Back to My Jobs"):
        st.experimental_set_query_params()
        st.experimental_rerun()

# 8. Otherwise show listings with View Matching buttons
else:
    tab1, tab2 = st.tabs(["📌 Post Job", "🔍 Find Job"])
    with tab1:
        st.subheader("📌 Posted Jobs")
        if jobs_df.empty:
            st.info("No posted jobs")
        else:
            for i, row in jobs_df.iterrows():
                st.markdown("---")
                st.markdown(f"**Job #{i+1}** — {row.job_type}")
                if st.button("View Matching", key=f"jm{i}"):
                    st.experimental_set_query_params(job_idx=i)
                    st.experimental_rerun()

    with tab2:
        st.subheader("🔍 Job Seekers")
        if seekers_df.empty:
            st.info("No job seekers")
        else:
            for j, row in seekers_df.iterrows():
                st.markdown("---")
                label = row.get("skills", row.get("job_detail", ""))
                st.markdown(f"**Find #{j+1}** — {label}")
                if st.button("View Matching", key=f"sk{j}"):
                    st.experimental_set_query_params(seeker_idx=j)
                    st.experimental_rerun()
