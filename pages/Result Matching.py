import streamlit as st
import pandas as pd
import json
from oauth2client.service_account import ServiceAccountCredentials
import gspread

# 1) Page config & guard
st.set_page_config(page_title="Result Matching | FAST LABOR", layout="centered")
if not st.session_state.get("logged_in", False):
    st.stop()

st.title("🔍 AI Matching – ผลการจับคู่")

# 2) Retrieve selected_job_id and seeker_idx
selected_job_id   = st.session_state.get("selected_job_id")
active_seeker_idx = st.session_state.get("seeker_idx")
if selected_job_id is None and active_seeker_idx is None:
    st.info("กรุณากลับไปเลือกงาน/ผู้สมัครจากหน้า My Jobs ก่อนค่ะ")
    st.stop()

# -----------------------------------------------------------------
# Helper: load any sheet into DataFrame
# -----------------------------------------------------------------
def _sheet_df(name: str) -> pd.DataFrame:
    SCOPE = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        json.loads(st.secrets["gcp"]["credentials"]), SCOPE
    )
    gc = gspread.authorize(creds)
    ws = gc.open("fastlabor").worksheet(name)
    vals = ws.get_all_values()
    df   = pd.DataFrame(vals[1:], columns=vals[0])
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    return df

# -----------------------------------------------------------------
# Helper: prepare match_results sheet
# -----------------------------------------------------------------
def _get_match_ws():
    SCOPE = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        json.loads(st.secrets["gcp"]["credentials"]), SCOPE
    )
    gc = gspread.authorize(creds)
    ws = gc.open("fastlabor").worksheet("match_results")
    headers = ws.row_values(1)
    return ws, [h.lower().strip() for h in headers]

# -----------------------------------------------------------------
# Load & encode data
# -----------------------------------------------------------------
from matching import encode_job_df, encode_worker_df, recommend_seekers, recommend

jobs_df    = encode_job_df(_sheet_df("post_job"))
seekers_df = encode_worker_df(_sheet_df("find_job"))

# -----------------------------------------------------------------
# Utility: compute avg salary
# -----------------------------------------------------------------
def avg_salary(row: pd.Series) -> str:
    try:
        s = float(row.get("start_salary") or row.get("salary") or 0)
        r = float(row.get("range_salary") or row.get("salary") or 0)
        if s or r:
            return f"{(s + r) / 2:.0f}"
    except:
        pass
    return "-"

