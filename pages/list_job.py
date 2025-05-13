# pages/list_job.py

import streamlit as st
import pandas as pd
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials

# --- Page config ---
st.set_page_config(page_title="My Jobs | FAST LABOR", layout="wide")

# --- CSS for card style ---
st.markdown("""
<style>
.card {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
  box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
}
.card h4 {
  margin: 0 0 8px 0;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center'>📄 My Jobs</h1>", unsafe_allow_html=True)

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

# --- Loader ---
def load_df(sheet_name: str) -> pd.DataFrame:
    ws   = sh.worksheet(sheet_name)
    vals = ws.get_all_values()
    header, data = vals[0], vals[1:]
    df = pd.DataFrame(data, columns=header)
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    return df

df_post = load_df("post_job")
df_find = load_df("find_job")

# --- Normalize salary columns ---
for df in (df_post, df_find):
    for col in ("start_salary", "range_salary"):
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().replace({"": None})

# --- Tabs ---
tab1, tab2 = st.tabs(["📌 Post Job", "🔍 Find Job"])

with tab1:
    st.subheader("📌 รายการโพสต์งาน")
    if df_post.empty:
        st.info("ยังไม่มีข้อมูลโพสต์งาน")
    else:
        for idx, row in df_post.iterrows():
            # Card container
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown(f"<h4>Job #{idx+1}</h4>", unsafe_allow_html=True)
            # Two-column layout
            colL, colR = st.columns([4,1])
            with colL:
                st.markdown(f"""
**Email:** {row['email']}  
**Job Type:** {row['job_type']}  
**Detail:** {row.get('skills', row.get('job_detail','–'))}  
**Date:** {row['job_date']}  
**Time:** {row['start_time']} – {row['end_time']}  
**Location:** {row.get('job_address') or f"{row['province']}/{row['district']}/{row['subdistrict']}"}  
""")
                # Salary
                min_sal = row.get("start_salary")
                max_sal = row.get("range_salary")
                if min_sal or max_sal:
                    sal = f"{min_sal or '-'} – {max_sal or '-'}"
                else:
                    sal = row.get("salary","–")
                st.markdown(f"**Salary:** {sal}")
            with colR:
                if st.button("View Matching", key=f"view_post_{idx}", use_container_width=True):
                    st.experimental_set_query_params(page="result_matching", job_idx=idx)
                    st.experimental_rerun()
            st.markdown("</div>", unsafe_allow_html=True)

with tab2:
    st.subheader("🔍 รายการค้นหางาน")
    if df_find.empty:
        st.info("ยังไม่มีข้อมูลค้นหางาน")
    else:
        for idx, row in df_find.iterrows():
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown(f"<h4>Find #{idx+1}</h4>", unsafe_allow_html=True)
            colL, colR = st.columns([4,1])
            with colL:
                st.markdown(f"""
**Email:** {row['email']}  
**Skill:** {row.get('skills', row.get('job_detail','–'))}  
**Date:** {row['job_date']}  
**Time:** {row['start_time']} – {row['end_time']}  
**Location:** {row['province']}/{row['district']}/{row['subdistrict']}  
""")
                # Start & Range Salary
                min_sal = row.get("start_salary") or "-"
                max_sal = row.get("range_salary") or "-"
                st.markdown(f"**Start Salary:** {min_sal}  \n**Range Salary:** {max_sal}")
            with colR:
                if st.button("View Matching", key=f"view_find_{idx}", use_container_width=True):
                    st.experimental_set_query_params(page="result_matching", seeker_idx=idx)
                    st.experimental_rerun()
            st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")
st.page_link("pages/home.py", label="🏠 Go to Homepage")
