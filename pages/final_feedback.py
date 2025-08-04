import streamlit as st
from utils.api import get_feedback
from utils.logger import setup_logger, log_user_action

# Setup logger
logger = setup_logger("final_feedback")

st.set_page_config(page_title="Interview Feedback", layout="wide")
st.title("📈 Interview Feedback")

# --- Login Check ---
email = st.session_state.get("email")
if not email:
    logger.warning("Unauthorized access attempt to final feedback")
    st.warning("Please log in first.")
    st.stop()
    
# if st.session_state.get("interview_state") != "completed":
#     logger.warning(f"Invalid interview state for final feedback access by user: {email}")
#     st.warning("You can only view feedback after completing the interview. Please complete your interview first.")
#     if st.button("← Go to Dashboard"):
#         st.switch_page("pages/dashboard.py")
#     st.stop()

logger.info(f"Final feedback page accessed by user: {email}")
log_user_action(logger, "Final feedback page accessed", email)

# --- Fetch Feedback ---
with st.spinner("🔄 Fetching your interview feedback... Please wait."):
    try:
        logger.info(f"Fetching final feedback for user: {email}")
        feedback = get_feedback(email)
        
        if feedback is None:
            logger.error(f"Failed to fetch feedback for user {email}: No response from API")
            st.error("Unable to connect to the server. Please try again later.")
            if st.button("🔄 Retry"):
                st.rerun()
            if st.button("← Go to Dashboard"):
                st.switch_page("pages/dashboard.py")
            st.stop()
            
        if not isinstance(feedback, dict):
            logger.error(f"Invalid feedback response format for user {email}: {type(feedback)}")
            st.error("Received invalid data format from server.")
            if st.button("← Go to Dashboard"):
                st.switch_page("pages/dashboard.py")
            st.stop()
            
    except Exception as e:
        logger.error(f"Unexpected error fetching feedback for user {email}: {str(e)}")
        st.error("An unexpected error occurred while loading your feedback.")
        if st.button("🔄 Retry"):
            st.rerun()
        if st.button("← Go to Dashboard"):
            st.switch_page("pages/dashboard.py")
        st.stop()

if feedback.get("status") != "success":
    error_msg = feedback.get("message", "Unknown error")
    logger.warning(f"API returned error for feedback request by user {email}: {error_msg}")
    st.warning(f"No feedback found or failed to load: {error_msg}")
    if st.button("← Go to Dashboard"):
        st.switch_page("pages/dashboard.py")
    st.stop()

data = feedback.get("data", {})
if not data:
    logger.warning(f"Empty feedback data for user: {email}")
    st.warning("No feedback data available.")
    if st.button("← Go to Dashboard"):
        st.switch_page("pages/dashboard.py")
    st.stop()

logger.info(f"Successfully loaded feedback for user: {email}")
overall = data.get("overall_feedback", {})
question_block = data.get("feedback_by_question", {})
questions = question_block.get("question_analysis", [])
overall_q_summary = question_block.get("overall_analysis")

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
    logger.error(f"Error displaying overall feedback for user {email}: {str(e)}")
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
                logger.error(f"Error displaying question {i} feedback for user {email}: {str(e)}")
                st.error(f"Error displaying feedback for question {i}")
                continue

except Exception as e:
    logger.error(f"Error displaying question feedback section for user {email}: {str(e)}")
    st.error("Error displaying detailed question feedback.")

# Mark feedback as viewed and add navigation
try:
    st.session_state.interview_state = "feedback_viewed"
    logger.info(f"Interview state updated to feedback_viewed for user: {email}")
    
    st.markdown("---")
    st.markdown("### 🎉 Interview Complete!")
    st.success("You have successfully completed your interview and viewed the feedback.")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🏠 Go to Dashboard", use_container_width=True):
            log_user_action(logger, "Go to Dashboard clicked from final feedback", email)
            st.switch_page("pages/dashboard.py")
    
    with col2:
        if st.button("🎤 Start New Interview", use_container_width=True):
            log_user_action(logger, "Start New Interview clicked from final feedback", email)
            st.switch_page("pages/interview.py")

    # Log successful page completion
    logger.info(f"Final feedback page completed successfully for user: {email}")
    
except Exception as e:
    logger.error(f"Error updating interview state for user {email}: {str(e)}")
    st.error("Error completing the feedback process.")

