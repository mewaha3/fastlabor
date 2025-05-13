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

# ---------------------------------------
# 1. โหลด credentials จาก .streamlit/secrets.toml
# ---------------------------------------
creds_dict = json.loads(st.secrets["gcp"]["credentials"])
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
gc = gspread.authorize(creds)

# ---------------------------------------
# 2. ดึงข้อมูล PostJob & FindJob
# ---------------------------------------
SPREADSHEET_NAME = "fastlabor"  # ชื่อ spreadsheet จริงๆ ของคุณ
sh = gc.open(SPREADSHEET_NAME)

jobs_df    = pd.DataFrame(sh.worksheet("post_job").get_all_records())
seekers_df = pd.DataFrame(sh.worksheet("find_job").get_all_records())

# ---------------------------------------
# 3. แปลงชนิดข้อมูล & สร้าง datetime
# ---------------------------------------
# PostJob: skills, job_date, start_time, end_time, province, district, subdistrict, start_salary, range_salary
# FindJob: skills or job_detail, job_date, start_time, end_time, province, district, subdistrict, salary

# ถ้า FindJob ใช้ 'job_detail' แทน 'skills' ให้รวมเป็นคอลัมน์เดียวกัน
if "skills" not in seekers_df.columns and "job_detail" in seekers_df.columns:
    seekers_df["skills"] = seekers_df["job_detail"].astype(str)
else:
    seekers_df["skills"] = seekers_df["skills"].astype(str)

# สร้างคอลัมน์ wages
jobs_df["min_wage"] = pd.to_numeric(jobs_df["start_salary"], errors="coerce")
jobs_df["max_wage"] = pd.to_numeric(jobs_df["range_salary"], errors="coerce")
seekers_df["expected_wage"] = pd.to_numeric(seekers_df.get("salary", 0), errors="coerce")

# รวมวันที่+เวลา
def make_dt(df, date_col, time_col, out_col):
    df[out_col] = pd.to_datetime(df[date_col].astype(str) + " " + df[time_col].astype(str),
                                  errors="coerce")
make_dt(jobs_df,    "job_date",  "start_time", "start_dt")
make_dt(jobs_df,    "job_date",  "end_time",   "end_dt")
make_dt(seekers_df,"job_date",  "start_time", "avail_start")
make_dt(seekers_df,"job_date",  "end_time",   "avail_end")

# ---------------------------------------
# 4. TF-IDF for skills
# ---------------------------------------
tfidf = TfidfVectorizer(token_pattern=r"(?u)\b\w+\b")
corpus = list(jobs_df["skills"]) + list(seekers_df["skills"])
tfidf_mat = tfidf.fit_transform(corpus)
job_tfidf    = tfidf_mat[: len(jobs_df)]
seeker_tfidf = tfidf_mat[len(jobs_df) :]

def skill_score(i, j):
    return cosine_similarity(job_tfidf[i], seeker_tfidf[j])[0, 0]

# ---------------------------------------
# 5. เวลา & พื้นที่ & ค่าจ้าง
# ---------------------------------------
def datetime_score(job, seeker):
    overlap = (min(job.end_dt, seeker.avail_end) -
               max(job.start_dt, seeker.avail_start)).total_seconds()
    return 1.0 if overlap > 0 else 0.0

def location_score(job, seeker):
    # ให้ 1.0 ถ้า province,district,subdistrict ตรงกันทั้งหมด
    return 1.0 if (
        job.province==seeker.province
        and job.district==seeker.district
        and job.subdistrict==seeker.subdistrict
    ) else 0.0

def wage_score(job, seeker):
    return 1.0 if (job.min_wage <= seeker.expected_wage <= job.max_wage) else 0.0

# ---------------------------------------
# 6. คำนวณคะแนนรวม
# ---------------------------------------
weights = {"skill":0.4, "time":0.2, "loc":0.2, "wage":0.2}

records = []
for i, job in jobs_df.iterrows():
    for j, seeker in seekers_df.iterrows():
        s_skill = skill_score(i, j)
        s_time  = datetime_score(job, seeker)
        s_loc   = location_score(job, seeker)
        s_wage  = wage_score(job, seeker)
        total   = (weights["skill"]*s_skill
                   + weights["time"]*s_time
                   + weights["loc"]*s_loc
                   + weights["wage"]*s_wage)
        if total>0:
            records.append({
                "job_idx": i,
                "seeker_idx": j,
                "job_id":    job.job_date.strftime("%Y%m%d")+"_"+str(i),
                "seeker_id": seekers_df.loc[j,"email"],
                "score":     total
            })

matches = pd.DataFrame(records)
if matches.empty:
    st.info("⚠️ ยังไม่มีคู่ที่ match ได้")
    st.stop()

matches = matches.sort_values(["job_id","score"], ascending=[True,False])
top3 = matches.groupby("job_id").head(3)

# ---------------------------------------
# 7. แสดงผล
# ---------------------------------------
for job_id, group in top3.groupby("job_id"):
    st.subheader(f"📄 Job {job_id}")
    job = jobs_df.loc[group["job_idx"].iloc[0]]
    st.markdown(f"**Skills:** {job.skills} — **Date:** {job.job_date} **{job.start_time}–{job.end_time}**")
    for _, row in group.iterrows():
        seeker = seekers_df.loc[row.seeker_idx]
        st.markdown(
            f"- **Seeker:** {seeker.email} (Score {row.score:.2f})  \n"
            f"  • Skills: {seeker.skills}  \n"
            f"  • Availability: {seeker.avail_start}–{seeker.avail_end}  \n"
            f"  • Location: {seeker.province}/{seeker.district}/{seeker.subdistrict}  \n"
            f"  • Expected Wage: {seeker.expected_wage}"
        )
    st.markdown("---")
