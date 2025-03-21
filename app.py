import streamlit as st

# Set page config (must be the first Streamlit command)
st.set_page_config(page_title="FAST LABOR", page_icon="⚙️", layout="centered")

# Custom CSS to match the design
st.markdown("""
<style>
    .title-text {
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 0;
    }
    .subtitle-text {
        font-size: 14px;
        color: #333;
        margin-top: 0;
    }
    .description-text {
        font-size: 12px;
        color: #555;
        margin-bottom: 20px;
    }
    .login-container {
        max-width: 400px;
        margin: 0 auto;
    }
    .login-header {
        text-align: center;
        font-weight: bold;
        margin: 20px 0;
    }
    .login-form {
        background-color: white;
        padding: 10px;
        border-radius: 5px;
    }
    .stButton>button {
        background-color: black;
        color: white;
        width: 100%;
        height: 40px;
        border-radius: 3px;
    }
    .centered-text {
        text-align: center;
    }
    .forgot-password {
        text-align: right;
        font-size: 12px;
        color: #ff0000;
    }
    .divider {
        margin: 15px 0;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Center the logo and title
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("https://raw.githubusercontent.com/username/fastlabor/main/image.png", width=100)  # Replace with your actual image path

# Title and description
st.markdown('<p class="title-text">About</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle-text">FAST LABOR - FAST JOB, FULL TRUST, GREAT WORKER</p>', unsafe_allow_html=True)
st.markdown('<p class="description-text">แพลตฟอร์มที่เชื่อมต่อคนทำงานและลูกค้าที่ต้องการแรงงานเร่งด่วน ไม่ว่าจะเป็นงานบ้าน งานสวน งานก่อสร้าง หรือจ้างแรงงานอื่น ๆ เราช่วยให้คุณหาคนทำงานได้อย่างรวดเร็วและง่ายดาย</p>', unsafe_allow_html=True)

# Login section
st.markdown('<div class="login-header">LOGIN</div>', unsafe_allow_html=True)

# Login form
with st.form("login_form"):
    # Email/Username field
    st.markdown('<label>Email address/Username</label>', unsafe_allow_html=True)
    email = st.text_input("", placeholder="example@fastlabor.com", label_visibility="collapsed")
    
    # Password field
    st.markdown('<label>Password</label>', unsafe_allow_html=True)
    password = st.text_input("", type="password", placeholder="••••••••••••••••", label_visibility="collapsed")
    
    # Forgot password link
    st.markdown('<div class="forgot-password"><a href="#">Forgot password?</a></div>', unsafe_allow_html=True)
    
    # Submit button
    submit_button = st.form_submit_button("Submit")

# Divider
st.markdown('<div class="divider">or</div>', unsafe_allow_html=True)

# New Register link
st.markdown('<div class="centered-text"><a href="#">New Register</a></div>', unsafe_allow_html=True)

# Handle form submission
if submit_button:
    # Replace with your actual authentication logic
    st.success("Login attempt with: " + email)
    # For demonstration purposes only
    # In a real app, you would check credentials against a database
