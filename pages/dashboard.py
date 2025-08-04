import json
import streamlit as st
from datetime import datetime
from utils.api import get_candidate_interviews
from utils.logger import setup_logger, log_user_action

# Setup logger
logger = setup_logger("dashboard")

# Config
st.set_page_config(page_title="Dashboard", layout="wide")

# Authentication check
if not st.session_state.get("logged_in"):
    logger.warning("Unauthorized access attempt to dashboard")
    st.warning("Please log in first.")
    st.stop()

# Session data
email = st.session_state.get("email")
name = st.session_state.get("name")
role = st.session_state.get("role")
skills = st.session_state.get("skills", [])
projects = st.session_state.get("projects", [])
education = st.session_state.get("education", [])
achievements = st.session_state.get("achievements", [])
experience = st.session_state.get("experience", [])

# Log user access
log_user_action(logger, "Dashboard accessed", email, role=role)

# Custom CSS
st.markdown("""
<style>
    .inline-list {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        padding: 0;
        list-style: none;
        margin: 0;
    }
    .inline-list li {
        background-color: #333;
        padding: 4px 10px;
        border-radius: 4px;
        font-size: 0.85rem;
        color: #fff;
    }
    .expander > summary {
        font-weight: 600;
        font-size: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown(f"### 👋 Welcome, **{name}**")
st.markdown(f"**Email:** {email} &nbsp;&nbsp;&nbsp;&nbsp; **Role:** {role}")
st.markdown("---")


# Helper: Normal section with optional list
def section(title, content):
    """Display content section with proper error handling."""
    try:
        if not content or (isinstance(content, list) and all(not str(i).strip() for i in content)):
            logger.debug(f"Skipping empty section: {title}")
            return
        
        with st.expander(f"{title}", expanded=True):
            if isinstance(content, list):
                for item in content:
                    if str(item).strip():
                        st.markdown(f"- {item}")
            else:
                st.markdown(content)
        
        logger.debug(f"Successfully displayed section: {title}")
    except Exception as e:
        logger.error(f"Error displaying section {title}: {str(e)}")
        st.error(f"Error displaying {title} section")


# Helper: Inline badge-like layout
def inline_section(title, items):
    """Display inline section with proper error handling."""
    try:
        if not items or not any(str(i).strip() for i in items):
            logger.debug(f"Skipping empty inline section: {title}")
            return
        
        with st.expander(f"{title}", expanded=True):
            st.markdown('<ul class="inline-list">', unsafe_allow_html=True)
            for item in items:
                if str(item).strip():
                    st.markdown(f'<li>{item}</li>', unsafe_allow_html=True)
            st.markdown('</ul>', unsafe_allow_html=True)
        
        logger.debug(f"Successfully displayed inline section: {title}")
    except Exception as e:
        logger.error(f"Error displaying inline section {title}: {str(e)}")
        st.error(f"Error displaying {title} section")


# Display sections with error handling
try:
    logger.info(f"Displaying profile sections for user: {email}")
    section("🎓 Education", education)
    section("🛠 Skills", skills)
    section("📁 Projects", projects)
    section("🏆 Achievements", achievements)
    section("💼 Experience", experience)
except Exception as e:
    logger.error(f"Error displaying profile sections: {str(e)}")
    st.error("Error loading profile information")

# CTA
st.markdown("---")
st.markdown("#### Ready for your next challenge?")

try:
    # Log navigation action when user clicks
    if st.button("Start New Interview", key="start_interview_btn"):
        log_user_action(logger, "Start Interview button clicked", email)
        st.switch_page("pages/interview.py")
except Exception as e:
    logger.error(f"Error with interview navigation: {str(e)}")
    st.error("Error loading interview page")

st.subheader("🗂️ Previous Interviews")

# Fetch and display previous interviews with comprehensive error handling
try:
    logger.info(f"Fetching interview history for user: {email}")
    response = get_candidate_interviews(email)
    
    if response is None:
        logger.warning(f"No response received from API for user: {email}")
        st.warning("Unable to connect to the server. Please try again later.")
    elif not isinstance(response, dict):
        logger.error(f"Invalid response format received for user {email}: {type(response)}")
        st.error("Received invalid data from server.")
    else:
        interviews = response.get("interviews", [])
        logger.info(f"Found {len(interviews)} interviews for user: {email}")
        if interviews:
            try:
                # Sort interviews by creation date
                sorted_interviews = sorted(interviews, key=lambda x: x.get("created_at", ""), reverse=True)
                
                for idx, interview in enumerate(sorted_interviews):
                    try:
                        # Validate interview data
                        if not isinstance(interview, dict):
                            logger.warning(f"Invalid interview data at index {idx} for user {email}")
                            continue
                        
                        interview_id = interview.get("id", "unknown")
                        created_at = interview.get("created_at")
                        score = interview.get("score", "N/A")
                        summary = interview.get("summary", "No summary available")
                        
                        col1, col2 = st.columns([6, 1])
                        
                        with col1:
                            # Format date safely
                            if created_at:
                                try:
                                    formatted_date = datetime.fromisoformat(created_at).strftime('%b %d, %Y %I:%M %p')
                                    st.markdown(f"📅 {formatted_date}")
                                except (ValueError, TypeError) as e:
                                    logger.warning(f"Invalid date format for interview {interview_id}: {created_at}")
                                    st.markdown(f"📅 {created_at}")
                            else:
                                st.markdown("📅 Date not available")
                            
                            st.markdown(f"🎯 Score: {score}/10")
                            st.markdown(f"**📝 Summary:** {summary}")
                        
                        with col2:
                            # Store interview ID in session state for feedback viewing
                            if st.button(f"🔍 View Feedback", key=f"feedback_{interview_id}_{idx}"):
                                st.session_state["selected_interview_id"] = interview_id
                                log_user_action(logger, "View Feedback clicked", email, interview_id=interview_id)
                                st.switch_page("pages/feedback_view.py")
                        
                        st.markdown("---")
                        
                    except Exception as e:
                        logger.error(f"Error displaying interview {idx} for user {email}: {str(e)}")
                        st.error(f"Error displaying interview data")
                        continue
                        
            except Exception as e:
                logger.error(f"Error processing interviews list for user {email}: {str(e)}")
                st.error("Error processing interview history")
        else:
            logger.info(f"No interviews found for user: {email}")
            st.info("No previous interviews found.")

except Exception as e:
    logger.error(f"Unexpected error loading interviews for user {email}: {str(e)}")
    st.error("An unexpected error occurred while loading your interview history. Please try refreshing the page.")

# Log page completion
logger.info(f"Dashboard page loaded successfully for user: {email}")