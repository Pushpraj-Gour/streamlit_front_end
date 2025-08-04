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
from utils.logger import setup_logger, log_user_action
from streamlit_mic_recorder import mic_recorder
import datetime

# Setup logger
logger = setup_logger("interview")

# Configuration
MAX_QUESTIONS = 3
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
        st.session_state.question_spoken = False
        st.session_state.recording_start_time = None

def add_custom_css():
    """Add custom CSS for professional and appealing design"""
    st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .main {
        font-family: 'Inter', sans-serif;
    }
    
    /* Custom Gradient Backgrounds */
    .welcome-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 20px 40px rgba(102, 126, 234, 0.3);
        backdrop-filter: blur(10px);
    }
    
    .recording-card {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 2rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin: 1.5rem 0;
        box-shadow: 0 15px 35px rgba(79, 172, 254, 0.3);
    }
    
    .stats-card {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: #2c3e50;
        margin: 1rem 0;
        box-shadow: 0 10px 25px rgba(168, 237, 234, 0.3);
    }
    
    .completion-card {
        background: linear-gradient(135deg, #96fbc4 0%, #f9f586 100%);
        padding: 2rem;
        border-radius: 20px;
        color: #2c3e50;
        text-align: center;
        margin: 1.5rem 0;
        box-shadow: 0 15px 35px rgba(150, 251, 196, 0.3);
    }
    
    /* Progress Bar Enhancement */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        height: 8px;
    }
    
    /* Button Enhancements */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 50px;
        padding: 0.7rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 25px rgba(102, 126, 234, 0.4);
    }
    
    /* Recording Animation */
    .recording-pulse {
        animation: pulse 1.5s infinite;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); opacity: 1; }
        50% { transform: scale(1.05); opacity: 0.7; }
        100% { transform: scale(1); opacity: 1; }
    }
    
    /* Custom Alert Styles */
    .success-alert {
        background: linear-gradient(135deg, #56ab2f 0%, #a8e6cf 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        text-align: center;
        font-weight: 500;
    }
    
    .error-alert {
        background: linear-gradient(135deg, #ff416c 0, #ff4b2b 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        text-align: center;
        font-weight: 500;
    }
    
    /* Instructions Enhancement */
    .instruction-item {
        background: rgba(255, 255, 255, 0.1);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        backdrop-filter: blur(10px);
    }
    
    /* Status Indicators */
    .status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
    }
    
    .status-pending { background-color: #f39c12; }
    .status-recording { background-color: #e74c3c; }
    .status-complete { background-color: #27ae60; }
    
    /* Recording Timer Component */
    .recording-timer {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        text-align: center;
        box-shadow: 0 8px 20px rgba(255, 107, 107, 0.3);
        animation: recordingPulse 2s infinite;
    }
    
    @keyframes recordingPulse {
        0% { transform: scale(1); box-shadow: 0 8px 20px rgba(255, 107, 107, 0.3); }
        50% { transform: scale(1.02); box-shadow: 0 12px 30px rgba(255, 107, 107, 0.5); }
        100% { transform: scale(1); box-shadow: 0 8px 20px rgba(255, 107, 107, 0.3); }
    }
    
    .timer-display {
        font-size: 2.5rem;
        font-weight: 700;
        font-family: 'Courier New', monospace;
        margin: 0.5rem 0;
    }
    
    </style>
    """, unsafe_allow_html=True)

def display_timer():
    """Display recording timer"""
    if st.session_state.recording_start_time:
        elapsed = time.time() - st.session_state.recording_start_time
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)
        
        timer_placeholder = st.empty()
        timer_placeholder.markdown(f"""
        <div class="timer-label">⏱️ Recording Time</div>
        <div class="timer-display">{minutes:02d}:{seconds:02d}</div>
        """, unsafe_allow_html=True)
        
        return timer_placeholder
    return None

def fetch_question(is_first_question=False):
    """Unified function to fetch questions"""
    email = st.session_state.get('email')
    try:
        if is_first_question:
            logger.info(f"Fetching initial question for user: {email}")
            response = get_initial_question(email)
        else:
            logger.info(f"Fetching next question for user: {email}")
            response = get_next_question()
        
        if response is None:
            logger.error(f"No response received when fetching question for user: {email}")
            st.markdown('<div class="error-alert">❌ Unable to connect to server. Please check your connection.</div>', unsafe_allow_html=True)
            return None
            
        if not isinstance(response, dict):
            logger.error(f"Invalid response format when fetching question for user {email}: {type(response)}")
            st.markdown('<div class="error-alert">❌ Received invalid response from server.</div>', unsafe_allow_html=True)
            return None
        
        if response.get("status") != "success":
            error_msg = response.get("message", "Unknown error")
            logger.error(f"API error fetching question for user {email}: {error_msg}")
            st.markdown(f'<div class="error-alert">❌ Failed to fetch question: {error_msg}</div>', unsafe_allow_html=True)
            return None
        
        question_data = response.get("data", {})
        if not isinstance(question_data, dict):
            logger.error(f"Invalid question data format for user {email}: {type(question_data)}")
            st.markdown('<div class="error-alert">❌ Invalid question data received.</div>', unsafe_allow_html=True)
            return None
            
        question = question_data.get("question", "")
        if not question.strip():
            logger.error(f"Empty question received for user: {email}")
            st.markdown('<div class="error-alert">❌ No question received from server.</div>', unsafe_allow_html=True)
            return None
        
        # Update state
        if is_first_question:
            st.session_state.current_question_index = 1
            st.session_state.total_questions_asked = 1
            logger.info(f"Initial question loaded for user {email}: {question[:50]}...")
        else:
            st.session_state.current_question_index += 1
            st.session_state.total_questions_asked += 1
            logger.info(f"Next question ({st.session_state.current_question_index}) loaded for user {email}: {question[:50]}...")
        
        st.session_state.current_question = question
        st.session_state.interview_state = 'asking'
        st.session_state.question_spoken = False  # Reset for new question
        
        # Add question to tracking
        st.session_state.questions_responses.append({
            'question': question,
            'response_status': 'PENDING',
            'question_index': st.session_state.current_question_index
        })
        
        log_user_action(logger, f"Question {st.session_state.current_question_index} fetched", email, 
                       question_type="initial" if is_first_question else "next")
        
        return question
        
    except Exception as e:
        logger.error(f"Unexpected error fetching question for user {email}: {str(e)}")
        st.markdown('<div class="error-alert">❌ An unexpected error occurred while fetching the question.</div>', unsafe_allow_html=True)
        return None

def upload_audio_to_backend(audio_bytes, question_text):
    """Sends the recorded audio bytes and question to the backend."""
    email = st.session_state.get('email')
    
    if not audio_bytes:
        logger.warning(f"No audio data to upload for user: {email}")
        st.markdown('<div class="error-alert">No audio data to upload.</div>', unsafe_allow_html=True)
        return None
    
    try:
        logger.info(f"Uploading audio response for user {email}, question: {question_text[:50]}...")
        
        files = {'audio_file': ('response.wav', audio_bytes, 'audio/wav')}
        payload = {'question': question_text}
        
        url = f"{BACKEND_URL}/interview/responses/upload"
        response = requests.post(url, files=files, data=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        logger.info(f"Audio upload successful for user: {email}")
        log_user_action(logger, "Audio response uploaded", email, question_length=len(question_text))
        
        return result
        
    except requests.exceptions.Timeout as e:
        logger.error(f"Upload timeout for user {email}: {str(e)}")
        st.markdown('<div class="error-alert">Upload timeout. Please check your connection and try again.</div>', unsafe_allow_html=True)
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Upload request failed for user {email}: {str(e)}")
        st.markdown(f'<div class="error-alert">Upload Failed: Could not send audio to the backend. Error: {e}</div>', unsafe_allow_html=True)
        return None
    except Exception as e:
        logger.error(f"Unexpected error during upload for user {email}: {str(e)}")
        st.markdown('<div class="error-alert">An unexpected error occurred during upload.</div>', unsafe_allow_html=True)
        return None

def start_interview():
    """Initialize the interview"""
    email = st.session_state.get('email')
    logger.info(f"Starting interview for user: {email}")
    log_user_action(logger, "Interview started", email)
    
    add_custom_css()
    
    st.markdown("# 🎤 AI Mock Interview Simulator")
    
    # Welcome section with enhanced design
    st.markdown(f"""
    <div class="welcome-card">
        <h2 style="margin: 0; color: white; font-weight: 700;">Welcome to Your Personalized Interview! 👋</h2>
        <p style="margin: 15px 0 0 0; font-size: 1.2rem; opacity: 0.9;">Get ready to practice with AI-powered questions tailored just for you.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Enhanced instructions with better layout
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
        <div class="stats-card">
            <h3 style="margin-top: 0; color: #2c3e50;">📋 How it works:</h3>
            <div class="instruction-item">
                <strong>🎧 Listen</strong> - Each question will be read aloud automatically
            </div>
            <div class="instruction-item">
                <strong>🎤 Record</strong> - Click to start recording your response
            </div>
            <div class="instruction-item">
                <strong>⚡ Submit</strong> - Stop recording to auto-submit and get next question
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stats-card">
            <h3 style="margin-top: 0; color: #2c3e50;">📊 Interview Details:</h3>
            <div class="instruction-item">
                <strong>Questions:</strong> {MAX_QUESTIONS} personalized questions
            </div>
            <div class="instruction-item">
                <strong>Format:</strong> Audio-based interaction
            </div>
            <div class="instruction-item">
                <strong>Duration:</strong> ~15-20 minutes
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Enhanced start button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Start Your Interview", type="primary", use_container_width=True):
            with st.spinner("🔄 Preparing your custom questions..."):
                if fetch_question(is_first_question=True):
                    st.rerun()

def display_question_and_record():
    """Display current question and handle recording/upload"""
    add_custom_css()

    # Enhanced header with better progress visualization
    progress = st.session_state.current_question_index / MAX_QUESTIONS
    st.progress(progress, text=f"Question {st.session_state.current_question_index} of {MAX_QUESTIONS}")

    # Question status indicators
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown(f"""
        <div style="display: flex; align-items: center; margin: 1rem 0;">
            <span class="status-indicator status-complete"></span>
            <span>Progress: {st.session_state.current_question_index}/{MAX_QUESTIONS}</span>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        if st.button("🛑 End Interview", type="secondary"):
            st.session_state.interview_state = 'complete'
            st.rerun()

    # Show the question block
    st.markdown(f"""
    <div style="background: linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%);
        border: 1px solid #e9ecef;
        border-left: 5px solid #667eea;
        border-radius: 15px;
        padding: 2rem;
        margin: 2rem 0;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        position: relative;">
        <div style="color: #2c3e50; font-size: 1.2rem; line-height: 1.7; font-weight: 500;
            padding: 1rem 0; border-left: 3px solid #667eea; padding-left: 1.5rem; margin-left: 1rem;">
            "{st.session_state.current_question}"
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Recording component
    recorder_key = f'recorder_{st.session_state.current_question_index}'
    if f'is_recording_{recorder_key}' not in st.session_state:
        st.session_state[f'is_recording_{recorder_key}'] = False

    # Speak question only once
    if not st.session_state.question_spoken:
        speak_question(st.session_state.current_question, show_repeat_button=False)
        st.session_state.question_spoken = True

    # Show mic and repeat button
    col1, col2 = st.columns([1, 1])
    with col1:
        audio = mic_recorder(
            start_prompt="🎤 Start Recording",
            stop_prompt="⏹️ Stop & Submit",
            just_once=True,
            key=recorder_key
        )
    with col2:
        if st.button("🔊 Repeat Question", key=f"repeat_{recorder_key}", use_container_width=True):
            speak_question(st.session_state.current_question, show_repeat_button=False)

    st.markdown("---")

    # Handle audio response
    if audio and audio.get('bytes'):
        st.session_state[f'is_recording_{recorder_key}'] = False
        st.session_state.recording_start_time = None

        with st.spinner("🔄 Processing your response..."):
            upload_response = upload_audio_to_backend(
                audio['bytes'],
                st.session_state.current_question
            )

            if upload_response:
                if st.session_state.questions_responses:
                    st.session_state.questions_responses[-1]['response_status'] = 'RECORDED'

                st.markdown('<div class="success-alert">✅ Response submitted successfully!</div>', unsafe_allow_html=True)

                if st.session_state.current_question_index >= MAX_QUESTIONS:
                    st.session_state.interview_state = 'complete'
                else:
                    st.session_state.interview_state = 'loading_next'

                time.sleep(2)
                st.rerun()
            else:
                st.markdown('<div class="error-alert">❌ Failed to submit response. Please try again.</div>', unsafe_allow_html=True)

def load_next_question():
    """Load the next question"""
    add_custom_css()
    
    st.markdown("# 🔄 Loading Next Question...")
    
    # Loading animation
    st.markdown("""
    <div style="text-align: center; margin: 3rem 0;">
        <div style="font-size: 3rem; margin-bottom: 1rem;">⏳</div>
        <div style="font-size: 1.2rem; color: #7f8c8d;">Preparing your next question...</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Auto-load next question
    if fetch_question(is_first_question=False):
        time.sleep(1)  # Brief pause for smooth transition
        st.rerun()
    else:
        st.markdown('<div class="error-alert">❌ Failed to load next question.</div>', unsafe_allow_html=True)
        st.session_state.interview_state = 'complete'
        st.rerun()

def handle_interview_completion():
    """Handle interview completion"""
    add_custom_css()
    
    st.markdown("# 🎉 Interview Complete!")
    
    # Calculate statistics
    total_answered = len([q for q in st.session_state.questions_responses 
                         if q.get('response_status') == 'RECORDED'])
    
    # Enhanced completion card
    st.markdown(f"""
    <div class="completion-card">
        <h2 style="margin-top: 0; color: #2c3e50;">🏆 Congratulations!</h2>
        <p style="font-size: 1.3rem; margin: 1rem 0;">You have successfully completed your mock interview!</p>
        <div style="font-size: 1.1rem; margin-top: 1.5rem;">
            <strong>Questions Answered:</strong> {total_answered} out of {st.session_state.total_questions_asked}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if total_answered > 0:
        # Interview summary
        st.markdown("""
        <div class="stats-card">
            <h3 style="margin-top: 0; color: #2c3e50;">📈 Interview Summary</h3>
            <div style="display: flex; justify-content: space-between; align-items: center; margin: 1rem 0;">
                <span>Completion Rate:</span>
                <span style="font-weight: 600;">{:.1%}</span>
            </div>
        </div>
        """.format(total_answered / st.session_state.total_questions_asked), unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("📊 Get Detailed Feedback", type="primary", use_container_width=True):
                st.session_state.interview_completed = True
                st.switch_page("pages/final_feedback.py") # TODO
                # st.switch_page("final_feedback.py")
        
        with col2:
            if st.button("🏠 Back to Dashboard", use_container_width=True):
                # Clear interview state
                for key in ['interview_state', 'current_question_index', 'current_question', 
                          'questions_responses', 'total_questions_asked', 'question_spoken', 'recording_start_time']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.switch_page("pages/dashboard.py")
    else:
        st.markdown('<div class="error-alert">⚠️ No questions were answered. Consider trying again!</div>', unsafe_allow_html=True)
        if st.button("🔄 Start New Interview", type="primary"):
            # Reset interview state
            for key in ['interview_state', 'current_question_index', 'current_question', 
                      'questions_responses', 'total_questions_asked', 'question_spoken', 'recording_start_time']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

def main():
    # Set page config for better appearance
    st.set_page_config(
        page_title="AI Mock Interview",
        page_icon="🎤",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Validate user session
    email = st.session_state.get('email')
    if not email or not st.session_state.get('logged_in'):
        logger.warning("Unauthorized access attempt to interview page")
        st.error("❌ User session not found. Please login again.")
        st.switch_page("home.py")
        return
    
    # Log interview page access
    logger.info(f"Interview page accessed by user: {email}")
    log_user_action(logger, "Interview page accessed", email)
    
    # Initialize interview state
    try:
        initialize_interview_state()
        logger.debug(f"Interview state initialized for user: {email}")
    except Exception as e:
        logger.error(f"Error initializing interview state for user {email}: {str(e)}")
        st.error("Error initializing interview. Please try again.")
        return
    
    # State machine with error handling
    try:
        current_state = st.session_state.get('interview_state', 'start')
        logger.debug(f"Interview state for user {email}: {current_state}")
        
        if current_state == 'start':
            start_interview()
        elif current_state == 'asking':
            display_question_and_record()
        elif current_state == 'loading_next':
            load_next_question()
        elif current_state == 'complete':
            handle_interview_completion()
        else:
            # Handle unexpected states
            logger.warning(f"Invalid interview state '{current_state}' for user {email}, restarting")
            add_custom_css()
            st.markdown('<div class="error-alert">❌ Invalid interview state. Restarting...</div>', unsafe_allow_html=True)
            st.session_state.interview_state = 'start'
            st.rerun()
            
    except Exception as e:
        logger.error(f"Unexpected error in interview state machine for user {email}: {str(e)}")
        st.error("An unexpected error occurred. Please try refreshing the page.")
        if st.button("🔄 Restart Interview"):
            # Reset interview state
            for key in ['interview_state', 'current_question_index', 'current_question', 
                       'questions_responses', 'total_questions_asked', 'interview_completed', 
                       'question_spoken', 'recording_start_time']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

if __name__ == "__main__":
    st.session_state.logged_in = True #TODO
    main()