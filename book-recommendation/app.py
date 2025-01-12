import streamlit as st
from auth import login_page, registration_page
from main_app import main_app


st.set_page_config(page_title="Book Recommendation System", layout="wide")
st.title("📚 Book Recommendation System")

# Main Logic
if "user_id" not in st.session_state or not st.session_state["user_id"]:
    action = st.sidebar.radio("Choose a page", ["Login", "Register"])
    if action == "Register":
        registration_page()
    else:
        login_page()
else:
    main_app()

