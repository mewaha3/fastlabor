# pages/result_matching.py

import streamlit as st
import pandas as pd
import json
from oauth2client.service_account import ServiceAccountCredentials
import gspread

# —————————————————————————————————————————
# 0. โหลด matching results (top3) + seekers_df จาก Google Sheets
# —————————————————————————————————————————
# (สมมติคุณมีฟังก์ชัน run_matching() คืน (top3, seekers_df))
# ต่อไปนี้เป็นตัวอย่างการเชื่อมและดึงข้อมูลจาก GSheet แล้วคำนวณ matching

# 1) เชื่อม GSheet
creds = ServiceAccountCredentials.from_json_keyfile_dict(
    json.loads(st.secrets["gcp"]["credentials"]),
    ["https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive"]
)
gc = gspread.authorize(creds)
sh = gc.open("fastlabor")

# 2) โหลด raw sheets
def load_df(title):
    ws   = sh.worksheet(title)
    vals = ws.get_all_values()
    df   = pd.DataFrame(vals[1:], columns=vals[0])
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    return df

jobs_df    = load_df("post_job")
seekers_df = load_df("find_job")

# 3) สร้างคอลัมน์สำคัญสำหรับ matching (เฉพาะ job_type, datetime, location, wage)
#    -- (คุณอาจ reuse โค้ด matching ที่มีอยู่)
seekers_df["skills"] = seekers_df.get("job_detail", seekers_df.get("skills",""))
# ... (logic เตรียม datetime, wages ตามก่อนหน้า) ...

# 4) คำนวณ matching (ใช้ job_type_score, datetime_score, ฯลฯ ตามโค้ดก่อนหน้า)
#    สมมติผลลัพธ์ออกมาเป็น DataFrame top3 มีคอลัมน์ ['seek_idx', 'seeker_id','score']
#    และ seekers_df index เป็น range 0..N, มีคอลัมน์ gender & skills/job_type

# —————————————————————————————————————————
# UI: Header + Nav
# —————————————————————————————————————————
st.set_page_config(layout="centered")
st.markdown("### FAST LABOR")
st.markdown("""
<style>
.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30px;
}
.nav-right a {
    margin-left: 20px;
    text-decoration: none;
    font-weight: bold;
}
</style>
<div class="header">
    <div><strong>FAST LABOR</strong></div>
    <div class="nav-right">
        <a href="/?page=find_job">Find Job</a>
        <a href="/?page=list_job">My Job</a>
        <a href="/?page=profile" style="background: black; color: white; padding: 4px 10px; border-radius: 4px;">Profile</a>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("## Result matching")
st.markdown("List of employee who was matching with job")

# (ถ้ามีโลโก้)
# st.image("image.png", width=150)

st.markdown("---")

# —————————————————————————————————————————
# 5. สร้าง form แสดง top3 คนจาก matching
# —————————————————————————————————————————
updated_priorities = {}
for idx, row in top3.reset_index(drop=True).iterrows():
    seeker = seekers_df.loc[row.seek_idx]
    with st.expander(f"Employee No.{idx+1}"):
        # เพศ / ทักษะ
        st.write(f"เพศ: {seeker.gender}")
        st.write(f"ทักษะ: {seeker.job_type if 'job_type' in seeker else seeker.skills}")
        # Priority dropdown
        pr = st.selectbox(
            "Priority",
            options=[1,2,3,4,5],
            index=idx if idx<5 else 0,
            key=f"priority_{row.seeker_id}"
        )
        updated_priorities[row.seeker_id] = pr

# —————————————————————————————————————————
# 6. ปุ่ม Confirm และนำไปหน้า status_matching
# —————————————————————————————————————————
if st.button("Confirm"):
    # ถ้าต้องการบันทึกลง GSheet หรือ DB ก็ทำที่นี่
    # for sid, pr in updated_priorities.items():
    #     … บันทึก …
    st.success("Your matching priorities have been saved!")
    # สลับไปหน้า status_matching (multipage)
    st.experimental_set_query_params(page="status_matching")
    st.experimental_rerun()