# -----------------------------------------------------------------
# 4) Employer view: show Top-5 seekers & choose priority
# -----------------------------------------------------------------
if selected_job_id is not None:
    # locate the selected job
    job_rows = jobs_df[jobs_df["job_id"] == selected_job_id]
    if job_rows.empty:
        st.error(f"ไม่พบงานที่มี Job ID = {selected_job_id}")
        st.stop()
    job_row_encoded = job_rows.iloc[0]

    # get many then filter unique to 5
    original = recommend_seekers(job_row_encoded, seekers_df, k=50, n=50)
    unique, seen = [], set()
    for rec in original.itertuples(index=False):
        if rec.email not in seen:
            unique.append(rec)
            seen.add(rec.email)
        if len(unique) == 5:
            break
    top5 = pd.DataFrame(unique)

    raw_seek = _sheet_df("find_job")
    raw_jobs = _sheet_df("post_job")
    priorities = {}

    for rank, rec in enumerate(top5.itertuples(index=False), start=1):
        st.divider()
        seeker = raw_seek[raw_seek.email == rec.email].iloc[0]
        name   = f"{seeker.first_name} {seeker.last_name}".strip() or "-"
        gender = seeker.gender or "-"
        date   = seeker.job_date or "-"
        time   = f"{seeker.start_time} – {seeker.end_time}"
        loc    = f"{seeker.province}/{seeker.district}/{seeker.subdistrict}"
        sal    = avg_salary(seeker)

        col1, col2 = st.columns([4,1])
        with col1:
            st.markdown(f"**Employee No.{rank}**")
            st.markdown(f"- **Name**: {name}")
            st.markdown(f"- **Gender**: {gender}")
            st.markdown(f"- **Job Type**: {rec.job_type}")
            st.markdown(f"- **Date**: {date}")
            st.markdown(f"- **Time**: {time}")
            st.markdown(f"- **Location**: {loc}")
            st.markdown(f"- **Salary**: {sal}")
            st.markdown(f"- **AI Score**: {rec.ai_score:.2f}")
        with col2:
            priorities[rank] = st.selectbox(
                "Priority", [1,2,3,4,5], index=rank-1, key=f"prio_{rank}"
            )

    if st.button("✅ Confirm Matches", use_container_width=True):
        ws, headers = _get_match_ws()
        match_data = []
        for rank, rec in enumerate(top5.itertuples(index=False), start=1):
            seeker   = raw_seek[raw_seek.email == rec.email].iloc[0].to_dict()
            job      = raw_jobs[raw_jobs.job_id == selected_job_id].iloc[0]
            job_sal  = job.get("salary", "")
            row = seeker.copy()
            # **ตรงนี้ เพิ่ม job_id ลงในแต่ละแถว**
            row["job_id"]       = selected_job_id
            row["priority"]     = priorities.get(rank,1)
            row["status"]       = "on queue"
            row["find_job_id"]  = rec.find_job_id if "find_job_id" in rec._fields else ""
            row["job_salary"]   = job_sal
            row["ai_score"]     = rec.ai_score
            match_data.append(row)

        if match_data:
            df_up = pd.DataFrame(match_data)
            cols  = [c.lower().strip() for c in df_up.columns]
            exist = [c for c in cols if c in headers]
            df_up = df_up[df_up.columns[df_up.columns.str.lower().str.strip().isin(exist)]]
            df_up = df_up[sorted(df_up.columns, key=lambda c: headers.index(c.lower().strip()))]
            start_row = len(ws.get_all_values()) + 1
            data = df_up.values.tolist()
            end_col = chr(ord("A") + df_up.shape[1] - 1)
            ws.update(f"A{start_row}:{end_col}{start_row+len(data)-1}", data)
            st.success("🎉 บันทึกผลการจับคู่เรียบร้อยแล้ว!")
        else:
            st.info("ไม่มีรายการจับคู่ที่จะบันทึก")

# -----------------------------------------------------------------
# 5) Worker view: show Top-5 jobs
# -----------------------------------------------------------------
elif active_seeker_idx is not None:
    seeker_row = seekers_df.iloc[active_seeker_idx]
    original = recommend(seeker_row, jobs_df, k=50, n=50)
    unique, seen = [], set()
    for rec in original.itertuples(index=False):
        if rec.job_id not in seen:
            unique.append(rec)
            seen.add(rec.job_id)
        if len(unique) == 5:
            break
    top5 = pd.DataFrame(unique)

    raw_jobs = _sheet_df("post_job")
    st.subheader("📋 งานที่ AI แนะนำสำหรับคุณ")

    for rank, rec in enumerate(top5.itertuples(index=False), start=1):
        st.divider()
        job  = raw_jobs[raw_jobs.job_id == rec.job_id].iloc[0]
        date = job.job_date or "-"
        time = f"{job.start_time} – {job.end_time}"
        loc  = f"{job.province}/{job.district}/{job.subdistrict}"
        sal  = avg_salary(job)

        st.markdown(f"**Job No.{rank}**")
        st.markdown(f"- **Job Type**: {rec.job_type}")
        st.markdown(f"- **Date**: {date}")
        st.markdown(f"- **Time**: {time}")
        st.markdown(f"- **Location**: {loc}")
        st.markdown(f"- **Salary**: {sal} THB")
        st.markdown(f"- **AI Score**: {rec.ai_score:.2f}")

# -----------------------------------------------------------------
st.divider()
if st.button("🔙 กลับหน้า My Jobs"):
    st.session_state.pop("selected_job_id", None)
    st.switch_page("pages/list_job.py")
