import streamlit as st
import streamlit.components.v1 as components
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
import time
import requests
from io import BytesIO
import threading
import queue
import numpy as np
import wave
import tempfile
import os
from utils.api import get_initial_question, get_next_question, upload_audio_response
from utils.text_to_speech_util import speak_question

st.set_page_config(page_title="Mock Interview", page_icon="🎤", layout="centered")

# Initialize session state
def initialize_session_state():
    if 'interview_state' not in st.session_state:
        st.session_state.interview_state = 'start'  # start, asking, recording, processing, complete
        st.session_state.current_question_index = 0
        st.session_state.current_question = ""
        st.session_state.total_questions_fetched = 0
        st.session_state.max_questions = 5
        st.session_state.is_recording = False
        st.session_state.audio_data = None
        st.session_state.questions_asked = []

def get_first_question():
    """Fetch the initial question"""
    try:
        initial_question = get_initial_question(st.session_state.email)
        if initial_question.get("status") != "success":
            st.error("Failed to fetch initial question. Please try again later.")
            return None
        
        question = initial_question.get("data", {}).get("question", "")
        st.session_state.total_questions_fetched += 1
        return question
    except Exception as e:
        st.error(f"Error fetching initial question: {str(e)}")
        return None

def get_next_question_data():
    """Fetch the next question"""
    try:
        next_question = get_next_question()
        if next_question.get("status") != "success":
            st.error("Failed to fetch next question. Please try again later.")
            return None
        
        question = next_question.get("data", {}).get("question", "")
        st.session_state.total_questions_fetched += 1
        return question
    except Exception as e:
        st.error(f"Error fetching next question: {str(e)}")
        return None

def upload_audio_response_data(question, audio_data):
    """Upload the recorded audio response"""
    try:
        response = upload_audio_response(question, audio_data)
        if response.status_code != 200:
            st.error("Failed to upload audio response. Please try again later.")
            return False
        return True
    except Exception as e:
        st.error(f"Error uploading audio: {str(e)}")
        return False

def create_audio_recorder():
    """Create audio recorder using streamlit-webrtc"""
    
    # Audio recording callback
    audio_frames = []
    
    def audio_frame_callback(frame):
        audio_frames.append(frame)
        return frame
    
    # WebRTC configuration
    rtc_configuration = RTCConfiguration({
        "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
    })
    
    webrtc_ctx = webrtc_streamer(
        key="audio_recorder",
        mode=WebRtcMode.SENDONLY,
        audio_receiver_size=256,
        media_stream_constraints={"video": False, "audio": True},
        rtc_configuration=rtc_configuration,
        audio_frame_callback=audio_frame_callback,
    )
    
    return webrtc_ctx, audio_frames

def simple_audio_recorder():
    """Alternative simple audio recorder using HTML5"""
    
    audio_recorder_html = """
    <div style="text-align: center; margin: 20px 0;">
        <button id="recordBtn" onclick="toggleRecording()" style="
            background-color: #ff4444;
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 25px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            margin: 10px;
            transition: all 0.3s ease;
        ">
            🎤 Start Recording
        </button>
        
        <div id="status" style="margin: 10px; font-weight: bold; color: #666;"></div>
        
        <audio id="audioPlayback" controls style="display: none; margin: 10px;"></audio>
    </div>

    <script>
    let mediaRecorder;
    let audioChunks = [];
    let isRecording = false;

    async function toggleRecording() {
        const recordBtn = document.getElementById('recordBtn');
        const status = document.getElementById('status');
        const audioPlayback = document.getElementById('audioPlayback');

        if (!isRecording) {
            // Start recording
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                mediaRecorder = new MediaRecorder(stream);
                audioChunks = [];

                mediaRecorder.ondataavailable = event => {
                    audioChunks.push(event.data);
                };

                mediaRecorder.onstop = () => {
                    const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                    const audioUrl = URL.createObjectURL(audioBlob);
                    audioPlayback.src = audioUrl;
                    audioPlayback.style.display = 'block';
                    
                    // Convert to base64 and send to Streamlit
                    const reader = new FileReader();
                    reader.onloadend = function() {
                        const base64data = reader.result.split(',')[1];
                        window.parent.postMessage({
                            type: 'audio_recorded',
                            data: base64data
                        }, '*');
                    };
                    reader.readAsDataURL(audioBlob);
                };

                mediaRecorder.start();
                isRecording = true;
                recordBtn.innerHTML = '⏹️ Stop Recording';
                recordBtn.style.backgroundColor = '#44ff44';
                status.innerHTML = '🔴 Recording in progress...';
            } catch (err) {
                console.error('Error accessing microphone:', err);
                status.innerHTML = '❌ Error: Could not access microphone';
            }
        } else {
            // Stop recording
            mediaRecorder.stop();
            mediaRecorder.stream.getTracks().forEach(track => track.stop());
            isRecording = false;
            recordBtn.innerHTML = '🎤 Start Recording';
            recordBtn.style.backgroundColor = '#ff4444';
            status.innerHTML = '✅ Recording completed';
        }
    }
    </script>
    """
    
    return components.html(audio_recorder_html, height=200)

