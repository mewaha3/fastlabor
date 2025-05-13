# pages/list_job.py

import streamlit as st
import pandas as pd
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# 1. อ่าน Query Params
params   = st.experimental_get_query_params()
job_idx  = params.get("job_idx", [None])[0]
seek_idx = params.get("seeker_idx", [None])[0]

# --- Google Sheets connection (เหมือนเดิม) ---
scope = ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/drive"]
if "gcp" in st.secrets:
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        json.loads(st.secrets["gcp"]["credentials"]), scope
    )
else:
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        "pages/credentials.json", scope
    )
gc    = gspread.authorize(creds)
sheet = gc.open("fastlabor")

def load_df(name: str) -> pd.DataFrame:
    ws   = sheet.worksheet(name)
    vals = ws.get_all_values()
    df   = pd.DataFrame(vals[1:], columns=vals[0])
    df.columns = df.columns.str.strip().str.lower().str.replace(" ","_")
    return df

jobs_df    = load_df("post_job")
seekers_df = load_df("find_job")

# Normalize datetime & wages for matching
jobs_df["job_date"]    = pd.to_datetime(jobs_df["job_date"], errors="coerce")
seekers_df["job_date"] = pd.to_datetime(seekers_df["job_date"], errors="coerce")

def mkdt(df, dcol, tcol, out):
    df[out] = pd.to_datetime(df[dcol].dt.strftime("%Y-%m-%d")+" "+df[tcol])
for df,dcols in ((jobs_df,("start_time","end_time")), (seekers_df,("start_time","end_time"))):
    mkdt(df, "job_date", dcols[0], "avail_start" if df is seekers_df else "start_dt")
    mkdt(df, "job_date", dcols[1], "avail_end"   if df is seekers_df else "end_dt")

for df in (jobs_df, seekers_df):
    for c in ("start_salary","range_salary"):
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

# ฟังก์ชัน score
def score(j,s):
    w = {"type":0.4,"time":0.2,"loc":0.2,"wage":0.2}
    s1 = 1 if j.job_type.lower()==s.job_type.lower() else 0
    s2 = 1 if (min(j.end_dt,s.avail_end)-max(j.start_dt,s.avail_start)).total_seconds()>0 else 0
    s3 = 1 if (j.province,district:=j.district,j.subdistrict)==(s.province,s.district,s.subdistrict) else 0
    s4 = 1 if j.start_salary<=s.start_salary<=j.range_salary else 0
    return s1*w["type"]+s2*w["time"]+s3*w["loc"]+s4*w["wage"]

# --- UI ---
st.set_page_config(layout="wide")
st.markdown("<h1>📄 My Jobs</h1>", unsafe_allow_html=True)

# ถ้ามี param ให้แสดงผล Matching
if job_idx is not None or seek_idx is not None:
    st.subheader("🔍 Matching Results")
    recs = []
    for i,j in jobs_df.iterrows():
        if job_idx is not None and str(i)!=job_idx: continue
        for k,s in seekers_df.iterrows():
            if seek_idx is not None and str(k)!=seek_idx: continue
            sc = score(j,s)
            if sc>0:
                recs.append((i,k,sc))

    if not recs:
        st.info("❌ ไม่พบคู่ Matching")
    else:
        # sort
        recs.sort(key=lambda x:-x[2])
        for rank,(i,k,sc) in enumerate(recs,1):
            job = jobs_df.loc[i]; s = seekers_df.loc[k]
            st.markdown(f"### Rank {rank} (score {sc:.2f})")
            st.markdown(f"- **Job**: {job.job_type} on {job.job_date.date()} ({job.start_time}–{job.end_time})")
            st.markdown(f"- **Seeker**: {s.email} ({s.skills})  \n  Available: {s.job_date.date()} {s.start_time}–{s.end_time}  \n  Wage: {s.start_salary}–{s.range_salary}")
    # ปุ่มกลับ
    if st.button("🔙 Back to My Jobs"):
        st.experimental_set_query_params()  # ล้าง params ทั้งหมด
        st.experimental_rerun()

else:
    # ปกติแสดง My Jobs
    tab1,tab2 = st.tabs(["📌 Post Job","🔍 Find Job"])
    with tab1:
        st.subheader("📌 รายการโพสต์งาน")
        for i,row in jobs_df.iterrows():
            st.markdown("---")
            st.markdown(f"**Job #{i+1}**  {row.job_type}")
            if st.button("View Matching", key=f"jm{i}"):
                st.experimental_set_query_params(job_idx=i)
                st.experimental_rerun()
    with tab2:
        st.subheader("🔍 รายการค้นหางาน")
        for k,row in seekers_df.iterrows():
            st.markdown("---")
            st.markdown(f"**Find #{k+1}**  {row.skills}")
            if st.button("View Matching", key=f"sk{k}"):
                st.experimental_set_query_params(seeker_idx=k)
                st.experimental_rerun()
