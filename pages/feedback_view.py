import json
import streamlit as st
import requests
from urllib.parse import urlparse, parse_qs
from utils.api import get_interview_feedback

st.set_page_config(page_title="Interview Feedback", layout="wide")
st.title("📈 Interview Feedback")

# --- Extract interview ID from URL ---
# query_params = st.experimental_get_query_params()
interview_id = 1

if not interview_id:
    st.error("No interview ID provided in the URL.")
    st.stop()

# --- Show loading spinner while fetching ---
with st.spinner("Loading feedback..."):
    try:
        response = get_interview_feedback(interview_id)
        with open("feedback.json", "w", encoding='utf-8') as f:
            json.dump(response, f, indent=4)
        if response.get("status") != "success":
            st.error("Failed to fetch feedback.")
            st.stop()
        data = response.get("data", {})
    except Exception as e:
        st.error(f"Error fetching feedback: {str(e)}")
        st.stop()

if not data:
    st.warning("No feedback data available for this interview.")
    st.stop()
overall = data.get("overall_feedback", {})
question_block = data.get("question_feedback", {})
questions = question_block.get("question_analysis", [])
overall_q_summary = question_block.get("overall_analysis")

# --- SECTION: Overall Evaluation ---
st.header("📋 Overall Evaluation")

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
    for skill in overall.get("technical_skills_with_score", []):
        st.markdown(f"- {skill}")

with skills_col2:
    st.subheader("💬 Soft Skills")
    for skill in overall.get("soft_skills_with_score", []):
        st.markdown(f"- {skill}")

# --- Reasoning Section ---
st.subheader("📑 Reasoning")
st.markdown(f"**Overall:** {overall.get('overall_reasoning', 'N/A')}")
st.markdown(f"**Communication:** {overall.get('overall_communication_reasoning', 'N/A')}")
st.markdown(f"**Content Quality:** {overall.get('overall_content_quality_reasoning', 'N/A')}")
st.markdown(f"**Domain Insight:** {overall.get('overall_domain_insight_reasoning', 'N/A')}")

st.divider()

# --- SECTION: Feedback by Question ---
st.header("🔍 Detailed Per-Question Feedback")

if overall_q_summary:
    with st.expander("📌 General Observations", expanded=False):
        st.write(overall_q_summary)

for i, q in enumerate(questions, start=1):
    with st.expander(f"❓ Q{i}: {q.get('question', 'Question')}", expanded=False):
        st.markdown(f"### ✍️ Question\n{q.get('question', '')}")
        st.markdown(f"**🧮 Score:** {q.get('overall_score', 'N/A')}")
        st.markdown(f"**📋 Summary Reasoning:** {q.get('overall_reasoning', 'N/A')}")

        detail = q.get("question_and_response_detailed_analysis", [])
        if detail:
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
                    st.markdown(f"- **Reasoning:** {reason}")

            st.subheader("✅ Ideal Answer")
            st.info(d.get("ideal_answer", "No ideal answer provided."))
