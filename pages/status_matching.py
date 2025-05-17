import streamlit as st
import pandas as pd
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials

# 1) Page config & header
st.set_page_config(page_title="Status Matching | FAST LABOR", layout="centered")
st.markdown("""
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
    <div><strong>FAST LABOR</strong></div>
    <div>
        <a href="/pages/find_job_matching.py" style="margin-right: 20px;">Find Job</a>
        <a href="/pages/list_job.py" style="margin-right: 20px;">My Job</a>
        <a href="/pages/profile.py" style="background-color: black; color: white; padding: 5px 10px; border-radius: 4px;">Profile</a>
    </div>
</div>
""", unsafe_allow_html=True)

st.title("📊 Status Matching")

# 2) Get findjob_id from session
findjob_id = st.session_state.get("status_job_id")
if not findjob_id:
    st.info("❌ กรุณากด ‘ดูสถานะการจับคู่’ จากหน้า My Jobs ก่อน")
    st.stop()

# 3) Connect to Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(
    json.loads(st.secrets["gcp"]["credentials"]), scope
)
gc = gspread.authorize(creds)
sh = gc.open("fastlabor")

# 4) Load match_results sheet
ws = sh.worksheet("match_results")
records = ws.get_all_records()
df = pd.DataFrame(records)

# 5) Filter to only this findjob_id
status_df = df[df["findjob_id"] == findjob_id].reset_index(drop=True)

if status_df.empty:
    st.info(f"❌ ไม่พบการจับคู่สำหรับ Find Job ID = {findjob_id}")
else:
    st.markdown(f"### Find Job ID: {findjob_id}")
    # Show each applicant
    for idx, row in status_df.iterrows():
        emp_no = idx + 1
        name     = f"{row.get('first_name','')} {row.get('last_name','')}".strip() or '-'
        gender   = row.get('gender','-')
        priority = row.get('priority','-')
        status   = row.get('status','-')
        # color mapping
        c = status.lower()
        color = (
            "green" if c == "accepted" else
            "orange" if c == "on queue" else
            "red" if c == "declined" else
            "gray"
        )

        st.markdown(f"**Employee No.{emp_no}**")
        st.markdown(f"- **Name:** {name}")
        st.markdown(f"- **Gender:** {gender}")
        st.markdown(f"- **Priority:** {priority}")

        st.markdown(
            f"<span style='padding:4px 8px; background-color:{color}; color:white; border-radius:4px;'>{status}</span>",
            unsafe_allow_html=True
        )
        st.markdown("---")

# 6) Back button
if st.button("🔙 กลับหน้า My Jobs"):
    st.switch_page("pages/list_job.py")
