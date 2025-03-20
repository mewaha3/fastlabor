import streamlit as st

st.set_page_config(page_title="Reset Password", page_icon="🔑", layout="centered")

st.image("image.png", width=150)  # Display logo
st.title("Reset Password")

st.markdown("Please enter a new password for your account.")

# Mock email field (Ideally, this should be pre-filled based on the user session)
email = st.text_input("Email", "xxxxx@gmail.com", disabled=True)

# Password fields
new_password = st.text_input("New Password", type="password")
confirm_password = st.text_input("Confirm Password", type="password")

# Submit button
if st.button("Reset"):
    if new_password and confirm_password:
        if new_password == confirm_password:
            st.success("Your password has been successfully reset. Please log in again.")
        else:
            st.error("Passwords do not match. Please try again.")
    else:
        st.error("Please fill in all fields.")

# ✅ Add a back button to return to login
st.page_link("app.py", label="Back to Login", icon="⬅️")
