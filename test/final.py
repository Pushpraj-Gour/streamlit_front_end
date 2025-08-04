import sys
import os
import io
import base64

# Add the parent directory (frontend_project) to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import streamlit.components.v1 as components
import time
import requests
from utils.api import get_initial_question, get_next_question, upload_audio_response
from utils.text_to_speech_util import speak_question
from streamlit_mic_recorder import mic_recorder

# Configuration
MAX_QUESTIONS = 5

def initialize_interview_state():
    """Initialize session state for interview"""
    if 'interview_state' not in st.session_state:
        st.session_state.interview_state = 'start'
        st.session_state.current_question_index = 0
        st.session_state.current_question = ""

def get_first_question():
    """Fetch the initial question"""
    try:
        initial_question_response = get_initial_question(st.session_state.email)
        
        if initial_question_response.get("status") != "success":
            st.error("❌ Failed to fetch initial question. Please try again later.")
            return None
        
        question = initial_question_response.get("data", {}).get("question", "")
        if not question:
            st.error("❌ No question received from server.")
            return None
        
        st.session_state.current_question = question
        st.session_state.current_question_index = 1
        st.session_state.total_questions_asked = 1
        st.session_state.interview_state = 'asking'

        return question
        
    except Exception as e:
        st.error(f"❌ Error fetching initial question: {str(e)}")
        return None

def get_next_question_data():
    """Fetch the next question"""
    try:
        next_question_response = get_next_question()
        
        if next_question_response.get("status") != "success":
            st.error("❌ Failed to fetch next question.")
            return None
        
        question = next_question_response.get("data", {}).get("question", "")
        if not question:
            st.error("❌ No question received from server.")
            return None
            
        st.session_state.current_question_index += 1
        st.session_state.total_questions_asked += 1
        st.session_state.current_question = question
        st.session_state.interview_state = 'asking'
        return question
        
    except Exception as e:
        st.error(f"❌ Error fetching next question: {str(e)}")
        return None


def start_interview():
    """Initialize the interview"""
    st.markdown("# 🎤 Mock Interview Simulator")
    
    # Welcome section
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 30px; border-radius: 15px; color: white; text-align: center; margin-bottom: 30px;">
        <h2 style="margin: 0; color: white;">Welcome to Your Personalized Interview! 👋</h2>
        <p style="margin: 10px 0 0 0; font-size: 18px;">Get ready to practice with AI-powered questions tailored just for you.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Instructions
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
        ### 📋 How it works:
        1. **🎧 Listen** - Each question will be read aloud
        2. **🎤 Record & Submit** - One-click recording and upload
        3. **⚡ Next** - Instantly get your next question
        """)
    
    with col2:
        st.markdown(f"""
        ### 📊 Interview Details:
        - **Questions:** {MAX_QUESTIONS} personalized questions
        - **Format:** Direct audio streaming
        - **Speed:** Instant upload & processing
        """)
    
    st.markdown("---")
    
    # Start button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Start Your Interview", type="primary", use_container_width=True):
            with st.spinner("🔄 Fetching your first question..."):
                question = get_first_question()
                if question:
                    st.session_state.current_question = question
                    st.session_state.current_question_index = 1
                    st.session_state.total_questions_asked = 1
                    st.session_state.interview_state = 'asking'
                    st.rerun()

BACKEND_URL = "http://127.0.0.1:8081"
def upload_audio_to_backend(audio_bytes, question_text):
    """Sends the recorded audio bytes and question to the backend."""
    if not audio_bytes:
        st.error("No audio data to upload.")
        return None
    try:
        files = {'audio_file': ('response.wav', audio_bytes, 'audio/wav')}
        payload = {'question': question_text}
        
        url = f"{BACKEND_URL}/interview/responses/upload"
        response = requests.post(url, files=files, data=payload)
        response.raise_for_status()
        
        return response.json()
        
    except requests.exceptions.RequestException as e:
        st.error(f"Upload Failed: Could not send audio to the backend. Error: {e}")
        return None


def display_question_and_record():
    """Display current question and handle direct recording/upload"""
    
    # Header with progress
    progress = st.session_state.current_question_index / MAX_QUESTIONS
    st.progress(progress, text=f"Question {st.session_state.current_question_index} of {MAX_QUESTIONS}")
    
    # Question display
    st.markdown("---")
    speak_question(st.session_state.current_question, show_repeat_button=True)
    st.markdown("---")
    
    # Recording section with direct upload
    st.markdown("### 🎙️ Your Response")

    audio = mic_recorder(
            start_prompt="Click to Record Answer ⏺️",
            stop_prompt="Click to Stop & Submit ⏹️",
            just_once=True, # Ensures the component reruns after stopping
            key='recorder'
        )

    if audio:
        # The user has clicked "Stop". The audio is now available.
        # We immediately process it without any extra steps.
        with st.spinner("Processing your answer..."):
            upload_response = upload_audio_to_backend(audio['bytes'], st.session_state.current_question)
            
            # Check if the interview is over
            if st.session_state.current_question_index >= MAX_QUESTIONS:
                st.session_state.interview_state = "finished"
            else:
                st.session_state.interview_state = "loading_question"
        # A brief pause to show success before moving on
        st.success("✅ Submitted! Loading next question...")
        time.sleep(2)
        st.rerun()



def handle_interview_completion():
    """Handle interview completion or early termination"""
    st.markdown("## 🛑 Interview Ended")
    
    questions_answered = len([q for q in st.session_state.questions_responses if q.get('response_status') == 'RECORDED'])
    
    if st.session_state.total_questions_asked > 0:
        st.info(f"You answered {questions_answered} out of {st.session_state.total_questions_asked} questions.")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("📊 Get Feedback", type="primary"):
                st.session_state.interview_completed = True
                st.switch_page("pages/feedback.py")
        
        with col2:
            if st.button("🏠 Back to Dashboard"):
                st.switch_page("pages/dashboard.py")
    else:
        st.warning("No questions were answered.")
        if st.button("🏠 Back to Dashboard", type="primary"):
            st.switch_page("pages/dashboard.py")

def get_question():
    """Fetch the next question from the backend"""
    st.session_state.interview_state = 'asking'
    if st.session_state.current_question_index == 0:
        
        return get_first_question()
    else:
        return get_next_question_data()
    

def main():
    # Check if user email exists
    if 'email' not in st.session_state or not st.session_state.email:
        st.error("❌ User session not found. Please login again.")
        st.switch_page("home.py")
        return
    
    # Initialize interview state
    initialize_interview_state()
    
    if st.session_state.interview_state == 'start':
        start_interview()
    elif st.session_state.interview_state == 'loading_question':
        get_question()
    elif st.session_state.interview_state == 'asking':
        display_question_and_record()
    elif st.session_state.interview_state == 'finished':
        handle_interview_completion()

if __name__ == "__main__":


    # Test session data
    st.session_state.email = "rajrjpushp@gmail.com"
    st.session_state.logged_in = True
    st.session_state.role = "AI/ML Engineer"
    st.session_state.name = "Pushpraj Gour"
    st.session_state.skills = "Python, C, SQL, TensorFlow, OpenCV, PyTorch, FastAPI, Keras, Scikit-Learn, streamlit, Seaborn, NumPy, Pandas, Matplotlib"
    st.session_state.projects = None
    st.session_state.education = "B.Tech in Electronics and Communication from RGPV University 2024"
    st.session_state.achievements = "Awarded Best Innovator in 2022, Published research paper on AI"
    st.session_state.experience = "2 years at ABC Corp as a Data Scientist, 1 year at DEF Ltd as a Machine Learning Engineer"
    main()