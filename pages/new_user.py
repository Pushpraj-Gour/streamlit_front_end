import streamlit as st
from utils.api import register_user

# Page config
st.set_page_config(page_title="Register", layout="centered")

# Custom CSS for compact and modern form
st.markdown("""
<style>
    .registration-box {
        background-color: #1e1e1e;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.4);
        max-width: 600px;
        margin: auto;
    }
    .registration-title {
        text-align: center;
        font-size: 1.5rem;
        margin-bottom: 1rem;
    }
    .stTextInput > div > input,
    .stTextArea > div > textarea,
    .stSelectbox > div {
        background-color: #2c2c2c;
        color: #fff;
        border: 1px solid #444;
        border-radius: 6px;
    }
</style>
""", unsafe_allow_html=True)

# Form container
with st.container():
    # st.markdown('<div class="registration-box">', unsafe_allow_html=True)
    st.markdown('<div class="registration-title">🆕 Register New User</div>', unsafe_allow_html=True)

    # Form fields
    name = st.text_input("Full Name *")
    email = st.text_input("Email *")
    role = st.selectbox("Role *", ["Software Engineer", "Data Scientist", "Product Manager"])
    education = st.text_area("Education *", placeholder="e.g., B.Tech in Computer Science from XYZ University")
    skills = st.text_area("Skills *", placeholder="e.g., Python, Java, SQL, Communication")
    
    with st.expander("📁 Optional Info"):
        projects = st.text_area("Projects")
        achievements = st.text_area("Achievements")
        experience = st.text_area("Experience")

    submit = st.button("🚀 Register", use_container_width=True)

    if submit:
        # Validation
        if not name.strip() or not email.strip() or not role or not skills.strip() or not education.strip():
            st.error("❌ Please fill in all required fields: Name, Email, Role, Skills, Education.")
        else:
            payload = {
                "candidate_name": name.strip(),
                "candidate_email": email.strip(),
                "role": role,
                "skills": skills.strip(),
                "education": education.strip(),
                "projects": projects.strip() if projects else None,
                "achievements": achievements.strip() if achievements else None,
                "experience": experience.strip() if experience else None
            }
            res = register_user(payload)
            if res.ok:
                st.success("✅ Registration successful! Redirecting...")
                st.session_state.email = email
                st.session_state.logged_in = True
                st.session_state.role = role
                st.session_state.name = name
                st.session_state.skills = skills.split(",") if skills else []
                st.session_state.projects = projects.split(",") if projects else []
                st.session_state.education = education.split(",") if education else []
                st.session_state.achievements = achievements.split(",") if achievements else []
                st.session_state.experience = experience.split(",") if experience else []
                
                st.switch_page("pages/dashboard.py")
            else:
                st.error("❌ Registration failed. Please try again later.")

    st.markdown("</div>", unsafe_allow_html=True)
