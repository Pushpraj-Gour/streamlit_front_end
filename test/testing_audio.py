import streamlit as st
import os
from datetime import datetime

SAVE_DIR = "recordings"
os.makedirs(SAVE_DIR, exist_ok=True)

st.title("🎙️ Audio Recorder App (Simple Version)")

# Record new audio
st.header("🛎️ Record a New Voice Clip")

audio_data = st.audio_input("Tap the mic to record")  # ✅ removed `type` argument

if audio_data:
    filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".wav"
    filepath = os.path.join(SAVE_DIR, filename)

    with open(filepath, "wb") as f:
        f.write(audio_data.getvalue())

    st.success(f"✅ Recording saved as: {filename}")
    st.audio(audio_data)

# List existing recordings
st.markdown("### 🎵 Saved Recordings")

recorded_files = sorted(os.listdir(SAVE_DIR), reverse=True)

if recorded_files:
    for file in recorded_files:
        file_path = os.path.join(SAVE_DIR, file)
        st.audio(file_path)
        st.caption(file)
else:
    st.info("No recordings yet. Record something above! 🎤")
