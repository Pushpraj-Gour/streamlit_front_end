import streamlit as st
import requests
import time

# The simple audio recorder library
from streamlit_mic_recorder import mic_recorder

# --- Configuration ---
MAX_QUESTIONS = 5
BACKEND_URL = "http://127.0.0.1:8081" # Make sure this is your backend URL

# --- Helper Functions for Backend Communication ---

def get_question_from_backend(email, index):
    """Fetches a question. Gets the first question if index is 0."""
    try:
        if index == 0:
            url = f"{BACKEND_URL}/interview/candidates/{email}/interview-questions"
        else:
            url = f"{BACKEND_URL}/interview/next-question"
            
        response = requests.get(url)
        response.raise_for_status() # Raise an error for bad status codes
        data = response.json()
        
        if data.get("status") == "success":
            return data.get("data", {}).get("question")
        else:
            st.error(f"Backend Error: {data.get('message', 'Unknown error')}")
            return None
            
    except requests.exceptions.RequestException as e:
        st.error(f"Network Error: Could not connect to the backend. Please ensure it is running. Error: {e}")
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
        response = requests.post(url, files=files, data=payload)
        response.raise_for_status()
        
        return response.json()
        
    except requests.exceptions.RequestException as e:
        st.error(f"Upload Failed: Could not send audio to the backend. Error: {e}")
        return None

# --- Main Application Logic ---

def main():
    st.title("🎤 Mock AI Interview")

    # Initialize all necessary session state variables
    if "interview_state" not in st.session_state:
        st.session_state.interview_state = "welcome"
        st.session_state.email = "rajrjpushp@gmail.com" # Mock email
        st.session_state.current_question = ""
        st.session_state.current_question_index = 0

    # --- STATE 1: WELCOME SCREEN ---
    if st.session_state.interview_state == "welcome":
        st.header("Ready to Start?")
        st.info("This is a mock interview where you will answer 5 questions. Your responses will be recorded and analyzed.")
        if st.button("🚀 Let's Begin!", type="primary"):
            st.session_state.interview_state = "loading_question"
            st.rerun()

    # --- STATE 2: LOADING THE QUESTION ---
    elif st.session_state.interview_state == "loading_question":
        with st.spinner("Fetching your next question..."):
            question = get_question_from_backend(st.session_state.email, st.session_state.current_question_index)
            if question:
                st.session_state.current_question = question
                st.session_state.current_question_index += 1
                st.session_state.interview_state = "showing_question"
                st.rerun()
            else:
                st.error("Could not fetch a question. Please try again.")
                st.session_state.interview_state = "welcome" # Go back to start

    # --- STATE 3: SHOWING THE QUESTION & DIRECT SUBMISSION ---
    elif st.session_state.interview_state == "showing_question":
        st.header(f"Question {st.session_state.current_question_index}/{MAX_QUESTIONS}")
        st.markdown(f"### {st.session_state.current_question}")
        st.write("---")
        
        # This is where the magic happens!
        # The mic_recorder widget is called, and if it returns audio,
        # we process it immediately in the same step.
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

    # --- STATE 4: FINISHED ---
    elif st.session_state.interview_state == "finished":
        st.balloons()
        st.success("🎉 Interview Complete!")
        st.header("Thank you for participating.")
        
        if st.button("Start Over"):
            # Clear all session data to reset the app
            for key in st.session_state.keys():
                del st.session_state[key]
            st.rerun()

if __name__ == "__main__":
    main()