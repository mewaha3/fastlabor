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
        if not df_post.empty:
            st.dataframe(df_post, use_container_width=True)
        else:
            st.info("ยังไม่มีข้อมูลการโพสต์งาน")

    with tab2:
        st.subheader("🔍 รายการค้นหางาน")
        if not df_find.empty:
            st.dataframe(df_find, use_container_width=True)
        else:
            st.info("ยังไม่มีข้อมูลการค้นหางาน")

except Exception as e:
    st.error(f"❌ ไม่สามารถโหลดข้อมูลจาก Google Sheets: {e}")
