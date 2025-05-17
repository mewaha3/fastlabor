import streamlit as st
import pandas as pd
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials
from matching import encode_job_df, encode_worker_df, recommend_seekers

# 1) Page config & header
st.set_page_config(page_title="Status Matching | FAST LABOR", layout="centered")
st.markdown("""
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
    <div><strong>FAST LABOR</strong></div>
    <div>
        <a href="/pages/list_job.py" style="margin-right: 20px;">My Job</a>
        <a href="/pages/find_job_matching.py" style="margin-right: 20px;">Find Job</a>
        <a href="/pages/profile.py" style="background-color: black; color: white; padding: 5px 10px; border-radius: 4px;">Profile</a>
    </div>
</div>
""", unsafe_allow_html=True)

st.title("📊 Status Matching")

# 2) Get job_id from session
job_id = st.session_state.get("status_job_id")
if not job_id:
    st.info("❌ กรุณากด ‘ดูสถานะการจับคู่’ จากหน้า My Jobs ก่อน")
    st.stop()

# 3) Connect to Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(st.secrets["gcp"]["credentials"]), scope)
gc = gspread.authorize(creds)

# raw data
raw_jobs    = pd.DataFrame(gc.open("fastlabor").worksheet("post_job").get_all_records())
raw_seekers = pd.DataFrame(gc.open("fastlabor").worksheet("find_job").get_all_records())
status_df   = pd.DataFrame(gc.open("fastlabor").worksheet("match_results").get_all_records())
status_df["findjob_id"] = status_df["findjob_id"].astype(str)

# 4) Compute top-5 recommendations
jobs_enc    = encode_job_df(raw_jobs)
seekers_enc = encode_worker_df(raw_seekers)
idxs = jobs_enc.index[jobs_enc["job_id"] == job_id].tolist()
if not idxs:
    st.error(f"❌ ไม่พบ Job ID = {job_id}")
    st.stop()
job_enc = jobs_enc.loc[idxs[0]]
top5 = recommend_seekers(job_enc, seekers_enc, n=5)

# 5) Helpers
def get_status_color(status: str) -> str:
    s = (status or "").lower()
    return "green" if s=="accepted" else "orange" if s=="on queue" else "red" if s=="declined" else "gray"

def avg_salary(raw):
    try:
        s = float(raw.get("start_salary") or raw.get("salary") or 0)
        r = float(raw.get("range_salary") or raw.get("salary") or 0)
        return f"{(s+r)/2:.0f}"
    except: return "-"

# 6) Display Top-5 with status and details
st.markdown(f"### Job ID: {job_id} — Top 5 Matches")
for rank, rec in enumerate(top5.itertuples(index=False), start=1):
    # find raw seeker and raw job
    seeker_raw = raw_seekers[raw_seekers["email"]==rec.email].iloc[0]
    status_row = status_df[status_df["findjob_id"]==str(seeker_raw["findjob_id"])]
    status = status_row.iloc[0]["status"] if not status_row.empty else "on queue"
    color  = get_status_color(status)
    job_raw = raw_jobs[raw_jobs["job_id"]==job_id].iloc[0]

    # details
    name     = f"{seeker_raw.first_name} {seeker_raw.last_name}".strip() or "-"
    gender   = seeker_raw.gender or "-"
    jtype    = rec.job_type or "-"
    date     = seeker_raw.job_date or "-"
    time     = f"{seeker_raw.start_time} – {seeker_raw.end_time}"
    loc      = f"{seeker_raw.province}/{seeker_raw.district}/{seeker_raw.subdistrict}"
    sal      = avg_salary(seeker_raw)
    ai_score = rec.ai_score

    st.markdown(f"**Match No.{rank}**")
    st.markdown(f"- **Name:** {name}")
    st.markdown(f"- **Gender:** {gender}")
    st.markdown(f"- **Job Type:** {jtype}")
    st.markdown(f"- **Date:** {date}")
    st.markdown(f"- **Time:** {time}")
    st.markdown(f"- **Location:** {loc}")
    st.markdown(f"- **Salary:** {sal}")
    st.markdown(f"- **AI Score:** {ai_score:.2f}")
    st.markdown(
        f"<span style='padding:4px 8px; background-color:{color}; color:white; border-radius:4px;'>{status}</span>",
        unsafe_allow_html=True
    )

    if status.lower()=="accepted":
        if st.button("ดูรายละเอียดงาน", key=f"detail_{seeker_raw['findjob_id']}"):
            # pass selected match into session for job_detail
            st.session_state["selected_job"] = {
                **job_raw.to_dict(),
                "findjob_id": seeker_raw["findjob_id"],
                "first_name": seeker_raw.first_name,
                "last_name": seeker_raw.last_name,
                "email": seeker_raw.email,
                "gender": seeker_raw.gender
            }
            st.switch_page("pages/job_detail.py")

    st.markdown("---")

# 7) Back button
if st.button("🔙 กลับหน้า My Jobs"):
    st.switch_page("pages/list_job.py")
