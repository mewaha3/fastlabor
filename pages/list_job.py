# pages/list_job.py

import streamlit as st
import pandas as pd
import json
from oauth2client.service_account import ServiceAccountCredentials
import gspread

st.set_page_config(page_title="My Jobs | FAST LABOR", layout="wide")
st.title("📄 My Jobs")

# —————————————————————————————————————————
# 1. Authenticate & connect to Google Sheets
# —————————————————————————————————————————
scope = ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/drive"]
if "gcp" in st.secrets:
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        json.loads(st.secrets["gcp"]["credentials"]), scope
    )
else:
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        "pages/credentials.json", scope
    )
client = gspread.authorize(creds)
sheet  = client.open("fastlabor")

# —————————————————————————————————————————
# 2. Robust loader using get_all_values()
# —————————————————————————————————————————
def load_df(name: str) -> pd.DataFrame:
    try:
        ws   = sheet.worksheet(name)
        vals = ws.get_all_values()
        header = vals[0]
        data   = vals[1:]
        df     = pd.DataFrame(data, columns=header)
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

# —————————————————————————————————————————
# 3. Tabs: Post Job / Find Job
# —————————————————————————————————————————
tab1, tab2 = st.tabs(["🔨 Post Job", "🔍 Find Job"])

with tab1:
    st.subheader("🔨 รายการโพสต์งาน")
    if df_post.empty:
        st.info("ยังไม่มีข้อมูลโพสต์งาน")
    else:
        for idx, row in df_post.iterrows():
            st.markdown("---")
            st.markdown(f"**Job #{idx+1}**: {row.get('job_type','–')} on {row.get('job_date','–')}")
            # View Matching button
            if st.button("View Matching", key=f"view_{idx}"):
                st.experimental_set_query_params(page="result_matching", job_idx=idx)
                st.experimental_rerun()

with tab2:
    st.subheader("🔍 รายการค้นหางาน")
    if df_find.empty:
        st.info("ยังไม่มีข้อมูลค้นหางาน")
    else:
        # Display the DataFrame safely
        st.dataframe(df_find, use_container_width=True)

# —————————————————————————————————————————
# 4. Back to home
# —————————————————————————————————————————
st.markdown("---")
st.page_link("pages/home.py", label="🏠 Go to Homepage")
