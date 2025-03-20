import streamlit as st

def registration_form():
    st.set_page_config(page_title="New Member Registration", page_icon="📝", layout="centered")

    st.image("image.png", width=150)  # Display logo
    st.title("New Member")

    # Registration Form
    with st.form(key="register_form"):
        first_name = st.text_input("First name *")
        last_name = st.text_input("Last name *")
        dob = st.date_input("Date of Birth *")
        gender = st.selectbox("Gender *", ["Male", "Female", "Other"])
        nationality = st.text_input("National *")
        member_type = st.selectbox("Member Type *", ["Employer", "Worker"])
        address = st.text_area("Address (House Number, Road, Soi.)")
        province = st.selectbox("Province *", ["Select"] + ["Option1", "Option2"])  # Replace with actual options
        district = st.selectbox("District *", ["Select"] + ["Option1", "Option2"])  # Replace with actual options
        subdistrict = st.selectbox("Subdistrict *", ["Select"] + ["Option1", "Option2"])  # Replace with actual options
        zip_code = st.selectbox("Zip Code *", ["Select"] + ["Option1", "Option2"])  # Replace with actual options
        email = st.text_input("Email address *")
        password = st.text_input("Password *", type="password")
        
        submit_button = st.form_submit_button("Submit")

    if submit_button:
        # Add functionality to save the data (e.g., to a database)
        st.success(f"Welcome, {first_name} {last_name}! You have successfully registered.")

if __name__ == "__main__":
    registration_form()
