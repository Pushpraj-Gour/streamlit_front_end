# 📁 utils/api.py
import requests

API_BASE = "http://127.0.0.1:8081"

def register_user(payload):
    res = requests.post(f"{API_BASE}/interview/candidates/register", json=payload)
    return res

def get_initial_question(email):
    res = requests.get(f"{API_BASE}/interview/candidates/{email}/interview-questions")
    return res.json()

def get_next_question():
    return requests.get(f"{API_BASE}/interview/next-question").json()

def upload_audio_response(question, audio_file):

    files = {
        "question": (None, question),
        "audio_file": ("response.wav", audio_file, "audio/wav")}
    res = requests.post(f"{API_BASE}/interview/responses/upload", files=files)
    return res

def get_feedback(email):
    res = requests.get(f"{API_BASE}/interview/candidate/{email}/overall/feedback")
    return res.json()

def login_user(email):
    res = requests.get(f"{API_BASE}/interview/candidate/{email}")
    return res.json()

def get_candidate_interviews(email):
    res = requests.get(f"{API_BASE}/interview/candidate/{email}/interviews")
    return res.json()

def get_interview_feedback(interview_id):
    res = requests.get(f"{API_BASE}/interview/{interview_id}/feedback")
    return res.json()
# You can expand this file with more endpoints as needed
