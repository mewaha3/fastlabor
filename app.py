import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

# ✅ ตั้งค่า Google Sheets API
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("pages/credentials.json", scope)
client = gspread.authorize(creds)

# ✅ เปิด Google Sheet
sheet = client.open("fastlabor").sheet1  # เปลี่ยนเป็นชื่อ Google Sheet ของคุณ

# ✅ โหลดข้อมูลทั้งหมดจาก Google Sheet
data = sheet.get_all_records()
df = pd.DataFrame(data)

# ✅ ตรวจสอบว่ามี session_state สำหรับ login หรือไม่
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
    for index, row in df.iterrows():
        if row["email"] == email and row["password"] == password:
            return True
    return False

# ✅ แสดงหน้า Dashboard ถ้าล็อกอินแล้ว
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
    login_button = st.button("Submit")
with col2:
    st.page_link("pages/reset_password.py", label="Forget password?", icon="🔑")

st.markdown("---")
st.markdown('<p style="text-align:center;">or</p>', unsafe_allow_html=True)

st.page_link("pages/register.py", label="New Register", icon="📝")

# ✅ ตรวจสอบข้อมูลที่ผู้ใช้ป้อน
if login_button:
    if check_login(email, password):
        st.session_state["logged_in"] = True
        st.session_state["email"] = email  # ✅ บันทึก email ที่ล็อกอินสำเร็จ
        st.success(f"Welcome, {email}!")

        # ✅ เปลี่ยนไปหน้า Home
        st.switch_page("pages/home.py")
    else:
        st.error("❌ Invalid email or password. Please try again.")
