import streamlit as st
import streamlit.components.v1 as components
from streamlit_webrtc import webrtc_streamer, WebRtcMode
import time
import requests
from io import BytesIO

st.set_page_config(page_title="Mock Interview", page_icon="🎤", layout="centered")

# Initialize session state
if "interview_started" not in st.session_state:
    st.session_state.interview_started = False
if "question_index" not in st.session_state:
    st.session_state.question_index = 0
if "recording_count" not in st.session_state:
    st.session_state.recording_count = 0
if "is_recording" not in st.session_state:
    st.session_state.is_recording = False
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "question_spoken_at" not in st.session_state:
    st.session_state.question_spoken_at = 0

# Dummy question list
questions = [
    "How do you handle missing values in a Pandas DataFrame?",
    "What is the difference between supervised and unsupervised learning?",
    "Explain the concept of overfitting in machine learning."
]
st.session_state.questions = questions


def speak_question(text):
    # Triggers browser TTS
    components.html(f"""
    <script>
        var msg = new SpeechSynthesisUtterance("{text}");
        window.speechSynthesis.speak(msg);
    </script>
    """, height=0)
    # Mark time spoken for delay logic
    st.session_state.question_spoken_at = time.time()


def start_interview():
    st.session_state.interview_started = True
    st.session_state.question_index = 0
    st.session_state.recording_count = 0
    speak_question(st.session_state.questions[0])


def advance_question():
    st.session_state.question_index += 1
    speak_question(st.session_state.questions[st.session_state.question_index])


def handle_audio_upload(audio_data, question):
    # Replace with your actual API
    url = "http://your-backend-api/submit_audio"
    files = {'file': ("response.wav", audio_data, "audio/wav")}
    data = {'question': question}
    response = requests.post(url, files=files, data=data)

    if response.status_code == 200:
        st.success("✅ Answer submitted.")
        return True
    else:
        st.error("❌ Failed to submit audio.")
        return False


# UI
st.title("🎤 Mock Interview")

if not st.session_state.interview_started:
    st.button("▶️ Start Interview", on_click=start_interview)
else:
    idx = st.session_state.question_index
    question = st.session_state.questions[idx]

    st.markdown(f"### Question {idx + 1}/3")
    st.markdown(f"**{question}**")

    # Speak the question (once)
    if "last_question_spoken" not in st.session_state or st.session_state.last_question_spoken != idx:
        speak_question(question)
        st.session_state.last_question_spoken = idx

    st.success("✅ Ready to record your answer.")
    
    # Recording button
    if "is_recording" not in st.session_state:
        st.session_state.is_recording = False

    button_label = "⏺️ Start Recording" if not st.session_state.is_recording else "⏹️ Stop Recording"

    if st.button(button_label, key=f"record_button_{idx}"):
        st.session_state.is_recording = not st.session_state.is_recording

        if not st.session_state.is_recording:
            # Recording stopped — capture and send audio
            webrtc_ctx = st.session_state.get("webrtc_ctx")
            if webrtc_ctx and webrtc_ctx.audio_receiver:
                audio_frames = webrtc_ctx.audio_receiver.get_frames(timeout=2)
                if audio_frames:
                    audio_bytes = b"".join([f.to_ndarray().tobytes() for f in audio_frames])
                    audio_io = BytesIO(audio_bytes)
                    st.audio(audio_io, format="audio/webm")

                    if handle_audio_upload(audio_io.getvalue(), question):
                        st.session_state.recording_count += 1
                        if st.session_state.recording_count >= 3:
                            st.success("✅ All questions answered.")
                            st.session_state.interview_started = False
                            st.switch_page("pages/feedback.py")
                        else:
                            advance_question()
                        st.rerun()

    # Always start webrtc when question is shown
    st.session_state.webrtc_ctx = webrtc_streamer(
        key=f"audio_stream_{idx}",
        mode=WebRtcMode.SENDRECV,
        rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
        media_stream_constraints={"video": False, "audio": True},
        audio_receiver_size=1024,
        sendback_audio=False,
    )

    st.divider()
    st.markdown(f"📝 Questions answered: `{st.session_state.recording_count}/3`")
    if st.button("🛑 End Interview Early"):
        st.session_state.interview_started = False
        st.switch_page("pages/feedback.py")
