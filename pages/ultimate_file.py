import streamlit as st
import requests

# The simple audio recorder library
from streamlit_mic_recorder import mic_recorder

# --- Configuration ---
MAX_QUESTIONS = 5
BACKEND_URL = "http://127.0.0.1:8081" # Your backend URL

# --- Backend Helper Functions ---
def get_question_from_backend(email, index):
    """Fetches a question from the backend."""
    try:
        url = f"{BACKEND_URL}/interview/candidates/{email}/interview-questions" if index == 0 else f"{BACKEND_URL}/interview/next-question"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data.get("data", {}).get("question") if data.get("status") == "success" else None
    except requests.exceptions.RequestException:
        st.error("Network Error: Could not connect to the backend.")
        return None

def upload_audio_to_backend(audio_bytes, question_text):
    """Uploads audio to the backend."""
    if not audio_bytes: return None
    try:
        files = {'audio_file': ('response.wav', audio_bytes, 'audio/wav')}
        payload = {'question': question_text}
        url = f"{BACKEND_URL}/interview/responses/upload"
        response = requests.post(url, files=files, data=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        st.error("Upload Failed: Could not send audio to the backend.")
        return None

# --- Main Application ---
def main():
    st.title("🎤 Mock AI Interview")

    # Initialize the application's state
    if "interview_state" not in st.session_state:
        st.session_state.interview_state = "welcome"
        st.session_state.email = "rajrjpushp@gmail.com"
        st.session_state.current_question_index = 0
        st.session_state.audio_bytes = None

    # State 1: Welcome Screen
    if st.session_state.interview_state == "welcome":
        if st.button("🚀 Let's Begin!", type="primary"):
            st.session_state.interview_state = "loading_question"
            st.rerun()

    # State 2: Fetching the Question from the Backend
    elif st.session_state.interview_state == "loading_question":
        with st.spinner("Fetching question..."):
            question = get_question_from_backend(st.session_state.email, st.session_state.current_question_index)
            if question:
                st.session_state.current_question = question
                st.session_state.current_question_index += 1
                st.session_state.audio_bytes = None
                st.session_state.interview_state = "showing_question"
                st.rerun()
            else:
                st.session_state.interview_state = "welcome"

    # State 3: Showing Question and Recording UI
    elif st.session_state.interview_state == "showing_question":
        st.header(f"Question {st.session_state.current_question_index}/{MAX_QUESTIONS}")
        st.markdown(f"### {st.session_state.current_question}")
        
        audio = mic_recorder(start_prompt="⏺️ Record Answer", stop_prompt="⏹️ Stop", key='recorder')

        if audio:
            st.session_state.audio_bytes = audio['bytes']
            st.session_state.interview_state = "processing_answer"
            st.rerun()
            
    # State 4: User has recorded, ready to submit
    elif st.session_state.interview_state == "processing_answer":
        st.success("✅ Answer recorded.")
        st.audio(st.session_state.audio_bytes)
        
        if st.button("Submit and Continue", type="primary"):
            with st.spinner("Submitting..."):
                upload_audio_to_backend(st.session_state.audio_bytes, st.session_state.current_question)
                
                if st.session_state.current_question_index >= MAX_QUESTIONS:
                    st.session_state.interview_state = "finished"
                else:
                    st.session_state.interview_state = "loading_question"
            st.rerun()

    # State 5: Interview Finished
    elif st.session_state.interview_state == "finished":
        st.balloons()
        st.success("🎉 Interview Complete!")
        if st.button("Start Over"):
            for key in st.session_state.keys(): del st.session_state[key]
            st.rerun()

if __name__ == "__main__":
    main()