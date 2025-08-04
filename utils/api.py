# 📁 utils/api.py
import requests
import logging
from typing import Optional, Dict, Any
from .logger import setup_logger, log_api_call

# Setup logger
logger = setup_logger("api")

API_BASE = "http://127.0.0.1:8081"

def _handle_api_response(response: requests.Response, endpoint: str, email: Optional[str] = None) -> Optional[Dict[Any, Any]]:
    """
    Handle API response with proper error logging.
    
    Args:
        response: requests.Response object
        endpoint: API endpoint called
        email: User email for logging context
        
    Returns:
        JSON response if successful, None if failed
    """
    try:
        response.raise_for_status()
        log_api_call(logger, endpoint, email, success=True)
        return response.json()
    except requests.exceptions.HTTPError as e:
        error_msg = f"HTTP {response.status_code}: {str(e)}"
        log_api_call(logger, endpoint, email, success=False, error_msg=error_msg)
        logger.error(f"API HTTP error for {endpoint}: {error_msg}")
        return None
    except requests.exceptions.ConnectionError as e:
        error_msg = f"Connection error: {str(e)}"
        log_api_call(logger, endpoint, email, success=False, error_msg=error_msg)
        logger.error(f"API connection error for {endpoint}: {error_msg}")
        return None
    except requests.exceptions.Timeout as e:
        error_msg = f"Timeout error: {str(e)}"
        log_api_call(logger, endpoint, email, success=False, error_msg=error_msg)
        logger.error(f"API timeout error for {endpoint}: {error_msg}")
        return None
    except requests.exceptions.RequestException as e:
        error_msg = f"Request error: {str(e)}"
        log_api_call(logger, endpoint, email, success=False, error_msg=error_msg)
        logger.error(f"API request error for {endpoint}: {error_msg}")
        return None
    except ValueError as e:
        error_msg = f"JSON decode error: {str(e)}"
        log_api_call(logger, endpoint, email, success=False, error_msg=error_msg)
        logger.error(f"API JSON decode error for {endpoint}: {error_msg}")
        return None

def register_user(payload):
    """Register a new user."""
    try:
        logger.info(f"Attempting to register user with email: {payload.get('email', 'unknown')}")
        res = requests.post(f"{API_BASE}/interview/candidates/register", json=payload)
        return res
    except Exception as e:
        logger.error(f"Error in register_user: {str(e)}")
        raise

def get_initial_question(email):
    """Get initial interview question for a candidate."""
    try:
        logger.info(f"Fetching initial question for email: {email}")
        res = requests.get(f"{API_BASE}/interview/candidates/{email}/interview-questions")
        return _handle_api_response(res, f"get_initial_question/{email}", email)
    except Exception as e:
        logger.error(f"Error in get_initial_question for {email}: {str(e)}")
        return None

def get_next_question():
    """Get next interview question."""
    try:
        logger.info("Fetching next interview question")
        res = requests.get(f"{API_BASE}/interview/next-question")
        return _handle_api_response(res, "get_next_question")
    except Exception as e:
        logger.error(f"Error in get_next_question: {str(e)}")
        return None

def upload_audio_response(question, audio_file):
    """Upload audio response for a question."""
    try:
        logger.info(f"Uploading audio response for question: {question[:50]}...")
        files = {
            "question": (None, question),
            "audio_file": ("response.wav", audio_file, "audio/wav")
        }
        res = requests.post(f"{API_BASE}/interview/responses/upload", files=files)
        return res
    except Exception as e:
        logger.error(f"Error in upload_audio_response: {str(e)}")
        raise

def get_feedback(email):
    """Get overall feedback for a candidate."""
    try:
        logger.info(f"Fetching feedback for email: {email}")
        res = requests.get(f"{API_BASE}/interview/candidate/{email}/overall/feedback")
        return _handle_api_response(res, f"get_feedback/{email}", email)
    except Exception as e:
        logger.error(f"Error in get_feedback for {email}: {str(e)}")
        return None

def login_user(email):
    """Login user and get their details."""
    try:
        logger.info(f"Attempting login for email: {email}")
        res = requests.get(f"{API_BASE}/interview/candidate/{email}")
        return _handle_api_response(res, f"login_user/{email}", email)
    except Exception as e:
        logger.error(f"Error in login_user for {email}: {str(e)}")
        return None

def get_candidate_interviews(email):
    """Get all interviews for a candidate."""
    try:
        logger.info(f"Fetching interviews for email: {email}")
        res = requests.get(f"{API_BASE}/interview/candidate/{email}/interviews")
        return _handle_api_response(res, f"get_candidate_interviews/{email}", email)
    except Exception as e:
        logger.error(f"Error in get_candidate_interviews for {email}: {str(e)}")
        return None

def get_interview_feedback(interview_id):
    """Get feedback for a specific interview."""
    try:
        logger.info(f"Fetching feedback for interview ID: {interview_id}")
        res = requests.get(f"{API_BASE}/interview/{interview_id}/feedback")
        return _handle_api_response(res, f"get_interview_feedback/{interview_id}")
    except Exception as e:
        logger.error(f"Error in get_interview_feedback for {interview_id}: {str(e)}")
        return None
# You can expand this file with more endpoints as needed
