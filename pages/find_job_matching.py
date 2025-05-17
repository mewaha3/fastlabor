import streamlit as st
import pandas as pd
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# 1) Page config
st.set_page_config(page_title="My Matches | FAST LABOR", layout="centered")

# 2) Ensure user is logged in
user_email = st.session_state.get("email")
if not user_email:
    st.error("❌ โปรดล็อกอินก่อนดูการจับคู่")
    st.stop()

st.title("🔍 รายการการจับคู่ของฉัน")

# ------------------------------------------------------------------
# Helper: load a sheet into a DataFrame
# ------------------------------------------------------------------
def _sheet_df(sheet_name: str) -> pd.DataFrame:
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(st.secrets["gcp"]["credentials"]), scope)
    client = gspread.authorize(creds)
    ws = client.open("fastlabor").worksheet(sheet_name)
    data = ws.get_all_values()
    df = pd.DataFrame(data[1:], columns=data[0])
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    return df

# ------------------------------------------------------------------
# Helper: update status in match_results (column 'status')
# ------------------------------------------------------------------
def _update_status(findjob_id: str, new_status: str):
    if new_status not in ("Accepted", "Declined"):
        st.error("❌ สถานะต้องเป็น Accepted หรือ Declined")
        return
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(st.secrets["gcp"]["credentials"]), scope)
    client = gspread.authorize(creds)
    ws = client.open("fastlabor").worksheet("match_results")
    df = _sheet_df("match_results")
    try:
        idx = df.index[df["findjob_id"] == findjob_id][0] + 2  # +2 for header and 0-based
        # find column index for 'status'
        header = df.columns.tolist()
        col_num = header.index("status") + 1  # 1-based
        col_letter = chr(ord("A") + col_num - 1)
        ws.update(f"{col_letter}{idx}", new_status)
        st.success(f"อัปเดต {findjob_id} → {new_status}")
    except IndexError:
        st.error(f"❌ ไม่พบ findjob_id = {findjob_id}")
    except Exception as e:
        st.error(f"❌ เกิดข้อผิดพลาดในการอัปเดต: {e}")

# ------------------------------------------------------------------
# Load match_results and filter for this user
# ------------------------------------------------------------------
matches = _sheet_df("match_results")
my_matches = matches[matches["email"] == user_email]

if my_matches.empty:
    st.info("❌ ยังไม่มีรายการจับคู่สำหรับคุณ")
else:
    for _, row in my_matches.iterrows():
        fid = row["findjob_id"]
        st.markdown(f"**Find Job ID:** `{fid}`")
        # Buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Accept", key=f"accept_{fid}"):
                _update_status(fid, "Accepted")
                st.experimental_rerun()
        with col2:
            if st.button("Decline", key=f"decline_{fid}"):
                _update_status(fid, "Declined")
                st.experimental_rerun()
        st.markdown("---")

# 4) Back button
if st.button("🔙 กลับหน้า My Jobs"):
    st.switch_page("pages/list_job.py")
