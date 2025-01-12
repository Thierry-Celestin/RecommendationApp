import streamlit as st
from mongodb.users import add_user, get_user_by_email, verify_password


# Registration Page
def registration_page():
    st.header("User Registration")
    with st.form("user_registration_form"):
        name = st.text_input("Full Name")
        email = st.text_input("Email Address")
        password = st.text_input("Password", type="password")
        favorite_genres = st.multiselect(
            "Favorite Genres",
            ["Fiction",
    "Non-Fiction",
    "Mystery",
    "Science Fiction",
    "Romance",
    "Fantasy",
    "Historical",
    "Biography"]
        )
        submit = st.form_submit_button("Register")
        if submit:
            user_id = add_user(name, email, password, favorite_genres)
            if user_id:
                st.success(f"User {name} registered successfully! ID: {user_id}")
            else:
                st.warning(f"Registration failed. The email {email} may already be in use.")

# Login Page
def login_page():
    st.header("User Login")
    with st.form("login_form"):
        email = st.text_input("Email Address")
        password = st.text_input("Password", type="password")
        login = st.form_submit_button("Login")
        if login:
            if verify_password(email, password):
                user = get_user_by_email(email)
                st.session_state["user_id"] = str(user["_id"])
                st.session_state["user_email"] = email
                st.success(f"Login successful! Welcome back, {user['name']}.")
                st.rerun()  # Redirect to the main app
            else:
                st.warning("Invalid email or password.")
