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
BACKEND_URL = "http://127.0.0.1:8081"

def initialize_interview_state():
    """Initialize session state for interview"""
    if 'interview_state' not in st.session_state:
        st.session_state.interview_state = 'start'
        st.session_state.current_question_index = 0
        st.session_state.current_question = ""
        st.session_state.questions_responses = []
        st.session_state.total_questions_asked = 0
        st.session_state.interview_completed = False

def fetch_question(is_first_question=False):
    """Unified function to fetch questions"""
    try:
        if is_first_question:
            response = get_initial_question(st.session_state.email)
        else:
            response = get_next_question()
        
        if response.get("status") != "success":
            st.error("❌ Failed to fetch question. Please try again later.")
            return None
        
        question = response.get("data", {}).get("question", "")
        if not question:
            st.error("❌ No question received from server.")
            return None
        
        # Update state
        if is_first_question:
            st.session_state.current_question_index = 1
            st.session_state.total_questions_asked = 1
        else:
            st.session_state.current_question_index += 1
            st.session_state.total_questions_asked += 1
        
        st.session_state.current_question = question
        st.session_state.interview_state = 'asking'
        
        # Add question to tracking
        st.session_state.questions_responses.append({
            'question': question,
            'response_status': 'PENDING',
            'question_index': st.session_state.current_question_index
        })
        
        return question
        
    except Exception as e:
        st.error(f"❌ Error fetching question: {str(e)}")
        return None

def upload_audio_to_backend(audio_bytes, question_text):
    """Sends the recorded audio bytes and question to the backend."""
    if not audio_bytes:
        st.error("No audio data to upload.")
        return None
    
    try:
        files = {'audio_file': ('response.wav', audio_bytes, 'audio/wav')}
        payload = {'question': question_text}
        
        url = f"{BACKEND_URL}/interview/responses/upload"
        response = requests.post(url, files=files, data=payload, timeout=30)
        response.raise_for_status()
        
        return response.json()
        
    except requests.exceptions.Timeout:
        st.error("Upload timeout. Please check your connection and try again.")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"Upload Failed: Could not send audio to the backend. Error: {e}")
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
                if fetch_question(is_first_question=True):
                    st.rerun()

def display_question_and_record():
    """Display current question and handle recording/upload"""
    
    # Header with progress
    progress = st.session_state.current_question_index / MAX_QUESTIONS
    st.progress(progress, text=f"Question {st.session_state.current_question_index} of {MAX_QUESTIONS}")
    
    # Early termination option
    col1, col2, col3 = st.columns([1, 2, 1])
    with col3:
        if st.button("🛑 End Interview", type="secondary"):
            st.session_state.interview_state = 'complete'
            st.rerun()
    
    # Question display
    st.markdown("---")
    speak_question(st.session_state.current_question, show_repeat_button=True)
    st.markdown("---")
    
    # Recording section
    st.markdown("### 🎙️ Your Response")

    # Use a unique key based on question index to reset recorder for each question
    recorder_key = f'recorder_{st.session_state.current_question_index}'
    
    audio = mic_recorder(
        start_prompt="Click to Record Answer ⏺️",
        stop_prompt="Click to Stop & Submit ⏹️",
        just_once=True,
        key=recorder_key
    )

    if audio and audio.get('bytes'):
        # Process the audio immediately
        with st.spinner("🔄 Processing your answer..."):
            upload_response = upload_audio_to_backend(
                audio['bytes'], 
                st.session_state.current_question
            )
            
            if upload_response:
                # Update response status
                if st.session_state.questions_responses:
                    st.session_state.questions_responses[-1]['response_status'] = 'RECORDED'
                
                st.success("✅ Answer submitted successfully!")
                
                # Check if interview should continue
                if st.session_state.current_question_index >= MAX_QUESTIONS:
                    st.session_state.interview_state = 'complete'
                else:
                    st.session_state.interview_state = 'loading_next'
                
                time.sleep(1)  # Brief pause for user feedback
                st.rerun()
            else:
                st.error("❌ Failed to submit answer. Please try again.")

def load_next_question():
    """Load the next question"""
    with st.spinner("🔄 Loading next question..."):
        if fetch_question(is_first_question=False):
            st.rerun()
        else:
            st.error("❌ Failed to load next question.")
            st.session_state.interview_state = 'complete'
            st.rerun()

def handle_interview_completion():
    """Handle interview completion"""
    st.markdown("# 🎉 Interview Complete!")
    
    # Calculate statistics
    total_answered = len([q for q in st.session_state.questions_responses 
                         if q.get('response_status') == 'RECORDED'])
    
    # Results summary
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%); 
                padding: 20px; border-radius: 10px; color: white; text-align: center; margin-bottom: 20px;">
        <h3 style="margin: 0; color: white;">Interview Summary</h3>
        <p style="margin: 10px 0 0 0;">You answered <strong>{total_answered}</strong> out of <strong>{st.session_state.total_questions_asked}</strong> questions</p>
    </div>
    """, unsafe_allow_html=True)
    
    if total_answered > 0:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("📊 Get Detailed Feedback", type="primary", use_container_width=True):
                st.session_state.interview_completed = True
                st.switch_page("pages/feedback.py")
        
        with col2:
            if st.button("🏠 Back to Dashboard", use_container_width=True):
                # Clear interview state
                for key in ['interview_state', 'current_question_index', 'current_question', 
                          'questions_responses', 'total_questions_asked']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.switch_page("pages/dashboard.py")
    else:
        st.warning("⚠️ No questions were answered. Consider trying again!")
        if st.button("🔄 Start New Interview", type="primary"):
            # Reset interview state
            for key in ['interview_state', 'current_question_index', 'current_question', 
                      'questions_responses', 'total_questions_asked']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

def main():
    # Validate user session
    if 'email' not in st.session_state or not st.session_state.email:
        st.error("❌ User session not found. Please login again.")
        st.switch_page("home.py")
        return
    
    # Initialize interview state
    initialize_interview_state()
    
    # State machine
    if st.session_state.interview_state == 'start':
        start_interview()
    elif st.session_state.interview_state == 'asking':
        display_question_and_record()
    elif st.session_state.interview_state == 'loading_next':
        load_next_question()
    elif st.session_state.interview_state == 'complete':
        handle_interview_completion()
    else:
        # Handle unexpected states
        st.error("❌ Invalid interview state. Restarting...")
        st.session_state.interview_state = 'start'
        st.rerun()

if __name__ == "__main__":
    # Test session data (should be removed in production)
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