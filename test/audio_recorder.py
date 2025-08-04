import sys
import os
import io
import base64

# Add the parent directory (frontend_project) to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from audio_recorder.a import audio_recorder
import base64

st.title("🎙️ Fast Audio Recorder with JS")

audio_data = fast_audio_recorder()

if audio_data:
    audio_bytes = base64.b64decode(audio_data)
    st.audio(audio_bytes, format="audio/webm")
    st.download_button("Download recording", data=audio_bytes, file_name="recording.webm")
