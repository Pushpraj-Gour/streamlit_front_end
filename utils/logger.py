import logging
import os
from datetime import datetime

from typing import Optional

def setup_logger(name: str = "streamlit_app") -> logging.Logger:
    """
    Set up a logger with file and console handlers.
    
    Args:
        name: Logger name
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger
    
    logger.setLevel(logging.INFO)
    
    # Create logs directory if it doesn't exist
    logs_dir = "logs"
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    # File handler
    log_filename = f"{logs_dir}/app_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_filename)
    file_handler.setLevel(logging.INFO)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def log_user_action(logger: logging.Logger, action: str, email: Optional[str] = None, **kwargs):
    """
    Log user actions with consistent format.
    
    Args:
        logger: Logger instance
        action: Action description
        email: User email (optional)
        **kwargs: Additional context
    """
    context = f"email={email}" if email else ""
    if kwargs:
        extra_context = ", ".join([f"{k}={v}" for k, v in kwargs.items()])
        context = f"{context}, {extra_context}" if context else extra_context
    
    log_message = f"User action: {action}"
    if context:
        log_message += f" | Context: {context}"
    
    logger.info(log_message)

def log_api_call(logger: logging.Logger, endpoint: str, email: Optional[str] = None, success: bool = True, error_msg: Optional[str] = None):
    """
    Log API calls with consistent format.
    
    Args:
        logger: Logger instance
        endpoint: API endpoint called
        email: User email (optional)
        success: Whether the call was successful
        error_msg: Error message if failed
    """
    status = "SUCCESS" if success else "FAILED"
    log_message = f"API call {status}: {endpoint}"
    
    if email:
        log_message += f" | User: {email}"
    
    if not success and error_msg:
        log_message += f" | Error: {error_msg}"
    
    if success:
        logger.info(log_message)
    else:
        logger.error(log_message)
