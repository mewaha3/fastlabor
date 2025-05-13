# pages/match.py
import streamlit as st
import pandas as pd
import json
import math
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import gspread
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(page_title="🔍 Matching Jobs", layout="wide")
st.title("🔍 Matching Results")

# ------------------------------------------------------------
# 1. โหลด Service Account credentials จาก Secrets
# ------------------------------------------------------------
# ต้องตั้งค่า .streamlit/secrets.toml ให้มี [gcp].credentials
creds_dict = json.loads(st.secrets["gcp"]["credentials"])
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
gc = gspread.authorize(creds)

# ------------------------------------------------------------
# 2. โหลดข้อมูลจาก Google Sheets
# ------------------------------------------------------------
SPREADSHEET_NAME = "fastlabor"
sheet = gc.open(SPREADSHEET_NAME)

ws_jobs    = sheet.worksheet("post_job")
ws_seekers = sheet.worksheet("find_job")

jobs_df    = pd.DataFrame(ws_jobs.get_all_records())
seekers_df = pd.DataFrame(ws_seekers.get_all_records())

# ------------------------------------------------------------
# 3. แปลงชนิดข้อมูลให้เหมาะสม
# ------------------------------------------------------------
# สมมติคอลัมน์:
# jobs_df:    ['job_id','required_skills','start','end','lat','lng','min_wage','max_wage']
# seekers_df: ['seeker_id','skills','avail_start','avail_end','lat','lng','expected_wage']

jobs_df['start'] = pd.to_datetime(jobs_df['start'])
jobs_df['end']   = pd.to_datetime(jobs_df['end'])
seekers_df['avail_start'] = pd.to_datetime(seekers_df['avail_start'])
seekers_df['avail_end']   = pd.to_datetime(seekers_df['avail_end'])

# ------------------------------------------------------------
# 4. เตรียม TF-IDF สำหรับ Skill Similarity
# ------------------------------------------------------------
tfidf = TfidfVectorizer(token_pattern=r"(?u)\b\w+\b")
corpus = list(jobs_df['required_skills']) + list(seekers_df['skills'])
tfidf_mat = tfidf.fit_transform(corpus)

job_tfidf    = tfidf_mat[: len(jobs_df)]
seeker_tfidf = tfidf_mat[len(jobs_df) :]


def skill_score(i_job: int, i_seek: int) -> float:
    """Cosine similarity ระหว่าง required_skills กับ skills"""
    return cosine_similarity(job_tfidf[i_job], seeker_tfidf[i_seek])[0, 0]


def datetime_score(job: pd.Series, seeker: pd.Series) -> float:
    """1.0 ถ้าช่วงเวลาทับซ้อนกัน มิฉะนั้น 0.0"""
    latest_start = max(job.start, seeker.avail_start)
    earliest_end = min(job.end, seeker.avail_end)
    overlap = (earliest_end - latest_start).total_seconds()
    return 1.0 if overlap > 0 else 0.0


def haversine(lat1, lon1, lat2, lon2):
    """คำนวณระยะทาง (km) โดยใช้สูตร Haversine"""
    r = 6371  # รัศมีโลก (กม.)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return r * c


def proximity_score(job: pd.Series, seeker: pd.Series, max_km: float = 50) -> float:
    """1.0 ถ้าระยะ 0 กม. ลดลงเหลือ 0 ที่ max_km"""
    dist = haversine(job.lat, job.lng, seeker.lat, seeker.lng)
    return max(0.0, 1 - dist / max_km)


def wage_score(job: pd.Series, seeker: pd.Series) -> float:
    """1.0 ถ้าค่าจ้างคาดหวังอยู่ในช่วง [min_wage,max_wage] มิฉะนั้น 0.0"""
    return 1.0 if (job.min_wage <= seeker.expected_wage <= job.max_wage) else 0.0


def match_score(
    job: pd.Series,
    seeker: pd.Series,
    w: dict = {"skill": 0.4, "time": 0.2, "prox": 0.2, "wage": 0.2},
) -> float:
    s1 = skill_score(job.name, seeker.name)
    s2 = datetime_score(job, seeker)
    s3 = proximity_score(job, seeker)
    s4 = wage_score(job, seeker)
    return w["skill"] * s1 + w["time"] * s2 + w["prox"] * s3 + w["wage"] * s4


# ------------------------------------------------------------
# 5. สร้าง DataFrame ของผลลัพธ์ Matching
# ------------------------------------------------------------
records = []
for i, job in jobs_df.iterrows():
    for j, seeker in seekers_df.iterrows():
        score = match_score(job, seeker)
        if score > 0:
            records.append(
                {
                    "job_id": job.job_id,
                    "seeker_id": seeker.seeker_id,
                    "score": score,
                }
            )

matches = pd.DataFrame(records)
if matches.empty:
    st.info("⚠️ ไม่มีคู่ที่ match ได้ในขณะนี้")
    st.stop()

matches = matches.sort_values(["job_id", "score"], ascending=[True, False])
top_matches = matches.groupby("job_id").head(3).reset_index(drop=True)

# ------------------------------------------------------------
# 6. แสดงผลใน Streamlit
# ------------------------------------------------------------
for job_id, group in top_matches.groupby("job_id"):
    st.subheader(f"📄 Job #{job_id}")
    for _, row in group.iterrows():
        seeker = seekers_df[seekers_df.seeker_id == row.seeker_id].iloc[0]
        st.markdown(
            f"""
- **Seeker #{row.seeker_id}** — Score: {row.score:.2f}  
  • Skills: {seeker.skills}  
  • Available: {seeker.avail_start.strftime('%Y-%m-%d %H:%M')} to {seeker.avail_end.strftime('%Y-%m-%d %H:%M')}  
  • Location: ({seeker.lat:.4f}, {seeker.lng:.4f})  
  • Expected Wage: {seeker.expected_wage}
"""
        )
    st.markdown("---")
