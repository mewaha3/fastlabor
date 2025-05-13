# pages/list_job.py

import streamlit as st
import pandas as pd
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# — 0. อ่าน query params
params   = st.experimental_get_query_params()
job_idx  = params.get("job_idx", [None])[0]
seek_idx = params.get("seeker_idx", [None])[0]

# — 1. Auth & connect to Google Sheets —
scope = ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/drive"]
if "gcp" in st.secrets:
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        json.loads(st.secrets["gcp"]["credentials"]), scope
    )
else:
    creds = ServiceAccountCredentials.from_json_keyfile_name("pages/credentials.json", scope)
gc    = gspread.authorize(creds)
sh    = gc.open("fastlabor")

# — 2. Loader —
def load_df(name: str) -> pd.DataFrame:
    ws   = sh.worksheet(name)
    vals = ws.get_all_values()
    df   = pd.DataFrame(vals[1:], columns=vals[0])
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    return df

jobs_df    = load_df("post_job")
seekers_df = load_df("find_job")

# — 3. เตรียม datetime & wages —
jobs_df["job_date"]    = pd.to_datetime(jobs_df["job_date"], errors="coerce")
seekers_df["job_date"] = pd.to_datetime(seekers_df["job_date"], errors="coerce")
def mkdt(df,d,t,out):
    df[out] = pd.to_datetime(
        df[d].dt.strftime("%Y-%m-%d")+" "+df[t].astype(str),
        errors="coerce"
    )
mkdt(jobs_df,    "job_date","start_time","start_dt")
mkdt(jobs_df,    "job_date","end_time",  "end_dt")
mkdt(seekers_df, "job_date","start_time","avail_start")
mkdt(seekers_df, "job_date","end_time",  "avail_end")
for df in (jobs_df,seekers_df):
    for c in ("start_salary","range_salary"):
        if c in df.columns:
            df[c] = pd.to_numeric(df[c],errors="coerce").fillna(0)

# — 4. Scoring funcs & weights —
def s1(j,s): return 1 if str(j.job_type).lower()==str(s.job_type).lower() else 0
def s2(j,s):
    ov=(min(j.end_dt,s.avail_end)-max(j.start_dt,s.avail_start)).total_seconds()
    return 1 if ov>0 else 0
def s3(j,s): return 1 if (j.province,j.district,j.subdistrict)==(s.province,s.district,s.subdistrict) else 0
def s4(j,s): return 1 if j.start_salary<=s.start_salary<=j.range_salary else 0
w={"type":0.4,"time":0.2,"loc":0.2,"wage":0.2}

st.set_page_config(layout="wide")
st.title("📄 My Jobs")

# — 5. ถ้ามี job_idx/seeker_idx ให้แสดง Matching —
if job_idx is not None or seek_idx is not None:
    st.subheader("🔍 Matching Results")
    rec=[]
    for i,j in jobs_df.iterrows():
        if job_idx is not None and str(i)!=job_idx: continue
        for k,s in seekers_df.iterrows():
            if seek_idx is not None and str(k)!=seek_idx: continue
            score = s1(j,s)*w["type"] + s2(j,s)*w["time"] + s3(j,s)*w["loc"] + s4(j,s)*w["wage"]
            if score>0: rec.append((i,k,score))
    if not rec:
        st.info("❌ No matches")
    else:
        rec.sort(key=lambda x:-x[2])
        for rank,(i,k,sc) in enumerate(rec,1):
            job = jobs_df.loc[i]; s = seekers_df.loc[k]
            st.markdown(f"### Rank {rank} — Score {sc:.2f}")
            st.markdown(f"""
- **Job**: {job.job_type} on {job.job_date.date()} ({job.start_time}–{job.end_time})  
- **Seeker**: {s.email}  
- **Skill**: {s.skills if "skills" in s else s.job_type}  
- **Available**: {s.job_date.date()} {s.start_time}–{s.end_time}  
- **Location**: {s.province}/{s.district}/{s.subdistrict}  
- **Wage**: {s.start_salary}–{s.range_salary}
""")
    if st.button("🔙 Back to My Jobs"):
        # ล้าง params แล้ว refresh จะกลับไป section listing
        st.experimental_set_query_params()
        st.experimental_rerun()

# — 6. แสดง two tabs listing jobs / seekers —
else:
    tab1, tab2 = st.tabs(["📌 Post Job","🔍 Find Job"])
    with tab1:
        st.subheader("📌 รายการโพสต์งาน")
        for i,row in jobs_df.iterrows():
            st.markdown("---")
            st.write(f"**Job #{i+1}** — {row.job_type}")
            if st.button("View Matching", key=f"jm{i}"):
                st.experimental_set_query_params(job_idx=i)
                # ไม่ต้อง explicit rerun; param change จะรีโหลดอัตโนมัติ

    with tab2:
        st.subheader("🔍 รายการค้นหางาน")
        for k,row in seekers_df.iterrows():
            st.markdown("---")
            lbl = row.get("skills", row.get("job_detail",""))
            st.write(f"**Find #{k+1}** — {lbl}")
            if st.button("View Matching", key=f"sk{k}"):
                st.experimental_set_query_params(seeker_idx=k)
                # ไม่ต้อง explicit rerun

# — 7. ปุ่มกลับ Home —
st.markdown("---")
st.page_link("pages/home.py", label="🏠 Go to Homepage")
