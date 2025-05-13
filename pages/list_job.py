# pages/job_detail.py

import streamlit as st
import pandas as pd
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(page_title="Job Detail", page_icon="📄", layout="wide")
st.title("📄 Job Detail")
st.write("ดูข้อมูลจากการโพสต์งานและการค้นหางาน")

# —————————————————————————————————————————
# 1. Auth & Load Sheets
# —————————————————————————————————————————
scope = ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/drive"]
if "gcp" in st.secrets:
    creds_dict = json.loads(st.secrets["gcp"]["credentials"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
else:
    creds = ServiceAccountCredentials.from_json_keyfile_name("pages/credentials.json", scope)

client = gspread.authorize(creds)
sh     = client.open("fastlabor")

def load_sheet(name):
    try:
        ws   = sh.worksheet(name)
        data = ws.get_all_records(expected_headers=1)
        df   = pd.DataFrame(data)
        # normalize column names
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

df_post = load_sheet("post_job")
df_find = load_sheet("find_job")

# —————————————————————————————————————————
# 2. Tabs: Post Job / Find Job
# —————————————————————————————————————————
tab1, tab2 = st.tabs(["📌 Post Job", "🔍 Find Job"])

with tab1:
    st.subheader("📌 รายการโพสต์งาน")
    if df_post.empty:
        st.info("ยังไม่มีข้อมูลการโพสต์งาน")
    else:
        # loop over each post
        for idx, row in df_post.iterrows():
            st.markdown("---")
            st.markdown(f"### Job #{idx+1}")
            # bullet list
            salary_min = row.get("start_salary") or "–"
            salary_max = row.get("range_salary") or "–"
            salary_display = f"{salary_min} – {salary_max}" if salary_min != "–" or salary_max != "–" else "–"

            st.markdown(
                f"""
- **Email**: {row.get("email", "–")}
- **Job Type**: {row.get("job_type", "–")}
- **Detail**: {row.get("job_detail", "–")}
- **Date & Time**: {row.get("job_date", "–")} {row.get("start_time","–")}–{row.get("end_time","–")}
- **Location**: {row.get("province","–")}/{row.get("district","–")}/{row.get("subdistrict","–")}
- **Salary**: {salary_display}
"""
            )
            # View Matching button
            if st.button("View Matching", key=f"view_{idx}"):
                st.experimental_set_query_params(page="result_matching", job_idx=idx)
                st.experimental_rerun()

with tab2:
    st.subheader("🔍 รายการค้นหางาน")
    if df_find.empty:
        st.info("ยังไม่มีข้อมูลการค้นหางาน")
    else:
        st.dataframe(df_find, use_container_width=True)

# —————————————————————————————————————————
# 3. Back to Home
# —————————————————————————————————————————
st.markdown("---")
st.page_link("pages/home.py", label="🏠 Go to Homepage")