def start_interview():
    """Initialize the interview"""
    st.markdown("### 🎯 Welcome to Your Mock Interview!")
    st.markdown("You will be asked **5 questions**. For each question:")
    st.markdown("1. 🎤 **Listen** to the question (it will be spoken automatically)")
    st.markdown("2. 🔴 **Record** your response using the record button")
    st.markdown("3. ⏭️ **Continue** to the next question")
    
    st.markdown("---")
    
    if st.button("🚀 Start Interview", type="primary", use_container_width=True):
        # Fetch first question
        question = get_first_question()
        if question:
            st.session_state.current_question = question
            st.session_state.current_question_index = 1
            st.session_state.interview_state = 'asking'
            st.rerun()

def display_question_and_record():
    """Display current question, speak it, and handle recording"""
    
    # Progress indicator
    progress = st.session_state.current_question_index / st.session_state.max_questions
    st.progress(progress, text=f"Question {st.session_state.current_question_index}/{st.session_state.max_questions}")
    
    st.markdown("---")
    
    # Display and speak the current question
    speak_question(st.session_state.current_question, show_repeat_button=True)
    
    st.markdown("---")
    
    # Recording section
    st.markdown("### 🎙️ Record Your Response")
    
    # Use simple HTML5 recorder
    simple_audio_recorder()
    
    # Handle audio data (this would need to be implemented with proper state management)
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("📤 Submit Response", type="primary", disabled=st.session_state.audio_data is None):
            if st.session_state.audio_data:
                st.session_state.interview_state = 'processing'
                st.rerun()
            else:
                st.warning("Please record your response first!")
    
    with col2:
        if st.button("⏭️ Skip Question"):
            st.session_state.interview_state = 'processing'
            st.session_state.audio_data = None  # No audio for skipped question
            st.rerun()

def process_audio_response():
    """Process the recorded audio and move to next question"""
    
    st.markdown("### ⏳ Processing Your Response...")
    
    with st.spinner("Uploading and processing your audio response..."):
        # Upload audio if available
        upload_success = True
        if st.session_state.audio_data:
            upload_success = upload_audio_response_data(
                st.session_state.current_question, 
                st.session_state.audio_data
            )
        
        if upload_success:
            # Add current question to asked questions
            st.session_state.questions_asked.append({
                'question': st.session_state.current_question,
                'index': st.session_state.current_question_index
            })
            
            # Check if we've completed all questions
            if st.session_state.current_question_index >= st.session_state.max_questions:
                st.session_state.interview_state = 'complete'
            else:
                # Get next question
                next_question = get_next_question_data()
                if next_question:
                    st.session_state.current_question = next_question
                    st.session_state.current_question_index += 1
                    st.session_state.audio_data = None  # Reset audio data
                    st.session_state.interview_state = 'asking'
                else:
                    st.session_state.interview_state = 'complete'
        else:
            st.error("Failed to process your response. Please try again.")
            st.session_state.interview_state = 'asking'
    
    time.sleep(2)  # Brief pause for user feedback
    st.rerun()

def show_completion():
    """Show interview completion screen"""
    
    st.balloons()
    
    st.markdown("## 🎉 Interview Completed!")
    st.markdown("### Thank you for participating in the mock interview.")
    
    st.markdown("---")
    
    # Show summary
    st.markdown("### 📊 Interview Summary")
    st.markdown(f"**Questions Asked:** {len(st.session_state.questions_asked)}")
    st.markdown(f"**Total Duration:** {st.session_state.max_questions} questions")
    
    # Show questions asked
    with st.expander("📝 Questions Asked"):
        for i, q_data in enumerate(st.session_state.questions_asked, 1):
            st.markdown(f"**{i}.** {q_data['question']}")
    
    st.markdown("---")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("🔄 Start New Interview", type="primary"):
            # Reset session state
            for key in list(st.session_state.keys()):
                if key.startswith(('interview_', 'current_', 'total_', 'is_', 'audio_', 'questions_')):
                    del st.session_state[key]
            st.rerun()
    
    with col2:
        if st.button("📊 View Results"):
            st.info("Results processing feature coming soon!")

def main():
    """Main application function"""
    
    st.title("🎤 Mock Interview System")
    
    # Initialize session state
    initialize_session_state()
    
    # Check if email is available (assuming it's set elsewhere)
    if 'email' not in st.session_state:
        st.session_state.email = "user@example.com"  # Default for testing
    
    # State machine for interview flow
    if st.session_state.interview_state == 'start':
        start_interview()
    elif st.session_state.interview_state == 'asking':
        display_question_and_record()
    elif st.session_state.interview_state == 'processing':
        process_audio_response()
    elif st.session_state.interview_state == 'complete':
        show_completion()
    
    # Debug info (remove in production)
    with st.expander("🔧 Debug Info"):
        st.json({
            "interview_state": st.session_state.interview_state,
            "current_question_index": st.session_state.current_question_index,
            "total_questions_fetched": st.session_state.total_questions_fetched,
            "has_audio_data": st.session_state.audio_data is not None
        })

if __name__ == "__main__":
    main()