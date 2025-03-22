import streamlit as st

st.set_page_config(layout="centered")

# Header & Navigation
st.markdown("""
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
    <div><strong>FAST LABOR</strong></div>
    <div>
        <a href="#" style="margin-right: 20px;">🏠</a>
        <a href="#" style="margin-right: 20px;">Find Job</a>
        <a href="#" style="margin-right: 20px;">My Job</a>
        <a href="#" style="background-color: black; color: white; padding: 5px 10px; border-radius: 4px;">Profile</a>
    </div>
</div>
""", unsafe_allow_html=True)

# Title
st.markdown("## Review Employer")
st.markdown("")

# Review Card UI
with st.container():
    st.markdown("""
    <div style="display: flex; justify-content: center;">
      <div style="border: 1px solid #ddd; border-radius: 12px; padding: 20px; width: 300px; text-align: center;">
        <div style="font-size: 22px; color: #999;">
            ☆☆☆☆☆
        </div>
        <h4 style="margin-top: 10px;">Review title</h4>
        <p style="color: #555;">Review body</p>
        <div style="display: flex; align-items: center; justify-content: center; margin-top: 15px;">
            <img src="https://randomuser.me/api/portraits/men/45.jpg" width="30" style="border-radius: 50%; margin-right: 10px;" />
            <div style="text-align: left;">
                <div style="font-weight: bold;">Reviewer name</div>
                <div style="font-size: 12px; color: gray;">Worker</div>
            </div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)
