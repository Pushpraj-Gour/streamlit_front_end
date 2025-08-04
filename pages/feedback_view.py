import json
import streamlit as st
import requests
from urllib.parse import urlparse, parse_qs
from utils.api import get_interview_feedback
from utils.logger import setup_logger, log_user_action

# Setup logger
logger = setup_logger("feedback_view")

st.set_page_config(page_title="Interview Feedback", layout="wide")
st.title("📈 Interview Feedback")

# Authentication check
if not st.session_state.get("logged_in"):
    logger.warning("Unauthorized access attempt to feedback view")
    st.warning("Please log in first.")
    st.stop()

email = st.session_state.get("email")
log_user_action(logger, "Feedback view accessed", email)

# --- Extract interview ID from URL or session state ---
interview_id = st.session_state.get("selected_interview_id", 1)  # Default to 1 for testing

if not interview_id:
    logger.warning(f"No interview ID provided for user: {email}")
    st.error("No interview ID provided. Please select an interview from the dashboard.")
    if st.button("← Back to Dashboard"):
        st.switch_page("pages/dashboard.py")
    st.stop()

logger.info(f"Loading feedback for interview ID: {interview_id}, user: {email}")

# --- Show loading spinner while fetching ---
with st.spinner("Loading feedback..."):
    try:
        response = get_interview_feedback(interview_id)
        
        if response is None:
            logger.error(f"Failed to fetch feedback for interview {interview_id}: No response from API")
            st.error("Unable to connect to the server. Please try again later.")
            if st.button("🔄 Retry"):
                st.rerun()
            if st.button("← Back to Dashboard"):
                st.switch_page("pages/dashboard.py")
            st.stop()
        
        # Save response for debugging (optional)
        try:
            with open("feedback.json", "w", encoding='utf-8') as f:
                json.dump(response, f, indent=4)
            logger.debug(f"Feedback response saved to feedback.json for interview {interview_id}")
        except Exception as save_error:
            logger.warning(f"Could not save feedback to file: {str(save_error)}")
        
        if not isinstance(response, dict):
            logger.error(f"Invalid response format for interview {interview_id}: {type(response)}")
            st.error("Received invalid data format from server.")
            if st.button("← Back to Dashboard"):
                st.switch_page("pages/dashboard.py")
            st.stop()
            
        if response.get("status") != "success":
            error_msg = response.get("message", "Unknown error")
            logger.error(f"API returned error for interview {interview_id}: {error_msg}")
            st.error(f"Failed to fetch feedback: {error_msg}")
            if st.button("← Back to Dashboard"):
                st.switch_page("pages/dashboard.py")
            st.stop()
            
        data = response.get("data", {})
        logger.info(f"Successfully loaded feedback for interview {interview_id}")
        
    except Exception as e:
        logger.error(f"Unexpected error fetching feedback for interview {interview_id}: {str(e)}")
        st.error(f"An unexpected error occurred while loading feedback.")
        if st.button("🔄 Retry"):
            st.rerun()
        if st.button("← Back to Dashboard"):
            st.switch_page("pages/dashboard.py")
        st.stop()

if not data:
    logger.warning(f"No feedback data available for interview {interview_id}")
    st.warning("No feedback data available for this interview.")
    if st.button("← Back to Dashboard"):
        st.switch_page("pages/dashboard.py")
    st.stop()
overall = data.get("overall_feedback", {})
question_block = data.get("question_feedback", {})
questions = question_block.get("question_analysis", [])
overall_q_summary = question_block.get("overall_analysis")

# Validate data structure
if not overall and not questions:
    logger.warning(f"Empty feedback data for interview {interview_id}")
    st.warning("Feedback data appears to be incomplete.")

# --- SECTION: Overall Evaluation ---
st.header("📋 Overall Evaluation")

