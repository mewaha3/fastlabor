# pages/list_job.py

import streamlit as st
import pandas as pd
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# 1. Read query params to decide mode
params   = st.experimental_get_query_params()
job_idx  = params.get("job_idx", [None])[0]
seek_idx = params.get("seeker_idx", [None])[0]

# 2. Auth & connect to Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
if "gcp" in st.secrets:
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        json.loads(st.secrets["gcp"]["credentials"]), scope
    )
else:
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        "pages/credentials.json", scope
    )
gc    = gspread.authorize(creds)
sh    = gc.open("fastlabor")

# 3. Loader (all values + normalize columns)
def load_df(name: str) -> pd.DataFrame:
    ws   = sh.worksheet(name)
    vals = ws.get_all_values()
    df   = pd.DataFrame(vals[1:], columns=vals[0])
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    return df

jobs_df    = load_df("post_job")
seekers_df = load_df("find_job")

# 4. Prepare date/time columns
jobs_df["job_date"]    = pd.to_datetime(jobs_df["job_date"], errors="coerce")
seekers_df["job_date"] = pd.to_datetime(seekers_df["job_date"], errors="coerce")

def make_dt(df, dcol, tcol, out):
    df[out] = pd.to_datetime(df[dcol].dt.strftime("%Y-%m-%d") + " " + df[tcol].astype(str), errors="coerce")

make_dt(jobs_df,    "job_date", "start_time", "start_dt")
make_dt(jobs_df,    "job_date", "end_time",   "end_dt")
make_dt(seekers_df, "job_date", "start_time", "avail_start")
make_dt(seekers_df, "job_date", "end_time",   "avail_end")

# 5. Normalize salary fields
for df in (jobs_df, seekers_df):
    for c in ("start_salary", "range_salary"):
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

# 6. Scoring functions
def job_type_score(j,s): return 1 if str(j.job_type).lower()==str(s.job_type).lower() else 0
def datetime_score(j,s):
    ov=(min(j.end_dt,s.avail_end)-max(j.start_dt,s.avail_start)).total_seconds()
    return 1 if ov>0 else 0
def location_score(j,s):
    return 1 if (j.province,j.district,j.subdistrict)==(s.province,s.district,s.subdistrict) else 0
def wage_score(j,s):
    return 1 if j.start_salary<=s.start_salary<=j.range_salary else 0

weights = {"type":0.4,"time":0.2,"loc":0.2,"wage":0.2}

# 7. Page layout
st.set_page_config(layout="wide")
st.title("📄 My Jobs")

# 8. If a job_idx or seeker_idx is set, show the Result Matching section
if job_idx is not None or seek_idx is not None:
    st.subheader("🔍 Matching Results")

    records = []
    for i, j in jobs_df.iterrows():
        if job_idx is not None and str(i)!=job_idx: continue
        for k, s in seekers_df.iterrows():
            if seek_idx is not None and str(k)!=seek_idx: continue
            sc = (
                job_type_score(j,s)*weights["type"] +
                datetime_score(j,s)*weights["time"] +
                location_score(j,s)*weights["loc"] +
                wage_score(j,s)*weights["wage"]
            )
            if sc>0:
                records.append((i,k,sc))
    if not records:
        st.info("⚠️ No matches found")
    else:
        records.sort(key=lambda x:-x[2])
        for rank, (i,k,sc) in enumerate(records, start=1):
            job    = jobs_df.loc[i]
            seeker = seekers_df.loc[k]
            st.markdown(f"### Rank {rank} — Score: {sc:.2f}")
            st.markdown(f"""
- **Job**: {job.job_type} on {job.job_date.date()} ({job.start_time}–{job.end_time})
- **Seeker**: {seeker.email}
- **Skill**: {getattr(seeker,'skills', seeker.job_type)}
- **Available**: {seeker.job_date.date()} {seeker.start_time}–{seeker.end_time}
- **Location**: {seeker.province}/{seeker.district}/{seeker.subdistrict}
- **Expected Wage**: {seeker.start_salary:.0f}–{seeker.range_salary:.0f}
""")
    if st.button("🔙 Back to My Jobs"):
        st.experimental_set_query_params()
        st.experimental_rerun()

# 9. Otherwise show the two tabs with listings
else:
    tab1, tab2 = st.tabs(["📌 Post Job", "🔍 Find Job"])

    with tab1:
        st.subheader("📌 รายการโพสต์งาน")
        if jobs_df.empty:
            st.info("ยังไม่มีข้อมูลโพสต์งาน")
        else:
            for i, row in jobs_df.iterrows():
                st.markdown("---")
                st.markdown(f"**Job #{i+1}** — {row.job_type}")
                if st.button("View Matching", key=f"jm{i}"):
                    st.experimental_set_query_params(job_idx=i)
                    st.experimental_rerun()

    with tab2:
        st.subheader("🔍 รายการค้นหางาน")
        if seekers_df.empty:
            st.info("ยังไม่มีข้อมูลค้นหางาน")
        else:
            for k, row in seekers_df.iterrows():
                st.markdown("---")
                label = row.get("skills", row.get("job_detail",""))
                st.markdown(f"**Find #{k+1}** — {label}")
                if st.button("View Matching", key=f"sk{k}"):
                    st.experimental_set_query_params(seeker_idx=k)
                    st.experimental_rerun()
