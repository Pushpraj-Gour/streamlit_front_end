import sys
import os
import io
import base64

# Add the parent directory (frontend_project) to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.api import login_user
import json
import streamlit as st
import streamlit.components.v1 as components
import time
from pages.pages_2 import initial_question, next_question, upload_audio, speak_question, record_audio
from utils.text_to_speech_util import speak_question

def main():
    st.title("Mock Interview Helper")
    # first_question = initial_question()
    first_question = "What are the fundamental differences between supervised and unsupervised learning?"

    # st.write("Question:", first_question)
    # list_of_questions = [
    #     "What are the fundamental differences between supervised and unsupervised learning?",
    #     "Can you explain the concept of overfitting in machine learning?",
    #     "What is the purpose of cross-validation in model evaluation?",
    #     "How do you handle missing data in a dataset?",
    #     "What is the difference between classification and regression tasks?",
    #     "Can you explain the bias-variance tradeoff?",
    #     "What are some common metrics used to evaluate classification models?",
    #     "How do you select important features for a machine learning model?",
    #     "What is the role of hyperparameter tuning in model optimization?",
    #     "Can you explain the concept of ensemble learning?"
    # ]
    # for question in list_of_questions:
    #     speak_question(first_question)
    #     time.sleep(5)  # Simulate time for speaking the question

    


if __name__ == "__main__":
    st.session_state.email = "rajrjpushp@gmail.com"
    st.session_state.logged_in = True
    st.session_state.role = "AI/ML Engineer"
    st.session_state.name = "Pushpraj Gour"
    st.session_state.skills = "Python, C, SQL, TensorFlow, OpenCV, PyTorch, FastAPI, Keras, Scikit-Learn, streamlit, Seaborn, NumPy, Pandas, Matplotlib"
    st.session_state.projects = None
    st.session_state.education = "B.Tech in Electrnoics and communication from RGPV University 2024"
    st.session_state.achievements = "Awarded Best Innovator in 2022, Published research paper on AI"
    st.session_state.experience = "2 years at ABC Corp as a Data Scientist, 1 year at DEF Ltd as a Machine Learning Engineer"
    main()