# pages/list_job.py

import streamlit as st
import pandas as pd
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials

# 1. ต้องเรียก set_page_config เป็นคำสั่งแรกสุด
st.set_page_config(page_title="My Jobs | FAST LABOR", layout="wide")

st.title("📄 My Jobs")

# 2. Auth & connect to Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
if "gcp" in st.secrets:
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        json.loads(st.secrets["gcp"]["credentials"]), scope
    )
else:
    creds = ServiceAccountCredentials.from_json_keyfile_name("pages/credentials.json", scope)
client = gspread.authorize(creds)
sh     = client.open("fastlabor")

# 3. Loader helper
def load_df(sheet_name: str) -> pd.DataFrame:
    ws   = sh.worksheet(sheet_name)
    vals = ws.get_all_values()
    df   = pd.DataFrame(vals[1:], columns=vals[0])
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    return df

df_post = load_df("post_job")
df_find = load_df("find_job")

# 4. Clean salary columns
for df in (df_post, df_find):
    for col in ("start_salary", "range_salary"):
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().replace({"": None})

# 5. Define simple CSS for our link-buttons
st.markdown("""
<style>
.link-button {
  display: inline-block;
  background: #f0f2f6;
  color: #0e1117;
  padding: 0.4rem 0.8rem;
  border-radius: 4px;
  text-decoration: none;
  border: 1px solid #ccc;
}
.link-button:hover {
  background: #e1e3e8;
}
</style>
""", unsafe_allow_html=True)

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
            detail  = row.get("skills", row.get("job_detail","–"))
            date    = row["job_date"]
            start   = row["start_time"]
            end     = row["end_time"]
            addr    = row.get("job_address") or f"{row['province']}/{row['district']}/{row['subdistrict']}"
            min_sal = row.get("start_salary") or row.get("salary","–")
            max_sal = row.get("range_salary") or row.get("salary","–")

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

            st.markdown("---")
            st.page_link("pages/Result Matching.py", label="🔍 View Matching ")

with tab2:
    st.subheader("🔍 รายการค้นหางาน")
    if df_find.empty:
        st.info("ยังไม่มีข้อมูลค้นหางาน")
    else:
        for idx, row in df_find.iterrows():
            st.markdown("---")
            st.markdown(f"### Find #{idx+1}")

            email   = row["email"]
            skill   = row.get("skills", row.get("job_detail","–"))
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
            st.markdown("---")
            st.page_link("pages/Result Matching.py", label="🔍 View Matching ")


# 7. Back to Homepage
st.markdown("---")
st.page_link("pages/home.py", label="🏠 Go to Homepage")
