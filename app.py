import streamlit as st
import webbrowser

st.set_page_config(page_title="Fast Labor Login", page_icon="🔧", layout="centered")

st.image("image.png", width=150)  # Display logo (replace with actual image)
st.title("FAST LABOR")

st.markdown("## LOGIN")
email = st.text_input("Email address/Username", placeholder="email@example.com")
password = st.text_input("Password", type="password", placeholder="Enter your password")

col1, col2 = st.columns([1, 3])
with col1:
    login_button = st.button("Submit")
with col2:
    if st.button("Forget password?", help="Click to reset password"):
        webbrowser.open("http://localhost:8502")  # Open Reset Password page

st.markdown("---")
st.markdown('<p style="text-align:center;">or</p>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center;"><a href="#" style="font-size:16px; color:blue;">New Register</a></p>', unsafe_allow_html=True)

if login_button:
    st.error("Invalid login. Try again or reset password.")  # Mock authentication failure
