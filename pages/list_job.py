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

# --- Robust loader ---
def load_df(name: str) -> pd.DataFrame:
    try:
        ws   = sh.worksheet(name)
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
            # Prepare fields
            email   = row.get("email","–")
            jtype   = row.get("job_type","–")
            detail  = row.get("skills", row.get("job_detail","–"))
            date    = row.get("job_date","–")
            start   = row.get("start_time","–")
            end     = row.get("end_time","–")
            addr    = row.get("job_address") or "/".join([
                        row.get("province","–"),
                        row.get("district","–"),
                        row.get("subdistrict","–")
                      ])
            # salary: try new columns, else old
            sal_min = row.get("start_salary") or ""
            sal_max = row.get("range_salary") or ""
            if sal_min or sal_max:
                salary = f"{sal_min} – {sal_max}"
            else:
                salary = row.get("salary","–") or "–"

            # render
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
            email  = row.get("email","–")
            skill  = row.get("skills", row.get("job_detail","–"))
            date   = row.get("job_date","–")
            start  = row.get("start_time","–")
            end    = row.get("end_time","–")
            addr   = "/".join([
                        row.get("province","–"),
                        row.get("district","–"),
                        row.get("subdistrict","–")
                     ])
            # expected wage: prefer salary column
            exp_wage = row.get("salary") or ""
            if not exp_wage:
                # or from range_salary
                exp_wage = row.get("start_salary") or ""
            exp_wage = exp_wage or "–"

            st.markdown(f"""
- **Email**: {email}
- **Skill**: {skill}
- **Available**: {date} {start}–{end}
- **Location**: {addr}
- **Expected Wage**: {exp_wage}
""")
            if st.button("View Matching", key=f"view_find_{idx}"):
                st.experimental_set_query_params(page="result_matching", seeker_idx=idx)
                st.experimental_rerun()

st.markdown("---")
st.page_link("pages/home.py", label="🏠 Go to Homepage")
