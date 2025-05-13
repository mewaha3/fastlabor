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
sh     = client.open("fastlabor")

# --- Robust loader using get_all_values() ---
def load_df(sheet_name: str) -> pd.DataFrame:
    try:
        ws   = sh.worksheet(sheet_name)
        vals = ws.get_all_values()
        header = vals[0]
        data   = vals[1:]
        df     = pd.DataFrame(data, columns=header)
        # normalize column names
        df.columns = (
            df.columns
              .str.strip()
              .str.lower()
              .str.replace(" ", "_")
        )
        return df
    except Exception as e:
        st.warning(f"⚠️ ไม่พบชีท `{sheet_name}`: {e}")
        return pd.DataFrame()

df_post = load_df("post_job")
df_find = load_df("find_job")

# --- Tabs: Post Job / Find Job ---
tab1, tab2 = st.tabs(["📌 Post Job", "🔍 Find Job"])

with tab1:
    st.subheader("📌 รายการโพสต์งาน")
    if df_post.empty:
        st.info("ยังไม่มีข้อมูลโพสต์งาน")
    else:
        for idx, row in df_post.iterrows():
            st.markdown("---")
            st.markdown(f"### Job #{idx+1}")
            # สร้างข้อความแบบ bullet list
            sal_min = row.get("start_salary") or "–"
            sal_max = row.get("range_salary") or "–"
            salary  = f"{sal_min} – {sal_max}" if (sal_min != "–" or sal_max != "–") else "–"

            st.markdown(f"""
- **Email**: {row.get("email","–")}
- **Job Type**: {row.get("job_type","–")}
- **Detail**: {row.get("skills", row.get("job_detail","–"))}
- **Date & Time**: {row.get("job_date","–")} {row.get("start_time","–")}-{row.get("end_time","–")}
- **Location**: {row.get("province","–")}/{row.get("district","–")}/{row.get("subdistrict","–")}
- **Salary**: {salary}
""")
            if st.button("View Matching", key=f"view_{idx}"):
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

st.markdown("---")
st.page_link("pages/home.py", label="🏠 Go to Homepage")
