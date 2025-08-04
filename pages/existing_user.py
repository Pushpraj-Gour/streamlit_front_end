import streamlit as st
from utils.api import login_user

# Page setup
st.set_page_config(
    page_title="Existing User Login",
    page_icon="🔐",
    layout="centered"
)

# Custom CSS
st.markdown("""
<style>
    /* Hide Streamlit branding */
    #MainMenu, header, footer {visibility: hidden;}

    .login-container {
        background: linear-gradient(135deg, #667eea, #764ba2);
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        color: white;
        max-width: 500px;
        margin: 2rem auto;
        text-align: center;
    }

    .login-title {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 1rem;
    }

    .login-subtitle {
        font-size: 1rem;
        font-weight: 300;
        margin-bottom: 2rem;
        color: rgba(255,255,255,0.85);
    }

    .stTextInput > div > input {
        background-color: white !important;
        color: black !important;
        border-radius: 10px;
    }

    .stButton > button {
        background: linear-gradient(135deg, #ff6b6b, #ee5a24);
        color: white;
        border: none;
        border-radius: 30px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 6px 20px rgba(255,107,107,0.3);
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(255,107,107,0.5);
    }

</style>
""", unsafe_allow_html=True)

# Login form container
st.markdown("""
<div class="login-container">
    <div class="login-title">🔐 Existing User Login</div>
    <div class="login-subtitle">Enter your email to continue your interview journey</div>
</div>
""", unsafe_allow_html=True)

# Spacer and centered layout
st.write("")  # spacer

with st.form("login_form", clear_on_submit=False):
    email = st.text_input("Email Address", placeholder="you@example.com")
    submitted = st.form_submit_button("Continue")

if submitted:
    if not email.strip():
        st.warning("Please enter a valid email address.")
    else:
        response = login_user(email)

        if response.get("status"):
            data = response.get("data", {})

            st.session_state.update({
                "email": email,
                "logged_in": True,
                "role": data.get("role", ""),
                "name": data.get("name", ""),
                "skills": data.get("skills", []),
                "projects": data.get("projects", []),
                "education": data.get("education", []),
                "achievements": data.get("achievements", []),
                "experience": data.get("experience", [])
            })

            st.success("✅ Logged in successfully. Redirecting...")
            # st.rerun()  # Optional if switch_page handles this

            st.switch_page("pages/dashboard.py")
        else:
            st.error("❌ User not found. Redirecting to registration...")
            st.switch_page("pages/new_user.py")
