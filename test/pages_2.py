import streamlit as st
import streamlit.components.v1 as components
from streamlit_webrtc import webrtc_streamer, WebRtcMode
import time
import requests
from io import BytesIO
from utils.api import get_initial_question, get_next_question, upload_audio_response
from utils.text_to_speech_util import speak_question

st.set_page_config(page_title="Mock Interview", page_icon="🎤", layout="centered")

st.session_state.total_questions_fetched = 0


def initial_question():  # Working
    initial_question = get_initial_question(st.session_state.email)
    if initial_question.get("status") != "success":
        st.error("Failed to fetch initial question. Please try again later.")
        st.stop()
    question = initial_question.get("data", {}).get("question", "")

    st.session_state.total_questions_fetched += 1

    return question

def next_question():
    next_question = get_next_question()
    if next_question.get("status") != "success":
        st.error("Failed to fetch next question. Please try again later.")
        st.stop()
    question = next_question.get("data", {}).get("question", "")
    st.session_state.total_questions_fetched += 1

    return question

def upload_audio(question, audio_data):
    response = upload_audio_response(question, audio_data)
    if response.status_code != 200:
        st.error("Failed to upload audio response. Please try again later.")
        return False
    return True

def record_audio():
    pass

def main():
    st.title("🎤 Mock Interview")

    first_question = initial_question()

    st.session_state.current_question = first_question
    st.session_state.question_index = 1

    speak_question(first_question)   # The function which claude wrote along with it we want to record the audio response


    for i in range(4): # Total 4 questions to ask
        next_question_button = st.button("Next Question", key="next_question_button")

        question = next_question()
        st.session_state.current_question = question
        st.session_state.question_index += 1
        speak_question(question)

    
















