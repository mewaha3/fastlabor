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

st.set_page_config(page_title="🔍 Matching Jobs", layout="wide")
st.title("🔍 Matching Results")

# 1. เชื่อม GSheet
creds_json = json.loads(st.secrets["gcp"]["credentials"])
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, scope)
gc = gspread.authorize(creds)

# 2. เปิด Spreadsheet
SPREADSHEET_NAME = "fastlabor"  # ชื่อจริงตามภาพ
sh = gc.open(SPREADSHEET_NAME)

# 3. ตรวจชื่อแท็บทั้งหมด
all_titles = [ws.title for ws in sh.worksheets()]
st.write("Available worksheets:", all_titles)

# 4. หาแท็บ post_job / find_job แบบ case-insensitive
def find_sheet(title_list, key):
    key = key.lower().replace(" ", "").replace("-", "").replace("_", "")
    for t in title_list:
        norm = t.lower().replace(" ", "").replace("-", "").replace("_", "")
        if norm == key:
            return t
    return None

jobs_tab    = find_sheet(all_titles, "post_job")
seekers_tab = find_sheet(all_titles, "find_job")

if not jobs_tab or not seekers_tab:
    st.error(f"Cannot find required sheets: post_job={jobs_tab}, find_job={seekers_tab}")
    st.stop()

# 5. ฟังก์ชันโหลด sheet แบบ robust
def load_sheet(ws):
    vals = ws.get_all_values()
    if len(vals) < 2:
        return pd.DataFrame()  # ไม่มี data
    header = vals[0]
    data   = vals[1:]
    return pd.DataFrame(data, columns=header)

jobs_df    = load_sheet(sh.worksheet(jobs_tab))
seekers_df = load_sheet(sh.worksheet(seekers_tab))

if jobs_df.empty or seekers_df.empty:
    st.warning("⚠️ post_job หรือ find_job ยังไม่มีข้อมูล")
    st.stop()

# 6. เตรียมคอลัมน์ skills & wages
if "skills" not in seekers_df.columns and "job_detail" in seekers_df.columns:
    seekers_df["skills"] = seekers_df["job_detail"].astype(str)
else:
    seekers_df["skills"] = seekers_df["skills"].astype(str)

jobs_df["min_wage"]        = pd.to_numeric(jobs_df.get("start_salary", 0), errors="coerce")
jobs_df["max_wage"]        = pd.to_numeric(jobs_df.get("range_salary", 0), errors="coerce")
seekers_df["expected_wage"]= pd.to_numeric(seekers_df.get("salary", 0), errors="coerce")

# 7. รวม date+time → datetime
def make_dt(df, date_col, time_col, out_col):
    df[out_col] = pd.to_datetime(
        df[date_col].astype(str) + " " + df[time_col].astype(str),
        errors="coerce"
    )
for df, s, e, o1, o2 in [
    (jobs_df, "job_date", "start_time", "start_dt"),
    (jobs_df, "job_date", "end_time",   "end_dt"),
    (seekers_df, "job_date", "start_time","avail_start"),
    (seekers_df, "job_date", "end_time","avail_end"),
]:
    make_dt(df, s, e, o1 if o1==o2 else o1)
    # note: if out_col differs, call twice
    if o1!=o2: make_dt(df, s, e, o2)

# 8. TF-IDF similarity
tfidf   = TfidfVectorizer(token_pattern=r"(?u)\b\w+\b")
corpus  = list(jobs_df["skills"]) + list(seekers_df["skills"])
tfidf_m = tfidf.fit_transform(corpus)
jt, stf = tfidf_m[: len(jobs_df)], tfidf_m[len(jobs_df):]

def skill_score(i,j): return cosine_similarity(jt[i], stf[j])[0,0]

# 9. อื่นๆ: time, location, wage
def datetime_score(job, seeker):
    ov = (min(job.end_dt, seeker.avail_end) - max(job.start_dt, seeker.avail_start)).total_seconds()
    return 1.0 if ov>0 else 0.0

def location_score(job, seeker):
    return 1.0 if (
        job.province==seeker.province
        and job.district==seeker.district
        and job.subdistrict==seeker.subdistrict
    ) else 0.0

def wage_score(job, seeker):
    return 1.0 if job.min_wage <= seeker.expected_wage <= job.max_wage else 0.0

# 10. คำนวณ match
weights = {"skill":0.4,"time":0.2,"loc":0.2,"wage":0.2}
rows=[]
for i,job in jobs_df.iterrows():
    for j,sk in seekers_df.iterrows():
        sc = (
            skill_score(i,j)*weights["skill"]+
            datetime_score(job,sk)*weights["time"]+
            location_score(job,sk)*weights["loc"]+
            wage_score(job,sk)*weights["wage"]
        )
        if sc>0: rows.append({"job_idx":i,"seek_idx":j,"job_id":job.date if hasattr(job,"date") else i,"seeker_id":sk.email,"score":sc})

dfm = pd.DataFrame(rows)
if dfm.empty:
    st.info("⚠️ ยังไม่มีคู่ที่ match")
    st.stop()

top3 = dfm.sort_values(["job_idx","score"],ascending=[True,False]).groupby("job_idx").head(3)

# 11. แสดงผล
for _, grp in top3.groupby("job_idx"):
    job = jobs_df.loc[grp.job_idx.iloc[0]]
    st.subheader(f"Job: {job.job_date} {job.start_time}-{job.end_time}")
    for _,r in grp.iterrows():
        sk = seekers_df.loc[r.seek_idx]
        st.markdown(f"- **{sk.email}** (Score {r.score:.2f})  \n• Skills: {sk.skills}  \n• Avail: {sk.avail_start}–{sk.avail_end}")
    st.markdown("---")
