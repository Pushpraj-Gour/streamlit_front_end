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

# Configuration
MAX_QUESTIONS = 5

def initialize_interview_state():
    """Initialize session state for interview"""
    if 'interview_state' not in st.session_state:
        st.session_state.interview_state = 'start'
        st.session_state.current_question_index = 0
        st.session_state.current_question = ""
        st.session_state.total_questions_asked = 0
        st.session_state.questions_responses = []

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
            
        return question
        
    except Exception as e:
        st.error(f"❌ Error fetching next question: {str(e)}")
        return None

def create_direct_audio_recorder():
    """Create audio recorder that directly uploads to backend"""
    
    # Get backend URL - adjust this to match your FastAPI backend
    backend_url = "http://127.0.0.1:8081"  # Change this to your actual backend URL
    
    recorder_html = f"""
    <div style="text-align: center; margin: 20px 0; padding: 20px; background: #f8f9fa; border-radius: 10px;">
        <div id="recordingControls">
            <button id="recordBtn" onclick="toggleRecording()" style="
                background: linear-gradient(45deg, #FF6B6B, #FF8E8E);
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 25px;
                font-size: 16px;
                font-weight: bold;
                cursor: pointer;
                margin: 10px;
                transition: all 0.3s ease;
                box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3);
            ">
                🎤 Start Recording
            </button>
        </div>
        
        <div id="status" style="margin: 15px 0; font-weight: bold; color: #555; min-height: 25px;"></div>
        
        <div id="uploadProgress" style="margin: 15px 0; display: none;">
            <div style="background: #e9ecef; border-radius: 10px; overflow: hidden;">
                <div id="progressBar" style="background: linear-gradient(45deg, #4ECDC4, #44A08D); height: 10px; width: 0%; transition: width 0.3s ease;"></div>
            </div>
            <div id="progressText" style="margin-top: 5px; font-size: 14px; color: #666;"></div>
        </div>
    </div>

    <script>
    let mediaRecorder;
    let audioChunks = [];
    let isRecording = false;
    const BACKEND_URL = '{backend_url}';

    async function toggleRecording() {{
        const recordBtn = document.getElementById('recordBtn');
        const status = document.getElementById('status');

        if (!isRecording) {{
            await startRecording();
        }} else {{
            await stopRecordingAndUpload();
        }}
    }}

    async function startRecording() {{
        const recordBtn = document.getElementById('recordBtn');
        const status = document.getElementById('status');
        
        try {{
            const stream = await navigator.mediaDevices.getUserMedia({{ 
                audio: {{ 
                    echoCancellation: true,
                    noiseSuppression: true,
                    sampleRate: 44100 
                }} 
            }});
            
            // Use the best available format
            let options = {{}};
            if (MediaRecorder.isTypeSupported('audio/webm;codecs=opus')) {{
                options.mimeType = 'audio/webm;codecs=opus';
            }} else if (MediaRecorder.isTypeSupported('audio/webm')) {{
                options.mimeType = 'audio/webm';
            }} else if (MediaRecorder.isTypeSupported('audio/mp4')) {{
                options.mimeType = 'audio/mp4';
            }}
            
            mediaRecorder = new MediaRecorder(stream, options);
            audioChunks = [];

            mediaRecorder.ondataavailable = event => {{
                if (event.data.size > 0) {{
                    audioChunks.push(event.data);
                }}
            }};

            mediaRecorder.start();
            isRecording = true;
            
            recordBtn.innerHTML = '⏹️ Stop & Submit';
            recordBtn.style.background = 'linear-gradient(45deg, #28a745, #20c997)';
            status.innerHTML = '🔴 Recording... Click "Stop & Submit" when finished.';
            status.style.color = '#dc3545';
            
        }} catch (err) {{
            console.error('Error accessing microphone:', err);
            status.innerHTML = '❌ Microphone access denied. Please check permissions.';
            status.style.color = '#dc3545';
        }}
    }}

    async function stopRecordingAndUpload() {{
        const recordBtn = document.getElementById('recordBtn');
        const status = document.getElementById('status');
        const uploadProgress = document.getElementById('uploadProgress');
        const progressBar = document.getElementById('progressBar');
        const progressText = document.getElementById('progressText');
        
        if (mediaRecorder && mediaRecorder.state !== 'inactive') {{
            mediaRecorder.stop();
            mediaRecorder.stream.getTracks().forEach(track => track.stop());
        }}
        
        isRecording = false;
        recordBtn.disabled = true;
        recordBtn.innerHTML = '⏳ Processing...';
        recordBtn.style.background = '#6c757d';
        status.innerHTML = '⏳ Preparing upload...';
        status.style.color = '#ffc107';

        // Wait for recording to complete
        await new Promise(resolve => {{
            mediaRecorder.onstop = resolve;
        }});

        if (audioChunks.length === 0) {{
            status.innerHTML = '❌ No audio recorded. Please try again.';
            status.style.color = '#dc3545';
            resetRecorder();
            return;
        }}

        // Create blob and upload directly
        const audioBlob = new Blob(audioChunks, {{ 
            type: mediaRecorder.mimeType || 'audio/webm'
        }});
        
        await uploadAudioDirectly(audioBlob);
    }}

    async function uploadAudioDirectly(audioBlob) {{
        const status = document.getElementById('status');
        const uploadProgress = document.getElementById('uploadProgress');
        const progressBar = document.getElementById('progressBar');
        const progressText = document.getElementById('progressText');
        
        try {{
            // Show upload progress
            uploadProgress.style.display = 'block';
            status.innerHTML = '📤 Uploading your response...';
            status.style.color = '#007bff';
            
            // Create FormData
            const formData = new FormData();
            formData.append('audio_file', audioBlob, 'recording.webm');
            formData.append('question', '{st.session_state.get("current_question", "")}');
            
            // Upload with progress tracking
            const xhr = new XMLHttpRequest();
            
            xhr.upload.addEventListener('progress', (e) => {{
                if (e.lengthComputable) {{
                    const percentComplete = (e.loaded / e.total) * 100;
                    progressBar.style.width = percentComplete + '%';
                    progressText.innerHTML = `Uploading... ${{Math.round(percentComplete)}}%`;
                }}
            }});
            
            xhr.onload = function() {{
                if (xhr.status === 200) {{
                    try {{
                        const response = JSON.parse(xhr.responseText);
                        status.innerHTML = '✅ Response uploaded successfully!';
                        status.style.color = '#28a745';
                        progressText.innerHTML = 'Upload complete!';
                        
                        // Notify Streamlit of successful upload
                        window.parent.postMessage({{
                            type: 'streamlit:setComponentValue',
                            value: {{
                                action: 'upload_success',
                                response: response,
                                transcript: response.transcript || 'Audio processed successfully'
                            }}
                        }}, '*');
                        
                    }} catch (e) {{
                        console.error('Error parsing response:', e);
                        handleUploadError('Invalid response from server');
                    }}
                }} else {{
                    handleUploadError(`Server error: ${{xhr.status}}`);
                }}
            }};
            
            xhr.onerror = function() {{
                handleUploadError('Network error during upload');
            }};
            
            xhr.open('POST', `${{BACKEND_URL}}/interview/responses/upload`);
            xhr.send(formData);
            
        }} catch (error) {{
            console.error('Upload error:', error);
            handleUploadError('Failed to upload audio');
        }}
    }}

    function handleUploadError(errorMessage) {{
        const status = document.getElementById('status');
        const uploadProgress = document.getElementById('uploadProgress');
        
        status.innerHTML = `❌ ${{errorMessage}}`;
        status.style.color = '#dc3545';
        uploadProgress.style.display = 'none';
        
        // Notify Streamlit of upload failure
        window.parent.postMessage({{
            type: 'streamlit:setComponentValue',
            value: {{
                action: 'upload_error',
                error: errorMessage
            }}
        }}, '*');
        
        resetRecorder();
    }}

    function resetRecorder() {{
        const recordBtn = document.getElementById('recordBtn');
        const uploadProgress = document.getElementById('uploadProgress');
        
        recordBtn.disabled = false;
        recordBtn.innerHTML = '🎤 Start Recording';
        recordBtn.style.background = 'linear-gradient(45deg, #FF6B6B, #FF8E8E)';
        uploadProgress.style.display = 'none';
        audioChunks = [];
    }}

    // Handle skip functionality
    window.skipQuestion = function() {{
        window.parent.postMessage({{
            type: 'streamlit:setComponentValue',
            value: {{
                action: 'question_skipped'
            }}
        }}, '*');
    }};
    </script>
    """
    
    return components.html(recorder_html, height=280)

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
    
    # Use a key to get component return value
    audio_component = create_direct_audio_recorder()
    # with open("audio_component")
    
    # Check for JavaScript messages via component return value
    if audio_component is not None:
        # Handle upload success
        if isinstance(audio_component, dict) and audio_component.get('action') == 'upload_success':
            # Store the response
            transcript = audio_component.get('transcript', 'Audio processed successfully')
            st.session_state.questions_responses.append({
                'question': st.session_state.current_question,
                'response_status': 'RECORDED',
                'transcript': transcript,
                'question_number': st.session_state.current_question_index
            })
            
            st.success("✅ Response uploaded successfully!")
            
            # Move to next question or complete interview
            if st.session_state.current_question_index >= MAX_QUESTIONS:
                st.success("🎉 All questions completed!")
                st.balloons()
                st.session_state.interview_completed = True
                time.sleep(1)
                st.switch_page("pages/feedback.py")
            else:
                # Get next question
                with st.spinner("🔄 Loading next question..."):
                    next_question = get_next_question_data()
                    if next_question:
                        st.session_state.current_question = next_question
                        st.session_state.current_question_index += 1
                        st.session_state.total_questions_asked += 1
                        time.sleep(0.5)  # Brief pause for user feedback
                        st.rerun()
                    else:
                        st.error("❌ Failed to fetch next question.")
                        st.session_state.interview_state = 'complete'
                        st.rerun()
        
        # Handle upload error
        elif isinstance(audio_component, dict) and audio_component.get('action') == 'upload_error':
            error_msg = audio_component.get('error', 'Unknown error')
            st.error(f"❌ Upload failed: {error_msg}")
        
        # Handle question skip
        elif isinstance(audio_component, dict) and audio_component.get('action') == 'question_skipped':
            # Store skipped response
            st.session_state.questions_responses.append({
                'question': st.session_state.current_question,
                'response_status': 'SKIPPED',
                'transcript': 'Question skipped by user',
                'question_number': st.session_state.current_question_index
            })
            
            st.info("⏭️ Question skipped")
            
            # Move to next question
            if st.session_state.current_question_index >= MAX_QUESTIONS:
                st.session_state.interview_state = 'complete'
                st.rerun()
            else:
                with st.spinner("🔄 Loading next question..."):
                    next_question = get_next_question_data()
                    if next_question:
                        st.session_state.current_question = next_question
                        st.session_state.current_question_index += 1
                        st.session_state.total_questions_asked += 1
                        time.sleep(0.5)
                        st.rerun()
    
    # Control buttons
    st.markdown("---")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("⏭️ Skip Question", key=f"skip_{st.session_state.current_question_index}"):
            # Handle skip directly in Python
            st.session_state.questions_responses.append({
                'question': st.session_state.current_question,
                'response_status': 'SKIPPED',
                'transcript': 'Question skipped by user',
                'question_number': st.session_state.current_question_index
            })
            
            if st.session_state.current_question_index >= MAX_QUESTIONS:
                st.session_state.interview_state = 'complete'
                st.rerun()
            else:
                next_question = get_next_question_data()
                if next_question:
                    st.session_state.current_question = next_question
                    st.session_state.current_question_index += 1
                    st.session_state.total_questions_asked += 1
                    st.rerun()
    
    with col2:
        if st.button("🛑 End Interview", key="end_interview", type="secondary"):
            st.session_state.interview_state = 'complete'
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

def main():
    """Main interview simulator function"""
    
    # Check if user email exists
    if 'email' not in st.session_state or not st.session_state.email:
        st.error("❌ User session not found. Please login again.")
        st.switch_page("pages/login.py")
        return
    
    # Initialize interview state
    initialize_interview_state()
    
    # Simplified state machine - direct flow
    if st.session_state.interview_state == 'start':
        start_interview()
    elif st.session_state.interview_state == 'asking':
        display_question_and_record()
    elif st.session_state.interview_state == 'complete':
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