import streamlit as st
import pandas as pd
import json
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials
import gspread
from gspread_dataframe import set_with_dataframe
from matching import encode_job_df, encode_worker_df, recommend, recommend_seekers

# 1) Page config & guard
st.set_page_config(page_title="Result Matching | FAST LABOR", layout="centered")
if not st.session_state.get("logged_in", False):
    st.stop()

# 2) Get active indices
active_job_idx = st.session_state.get("job_idx")
active_seeker_idx = st.session_state.get("seeker_idx")
if active_job_idx is None and active_seeker_idx is None:
    st.info("กรุณากลับไปเลือกงาน/ผู้สมัครจากหน้า My Jobs ก่อนค่ะ")
    st.stop()

# Helper to load sheet into DataFrame
@st.cache_data
def _sheet_df(sheet_name: str) -> pd.DataFrame:
    SCOPE = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds_dict = json.loads(st.secrets["gcp"]["credentials_json"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPE)
    client = gspread.authorize(creds)
    sheet = client.open("fastlabor").worksheet(sheet_name)
    df = pd.DataFrame(sheet.get_all_records())
    df.columns = df.columns.str.lower().str.replace(" ", "_")
    return df

# Load data
jobs_raw = _sheet_df('post_job')
seekers_raw = _sheet_df('find_job')

# Encode once
jobs_encoded = encode_job_df(jobs_raw)
seekers_encoded = encode_worker_df(seekers_raw)

st.title("🔍 AI Matching – ผลการจับคู่")

# Employer view
if active_job_idx is not None:
    job_row = jobs_encoded.iloc[[active_job_idx]]
    top_seekers = recommend_seekers(job_row, seekers_encoded, n=5)

    st.subheader("ผู้สมัครที่ AI แนะนำ")
    priorities = []
    for idx, row in top_seekers.iterrows():
        seeker = seekers_raw.iloc[idx]
        col1, col2 = st.columns([3,1])
        with col1:
            st.markdown(f"**Name:** {seeker['name']}  ")
            st.markdown(f"**Gender:** {seeker['gender']}  ")
            st.markdown(f"**Job Type:** {seeker['job_type']}  ")
            st.markdown(f"**Date:** {seeker['job_date']}  ")
            st.markdown(f"**Time:** {seeker['start_time']} - {seeker['end_time']}  ")
            st.markdown(f"**Location:** {seeker['province']}, {seeker['district']}  ")
            st.markdown(f"**Salary Expectation:** {seeker['start_salary']} - {seeker['range_salary']}  ")
            # Display AI score
            st.markdown(f"**AI Score:** {row['ai_score']:.2f}  ")
        with col2:
            pr = st.selectbox(
                f"Priority for {seeker['name']}",
                options=[1,2,3,4,5],
                key=f"priority_{idx}"
            )
            priorities.append(pr)

    if st.button("✅ Confirm Matches"):
        # Prepare to save
        matches = []
        for (idx, row), priority in zip(top_seekers.iterrows(), priorities):
            seeker = seekers_raw.iloc[idx]
            matches.append({
                'job_id': jobs_raw.iloc[active_job_idx]['job_id'],
                'seeker_email': seeker['email'],
                'priority': priority,
                'status': 'on queue',
                'ai_score': row['ai_score']
            })
        if matches:
            sheet = gspread.authorize(ServiceAccountCredentials.from_json_keyfile_dict(
                json.loads(st.secrets['gcp']['credentials_json']), SCOPE
            )).open('fastlabor').worksheet('match_results')
            df_matches = pd.DataFrame(matches)
            set_with_dataframe(sheet, df_matches)
            st.success("🎉 บันทึกผลการจับคู่เรียบร้อยแล้ว!")
        else:
            st.warning("ไม่มีรายการจับคู่ที่จะบันทึก")

# Worker view
elif active_seeker_idx is not None:
    seeker_row = seekers_encoded.iloc[[active_seeker_idx]]
    top_jobs = recommend(seeker_row, jobs_encoded, n=5)

    st.subheader("งานที่ AI แนะนำ")
    for idx, row in top_jobs.iterrows():
        job = jobs_raw.iloc[idx]
        st.markdown(f"**Job Type:** {job['job_type']}  ")
        st.markdown(f"**Date:** {job['job_date']}  ")
        st.markdown(f"**Time:** {job['start_time']} - {job['end_time']}  ")
        st.markdown(f"**Location:** {job['province']}, {job['district']}  ")
        st.markdown(f"**Salary:** {job['start_salary']} - {job['range_salary']}  ")
        # Display AI score
        st.markdown(f"**AI Score:** {row['ai_score']:.2f}  ")
        st.markdown("---")

# Back button
action = st.button("🔙 กลับหน้า My Jobs")
if action:
    st.session_state.pop('job_idx', None)
    st.session_state.pop('seeker_idx', None)
    st.experimental_rerun()
