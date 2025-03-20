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
    sheet = client.open("fastlabor").sheet1  # เปลี่ยนเป็นชื่อ Google Sheets ของคุณ

    # ✅ โหลดข้อมูลทั้งหมดจาก Google Sheets
    data = sheet.get_all_records()
    df = pd.DataFrame(data)

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

# ✅ เพิ่ม Custom CSS เพื่อทำให้ UI สวยขึ้น
st.markdown("""
    <style>
        .login-container {
            max-width: 400px;
            margin: auto;
            padding: 2rem;
            background: white;
            border-radius: 10px;
            box-shadow: 0 0 15px rgba(0, 0, 0, 0.2);
            text-align: center;
        }
        .stTextInput, .stButton {
            margin-bottom: 15px;
        }
        .login-title {
            font-size: 26px;
            font-weight: bold;
            color: #4F8BF9;
        }
        .login-subtitle {
            font-size: 16px;
            color: #6c757d;
        }
        .login-btn {
            background-color: #4F8BF9 !important;
            color: white !important;
            width: 100%;
            border-radius: 8px;
            padding: 10px;
            font-size: 16px;
        }
        .login-btn:hover {
            background-color: #357ABD !important;
        }
        .login-footer {
            font-size: 14px;
            color: #6c757d;
            margin-top: 15px;
        }
    </style>
""", unsafe_allow_html=True)

# ✅ LOGO & TITLE
st.image("image.png", width=150)  # แสดงโลโก้
st.markdown('<div class="login-title">FAST LABOR</div>', unsafe_allow_html=True)
st.markdown('<div class="login-subtitle">FAST JOB, FULL TRUST, GREAT WORKER</div>', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# ✅ กล่อง Login แบบสวยงาม
with st.container():
    st.markdown('<div class="login-container">', unsafe_allow_html=True)

    # ✅ ฟอร์ม Login
    email = st.text_input("Email address/Username", placeholder="email@example.com")
    password = st.text_input("Password", type="password", placeholder="Enter your password")

    # ✅ ปุ่ม Login
    if st.button("Login", key="login_btn", help="Click to login", use_container_width=True):
        if email and password:
            if email in df["email"].values and df[df["email"] == email]["password"].values[0] == password:
                st.session_state["logged_in"] = True
                st.session_state["email"] = email
                st.success(f"✅ Welcome, {email}!")

                # ✅ เปลี่ยนไปหน้า Home
                st.switch_page("pages/home.py")
            else:
                st.error("❌ Invalid email or password. Please try again.")
        else:
            st.warning("⚠️ กรุณากรอกข้อมูลให้ครบ")

    # ✅ ลิงก์ไปยัง Forget Password
    st.page_link("pages/reset_password.py", label="🔑 Forget password?", icon="🔑")

    st.markdown('<div class="login-footer">or</div>', unsafe_allow_html=True)

    # ✅ ปุ่ม Register
    st.page_link("pages/register.py", label="📝 New Register", icon="📝")

    st.markdown('</div>', unsafe_allow_html=True)