try:
    # --- Compact metric row ---
    metric_cols = st.columns(4)
    metric_cols[0].metric("⭐ Overall Score", f"{overall.get('overall_score', 'N/A')}/10")
    metric_cols[1].metric("💬 Communication", f"{overall.get('overall_communication_score', 'N/A')}/10")
    metric_cols[2].metric("🧠 Content Quality", f"{overall.get('overall_content_quality_score', 'N/A')}/10")
    metric_cols[3].metric("📚 Domain Insight", f"{overall.get('overall_domain_insight_score', 'N/A')}/10")

    # --- Skills Section (below metrics, side-by-side) ---
    skills_col1, skills_col2 = st.columns(2)
    with skills_col1:
        st.subheader("🛠️ Technical Skills")
        technical_skills = overall.get("technical_skills_with_score", [])
        if technical_skills:
            for skill in technical_skills:
                st.markdown(f"- {skill}")
        else:
            st.markdown("- No technical skills data available")

    with skills_col2:
        st.subheader("💬 Soft Skills")
        soft_skills = overall.get("soft_skills_with_score", [])
        if soft_skills:
            for skill in soft_skills:
                st.markdown(f"- {skill}")
        else:
            st.markdown("- No soft skills data available")

    # --- Reasoning Section ---
    st.subheader("📑 Reasoning")
    st.markdown(f"**Overall:** {overall.get('overall_reasoning', 'N/A')}")
    st.markdown(f"**Communication:** {overall.get('overall_communication_reasoning', 'N/A')}")
    st.markdown(f"**Content Quality:** {overall.get('overall_content_quality_reasoning', 'N/A')}")
    st.markdown(f"**Domain Insight:** {overall.get('overall_domain_insight_reasoning', 'N/A')}")

    st.divider()

except Exception as e:
    logger.error(f"Error displaying overall feedback for interview {interview_id}: {str(e)}")
    st.error("Error displaying overall feedback section.")

# --- SECTION: Feedback by Question ---
st.header("🔍 Detailed Per-Question Feedback")

try:
    if overall_q_summary:
        with st.expander("📌 General Observations", expanded=False):
            st.write(overall_q_summary)

    if not questions:
        st.info("No detailed question feedback available.")
    else:
        for i, q in enumerate(questions, start=1):
            try:
                question_text = q.get('question', f'Question {i}')
                response_text = q.get('response', 'No response provided')
                with st.expander(f"❓ Q{i}: {question_text}", expanded=False):
                    st.markdown(f"### ✍️ Your Response\n{response_text}")
                    st.markdown(f"**🧮 Score:** {q.get('overall_score', 'N/A')}")
                    st.markdown(f"**📋 Summary Reasoning:** {q.get('overall_reasoning', 'N/A')}")

                    detail = q.get("question_and_response_detailed_analysis", [])
                    if detail and len(detail) > 0:
                        d = detail[0]
                        scores = {
                            "🗣️ Communication": (d.get("communication_score"), d.get("communication_reasoning")),
                            "🧾 Content Quality": (d.get("content_quality_score"), d.get("content_quality_reasoning")),
                            "📘 Domain Insight": (d.get("domain_insight_score"), d.get("domain_insight_reasoning")),
                            "🧭 Strategic Depth": (d.get("strategic_depth_score"), d.get("strategic_depth_reasoning")),
                            "👔 Professional Tone": (d.get("professional_tone_score"), d.get("professional_tone_reasoning")),
                        }

                        st.subheader("🔬 Detailed Evaluation")
                        for title, (score, reason) in scores.items():
                            with st.container():
                                st.markdown(f"**{title}**")
                                st.markdown(f"- **Score:** {score}/10" if isinstance(score, int) else "- Score: N/A")
                                st.markdown(f"- **Reasoning:** {reason if reason else 'N/A'}")

                        st.subheader("✅ Ideal Answer")
                        ideal_answer = d.get("ideal_answer", "No ideal answer provided.")
                        st.info(ideal_answer)
                    else:
                        st.info("No detailed analysis available for this question.")
                        
            except Exception as e:
                logger.error(f"Error displaying question {i} feedback for interview {interview_id}: {str(e)}")
                st.error(f"Error displaying feedback for question {i}")
                continue

except Exception as e:
    logger.error(f"Error displaying question feedback section for interview {interview_id}: {str(e)}")
    st.error("Error displaying detailed question feedback.")

# Add navigation back to dashboard
st.markdown("---")
if st.button("← Back to Dashboard", key="back_to_dashboard"):
    log_user_action(logger, "Back to Dashboard clicked", email, interview_id=interview_id)
    st.switch_page("pages/dashboard.py")

# Log successful page completion
logger.info(f"Feedback view completed successfully for interview {interview_id}, user: {email}")
