import streamlit as st
import gspread
import json
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

# ✅ ตั้งค่า Google Sheets API
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

try:
    # ✅ โหลด Credentials จาก Streamlit Secrets (สำหรับ Cloud)
    if "gcp" in st.secrets:
        credentials_dict = json.loads(st.secrets["gcp"]["credentials"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
    else:
        # ✅ โหลด Credentials จากไฟล์ (สำหรับ Local)
        creds = ServiceAccountCredentials.from_json_keyfile_name("pages/credentials.json", scope)

    # ✅ เชื่อมต่อ Google Sheets
    client = gspread.authorize(creds)
    sheet = client.open("fastlabor").sheet1  

    # ✅ โหลดข้อมูลทั้งหมดจาก Google Sheets
    values = sheet.get_all_values()

    if not values or len(values) < 2:
        st.error("❌ ไม่พบข้อมูลใน Google Sheets (Sheet ว่าง)")
        st.stop()

    headers = [h.strip().lower() for h in values[0]]  # ✅ แปลง header เป็นพิมพ์เล็ก
    rows = values[1:]
    df = pd.DataFrame(rows, columns=headers)

    # ✅ Debug: แสดงชื่อคอลัมน์ทั้งหมด
    st.write("📌 Headers from Google Sheets:", headers)

    # ✅ ตรวจสอบว่ามีคอลัมน์ email และ password หรือไม่
    if "email" not in headers or "password" not in headers:
        st.error("❌ ไม่พบคอลัมน์ 'email' หรือ 'password' ใน Google Sheets")
        st.stop()

except Exception as e:
    st.error(f"❌ ไม่สามารถเชื่อมต่อกับ Google Sheets: {e}")
    st.stop()

# ✅ ตรวจสอบว่า Session State สำหรับล็อกอินมีหรือไม่
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "email" not in st.session_state:
    st.session_state["email"] = None

# ✅ ตั้งค่าหน้า Streamlit
st.set_page_config(page_title="Fast Labor Login", page_icon="🔧", layout="centered")

st.image("image.png", width=150)  # แสดงโลโก้
st.title("FAST LABOR")

st.markdown("### About")
st.write("""
**FAST LABOR - FAST JOB, FULL TRUST, GREAT WORKER**  
แพลตฟอร์มที่เชื่อมต่อคนทำงานและลูกค้าที่ต้องการแรงงานเร่งด่วน ไม่ว่าจะเป็นงานบ้าน งานสวน งานก่อสร้าง หรือจ้างแรงงานอื่น ๆ  
เราช่วยให้คุณหาคนทำงานได้อย่างรวดเร็วและง่ายดาย
""")

# ✅ ฟังก์ชันตรวจสอบการล็อกอิน
def check_login(email, password):
    email = email.strip().lower()  
    for index, row in df.iterrows():
        if row.get("email", "").strip().lower() == email and row.get("password", "").strip() == password:
            return True
    return False

# ✅ ถ้าผู้ใช้ล็อกอินแล้วให้แสดงหน้า Dashboard
if st.session_state["logged_in"]:
    st.success(f"✅ Logged in as {st.session_state['email']}")

    # ปุ่มไปหน้า Home
    st.page_link("pages/home.py", label="Go to Homepage", icon="🏠")

    # ปุ่ม Logout
    if st.button("Logout"):
        st.session_state["logged_in"] = False
        st.session_state["email"] = None
        st.experimental_rerun()

    st.stop()

# ✅ ฟอร์ม Login
st.markdown("## LOGIN")
email = st.text_input("Email address/Username", placeholder="email@example.com")
password = st.text_input("Password", type="password", placeholder="Enter your password")

col1, col2 = st.columns([1, 3])
with col1:
    login_button = st.button("Login")
with col2:
    st.page_link("pages/reset_password.py", label="Forget password?", icon="🔑")

st.markdown("---")
st.markdown('<p style="text-align:center;">or</p>', unsafe_allow_html=True)

st.page_link("pages/register.py", label="New Register", icon="📝")

# ✅ ตรวจสอบข้อมูลที่ผู้ใช้ป้อน
if login_button:
    if check_login(email, password):
        st.session_state["logged_in"] = True
        st.session_state["email"] = email  
        st.success(f"Welcome, {email}!")

        # ✅ เปลี่ยนไปหน้า Home
        st.switch_page("pages/home.py")
    else:
        st.error("❌ Invalid email or password. Please try again.")
