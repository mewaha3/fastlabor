import streamlit as st

# Mock user database (replace with actual database authentication)
USER_CREDENTIALS = {
    "user@example.com": "password123",
    "admin@fastlabor.com": "adminpass"
}

def main():
    st.set_page_config(page_title="Fast Labor Login", page_icon="🔧", layout="centered")

    st.image("image.png", width=150)  # Display logo (replace with actual image)
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
        st.markdown('<a href="#" style="color:red; font-size:12px;">Forget password?</a>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<p style="text-align:center;">or</p>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center;"><a href="#" style="font-size:16px; color:blue;">New Register</a></p>', unsafe_allow_html=True)

    # Authentication logic
    if login_button:
        if email in USER_CREDENTIALS and USER_CREDENTIALS[email] == password:
            st.success(f"Welcome, {email}!")
        else:
            st.error("Invalid email or password. Please try again.")

    # Footer
    st.markdown("---")
    st.markdown("### FAST LABOR")
    st.write("Follow us on:")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('[Facebook](#)')
    with col2:
        st.markdown('[Instagram](#)')
    with col3:
        st.markdown('[LinkedIn](#)')
    with col4:
        st.markdown('[YouTube](#)')

if __name__ == "__main__":
    main()
