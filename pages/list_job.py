import streamlit as st
import gspread
import json
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(page_title="Job Detail", page_icon="📄", layout="wide")
st.title("📄 Job Detail")
st.write("ดูข้อมูลจากการโพสต์งานและการค้นหางาน")

# ✅ Auth Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
try:
    if "gcp" in st.secrets:
        credentials_dict = json.loads(st.secrets["gcp"]["credentials"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
    else:
        creds = ServiceAccountCredentials.from_json_keyfile_name("pages/credentials.json", scope)

    client = gspread.authorize(creds)
    spreadsheet = client.open("fastlabor")

    # ✅ Load data from both sheets
    def load_sheet(sheet_name):
        try:
            worksheet = spreadsheet.worksheet(sheet_name)
            data = worksheet.get_all_records()
            return pd.DataFrame(data)
        except Exception as e:
            st.warning(f"⚠️ ไม่พบชีท {sheet_name}: {e}")
            return pd.DataFrame()

    df_post = load_sheet("post_job")
    df_find = load_sheet("find_job")

    # ✅ Tabs: Post Job / Find Job
    tab1, tab2 = st.tabs(["📌 Post Job", "🔍 Find Job"])

    with tab1:
        st.subheader("📌 รายการโพสต์งาน")
        if df_post.empty:
            st.info("ยังไม่มีข้อมูลการโพสต์งาน")
        else:
            # Loop แสดงแต่ละงาน พร้อมปุ่ม View Matching
            for idx, row in df_post.iterrows():
                st.markdown("---")
                st.markdown(f"**Job #{idx+1}**")
                cols = st.columns([4,1])
                with cols[0]:
                    st.write(f"- **Email:** {row['email']}")
                    st.write(f"- **Job Type:** {row.get('job_type','')}")
                    st.write(f"- **Detail:** {row.get('job_detail', '')}")
                    st.write(f"- **Date:** {row.get('job_date','')} {row.get('start_time','')}-{row.get('end_time','')}")
                    st.write(f"- **Location:** {row.get('province','')}/{row.get('district','')}/{row.get('subdistrict','')}")
                    st.write(f"- **Salary:** {row.get('start_salary','')}–{row.get('range_salary','')}")
                with cols[1]:
                    if st.button("View Matching", key=f"view_{idx}"):
                        # ส่งพารามิเตอร์ job_idx ไปยังหน้า result_matching
                        st.experimental_set_query_params(page="result_matching", job_idx=idx)
                        st.experimental_rerun()

    with tab2:
        st.subheader("🔍 รายการค้นหางาน")
        if df_find.empty:
            st.info("ยังไม่มีข้อมูลการค้นหางาน")
        else:
            st.dataframe(df_find, use_container_width=True)

except Exception as e:
    st.error(f"❌ ไม่สามารถโหลดข้อมูลจาก Google Sheets: {e}")

# ลิงก์กลับหน้า Home
st.markdown("---")
st.page_link("pages/home.py", label="Go to Homepage", icon="🏠")
