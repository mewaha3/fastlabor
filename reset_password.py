import streamlit as st

st.set_page_config(page_title="Reset Password", page_icon="🔧", layout="centered")

st.image("image.png", width=150)
st.title("FAST LABOR")

st.markdown("## Reset Password")
email = st.text_input("Email", placeholder="xxxxx@gmail.com", disabled=True)
new_password = st.text_input("New Password", type="password")
confirm_password = st.text_input("Confirm Password", type="password")

if st.button("Reset"):
    if not new_password or not confirm_password:
        st.error("Please fill in all fields.")
    elif new_password != confirm_password:
        st.error("Passwords do not match.")
    elif len(new_password) < 6:
        st.error("Password must be at least 6 characters long.")
    else:
        st.success("Password reset successful! You can now log in.")

st.markdown("---")
st.markdown('[Go back to Login](http://localhost:8501)', unsafe_allow_html=True)
