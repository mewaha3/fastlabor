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
# 1. หน้า Streamlit config & title
# —————————————————————————————————————————
st.set_page_config(page_title="🔍 Matching Jobs", layout="wide")
st.title("🔍 Matching Results")

# —————————————————————————————————————————
# 2. โหลด Google Sheets credentials จาก .streamlit/secrets.toml
# —————————————————————————————————————————
# ในไฟล์ .streamlit/secrets.toml ให้มี:
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
# 3. เปิด Spreadsheet & โหลด Data
# —————————————————————————————————————————
# ชื่อสเปรดชีตตามภาพคือ "fastlabor"
SPREADSHEET_NAME = "fastlabor"
sh = gc.open(SPREADSHEET_NAME)

# โหลดแท็บ post_job กับ find_job
jobs_df    = pd.DataFrame(sh.worksheet("post_job").get_all_records())
seekers_df = pd.DataFrame(sh.worksheet("find_job").get_all_records())

# —————————————————————————————————————————
# 4. เตรียมข้อมูลให้พร้อมสำหรับ matching
# —————————————————————————————————————————
# รวมคอลัมน์ skills ใน seekers ถ้ามี job_detail แทน
if "skills" not in seekers_df.columns and "job_detail" in seekers_df.columns:
    seekers_df["skills"] = seekers_df["job_detail"].astype(str)
else:
    seekers_df["skills"] = seekers_df["skills"].astype(str)

# แปลงค่าจ้างเป็นตัวเลข
jobs_df["min_wage"]       = pd.to_numeric(jobs_df["start_salary"], errors="coerce")
jobs_df["max_wage"]       = pd.to_numeric(jobs_df["range_salary"], errors="coerce")
seekers_df["expected_wage"] = pd.to_numeric(seekers_df.get("salary", 0), errors="coerce")

# ฟังก์ชันรวมวันที่+เวลา เป็น datetime
def make_dt(df, date_col, time_col, out_col):
    df[out_col] = pd.to_datetime(
        df[date_col].astype(str) + " " + df[time_col].astype(str),
        errors="coerce"
    )

make_dt(jobs_df,     "job_date",  "start_time", "start_dt")
make_dt(jobs_df,     "job_date",  "end_time",   "end_dt")
make_dt(seekers_df,  "job_date",  "start_time", "avail_start")
make_dt(seekers_df,  "job_date",  "end_time",   "avail_end")

# —————————————————————————————————————————
# 5. สร้าง TF-IDF matrix สำหรับ skills
# —————————————————————————————————————————
tfidf = TfidfVectorizer(token_pattern=r"(?u)\b\w+\b")
corpus = list(jobs_df["skills"]) + list(seekers_df["skills"])
tfidf_mat    = tfidf.fit_transform(corpus)
job_tfidf    = tfidf_mat[: len(jobs_df)]
seeker_tfidf = tfidf_mat[len(jobs_df) :]

def skill_score(i, j):
    return cosine_similarity(job_tfidf[i], seeker_tfidf[j])[0, 0]

# —————————————————————————————————————————
# 6. ฟังก์ชันคะแนนเวลา, พื้นที่, ค่าจ้าง
# —————————————————————————————————————————
def datetime_score(job, seeker):
    overlap = (
        min(job.end_dt, seeker.avail_end)
        - max(job.start_dt, seeker.avail_start)
    ).total_seconds()
    return 1.0 if overlap > 0 else 0.0

def location_score(job, seeker):
    return 1.0 if (
        job.province   == seeker.province
        and job.district == seeker.district
        and job.subdistrict == seeker.subdistrict
    ) else 0.0

def wage_score(job, seeker):
    return 1.0 if (
        job.min_wage <= seeker.expected_wage <= job.max_wage
    ) else 0.0

# —————————————————————————————————————————
# 7. คำนวณคะแนนรวม & สะสมผลลัพธ์
# —————————————————————————————————————————
weights = {"skill": 0.4, "time": 0.2, "loc": 0.2, "wage": 0.2}
records = []

for i, job in jobs_df.iterrows():
    for j, seeker in seekers_df.iterrows():
        s1 = skill_score(i, j)
        s2 = datetime_score(job, seeker)
        s3 = location_score(job, seeker)
        s4 = wage_score(job, seeker)
        total = s1*weights["skill"] + s2*weights["time"] + s3*weights["loc"] + s4*weights["wage"]
        if total > 0:
            records.append({
                "job_idx":    i,
                "seeker_idx": j,
                "job_id":     f"{job.job_date.strftime('%Y%m%d')}_{i}",
                "seeker_id":  seeker.email,
                "score":      total
            })

matches = pd.DataFrame(records)
if matches.empty:
    st.info("⚠️ ยังไม่มีคู่ที่ match ได้")
    st.stop()

matches = matches.sort_values(["job_id","score"], ascending=[True,False])
top3   = matches.groupby("job_id").head(3)

# —————————————————————————————————————————
# 8. แสดงผลลัพธ์บน Streamlit
# —————————————————————————————————————————
for job_id, group in top3.groupby("job_id"):
    st.subheader(f"📄 Job {job_id}")
    job = jobs_df.loc[group["job_idx"].iloc[0]]
    st.markdown(f"**Skills:** {job.skills} | **Date:** {job.job_date} {job.start_time}–{job.end_time}")

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
