# pages/list_job.py

import streamlit as st
import pandas as pd
import gspread
import json
from urllib.parse import urlencode
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(page_title="My Jobs | FAST LABOR", layout="wide")
st.markdown("<h1 style='text-align:center'>📄 My Jobs</h1>", unsafe_allow_html=True)

# --- 1. Authenticate & connect to Google Sheets ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
if "gcp" in st.secrets:
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        json.loads(st.secrets["gcp"]["credentials"]), scope
    )
else:
    creds = ServiceAccountCredentials.from_json_keyfile_name("pages/credentials.json", scope)
client = gspread.authorize(creds)
sh     = client.open("fastlabor")

# --- 2. Robust loader using get_all_values() ---
def load_df(sheet_name: str) -> pd.DataFrame:
    ws   = sh.worksheet(sheet_name)
    vals = ws.get_all_values()
    header, data = vals[0], vals[1:]
    df   = pd.DataFrame(data, columns=header)
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    return df

df_post = load_df("post_job")
df_find = load_df("find_job")

# --- 3. Clean up salary columns ---
for df in (df_post, df_find):
    for col in ("start_salary", "range_salary"):
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().replace({"": None})

# --- 4. Tabs: Post Job / Find Job ---
tab1, tab2 = st.tabs(["📌 Post Job", "🔍 Find Job"])

with tab1:
    st.subheader("📌 รายการโพสต์งาน")
    if df_post.empty:
        st.info("ยังไม่มีข้อมูลโพสต์งาน")
    else:
        for idx, row in df_post.iterrows():
            st.markdown("---")
            st.markdown(f"### Job #{idx+1}")

            # Details
            email   = row["email"]
            jtype   = row["job_type"]
            detail  = row.get("skills", row.get("job_detail", "-"))
            date    = row["job_date"]
            start   = row["start_time"]
            end     = row["end_time"]
            addr    = row.get("job_address") or f"{row['province']}/{row['district']}/{row['subdistrict']}"
            min_sal = row.get("start_salary") or row.get("salary", "-")
            max_sal = row.get("range_salary") or row.get("salary", "-")

            st.markdown(f"""
- **Email**: {email}
- **Job Type**: {jtype}
- **Detail**: {detail}
- **Date**: {date}
- **Time**: {start} – {end}
- **Location**: {addr}
- **Salary**: {min_sal} – {max_sal}
""")

            # Link to Result Matching with job_idx
            params = urlencode({"page": "result_matching", "job_idx": idx})
            st.markdown(f"[🔍 View Matching →](/?{params})", unsafe_allow_html=True)

with tab2:
    st.subheader("🔍 รายการค้นหางาน")
    if df_find.empty:
        st.info("ยังไม่มีข้อมูลค้นหางาน")
    else:
        for idx, row in df_find.iterrows():
            st.markdown("---")
            st.markdown(f"### Find #{idx+1}")

            # Details
            email   = row["email"]
            skill   = row.get("skills", row.get("job_detail", "-"))
            date    = row["job_date"]
            start   = row["start_time"]
            end     = row["end_time"]
            addr    = f"{row['province']}/{row['district']}/{row['subdistrict']}"
            min_sal = row.get("start_salary", "-")
            max_sal = row.get("range_salary", "-")

            st.markdown(f"""
- **Email**: {email}
- **Skill**: {skill}
- **Date**: {date}
- **Time**: {start} – {end}
- **Location**: {addr}
- **Start Salary**: {min_sal}
- **Range Salary**: {max_sal}
""")


            st.markdown(f"[🔍 View Matching →](/?{params})", unsafe_allow_html=True)

# --- 5. Back to Home ---
st.markdown("---")
st.markdown("[🏠 Go to Homepage](/?page=home)", unsafe_allow_html=True)
