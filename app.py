# import streamlit as st
# import requests

# API_BASE = "http://127.0.0.1:8081"

# # Session state initialization
# if 'page' not in st.session_state:
#     st.session_state.page = 'landing'
# if 'email' not in st.session_state:
#     st.session_state.email = ''
# if 'user_data' not in st.session_state:
#     st.session_state.user_data = {}

# # Navigation helper
# def navigate(page):
#     st.session_state.page = page

# # === Landing Page ===
# def landing_page():
#     st.title("🎤 Mock Interview Simulator")
#     st.write("Practice real interviews, get feedback, and level up your skills.")

#     st.button("Existing User", on_click=lambda: navigate('existing_user'))
#     st.button("New User", on_click=lambda: navigate('new_user'))

# # === Existing User Page ===
# def existing_user_page():
#     st.title("🔐 Existing User Login")
#     email = st.text_input("Enter your email", key="login_email")
#     if st.button("Login"):
#         try:
#             res = requests.get(f"{API_BASE}/interview/candidate/{email}")
#             if res.ok and res.json().get("status") == "success":
#                 st.session_state.email = email
#                 st.session_state.user_data = res.json().get("data", {})
#                 navigate('dashboard')
#             else:
#                 st.warning("User not found. Redirecting to registration...")
#                 navigate('new_user')
#         except Exception as e:
#             st.error(f"Error: {e}")
#             navigate('new_user')

# # === New User Page ===
# def new_user_page():
#     st.title("🆕 New User Registration")
#     with st.form("register_form"):
#         name = st.text_input("Name")
#         email = st.text_input("Email")
#         role = st.text_input("Role")
#         skills = st.text_area("Skills")
#         projects = st.text_area("Projects")
#         education = st.text_area("Education")
#         achievements = st.text_area("Achievements")
#         experience = st.text_area("Experience")

#         submitted = st.form_submit_button("Register")
#         if submitted:
#             payload = {
#                 "candidate_name": name,
#                 "candidate_email": email,
#                 "role": role,
#                 "skills": skills,
#                 "projects": projects,
#                 "education": education,
#                 "achievements": achievements,
#                 "experience": experience
#             }
#             try:
#                 res = requests.post(f"{API_BASE}/interview/candidates/register", json=payload)
#                 if res.status_code == 201:
#                     st.session_state.email = email
#                     st.success("Registered successfully.")
#                     navigate("dashboard")
#                 else:
#                     st.error("Registration failed.")
#             except Exception as e:
#                 st.error(f"Error: {e}")

# # === Dashboard Page ===
# def dashboard_page():
#     st.title("🏠 Dashboard")
#     st.write(f"Welcome, {st.session_state.email}")
#     st.json(st.session_state.user_data)

#     if st.button("Start New Interview"):
#         navigate("interview")

#     if st.button("View Feedback"):
#         navigate("feedback")

# # === Interview Page ===
# def interview_page():
#     st.title("🎙️ Interview Session")
#     if "questions" not in st.session_state:
#         try:
#             res = requests.get(f"{API_BASE}/interview/candidates/{st.session_state.email}/interview-questions")
#             data = res.json()
#             if data.get("status") == "success":
#                 st.session_state.questions = [data["data"]["question"]]
#                 st.session_state.question_index = 0
#             else:
#                 st.error(data.get("message", "Failed to fetch question"))
#                 return
#         except Exception as e:
#             st.error(f"Error fetching questions: {e}")
#             return

#     question = st.session_state.questions[st.session_state.question_index]
#     st.write(f"**Question {st.session_state.question_index + 1}:** {question}")
#     answer = st.text_area("Your answer here")

#     if st.button("Submit Response"):
#         try:
#             res = requests.post(
#                 f"{API_BASE}/interview/responses/upload",
#                 data={"question": question, "text_response": answer}
#             )
#             if res.ok:
#                 st.success("Response submitted.")
#                 st.session_state.question_index += 1
#                 if st.session_state.question_index >= 3:
#                     st.success("Interview complete.")
#                     navigate("feedback")
#                 else:
#                     res = requests.get(f"{API_BASE}/interview/next-question")
#                     q = res.json().get("data", {}).get("question")
#                     if q:
#                         st.session_state.questions.append(q)
#             else:
#                 st.error("Failed to submit.")
#         except Exception as e:
#             st.error(f"Error: {e}")

# # === Feedback Page ===
# def feedback_page():
#     st.title("📝 Feedback Report")
#     try:
#         res = requests.get(f"{API_BASE}/interview/candidate/overall/feedback")
#         data = res.json()
#         if data.get("status") == "success":
#             overall = data["data"]["overall_feedback"]
#             questions = data["data"]["feedback_by_question"]
#             st.subheader("📊 Overall Feedback")
#             st.write(overall)

#             st.subheader("🔍 Per-Question Feedback")
#             for qf in questions:
#                 st.markdown(f"**Q:** {qf['question']}")
#                 st.write(f"**Score:** {qf['overall_score']}/10")
#                 st.write(f"**Reasoning:** {qf['overall_reasoning']}")
#                 st.markdown("---")
#         else:
#             st.warning(data.get("message", "No feedback found."))
#     except Exception as e:
#         st.error(f"Error: {e}")

# # === Page Router ===
# pages = {
#     "landing": landing_page,
#     "existing_user": existing_user_page,
#     "new_user": new_user_page,
#     "dashboard": dashboard_page,
#     "interview": interview_page,
#     "feedback": feedback_page
# }

# pages[st.session_state.page]()
