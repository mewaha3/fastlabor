import streamlit as st
import pandas as pd
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# 1) Page Config
st.set_page_config(page_title="Find Job Matches | FAST LABOR", layout="centered")

# Header & Navigation
st.markdown("""
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
    <div><strong>FAST LABOR</strong></div>
    <div>
        <a href="/pages/find_job.py" style="margin-right: 20px;">Find Job</a>
        <a href="/pages/list_job.py" style="margin-right: 20px;">My Job</a>
        <a href="/pages/profile.py" style="background-color: black; color: white; padding: 5px 10px; border-radius: 4px;">Profile</a>
    </div>
</div>
""", unsafe_allow_html=True)

# Title
st.markdown("## Find Job Matches")
st.markdown("เลือก Accept/Decline เพื่ออัปเดตสถานะการจับคู่ใน Google Sheets")

# Ensure logged in
logged_in_email = st.session_state.get("email")
if not logged_in_email:
    st.error("❌ โปรดล็อกอินก่อนดูการจับคู่")
    st.stop()

# ------------------------------------------------------------------
# Helper: load sheet to DataFrame
# ------------------------------------------------------------------
def _sheet_df(name: str) -> pd.DataFrame:
    SCOPE = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(st.secrets["gcp"]["credentials"]), SCOPE)
    gc = gspread.authorize(creds)
    ws = gc.open("fastlabor").worksheet(name)
    vals = ws.get_all_values()
    df = pd.DataFrame(vals[1:], columns=vals[0])
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    return df

# ------------------------------------------------------------------
# Helper: update status in match_results sheet (column O)
# ------------------------------------------------------------------
def _update_match_status(find_job_id: str, status: str):
    if status not in ["Accepted", "Declined"]:
        st.error("❌ สถานะต้องเป็น 'Accepted' หรือ 'Declined'")
        return
    SCOPE = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(st.secrets["gcp"]["credentials"]), SCOPE)
    gc = gspread.authorize(creds)
    ws = gc.open("fastlabor").worksheet("match_results")
    df = _sheet_df("match_results")
    try:
        row_idx = df[df["findjob_id"] == find_job_id].index[0] + 2  # +2 for header row
        ws.update(f"O{row_idx}", status)
        st.success(f"✅ อัปเดตสถานะ findjob_id={find_job_id} → {status}")
    except IndexError:
        st.error(f"❌ ไม่พบ findjob_id={find_job_id} ใน match_results")
    except Exception as e:
        st.error(f"❌ เกิดข้อผิดพลาด: {e}")

# ------------------------------------------------------------------
# Load & display all matches for this user (no removal of old rows)
# ------------------------------------------------------------------
match_df = _sheet_df("match_results")
user_matches = match_df[match_df["email"] == logged_in_email]

if user_matches.empty:
    st.info("❌ ไม่มีการจับคู่สำหรับบัญชีนี้")
else:
    for _, row in user_matches.iterrows():
        find_id = row["findjob_id"]
        st.markdown(f"### Find Job ID: {find_id}")
        st.write(f"- ประเภทงาน: {row.get('job_type','-')}")
        st.write(f"- รายละเอียด: {row.get('job_detail','-')}")
        st.write(f"- วันเวลา: {row.get('job_date','-')} | {row.get('start_time','-')}–{row.get('end_time','-')}")
        st.write(f"- สถานที่: {row.get('province','-')}/{row.get('district','-')}/{row.get('subdistrict','-')}")
        st.write(f"- ค่าจ้าง: {row.get('job_salary','-')} THB")
        st.write(f"- สถานะปัจจุบัน: {row.get('status','-')}")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Decline", key=f"decline_{find_id}"):
                _update_match_status(find_id, "Declined")
        with col2:
            if st.button("Accept", key=f"accept_{find_id}"):
                _update_match_status(find_id, "Accepted")
        st.markdown("---")

# Back to My Jobs
st.divider()
if st.button("🔙 กลับหน้า My Jobs"):
    st.switch_page("pages/list_job.py")
