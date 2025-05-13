import streamlit as st
import pandas as pd
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(page_title="Job Detail", page_icon="📄", layout="wide")
st.title("📄 Job Detail")
st.write("ดูข้อมูลจากการโพสต์งานและการค้นหางาน")

# --- Auth & connect ---
scope = ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/drive"]
if "gcp" in st.secrets:
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        json.loads(st.secrets["gcp"]["credentials"]), scope
    )
else:
    creds = ServiceAccountCredentials.from_json_keyfile_name("pages/credentials.json", scope)
client = gspread.authorize(creds)
sh     = client.open("fastlabor")

# --- Robust loader ---
def load_df(name: str) -> pd.DataFrame:
    try:
        ws   = sh.worksheet(name)
        vals = ws.get_all_values()
        header = vals[0]
        data   = vals[1:]
        df     = pd.DataFrame(data, columns=header)
        df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
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
        st.info("ยังไม่มีข้อมูลการโพสต์งาน")
    else:
        for idx, row in df_post.iterrows():
            st.markdown("---")
            st.markdown(f"### Job #{idx+1}")
            sal = f\"{row.get('start_salary','–')} – {row.get('range_salary','–')}\" if row.get('start_salary') or row.get('range_salary') else "–"
            st.markdown(f\"\"\"
- **Email**: {row.get('email','–')}
- **Job Type**: {row.get('job_type','–')}
- **Detail**: {row.get('skills', row.get('job_detail','–'))}
- **Date & Time**: {row.get('job_date','–')} {row.get('start_time','–')}-{row.get('end_time','–')}
- **Location**: {row.get('province','–')}/{row.get('district','–')}/{row.get('subdistrict','–')}
- **Salary**: {sal}
\"\"\")

            if st.button("View Matching", key=f"view_{idx}"):
                st.experimental_set_query_params(page="result_matching", job_idx=idx)
                st.experimental_rerun()

with tab2:
    st.subheader("🔍 รายการค้นหางาน")
    if df_find.empty:
        st.info("ยังไม่มีข้อมูลการค้นหางาน")
    else:
        # แทน dataframe ใช้ loop แถวเพื่อหลีกเลี่ยง Arrow error
        for idx, row in df_find.iterrows():
            st.markdown("---")
            st.markdown(f"**Find #{idx+1}**")
            st.markdown(f\"\"\"
- **Email**: {row.get('email','–')}
- **Skill**: {row.get('skills','–')}
- **Available**: {row.get('job_date','–')} {row.get('start_time','–')}-{row.get('end_time','–')}
- **Location**: {row.get('province','–')}/{row.get('district','–')}/{row.get('subdistrict','–')}
- **Expected Wage**: {row.get('salary','–')}
\"\"\")

st.markdown("---")
st.page_link("pages/home.py", label="🏠 Go to Homepage")
