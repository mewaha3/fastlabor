# pages/match.py

import streamlit as st
import pandas as pd
import json
import math
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials
import gspread
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# —————————————————————————————————————————
# 1. Streamlit page config & title
# —————————————————————————————————————————
st.set_page_config(page_title="🔍 Matching Jobs", layout="wide")
st.title("🔍 Matching Results")

# —————————————————————————————————————————
# 2. Load Google Sheets credentials from Secrets
# —————————————————————————————————————————
# In .streamlit/secrets.toml:
# [gcp]
# credentials = """ { …service account JSON… } """
creds_json = json.loads(st.secrets["gcp"]["credentials"])
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, scope)
gc = gspread.authorize(creds)

# —————————————————————————————————————————
# 3. Open Spreadsheet & load worksheets
# —————————————————————————————————————————
SPREADSHEET_NAME = "fastlabor"   # Exact sheet name
sh = gc.open(SPREADSHEET_NAME)

# Detect available tabs
tabs = [ws.title for ws in sh.worksheets()]
st.write("Available worksheets:", tabs)

# Load the correct tabs (case-insensitive match)
def find_tab(name):
    n = name.lower().replace(" ", "").replace("_","")
    for t in tabs:
        if t.lower().replace(" ", "").replace("_","") == n:
            return t
    return None

jobs_tab    = find_tab("post_job")
seekers_tab = find_tab("find_job")
if not jobs_tab or not seekers_tab:
    st.error(f"Cannot find worksheets: post_job={jobs_tab}, find_job={seekers_tab}")
    st.stop()

jobs_ws    = sh.worksheet(jobs_tab)
seekers_ws = sh.worksheet(seekers_tab)

# Load robustly with get_all_values()
def load_sheet(ws):
    vals = ws.get_all_values()
    if len(vals) < 2:
        return pd.DataFrame()  # no data
    header = vals[0]
    data   = vals[1:]
    return pd.DataFrame(data, columns=header)

jobs_df    = load_sheet(jobs_ws)
seekers_df = load_sheet(seekers_ws)

if jobs_df.empty or seekers_df.empty:
    st.warning("⚠️ post_job or find_job has no records yet")
    st.stop()

# —————————————————————————————————————————
# 4. Prepare columns: skills & wages
# —————————————————————————————————————————
# In seekers, if 'job_detail' used instead of 'skills', copy it:
if "skills" not in seekers_df.columns and "job_detail" in seekers_df.columns:
    seekers_df["skills"] = seekers_df["job_detail"].astype(str)
else:
    seekers_df["skills"] = seekers_df["skills"].astype(str)

jobs_df["min_wage"]         = pd.to_numeric(jobs_df.get("start_salary",0), errors="coerce")
jobs_df["max_wage"]         = pd.to_numeric(jobs_df.get("range_salary",0), errors="coerce")
seekers_df["expected_wage"] = pd.to_numeric(seekers_df.get("salary",0), errors="coerce")

# —————————————————————————————————————————
# 5. Combine date+time => datetime
# —————————————————————————————————————————
def make_dt(df, date_col, time_col, out_col):
    df[out_col] = pd.to_datetime(
        df[date_col].astype(str)+" "+df[time_col].astype(str),
        errors="coerce"
    )

make_dt(jobs_df,    "job_date",  "start_time",   "start_dt")
make_dt(jobs_df,    "job_date",  "end_time",     "end_dt")
make_dt(seekers_df, "job_date",  "start_time",   "avail_start")
make_dt(seekers_df, "job_date",  "end_time",     "avail_end")

# —————————————————————————————————————————
# 6. Build TF-IDF for skills
# —————————————————————————————————————————
tfidf = TfidfVectorizer(token_pattern=r"(?u)\b\w+\b")
corpus = list(jobs_df["skills"]) + list(seekers_df["skills"])
mat    = tfidf.fit_transform(corpus)
jt     = mat[: len(jobs_df)]
stf    = mat[len(jobs_df):]

def skill_score(i,j):
    return cosine_similarity(jt[i], stf[j])[0,0]

# —————————————————————————————————————————
# 7. Time, location & wage scoring
# —————————————————————————————————————————
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
# 8. Compute matches
# —————————————————————————————————————————
weights = {"skill":0.4, "time":0.2, "loc":0.2, "wage":0.2}
records = []

for i, job in jobs_df.iterrows():
    for j, seeker in seekers_df.iterrows():
        s1 = skill_score(i,j)
        s2 = datetime_score(job,seeker)
        s3 = location_score(job,seeker)
        s4 = wage_score(job,seeker)
        total = s1*weights["skill"] + s2*weights["time"] + s3*weights["loc"] + s4*weights["wage"]
        if total > 0:
            records.append({
                "job_idx":    i,
                "seek_idx":   j,
                "job_id":     f"{job.job_date}_{i}",
                "seeker_id":  seeker.email,
                "score":      total
            })

matches = pd.DataFrame(records)
if matches.empty:
    st.info("⚠️ ไม่มีคู่ที่ match ได้")
    st.stop()

# Top-3 per job
top3 = matches.sort_values(["job_idx","score"],ascending=[True,False]).groupby("job_idx").head(3)

# —————————————————————————————————————————
# 9. Display results
# —————————————————————————————————————————
for _, grp in top3.groupby("job_idx"):
    job = jobs_df.loc[grp.job_idx.iloc[0]]
    st.subheader(f"📄 Job: {job.job_date} {job.start_time}–{job.end_time}")
    for _, r in grp.iterrows():
        sk = seekers_df.loc[r.seek_idx]
        st.markdown(
            f"- **{sk.email}** (Score {r.score:.2f})  \n"
            f"  • Skills: {sk.skills}  \n"
            f"  • Availability: {sk.avail_start}–{sk.avail_end}  \n"
            f"  • Location: {sk.province}/{sk.district}/{sk.subdistrict}  \n"
            f"  • Expected Wage: {sk.expected_wage}"
        )
    st.markdown("---")
