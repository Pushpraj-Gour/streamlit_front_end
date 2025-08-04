#!/usr/bin/env python3
"""
Test script to verify logging and error handling functionality.
Run this script to test the logging setup before running the main application.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.logger import setup_logger, log_user_action, log_api_call
from utils.api import get_candidate_interviews, login_user

def test_logging():
    """Test basic logging functionality."""
    print("Testing logging functionality...")
    
    # Setup logger
    logger = setup_logger("test")
    
    # Test different log levels
    logger.info("Testing INFO level logging")
    logger.warning("Testing WARNING level logging")
    logger.error("Testing ERROR level logging")
    
    # Test user action logging
    log_user_action(logger, "Test user action", email="test@example.com", test_param="test")
    
    # Test API call logging
    log_api_call(logger, "test_endpoint", email="test@example.com", success=True)
    log_api_call(logger, "test_endpoint", email="test@example.com", success=False, error_msg="Test error")
    
    print("✅ Logging test completed. Check logs/ directory for log files.")

def test_api_error_handling():
    """Test API error handling."""
    print("Testing API error handling...")
    
    # Test with invalid email (should handle gracefully)
    result = login_user("invalid@example.com")
    if result is None:
        print("✅ API error handling working correctly (returned None for invalid user)")
    else:
        print("⚠️  API error handling may need improvement")
    
    # Test with empty email
    result = get_candidate_interviews("")
    if result is None:
        print("✅ API error handling working correctly (returned None for empty email)")
    else:
        print("⚠️  API error handling may need improvement")

def test_log_file_creation():
    """Test that log files are created properly."""
    print("Testing log file creation...")
    
    import os
    from datetime import datetime
    
    log_dir = "logs"
    log_filename = f"app_{datetime.now().strftime('%Y%m%d')}.log"
    log_path = os.path.join(log_dir, log_filename)
    
    if os.path.exists(log_path):
        print(f"✅ Log file created successfully: {log_path}")
        
        # Check if file has content
        with open(log_path, 'r') as f:
            content = f.read()
            if content.strip():
                print(f"✅ Log file has content ({len(content)} characters)")
            else:
                print("⚠️  Log file is empty")
    else:
        print(f"❌ Log file not found: {log_path}")

def main():
    """Run all tests."""
    print("🔍 Running logging and error handling tests...\n")
    
    test_logging()
    print()
    
    test_api_error_handling()
    print()
    
    test_log_file_creation()
    print()
    
    print("🎉 All tests completed!")
    print("\nNext steps:")
    print("1. Check the logs/ directory for log files")
    print("2. Review log content to ensure proper formatting")
    print("3. Run the Streamlit application to test in real environment")

if __name__ == "__main__":
    main()
