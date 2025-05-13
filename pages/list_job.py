# pages/list_job.py

import streamlit as st
import pandas as pd
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(page_title="My Jobs | FAST LABOR", layout="wide")
st.title("📄 My Jobs")

# --- 1. Auth & connect to Google Sheets ---
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
    header = vals[0]
    data   = vals[1:]
    df     = pd.DataFrame(data, columns=header)
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    return df

df_post = load_df("post_job")
df_find = load_df("find_job")

# --- 3. Normalize salary columns to strings without extra spaces ---
for df in (df_post, df_find):
    for c in ["start_salary","range_salary"]:
        if c in df.columns:
            # strip whitespace, convert empty to None
            df[c] = df[c].astype(str).str.strip().replace({"": None})

# --- 4. Tabs ---
tab1, tab2 = st.tabs(["📌 Post Job", "🔍 Find Job"])

with tab1:
    st.subheader("📌 รายการโพสต์งาน")
    if df_post.empty:
        st.info("ยังไม่มีข้อมูลโพสต์งาน")
    else:
        for idx, row in df_post.iterrows():
            st.markdown("---")
            st.markdown(f"### Job #{idx+1}")

            email   = row["email"]
            jtype   = row["job_type"]
            detail  = row.get("skills", row.get("job_detail","–"))
            date    = row["job_date"]
            start   = row["start_time"]
            end     = row["end_time"]
            addr    = row.get("job_address") or f"{row['province']}/{row['district']}/{row['subdistrict']}"

            # Salary display
            min_sal = row.get("start_salary")
            max_sal = row.get("range_salary")
            if min_sal or max_sal:
                salary = f"{min_sal or '–'} – {max_sal or '–'}"
            else:
                salary = row.get("salary","–")

            st.markdown(f"""
- **Email**: {email}
- **Job Type**: {jtype}
- **Detail**: {detail}
- **Date & Time**: {date} {start}–{end}
- **Location**: {addr}
- **Salary**: {salary}
""")
            if st.button("View Matching", key=f"view_post_{idx}"):
                st.experimental_set_query_params(page="result_matching", job_idx=idx)
                st.experimental_rerun()

with tab2:
    st.subheader("🔍 รายการค้นหางาน")
    if df_find.empty:
        st.info("ยังไม่มีข้อมูลค้นหางาน")
    else:
        for idx, row in df_find.iterrows():
            st.markdown("---")
            st.markdown(f"### Find #{idx+1}")

            email = row["email"]
            skill = row.get("skills", row.get("job_detail","–"))
            date  = row["job_date"]
            start = row["start_time"]
            end   = row["end_time"]
            addr  = f"{row['province']}/{row['district']}/{row['subdistrict']}"

            # Available
            avail = f"{date} {start}–{end}"

            # Start & Range Salary (must use the normalized columns)
            min_sal = row.get("start_salary") or "–"
            max_sal = row.get("range_salary") or "–"

            st.markdown(f"""
- **Email**: {email}
- **Skill**: {skill}
- **Available**: {avail}
- **Location**: {addr}
- **Start Salary**: {min_sal}
- **Range Salary**: {max_sal}
""")
            if st.button("View Matching", key=f"view_find_{idx}"):
                st.experimental_set_query_params(page="result_matching", seeker_idx=idx)
                st.experimental_rerun()

# --- 5. Back to Home ---
st.markdown("---")
st.page_link("pages/home.py", label="🏠 Go to Homepage")
