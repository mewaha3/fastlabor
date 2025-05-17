import streamlit as st
import pandas as pd
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials

# 1) Page config & login guard
st.set_page_config(page_title="My Jobs | FAST LABOR", layout="wide")
if not st.session_state.get("logged_in", False):
    st.experimental_set_query_params(page="login")
    st.stop()

st.title("📄 My Jobs")

# 2) Connect to Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_info = json.loads(st.secrets.get("gcp", {}).get("credentials", "{}"))
creds = (
    ServiceAccountCredentials.from_json_keyfile_dict(creds_info, scope)
    if creds_info
    else ServiceAccountCredentials.from_json_keyfile_name("pages/credentials.json", scope)
)
gc = gspread.authorize(creds)
spreadsheet = gc.open("fastlabor")

# 3) Helper: load sheet into DataFrame
def load_df(sheet_name: str) -> pd.DataFrame:
    ws = spreadsheet.worksheet(sheet_name)
    vals = ws.get_all_values()
    df = pd.DataFrame(vals[1:], columns=vals[0])
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    return df

# load dataframes
df_post = load_df("post_job")
df_find = load_df("find_job")

# 4) Filter only own records
user_email = st.session_state.get("email")
df_post = df_post[df_post.email == user_email].reset_index(drop=True)
df_find = df_find[df_find.email == user_email].reset_index(drop=True)

# 5) Clean salary columns
for df in (df_post, df_find):
    for col in ("start_salary", "range_salary", "salary"):
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().replace({"": None})

# 6) Tabs
tab1, tab2 = st.tabs(["📌 Post Job", "🔍 Find Job"])

with tab1:
    st.subheader("📌 รายการที่ฉันโพสต์งาน")
    if df_post.empty:
        st.info("คุณยังไม่มีโพสต์งาน")
    else:
        for _, row in df_post.iterrows():
            st.divider()
            job_id = row.get("job_id") or ""
            st.markdown(f"### Job ID: {job_id}")
            jtype = row.get("job_type", "-")
            detail = row.get("job_detail", "-")
            date = row.get("job_date", "-")
            start = row.get("start_time", "-")
            end = row.get("end_time", "-")
            addr = row.get("job_address") or f"{row['province']}/{row['district']}/{row['subdistrict']}"
            # salary logic
            if (row.get("start_salary") or row.get("range_salary")):
                salary = f"{row.get('start_salary','-')} – {row.get('range_salary','-')}"
            else:
                salary = row.get("salary", "-")
            st.markdown(f"""
| ฟิลด์       | รายละเอียด                    |
|------------|-------------------------------|
| Job Type   | {jtype}                        |
| Detail     | {detail}                      |
| Date       | {date}                        |
| Time       | {start} – {end}               |
| Location   | {addr}                        |
| Salary     | {salary}                      |
"""
            )
            if st.button("🔍 ดูการจับคู่", key=f"post_{job_id}"):
                # store selected job_id instead of index
                st.session_state["selected_job_id"] = job_id
                st.session_state.pop("seeker_idx", None)
                st.switch_page("Result Matching")

with tab2:
    st.subheader("🔍 รายการที่ฉันค้นหางาน")
    if df_find.empty:
        st.info("คุณยังไม่มีการค้นหางาน")
    else:
        for _, row in df_find.iterrows():
            st.divider()
            find_id = row.get("findjob_id") or ""
            st.markdown(f"### Find ID: {find_id}")
            jtype = row.get("job_type", "-")
            skill = row.get("skills", "-")
            date = row.get("job_date", "-")
            start = row.get("start_time", "-")
            end = row.get("end_time", "-")
            addr = f"{row['province']}/{row['district']}/{row['subdistrict']}"
            min_sal = row.get("start_salary") or '-'
            max_sal = row.get("range_salary") or '-'
            st.markdown(f"""
| ฟิลด์          | รายละเอียด              |
|---------------|-------------------------|
| Job Type      | {jtype}                |
| Skill         | {skill}                |
| Date          | {date}                 |
| Time          | {start} – {end}        |
| Location      | {addr}                 |
| Start Salary  | {min_sal}              |
| Range Salary  | {max_sal}              |
"""
            )

# 7) Back to Home
st.divider()
st.page_link(page="home", label="🏠 หน้าแรก")
