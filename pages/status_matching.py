import streamlit as st
import pandas as pd
import json
import gspread
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
scope = ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(
    json.loads(st.secrets["gcp"]["credentials"]), scope
)
gc = gspread.authorize(creds)
sh = gc.open("fastlabor")

# 4) Load raw tables
raw_jobs    = pd.DataFrame(sh.worksheet("post_job") .get_all_records())
raw_seekers = pd.DataFrame(sh.worksheet("find_job") .get_all_records())
status_df   = pd.DataFrame(sh.worksheet("match_results").get_all_records())

# ensure findjob_id column is string for matching
status_df["findjob_id"] = status_df["findjob_id"].astype(str)

# 5) Compute Top-5 seekers
jobs_enc    = encode_job_df(raw_jobs)
seekers_enc = encode_worker_df(raw_seekers)
idxs = jobs_enc.index[jobs_enc["job_id"] == job_id].tolist()
if not idxs:
    st.error(f"❌ ไม่พบ Job ID = {job_id}")
    st.stop()
job_enc = jobs_enc.loc[idxs[0]]
original = recommend_seekers(job_enc, seekers_enc, n=50)  # ขอ 50 ก่อนคัดไม่ซ้ำ

# คัดไม่ซ้ำตามอีเมล
unique_recs = []
seen_emails = set()
for rec in original.itertuples(index=False):
    if rec.email not in seen_emails:
        unique_recs.append(rec)
        seen_emails.add(rec.email)
    if len(unique_recs) == 5:
        break

# 6) Render
st.markdown(f"### Job ID: {job_id} — Top 5 Matches")
for rank, rec in enumerate(unique_recs, start=1):
    # หา raw seeker
    seeker = raw_seekers[raw_seekers["email"] == rec.email].iloc[0]
    fid    = str(seeker["findjob_id"])
    name   = f"{seeker.first_name} {seeker.last_name}".strip() or "-"
    # … แปลงฟิลด์อื่นๆ เหมือนเดิม …

    # lookup status
    sr     = status_df[status_df["findjob_id"] == fid]
    status = sr.iloc[0]["status"] if not sr.empty else "on queue"
    color  = get_status_color(status)

    st.markdown(f"**Match No.{rank}**")
    st.markdown(f"- **Name:** {name}")
    # … พิมพ์ field อื่นๆ …
    st.markdown(f"- **AI Score:** {rec.ai_score:.2f}")
    st.markdown(
        f"<span style='padding:4px 8px; background-color:{color}; color:white; border-radius:4px;'>"
        f"{status}"
        f"</span>",
        unsafe_allow_html=True
    )

    if status.lower() == "accepted":
        if st.button("ดูรายละเอียดงาน", key=f"detail_{fid}"):
            job_raw = raw_jobs[raw_jobs["job_id"] == job_id].iloc[0]
            st.session_state["selected_job"] = {
                **job_raw.to_dict(),
                "findjob_id": fid,
                **seeker[["first_name","last_name","email","gender"]].to_dict()
            }
            st.switch_page("pages/job_detail.py")

    st.markdown("---")

# 7) Back button
if st.button("🔙 กลับหน้า My Jobs"):
    st.switch_page("pages/list_job.py")
