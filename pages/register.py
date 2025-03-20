import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Connect to Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open("FastLaborUsers").sheet1  # Replace with your Google Sheet name

st.set_page_config(page_title="New Member Registration", page_icon="📝", layout="centered")

st.image("image.png", width=150)  # Display logo
st.title("New Member")

with st.form(key="register_form"):
    first_name = st.text_input("First name *")
    last_name = st.text_input("Last name *")
    email = st.text_input("Email address *")
    password = st.text_input("Password *", type="password")
    submit_button = st.form_submit_button("Submit")

if submit_button:
    if first_name and last_name and email and password:
        sheet.append_row([first_name, last_name, email, password])
        st.success(f"Welcome, {first_name}! You have successfully registered.")
    else:
        st.error("Please fill in all required fields.")

st.page_link("app.py", label="Back to Login", icon="⬅️")
