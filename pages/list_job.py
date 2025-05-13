# pages/list_job.py

import streamlit as st
import pandas as pd
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials

# 1. ต้องเรียก set_page_config เป็นคำสั่งแรกสุด
st.set_page_config(page_title="My Jobs | FAST LABOR", layout="wide")

# 2. Auth guard (สมมติคุณเซ็ต st.session_state["logged_in"] ใน login.py)
if not st.session_state.get("logged_in", False):
    st.experimental_set_query_params(page="login")
    st.stop()

st.title("📄 My Jobs")

# 3. เชื่อม Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
if "gcp" in st.secrets:
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        json.loads(st.secrets["gcp"]["credentials"]), scope
    )
else:
    creds = ServiceAccountCredentials.from_json_keyfile_name("pages/credentials.json", scope)
client = gspread.authorize(creds)
sh     = client.open("fastlabor")

# 4. Loader helper
def load_df(sheet_name: str) -> pd.DataFrame:
    ws   = sh.worksheet(sheet_name)
    vals = ws.get_all_values()
    df   = pd.DataFrame(vals[1:], columns=vals[0])
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    return df

df_post = load_df("post_job")
df_find = load_df("find_job")

# 5. Clean salary columns
for df in (df_post, df_find):
    for col in ("start_salary", "range_salary"):
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().replace({"": None})

# 6. Tabs for Post Job / Find Job
tab1, tab2 = st.tabs(["📌 Post Job", "🔍 Find Job"])

with tab1:
    st.subheader("📌 รายการโพสต์งาน")
    if df_post.empty:
        st.info("ยังไม่มีข้อมูลโพสต์งาน")
    else:
        for idx, row in df_post.iterrows():
            st.markdown("---")
            st.markdown(f"### Job #{idx+1}")

            # Extract fields
            email   = row["email"]
            jtype   = row["job_type"]
            detail  = row.get("skills", row.get("job_detail", "–"))
            date    = row["job_date"]
            start   = row["start_time"]
            end     = row["end_time"]
            addr    = row.get("job_address") or f"{row['province']}/{row['district']}/{row['subdistrict']}"
            min_sal = row.get("start_salary") or row.get("salary", "–")
            max_sal = row.get("range_salary") or row.get("salary", "–")

            # Render Markdown
            st.markdown(f"""
- **Email**: {email}
- **Job Type**: {jtype}
- **Detail**: {detail}
- **Date**: {date}
- **Time**: {start} – {end}
- **Location**: {addr}
- **Salary**: {min_sal} – {max_sal}
""")

            # ← ตรงนี้สำคัญ ต้องเรียกเป็น keyword args ทั้งหมด
            st.page_link(
                label="🔍 View Matching",
                page="result_matching",
                params={"job_idx": idx}
            )

with tab2:
    st.subheader("🔍 รายการค้นหางาน")
    if df_find.empty:
        st.info("ยังไม่มีข้อมูลค้นหางาน")
    else:
        for idx, row in df_find.iterrows():
            st.markdown("---")
            st.markdown(f"### Find #{idx+1}")

            email   = row["email"]
            skill   = row.get("skills", row.get("job_detail", "–"))
            date    = row["job_date"]
            start   = row["start_time"]
            end     = row["end_time"]
            addr    = f"{row['province']}/{row['district']}/{row['subdistrict']}"
            min_sal = row.get("start_salary") or "–"
            max_sal = row.get("range_salary") or "–"

            st.markdown(f"""
- **Email**: {email}
- **Skill**: {skill}
- **Date**: {date}
- **Time**: {start} – {end}
- **Location**: {addr}
- **Start Salary**: {min_sal}
- **Range Salary**: {max_sal}
""")
            st.page_link(
                label="🔍 View Matching",
                page="result_matching",
                params={"seeker_idx": idx}
            )

# 7. Back to Homepage
st.markdown("---")
st.page_link(label="🏠 Go to Homepage", page="home")
