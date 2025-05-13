# pages/list_job.py

import streamlit as st
import pandas as pd
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(page_title="My Jobs | FAST LABOR", layout="wide")
st.title("📄 My Jobs")

# --- Auth & connect ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
if "gcp" in st.secrets:
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        json.loads(st.secrets["gcp"]["credentials"]), scope
    )
else:
    creds = ServiceAccountCredentials.from_json_keyfile_name("pages/credentials.json", scope)
client = gspread.authorize(creds)
sheet  = client.open("fastlabor")

# --- Robust loader ---
def load_df(name: str) -> pd.DataFrame:
    try:
        ws   = sheet.worksheet(name)
        vals = ws.get_all_values()
        df   = pd.DataFrame(vals[1:], columns=vals[0])
        df.columns = (
            df.columns
              .str.strip()
              .str.lower()
              .str.replace(" ", "_")
        )
        return df
    except Exception as e:
        st.warning(f"⚠️ ไม่พบชีท `{name}`: {e}")
        return pd.DataFrame()

df_post = load_df("post_job")
df_find = load_df("find_job")

# --- Tabs ---
tab1, tab2 = st.tabs(["📌 Post Job", "🔍 Find Job"])

with tab1:
    st.subheader("📌 รายการโพสต์งาน")
    if df_post.empty:
        st.info("ยังไม่มีข้อมูลโพสต์งาน")
    else:
        for idx, row in df_post.iterrows():
            st.markdown("---")
            st.markdown(f"### Job #{idx+1}")
            sal_min = row.get("start_salary") or "–"
            sal_max = row.get("range_salary") or "–"
            salary  = f"{sal_min} – {sal_max}" if (sal_min!="–" or sal_max!="–") else "–"
            st.markdown(f"""
- **Email**: {row.get("email","–")}
- **Job Type**: {row.get("job_type","–")}
- **Detail**: {row.get("skills", row.get("job_detail","–"))}
- **Date & Time**: {row.get("job_date","–")} {row.get("start_time","–")}-{row.get("end_time","–")}
- **Location**: {row.get("province","–")}/{row.get("district","–")}/{row.get("subdistrict","–")}
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
            st.markdown(f"""
- **Email**: {row.get("email","–")}
- **Skill**: {row.get("skills","–")}
- **Available**: {row.get("job_date","–")} {row.get("start_time","–")}-{row.get("end_time","–")}
- **Location**: {row.get("province","–")}/{row.get("district","–")}/{row.get("subdistrict","–")}
- **Expected Wage**: {row.get("salary","–")}
""")
            # ปุ่ม View Matching ใน Find Job
            if st.button("View Matching", key=f"view_find_{idx}"):
                st.experimental_set_query_params(page="result_matching", seeker_idx=idx)
                st.experimental_rerun()

# --- Back to home ---
st.markdown("---")
st.page_link("pages/home.py", label="🏠 Go to Homepage")
