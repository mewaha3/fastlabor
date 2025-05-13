import pandas as pd
import numpy as np
from datetime import datetime
from geopy.distance import geodesic
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

import gspread, json
from oauth2client.service_account import ServiceAccountCredentials

# ------------------------------------------------------------
# 1. ตั้งค่าเชื่อม Google Sheets
# ------------------------------------------------------------
scope = ["https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive"]
creds_dict = json.loads(st.secrets["gcp"]["credentials"])  # เก็บไฟล์ service account JSON ใน Secrets
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# เปิด Spreadsheet ชื่อ “FAST_LABOR”
sheet = client.open("FAST_LABOR")

# โหลดข้อมูลจากสอง worksheet
ws_jobs    = sheet.worksheet("post_job")
ws_seekers = sheet.worksheet("find_job")

jobs_df    = pd.DataFrame(ws_jobs.get_all_records())
seekers_df = pd.DataFrame(ws_seekers.get_all_records())

# ------------------------------------------------------------
# 2. เตรียมข้อมูล และแปลงชนิด field
# ------------------------------------------------------------
# สมมติคอลัมน์ตามนี้:
# jobs_df:    ['job_id','required_skills','start','end','lat','lng','min_wage','max_wage']
# seekers_df: ['seeker_id','skills','avail_start','avail_end','lat','lng','expected_wage']

# แปลง datetime
jobs_df['start'] = pd.to_datetime(jobs_df['start'])
jobs_df['end']   = pd.to_datetime(jobs_df['end'])
seekers_df['avail_start'] = pd.to_datetime(seekers_df['avail_start'])
seekers_df['avail_end']   = pd.to_datetime(seekers_df['avail_end'])

# ------------------------------------------------------------
# 3. เตรียม TF-IDF สำหรับ Skill Similarity
# ------------------------------------------------------------
tfidf = TfidfVectorizer(token_pattern=r"(?u)\b\w+\b")
corpus = list(jobs_df['required_skills']) + list(seekers_df['skills'])
tfidf_mat = tfidf.fit_transform(corpus)
job_tfidf    = tfidf_mat[:len(jobs_df)]
seeker_tfidf = tfidf_mat[len(jobs_df):]

def skill_score(i, j):
    return cosine_similarity(job_tfidf[i], seeker_tfidf[j])[0,0]

def datetime_score(job, seeker):
    latest_start = max(job.start, seeker.avail_start)
    earliest_end  = min(job.end, seeker.avail_end)
    return 1.0 if (earliest_end - latest_start).total_seconds() > 0 else 0.0

def proximity_score(job, seeker, max_km=50):
    dist = geodesic((job.lat, job.lng), (seeker.lat, seeker.lng)).km
    return max(0.0, 1 - dist/max_km)

def wage_score(job, seeker):
    return 1.0 if (job.min_wage <= seeker.expected_wage <= job.max_wage) else 0.0

def match_score(job_idx, seeker_idx, w={'skill':0.4,'time':0.2,'prox':0.2,'wage':0.2}):
    job    = jobs_df.iloc[job_idx]
    seeker = seekers_df.iloc[seeker_idx]
    s1 = skill_score(job_idx, seeker_idx)
    s2 = datetime_score(job, seeker)
    s3 = proximity_score(job, seeker)
    s4 = wage_score(job, seeker)
    return w['skill']*s1 + w['time']*s2 + w['prox']*s3 + w['wage']*s4

# ------------------------------------------------------------
# 4. สร้าง DataFrame ผลลัพธ์ Matching
# ------------------------------------------------------------
records = []
for i, job in jobs_df.iterrows():
    for j, seeker in seekers_df.iterrows():
        score = match_score(i, j)
        if score > 0:
            records.append({
                'job_id': job.job_id,
                'seeker_id': seeker.seeker_id,
                'score': score
            })

matches = pd.DataFrame(records)
matches = matches.sort_values(['job_id','score'], ascending=[True, False])

# เก็บเฉพาะ Top-3 ต่อ job
top_matches = matches.groupby('job_id').head(3).reset_index(drop=True)

# ------------------------------------------------------------
# 5. นำไปแสดง (ตัวอย่างใน Streamlit)
# ------------------------------------------------------------
import streamlit as st

st.header("🔍 Matching Results")
for job_id, group in top_matches.groupby('job_id'):
    st.subheader(f"Job #{job_id}")
    for _, row in group.iterrows():
        seeker = seekers_df[seekers_df.seeker_id == row.seeker_id].iloc[0]
        st.write(f"- Seeker #{row.seeker_id}, Score: {row.score:.2f}")
        st.write(f"  - Skills: {seeker.skills}")
        st.write(f"  - Available: {seeker.avail_start} to {seeker.avail_end}")
        st.write(f"  - Location: ({seeker.lat}, {seeker.lng}), Expected Wage: {seeker.expected_wage}")
    st.markdown("---")
