import streamlit as st
from utils.api import register_user
from utils.logger import setup_logger, log_user_action
import re

# Setup logger
logger = setup_logger("new_user")

# Page config
st.set_page_config(page_title="Register", layout="centered")

# Log page access
logger.info("New user registration page accessed")

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
job_roles = [
    "Academic Researcher",
    "Accountant",
    "AI/ML Engineer",
    "Aerospace Engineer",
    "Art Director",
    "Auditor",
    "Automotive Technician",
    "Biomedical Engineer",
    "Blockchain Developer",
    "Business Analyst",
    "Chef",
    "Chemical Engineer",
    "Civil Engineer",
    "Cloud Solutions Architect",
    "Content Writer",
    "Copywriter",
    "Customer Service Representative",
    "Cybersecurity Analyst",
    "Data Engineer",
    "Data Scientist",
    "Dentist",
    "DevOps Engineer",
    "Drone Operator",
    "E-commerce Manager",
    "Education Counselor",
    "Electrician",
    "Electrical Engineer",
    "Entrepreneur",
    "Environmental Engineer",
    "ESG Analyst",
    "Ethical Hacker",
    "Financial Analyst",
    "Flight Attendant",
    "Graphic Designer",
    "Government Officer",
    "Healthcare Administrator",
    "High School Science Teacher",
    "Hotel Manager",
    "Human Resources Manager",
    "HVAC Technician",
    "Instructional Designer",
    "Industrial Engineer",
    "Investment Banker",
    "IT Support Specialist",
    "Journalist",
    "Lawyer",
    "Lecturer",
    "Legal Advisor",
    "Marketing Manager",
    "Mechanical Engineer",
    "Medical Doctor",
    "Medical Laboratory Technician",
    "Nurse",
    "Operations Manager",
    "Paralegal",
    "Pharmacist",
    "Photographer",
    "Physiotherapist",
    "Plumber",
    "Police Inspector",
    "Product Manager",
    "Project Manager",
    "Psychologist",
    "Public Policy Analyst",
    "QA/Test Engineer",
    "Radiologist",
    "Registered Nurse",
    "Reporter",
    "Sales Executive",
    "Sales Manager",
    "School Teacher",
    "Social Media Manager",
    "Software Engineer",
    "Startup Founder",
    "Substance Abuse Counselor",
    "Supply Chain Analyst",
    "Surgeon",
    "Sustainability Consultant",
    "Travel Agent",
    "University Professor",
    "User Experience (UX) Designer",
    "UX/UI Designer",
    "Video Editor",
    "Virtual Reality Designer",
    "Welder"
]

# Form container
with st.container():
    # st.markdown('<div class="registration-box">', unsafe_allow_html=True)
    st.markdown('<div class="registration-title">🆕 Register New User</div>', unsafe_allow_html=True)

    # Form fields
    name = st.text_input("Full Name *")
    email = st.text_input("Email *")
    role = st.selectbox("Role *", job_roles)
    education = st.text_area("Education *", placeholder="e.g., B.Tech in Computer Science from XYZ University")
    skills = st.text_area("Skills *", placeholder="e.g., Python, Java, SQL, Communication")
    
    with st.expander("📁 Optional Info"):
        projects = st.text_area("Projects")
        achievements = st.text_area("Achievements")
        experience = st.text_area("Experience")

    submit = st.button("🚀 Register", use_container_width=True)

    if submit:
        try:
            logger.info(f"Registration attempt for email: {email.strip()}")
            log_user_action(logger, "Registration attempt", email.strip())
            
            # Enhanced validation
            validation_errors = []
            
            if not name.strip():
                validation_errors.append("Name is required")
            if not email.strip():
                validation_errors.append("Email is required")
            elif not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email.strip()):
                validation_errors.append("Please enter a valid email address")
            if not role:
                validation_errors.append("Role is required")
            if not skills.strip():
                validation_errors.append("Skills are required")
            if not education.strip():
                validation_errors.append("Education is required")
            
            if validation_errors:
                logger.warning(f"Registration validation failed for {email.strip()}: {', '.join(validation_errors)}")
                st.error(f"❌ Please fix the following errors:\n• " + "\n• ".join(validation_errors))
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
                
                logger.info(f"Submitting registration for email: {email.strip()}")
                res = register_user(payload)
                
                if res is None:
                    logger.error(f"Registration failed - no response from API for email: {email.strip()}")
                    st.error("❌ Unable to connect to the server. Please try again later.")
                elif res.ok:
                    logger.info(f"Registration successful for email: {email.strip()}")
                    log_user_action(logger, "Registration successful", email.strip(), role=role)
                    
                    # Store user data in session
                    st.session_state.update({
                        "email": email.strip(),
                        "logged_in": True,
                        "role": role,
                        "name": name.strip(),
                        "skills": [s.strip() for s in skills.split(",") if s.strip()],
                        "projects": [p.strip() for p in projects.split(",") if p.strip()] if projects else [],
                        "education": [e.strip() for e in education.split(",") if e.strip()],
                        "achievements": [a.strip() for a in achievements.split(",") if a.strip()] if achievements else [],
                        "experience": [ex.strip() for ex in experience.split(",") if ex.strip()] if experience else []
                    })
                    
                    st.success("✅ Registration successful! Redirecting...")
                    st.switch_page("pages/dashboard.py")
                else:
                    logger.error(f"Registration failed for email {email.strip()}: HTTP {res.status_code}")
                    try:
                        error_data = res.json()
                        error_msg = error_data.get("message", "Unknown error")
                        logger.error(f"Registration error details: {error_msg}")
                    except:
                        logger.error("Could not parse error response from registration API")
                    
                    st.error("❌ Registration failed. Please try again later.")
                    
        except Exception as e:
            logger.error(f"Unexpected error during registration for email {email.strip()}: {str(e)}")
            st.error("❌ An unexpected error occurred during registration. Please try again.")

    st.markdown("</div>", unsafe_allow_html=True)
