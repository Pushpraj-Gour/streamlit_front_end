# Logging and Error Handling Guide

## Overview
This Streamlit application now includes comprehensive logging and error handling to improve debugging, monitoring, and user experience.

## Logging Features

### 1. Logger Setup
- **Location**: `utils/logger.py`
- **Features**:
  - File and console logging
  - Daily log rotation
  - Structured log messages
  - User action tracking
  - API call monitoring

### 2. Log Levels
- **INFO**: General application flow, user actions, successful operations
- **WARNING**: Non-critical issues, missing data, fallback behaviors
- **ERROR**: Critical errors, API failures, exceptions
- **DEBUG**: Detailed debugging information (only in development)

### 3. Log File Location
- **Directory**: `logs/`
- **Format**: `app_YYYYMMDD.log`
- **Example**: `logs/app_20250804.log`

### 4. Log Message Format
```
2025-08-04 10:30:15,123 - dashboard - INFO - section:65 - User action: Dashboard accessed | Context: email=user@example.com, role=Software Engineer
```

## Error Handling Features

### 1. API Error Handling
- **Connection errors**: Network issues, server unavailable
- **HTTP errors**: 4xx and 5xx status codes
- **Timeout errors**: Slow or unresponsive API
- **JSON parsing errors**: Malformed response data
- **Request errors**: General request failures

### 2. User Interface Error Handling
- **Graceful degradation**: Show meaningful error messages to users
- **Fallback content**: Display alternative content when data is unavailable
- **Input validation**: Prevent invalid data submission
- **Session state protection**: Handle missing or corrupted session data

### 3. Data Validation
- **Type checking**: Ensure data types match expectations
- **Null/empty checks**: Handle missing or empty data gracefully
- **Format validation**: Validate dates, emails, and other formatted data

## Implementation Examples

### 1. Dashboard Page (`pages/dashboard.py`)
- ✅ User authentication logging
- ✅ API call error handling
- ✅ Data validation for interview history
- ✅ Safe date formatting
- ✅ Graceful fallbacks for missing data

### 2. API Module (`utils/api.py`)
- ✅ Request timeout handling
- ✅ HTTP status code checking
- ✅ Connection error handling
- ✅ JSON parsing error handling
- ✅ Comprehensive logging for all API calls

## Usage Guidelines

### 1. For Developers
```python
from utils.logger import setup_logger, log_user_action, log_api_call

# Setup logger for your module
logger = setup_logger("module_name")

# Log user actions
log_user_action(logger, "User clicked button", email="user@example.com", button="submit")

# Log API calls
log_api_call(logger, "POST /api/register", email="user@example.com", success=True)

# General logging
logger.info("Operation completed successfully")
logger.warning("Non-critical issue detected")
logger.error("Critical error occurred")
```

### 2. Error Handling Pattern
```python
try:
    # Risky operation
    result = some_api_call()
    logger.info("API call successful")
    return result
except ConnectionError as e:
    logger.error(f"Connection failed: {str(e)}")
    st.error("Unable to connect to server. Please try again later.")
    return None
except Exception as e:
    logger.error(f"Unexpected error: {str(e)}")
    st.error("An unexpected error occurred. Please contact support.")
    return None
```

## Monitoring and Debugging

### 1. Log Analysis
- Check `logs/` directory for daily log files
- Search for ERROR level messages for critical issues
- Monitor API call success rates
- Track user action patterns

### 2. Common Issues
- **API timeouts**: Check network connectivity and server status
- **Authentication failures**: Verify user credentials and session state
- **Data parsing errors**: Check API response format and data types
- **UI rendering issues**: Check for missing data and validation errors

### 3. Performance Monitoring
- Monitor log file sizes (automatic daily rotation)
- Track API response times
- Monitor error rates and patterns

## Configuration

### 1. Log Level Configuration
Modify `utils/logger.py` to change log levels:
```python
logger.setLevel(logging.DEBUG)  # For development
logger.setLevel(logging.INFO)   # For production
```

### 2. Log File Configuration
Adjust log file settings in `utils/logger.py`:
```python
log_filename = f"{logs_dir}/app_{datetime.now().strftime('%Y%m%d')}.log"
```

## Best Practices

### 1. Logging
- Log user actions for audit trails
- Include context in log messages (user email, IDs, etc.)
- Use appropriate log levels
- Avoid logging sensitive information (passwords, API keys)

### 2. Error Handling
- Always handle exceptions in user-facing code
- Provide meaningful error messages to users
- Log technical details for developers
- Implement graceful fallbacks

### 3. Performance
- Use lazy evaluation for debug messages
- Rotate logs regularly to manage disk space
- Monitor log file sizes and performance impact

## Troubleshooting

### 1. Logging Issues
- **No log files created**: Check directory permissions for `logs/`
- **Empty log files**: Verify logger configuration and log levels
- **Performance issues**: Check log file sizes and rotation settings

### 2. Error Handling Issues
- **Unhandled exceptions**: Add try-catch blocks around risky operations
- **User confusion**: Improve error messages and fallback content
- **Silent failures**: Add appropriate logging for all error conditions

## Future Enhancements

1. **Structured Logging**: Implement JSON-formatted logs for better parsing
2. **External Monitoring**: Integration with monitoring services (e.g., Sentry)
3. **Metrics Collection**: Add performance and usage metrics
4. **Alert System**: Automated alerts for critical errors
5. **Log Aggregation**: Centralized logging for multiple instances
