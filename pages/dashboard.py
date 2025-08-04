import json
import streamlit as st
from datetime import datetime
from utils.api import get_candidate_interviews

# Config
st.set_page_config(page_title="Dashboard", layout="wide")

# Authentication check
if not st.session_state.get("logged_in"):
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
    if not content or (isinstance(content, list) and all(not str(i).strip() for i in content)):
        return
    with st.expander(f"{title}", expanded=True):
        if isinstance(content, list):
            for item in content:
                if str(item).strip():
                    st.markdown(f"- {item}")
        else:
            st.markdown(content)


# Helper: Inline badge-like layout
def inline_section(title, items):
    if not items or not any(str(i).strip() for i in items):
        return
    with st.expander(f"{title}", expanded=True):
        st.markdown('<ul class="inline-list">', unsafe_allow_html=True)
        for item in items:
            if str(item).strip():
                st.markdown(f'<li>{item}</li>', unsafe_allow_html=True)
        st.markdown('</ul>', unsafe_allow_html=True)


# Display sections
section("🎓 Education", education)
section("🛠 Skills", skills)
section("📁 Projects", projects)
section("🏆 Achievements", achievements)
section("💼 Experience", experience)

# CTA
st.markdown("---")
st.markdown("#### Ready for your next challenge?")
st.page_link("pages/final_3.py", label="Start New Interview")


st.subheader("🗂️ Previous Interviews")

try:
    response = get_candidate_interviews(email)
    with open("details.json", "w", encoding='utf-8') as f:
        json.dump(response, f, indent=4)
    if response:
        interviews = response.get("interviews", [])
        if interviews:
            for interview in sorted(interviews, key=lambda x: x["created_at"], reverse=True):
                col1, col2 = st.columns([6, 1])
                with col1:
                    st.markdown(f"📅 {datetime.fromisoformat(interview['created_at']).strftime('%b %d, %Y %I:%M %p')}")
                    st.markdown(f"🎯 Score: {interview['score']}/10")
                    st.markdown(f"**📝 Summary:** {interview['summary']}")
                with col2:
                    # feedback_url = f
                    st.page_link("pages/feedback_view.py", label="🔍 View Feedback")
                st.markdown("---")
        else:
            st.info("No previous interviews found.")
    else:
        st.error("Failed to fetch interview history.")
except Exception as e:
    st.error(f"Error loading interviews: {str(e)}")