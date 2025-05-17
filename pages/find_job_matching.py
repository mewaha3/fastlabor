import streamlit as st
import pandas as pd
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ------------------------------------------------------------------
# 1) Page config & ensure login
# ------------------------------------------------------------------
st.set_page_config(page_title="Find Job Matches | FAST LABOR", layout="centered")
user_email = st.session_state.get("email")
if not user_email:
    st.error("❌ โปรดล็อกอินก่อนดูการจับคู่")
    st.stop()

st.title("🔍 รายการจับคู่ของฉัน")

# ------------------------------------------------------------------
# 2) Helpers
# ------------------------------------------------------------------
def _sheet_df(sheet_name: str) -> pd.DataFrame:
    """Load a sheet into a DataFrame with normalized column names."""
    SCOPE = ["https://www.googleapis.com/auth/spreadsheets",
             "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        json.loads(st.secrets["gcp"]["credentials"]), SCOPE)
    gc = gspread.authorize(creds)
    ws = gc.open("fastlabor").worksheet(sheet_name)
    all_values = ws.get_all_values()
    if not all_values:
        return pd.DataFrame()
    df = pd.DataFrame(all_values[1:], columns=all_values[0])
    df.columns = (df.columns
                  .str.strip()
                  .str.lower()
                  .str.replace(" ", "_"))
    return df

def _update_status(findjob_id: str, new_status: str):
    """Update the 'status' column in match_results for a given findjob_id."""
    if new_status not in ("Accepted", "Declined"):
        st.error("❌ สถานะต้องเป็น Accepted หรือ Declined")
        return
    SCOPE = ["https://www.googleapis.com/auth/spreadsheets",
             "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        json.loads(st.secrets["gcp"]["credentials"]), SCOPE)
    gc = gspread.authorize(creds)
    ws = gc.open("fastlabor").worksheet("match_results")

    df = _sheet_df("match_results")
    # find the row index (1-based including header)
    try:
        row_ix = df.index[df["findjob_id"] == findjob_id][0] + 2
    except IndexError:
        st.error(f"❌ ไม่พบ findjob_id = {findjob_id}")
        return

    # find the column number for 'status'
    try:
        col_ix = list(df.columns).index("status") + 1
    except ValueError:
        st.error("❌ ไม่พบคอลัมน์ 'status' ใน match_results")
        return

    cell = f"{chr(ord('A') + col_ix - 1)}{row_ix}"
    ws.update(cell, new_status)
    st.success(f"✅ อัปเดต findjob_id={findjob_id} → {new_status}")

# ------------------------------------------------------------------
# 3) Load match_results & filter by user, dedupe
# ------------------------------------------------------------------
match_df = _sheet_df("match_results")
if match_df.empty:
    st.info("📄 ไม่มีข้อมูล match_results")
    st.stop()

# only rows for this user
my_df = match_df[match_df["email"] == user_email]
# dedupe on findjob_id, keep first
my_df = my_df.drop_duplicates(subset="findjob_id", keep="first").reset_index(drop=True)

if my_df.empty:
    st.info("❌ ไม่มีรายการจับคู่สำหรับบัญชีนี้")
    st.stop()

# ------------------------------------------------------------------
# 4) Display each match with Accept/Decline
# ------------------------------------------------------------------
for _, row in my_df.iterrows():
    fid = row["findjob_id"]
    st.markdown(f"### Find Job ID: {fid}")
    st.write(f"- ประเภทงาน: {row.get('job_type','-')}")
    st.write(f"- รายละเอียด: {row.get('job_detail','-')}")
    st.write(f"- วันเวลา: {row.get('job_date','-')} | {row.get('start_time','-')}–{row.get('end_time','-')}")
    st.write(f"- สถานที่: {row.get('province','-')}/{row.get('district','-')}/{row.get('subdistrict','-')}")
    st.write(f"- ค่าจ้าง: {row.get('job_salary','-')} THB/day")
    st.write(f"- สถานะปัจจุบัน: **{row.get('status','-')}**")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Decline", key=f"decline_{fid}"):
            _update_status(fid, "Declined")
            st.experimental_rerun()
    with col2:
        if st.button("Accept", key=f"accept_{fid}"):
            _update_status(fid, "Accepted")
            # เก็บ row ทั้งหมดไว้ใช้หน้า job_detail
            st.session_state["selected_job"] = row.to_dict()
            st.experimental_rerun()  # หรือ st.switch_page(...) ถ้าจะไปหน้าอื่น

    st.markdown("---")

# ------------------------------------------------------------------
# 5) Back to My Jobs
# ------------------------------------------------------------------
if st.button("🔙 กลับหน้า My Jobs"):
    st.switch_page("pages/list_job.py")
