# pages/list_job.py

import streamlit as st
import pandas as pd
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(page_title="My Jobs | FAST LABOR", layout="wide")
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
def load_df(name: str) -> pd.DataFrame:
    ws   = sh.worksheet(name)
    vals = ws.get_all_values()
    df   = pd.DataFrame(vals[1:], columns=vals[0])
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    return df

df_post = load_df("post_job")
df_find = load_df("find_job")

tab1, tab2 = st.tabs(["📌 Post Job", "🔍 Find Job"])

def render_card(title, fields: dict, button_key, page_param, idx):
    """Helper: render a bordered “card” with fields dict and a button."""
    st.markdown(
        "<div style='border:1px solid #ddd; border-radius:8px; padding:16px; margin-bottom:16px;'>",
        unsafe_allow_html=True
    )
    st.markdown(f"#### {title}")
    cols = st.columns([3,1])
    with cols[0]:
        for label, val in fields.items():
            st.markdown(f"**{label}:**  {val}")
    with cols[1]:
        if st.button("View Matching", key=button_key):
            st.experimental_set_query_params(**{page_param: idx})
            st.experimental_rerun()
    st.markdown("</div>", unsafe_allow_html=True)

with tab1:
    st.subheader("📌 รายการโพสต์งาน")
    if df_post.empty:
        st.info("ยังไม่มีข้อมูลโพสต์งาน")
    else:
        for i, row in df_post.iterrows():
            # prepare data
            addr = row.get("job_address") or f"{row['province']}/{row['district']}/{row['subdistrict']}"
            min_s, max_s = row.get("start_salary") or "-", row.get("range_salary") or "-"
            salary = f"{min_s} – {max_s}" if min_s!="-” or max_s!="-” else row.get("salary","–")
            fields = {
                "Email": row["email"],
                "Job Type": row["job_type"],
                "Detail": row.get("skills", row.get("job_detail","–")),
                "Date": row["job_date"],
                "Time": f"{row['start_time']} – {row['end_time']}",
                "Location": addr,
                "Salary": salary
            }
            render_card(f"Job #{i+1}", fields, f"view_post_{i}", "job_idx", i)

with tab2:
    st.subheader("🔍 รายการค้นหางาน")
    if df_find.empty:
        st.info("ยังไม่มีข้อมูลค้นหางาน")
    else:
        for i, row in df_find.iterrows():
            addr = f"{row['province']}/{row['district']}/{row['subdistrict']}"
            fields = {
                "Email": row["email"],
                "Skill": row.get("skills", row.get("job_detail","–")),
                "Date": row["job_date"],
                "Time": f"{row['start_time']} – {row['end_time']}",
                "Location": addr,
                "Start Salary": row.get("start_salary","–"),
                "Range Salary": row.get("range_salary","–")
            }
            render_card(f"Find #{i+1}", fields, f"view_find_{i}", "seeker_idx", i)

st.markdown("---")
st.markdown("[🏠 Go to Homepage](?page=home)")
