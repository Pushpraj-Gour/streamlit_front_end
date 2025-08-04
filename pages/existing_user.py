import streamlit as st
from utils.api import login_user
from utils.logger import setup_logger, log_user_action

# Setup logger
logger = setup_logger("existing_user")

# Page setup
st.set_page_config(
    page_title="Existing User Login",
    page_icon="🔐",
    layout="centered"
)

# Log page access
logger.info("Existing user login page accessed")

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
        logger.warning("Login attempt with empty email")
        st.warning("Please enter a valid email address.")
    else:
        try:
            logger.info(f"Login attempt for email: {email}")
            log_user_action(logger, "Login attempt", email)
            
            response = login_user(email)

            if response is None:
                logger.warning(f"Login failed - no response from API for email: {email}")
                st.error("❌ Unable to connect to the server. Please try again later.")
            elif not isinstance(response, dict):
                logger.error(f"Login failed - invalid response format for email: {email}")
                st.error("❌ Received invalid response from server.")
            elif response.get("status"):
                data = response.get("data", {})
                
                # Validate required data fields
                if not data.get("name"):
                    logger.warning(f"Login successful but missing name data for email: {email}")
                
                st.session_state.update({
                    "email": email,
                    "logged_in": True,
                    "role": data.get("role", ""),
                    "name": data.get("name", "User"),
                    "skills": data.get("skills", []),
                    "projects": data.get("projects", []),
                    "education": data.get("education", []),
                    "achievements": data.get("achievements", []),
                    "experience": data.get("experience", [])
                })

                logger.info(f"Login successful for email: {email}")
                log_user_action(logger, "Login successful", email, role=data.get("role", ""))
                
                st.success("✅ Logged in successfully. Redirecting...")
                st.switch_page("pages/dashboard.py")
            else:
                logger.info(f"Login failed - user not found for email: {email}")
                log_user_action(logger, "Login failed - user not found", email)
                st.error("❌ User not found. Redirecting to registration...")
                st.switch_page("pages/new_user.py")
                
        except Exception as e:
            logger.error(f"Unexpected error during login for email {email}: {str(e)}")
            st.error("❌ An unexpected error occurred. Please try again later.")
            # Optionally provide a way to retry or go to registration
