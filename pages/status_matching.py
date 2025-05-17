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

# 3) Load Google Sheets data
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(
    json.loads(st.secrets["gcp"]["credentials"]), scope
)
gc = gspread.authorize(creds)
# Load raw sheets
ws_post = gc.open("fastlabor").worksheet("post_job")
raw_jobs = pd.DataFrame(ws_post.get_all_records())
ws_find = gc.open("fastlabor").worksheet("find_job")
raw_seekers = pd.DataFrame(ws_find.get_all_records())

# 4) Encode & run matching to get top-5 recommendations
jobs_df     = encode_job_df(raw_jobs)
seekers_df  = encode_worker_df(raw_seekers)
job_row_idx = jobs_df.index[jobs_df["job_id"] == job_id].tolist()
if not job_row_idx:
    st.error(f"❌ ไม่พบ Job ID = {job_id} ในข้อมูลโพสต์")
    st.stop()
job_row_encoded = jobs_df.iloc[job_row_idx[0]]
top5 = recommend_seekers(job_row_encoded, seekers_df, n=5)

# 5) Load statuses from match_results sheet if any
ws_status = gc.open("fastlabor").worksheet("match_results")
status_df = pd.DataFrame(ws_status.get_all_records())
status_df["findjob_id"] = status_df["findjob_id"].astype(str)

# helper to pick status
def lookup_status(findjob_id: str) -> str:
    rec = status_df[status_df["findjob_id"] == findjob_id]
    return rec.iloc[0]["status"] if not rec.empty else "on queue"

# helper for status color
def get_status_color(status: str) -> str:
    s = (status or "").lower()
    return "green" if s == "accepted" else \
           "orange" if s == "on queue" else \
           "red" if s == "declined" else \
           "gray"

# 6) Display top-5 and their status
st.markdown(f"### Job ID: {job_id} — Top 5 Matches")
for rank, rec in enumerate(top5.itertuples(index=False), start=1):
    seeker = raw_seekers[raw_seekers["email"] == rec.email].iloc[0]
    name = f"{seeker.first_name} {seeker.last_name}".strip() or "-"
    status = lookup_status(str(rec.find_job_id))
    color = get_status_color(status)

    st.markdown(f"**Match No.{rank}**")
    st.markdown(f"- **Name:** {name}")
    st.markdown(f"- **Job Type:** {rec.job_type}")
    st.markdown(f"- **AI Score:** {rec.ai_score:.2f}")
    st.markdown(
        f"<span style='padding:4px 8px; background-color:{color}; color:white; border-radius:4px;'>{status}</span>",
        unsafe_allow_html=True
    )
    st.markdown("---")

# 7) Back button
if st.button("🔙 กลับหน้า My Jobs"):
    st.switch_page("pages/list_job.py")
