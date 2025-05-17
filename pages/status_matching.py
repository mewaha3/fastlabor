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

# 3) Load raw data
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(st.secrets["gcp"]["credentials"]), scope)
gc = gspread.authorize(creds)
# raw sheets
raw_jobs     = pd.DataFrame(gc.open("fastlabor").worksheet("post_job").get_all_records())
raw_seekers  = pd.DataFrame(gc.open("fastlabor").worksheet("find_job").get_all_records())
# status sheet
status_df    = pd.DataFrame(gc.open("fastlabor").worksheet("match_results").get_all_records())
status_df["findjob_id"] = status_df["findjob_id"].astype(str)

# 4) Encode & compute top-5 recommendations
jobs_df    = encode_job_df(raw_jobs)
seekers_df = encode_worker_df(raw_seekers)
# find encoded job row
idxs = jobs_df.index[jobs_df["job_id"] == job_id].tolist()
if not idxs:
    st.error(f"❌ ไม่พบ Job ID = {job_id} ในข้อมูลโพสต์")
    st.stop()
job_row_enc = jobs_df.loc[idxs[0]]
top5 = recommend_seekers(job_row_enc, seekers_df, n=5)

# 5) Status color helper
def get_status_color(status: str) -> str:
    s = (status or "").lower()
    return "green" if s == "accepted" else \
           "orange" if s == "on queue" else \
           "red" if s == "declined" else \
           "gray"

# 6) Display Top-5 with their current status
st.markdown(f"### Job ID: {job_id} — Top 5 Matches")
for rank, rec in enumerate(top5.itertuples(index=False), start=1):
    # find raw seeker row to get findjob_id and names
    raw = raw_seekers[raw_seekers["email"] == rec.email]
    if raw.empty:
        continue
    raw = raw.iloc[0]
    find_id = str(raw["findjob_id"])
    name    = f"{raw.get('first_name','')} {raw.get('last_name','')}".strip() or "-"
    ai_score= rec.ai_score

    # lookup status
    stat_rec = status_df[status_df["findjob_id"] == find_id]
    status   = stat_rec.iloc[0]["status"] if not stat_rec.empty else "on queue"
    color    = get_status_color(status)

    st.markdown(f"**Match No.{rank}**")
    st.markdown(f"- **Name:** {name}")
    st.markdown(f"- **AI Score:** {ai_score:.2f}")
    st.markdown(
        f"<span style='padding:4px 8px; background-color:{color}; color:white; border-radius:4px;'>"
        f"{status}"
        f"</span>",
        unsafe_allow_html=True
    )
    st.markdown("---")

# 7) Back button
if st.button("🔙 กลับหน้า My Jobs"):
    st.switch_page("pages/list_job.py")
