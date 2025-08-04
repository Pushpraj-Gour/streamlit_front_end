import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Mock Interview Simulator",
    page_icon="🎤",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    /* Hide Streamlit default UI */
    #MainMenu, footer, header {visibility: hidden;}

    /* General container */
    .main-container.hero-strip {
    background: linear-gradient(135deg, #667eea, #764ba2);
    padding: 2rem;
    border-radius: 15px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.1);
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 160px;
    flex-direction: column;
    text-align: center;
}

    /* Hero */
    .hero-content {
    color: white;
}

.hero-title {
    font-size: 2.2rem;
    font-weight: 700;
    margin: 0;
    line-height: 1.2;
}

.hero-subtitle {
    font-size: 1rem;
    font-weight: 300;
    margin-top: 0.3rem;
    color: rgba(255,255,255,0.9);
}

    /* Features */
    .features-container {
        display: flex;
        gap: 1rem;
        flex-wrap: wrap;
        justify-content: center;
        margin: 2rem 0;
    }
    .feature-card {
        flex: 1;
        min-width: 250px;
        background: rgba(255,255,255,0.1);
        border: 1px solid rgba(255,255,255,0.2);
        border-radius: 15px;
        padding: 1.5rem;
        text-align: center;
        color: white;
        backdrop-filter: blur(10px);
    }
    .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }

    /* Stats */
    .stats-container {
        display: flex;
        justify-content: space-around;
        margin: 2rem 0;
        background: rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 1rem;
    }
    .stat-item {
        text-align: center;
        color: white;
    }
    .stat-number {
        font-size: 2rem;
        font-weight: bold;
    }
    .stat-label {
        opacity: 0.8;
        font-size: 0.9rem;
    }

    /* Buttons */
    .custom-button {
        background: linear-gradient(45deg, #74b9ff, #0984e3);
        color: white;
        padding: 1rem 2rem;
        border-radius: 30px;
        font-size: 1.1rem;
        font-weight: 600;
        border: none;
        cursor: pointer;
        width: 100%;
        transition: all 0.3s ease;
    }
    .custom-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(116,185,255,0.4);
    }
    .button-wrapper {
        text-align: center;
        margin: 2rem 0;
    }

    /* Steps */
    .how-it-works {
        text-align: center;
        color: rgba(255,255,255,0.9);
        margin-top: 2rem;
    }
    .how-it-works h4 {
        color: white;
        margin-bottom: 1rem;
    }
    .steps-container {
        display: flex;
        justify-content: space-around;
        flex-wrap: wrap;
        gap: 1rem;
    }
    .step {
        flex: 1;
        min-width: 200px;
        text-align: center;
    }

    /* Responsive */
    @media (max-width: 768px) {
        .hero-title { font-size: 2rem; }
        .hero-subtitle { font-size: 1rem; }
        .custom-button { width: 90%; }
        .stats-container { flex-direction: column; gap: 1rem; }
    }
</style>
""", unsafe_allow_html=True)

# Content Start
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# Hero
# Main container with hero banner and content
st.markdown("""
<div class="main-container hero-strip">
    <div class="hero-content">
        <div class="hero-title">Mock Interview Simulator</div>
        <div class="hero-subtitle">Master your interview skills with AI-powered personalized practice sessions</div>
    </div>
</div>
""", unsafe_allow_html=True)


# Features
st.markdown("""
<div class="features-container">
    <div class="feature-card">
        <div class="feature-icon">🤖</div>
        <div><strong>AI-Powered Questions</strong></div>
        <div>Personalized questions based on your profile</div>
    </div>
    <div class="feature-card">
        <div class="feature-icon">🎯</div>
        <div><strong>Real-time Feedback</strong></div>
        <div>Instant evaluation with actionable insights</div>
    </div>
    <div class="feature-card">
        <div class="feature-icon">📊</div>
        <div><strong>Progress Tracking</strong></div>
        <div>Track improvements over time</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Stats
# st.markdown("""
# <div class="stats-container">
#     <div class="stat-item">
#         <div class="stat-number">1000+</div>
#         <div class="stat-label">Questions Available</div>
#     </div>
#     <div class="stat-item">
#         <div class="stat-number">95%</div>
#         <div class="stat-label">Success Rate</div>
#     </div>
#     <div class="stat-item">
#         <div class="stat-number">24/7</div>
#         <div class="stat-label">Availability</div>
#     </div>
# </div>
# """, unsafe_allow_html=True)

# Buttons
st.markdown('<div class="button-wrapper">', unsafe_allow_html=True)
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    # st.markdown("#### Choose Your Path")
    col_left, col_right = st.columns(2)

    with col_left:
        if st.button("🔐 Existing User", use_container_width=True):
            st.switch_page("pages/existing_user.py")
    with col_right:
        if st.button("🆕 New User", use_container_width=True):
            st.switch_page("pages/new_user.py")

st.markdown('</div>', unsafe_allow_html=True)

# How It Works
st.markdown("""
<div class="how-it-works">
    <h4>How It Works</h4>
    <div class="steps-container">
        <div class="step">
            <div style="font-size: 2rem;">1️⃣</div>
            <strong>Create Profile</strong><br>
            <span style="font-size: 0.9rem;">Add your skills and experience</span>
        </div>
        <div class="step">
            <div style="font-size: 2rem;">2️⃣</div>
            <strong>Practice Interview</strong><br>
            <span style="font-size: 0.9rem;">Answer AI-generated questions</span>
        </div>
        <div class="step">
            <div style="font-size: 2rem;">3️⃣</div>
            <strong>Get Feedback</strong><br>
            <span style="font-size: 0.9rem;">Receive improvement tips</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
<hr>
<div style="text-align: center; color: rgba(255,255,255,0.7); font-size: 0.9rem;">
    Made with ❤️ for interview success • Start practicing today and land your dream job!
</div>
""", unsafe_allow_html=True)
