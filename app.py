import streamlit as st

def main():
    st.set_page_config(page_title="Fast Labor Login", page_icon="🔧", layout="centered")

    st.image("image.png", width=150)  # Display logo
    st.title("FAST LABOR")

    st.markdown("### About")
    st.write("""
    **FAST LABOR - FAST JOB, FULL TRUST, GREAT WORKER**  
    แพลตฟอร์มที่เชื่อมต่อคนทำงานและลูกค้าที่ต้องการแรงงานเร่งด่วน ไม่ว่าจะเป็นงานบ้าน งานสวน งานก่อสร้าง หรือจ้างแรงงานอื่น ๆ  
    เราช่วยให้คุณหาคนทำงานได้อย่างรวดเร็วและง่ายดาย
    """)

    # Login Form
    st.markdown("## LOGIN")
    email = st.text_input("Email address/Username", placeholder="email@example.com")
    password = st.text_input("Password", type="password", placeholder="Enter your password")

    col1, col2 = st.columns([1, 3])
    with col1:
        login_button = st.button("Submit")
    with col2:
        # ✅ Link to Reset Password Page
        st.page_link("pages/reset_password.py", label="Forget password?", icon="🔑")

    st.markdown("---")
    st.markdown('<p style="text-align:center;">or</p>', unsafe_allow_html=True)

    # ✅ Link to Register Page
    st.page_link("pages/register.py", label="New Register", icon="📝")

    # Authentication logic (Mock database)
    USER_CREDENTIALS = {
        "user@example.com": "password123",
        "admin@fastlabor.com": "adminpass"
    }

    if login_button:
        if email in USER_CREDENTIALS and USER_CREDENTIALS[email] == password:
            st.success(f"Welcome, {email}!")
        else:
            st.error("Invalid email or password. Please try again.")

if __name__ == "__main__":
    main()
