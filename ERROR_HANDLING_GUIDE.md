# Error Handling Guide

## Overview

The Student Progress Backend implements comprehensive error handling throughout the application with proper HTTP status codes, structured error responses, and detailed logging. This guide provides examples of all error scenarios and their expected responses.

## Error Response Format

All errors follow a consistent JSON structure:

```json
{
  "error": "ERROR_CODE",
  "message": "Human-readable error message",
  "details": {
    "additional": "context information"
  }
}
```

## Error Categories

### 1. Authentication Errors (401 Unauthorized)

#### Missing Authorization Header
**Request:** GET `/auth/me` without Authorization header
**Response:**
```json
{
  "error": "AUTHENTICATION_ERROR",
  "message": "Authorization header is required",
  "details": {
    "missing_header": "Authorization"
  }
}
```

#### Invalid Bearer Token Format
**Request:** GET `/auth/me` with `Authorization: InvalidFormat`
**Response:**
```json
{
  "error": "AUTHENTICATION_ERROR",
  "message": "Bearer token is required",
  "details": {
    "invalid_format": "Expected 'Bearer <token>'"
  }
}
```

#### Expired JWT Token
**Request:** Any authenticated endpoint with expired token
**Response:**
```json
{
  "error": "JWT_ERROR",
  "message": "Token has expired",
  "details": {}
}
```

#### Invalid JWT Signature
**Request:** Any authenticated endpoint with tampered token
**Response:**
```json
{
  "error": "JWT_ERROR",
  "message": "Invalid token signature",
  "details": {}
}
```

### 2. Authorization Violations (403 Forbidden)

#### Student Not Enrolled
**Request:** OAuth callback for non-enrolled student
**Response:**
```json
{
  "error": "STUDENT_NOT_ENROLLED",
  "message": "Student 'username' is not enrolled. Please contact a mentor for enrollment.",
  "details": {
    "github_id": "123456"
  }
}
```

#### Insufficient Permissions
**GraphQL Error:** Student trying to access mentor-only mutation
**Response:**
```json
{
  "data": null,
  "errors": [
    {
      "message": "INSUFFICIENT_PERMISSIONS: Insufficient permissions for 'enroll_student'. Required role: MENTOR",
      "locations": [{"line": 1, "column": 1}],
      "path": ["enrollStudent"]
    }
  ]
}
```

#### Wrong Role Access
**GraphQL Error:** Mentor trying to access student-only query
**Response:**
```json
{
  "data": null,
  "errors": [
    {
      "message": "Student access required. This operation is restricted to students only.",
      "locations": [{"line": 1, "column": 1}],
      "path": ["getMyContributionMetrics"]
    }
  ]
}
```

### 3. Validation Errors (400 Bad Request)

#### Empty Required Fields
**GraphQL Error:** Empty username/email in enrollment
**Response:**
```json
{
  "data": null,
  "errors": [
    {
      "message": "INVALID_INPUT: Invalid github_username: GitHub username is required and cannot be empty",
      "locations": [{"line": 1, "column": 1}],
      "path": ["enrollStudent"]
    }
  ]
}
```

#### Invalid Email Format
**GraphQL Error:** Malformed email address
**Response:**
```json
{
  "data": null,
  "errors": [
    {
      "message": "INVALID_INPUT: Invalid email: Invalid email format",
      "locations": [{"line": 1, "column": 1}],
      "path": ["enrollStudent"]
    }
  ]
}
```

#### Invalid URL Format
**GraphQL Error:** Invalid repository URL
**Response:**
```json
{
  "data": null,
  "errors": [
    {
      "message": "INVALID_INPUT: Invalid repo_url: Repository URL must be a valid HTTP/HTTPS URL",
      "locations": [{"line": 1, "column": 1}],
      "path": ["createRepository"]
    }
  ]
}
```

#### Invalid Metric Values
**GraphQL Error:** Negative commit count or invalid consistency score
**Response:**
```json
{
  "data": null,
  "errors": [
    {
      "message": "INVALID_INPUT: Invalid commit_count: Commit count must be non-negative",
      "locations": [{"line": 1, "column": 1}],
      "path": ["saveContributionMetrics"]
    }
  ]
}
```

#### Invalid ObjectId Format
**GraphQL Error:** Malformed MongoDB ObjectId
**Response:**
```json
{
  "data": null,
  "errors": [
    {
      "message": "INVALID_INPUT: Invalid repo_id: Invalid repository ID format: invalid-id",
      "locations": [{"line": 1, "column": 1}],
      "path": ["getAllContributionMetrics"]
    }
  ]
}
```

### 4. Not Found Errors (404 Not Found)

#### User Not Found
**Request:** Valid JWT but user doesn't exist in database
**Response:**
```json
{
  "error": "USER_NOT_FOUND",
  "message": "User not found: github_123456",
  "details": {
    "github_id": "github_123456"
  }
}
```

#### Repository Not Found
**GraphQL Error:** Accessing non-existent repository
**Response:**
```json
{
  "data": null,
  "errors": [
    {
      "message": "REPOSITORY_NOT_FOUND: Repository not found: 507f1f77bcf86cd799439011",
      "locations": [{"line": 1, "column": 1}],
      "path": ["saveContributionMetrics"]
    }
  ]
}
```

### 5. Conflict Errors (409 Conflict)

#### Duplicate Resource
**GraphQL Error:** Creating repository with existing URL
**Response:**
```json
{
  "data": null,
  "errors": [
    {
      "message": "DUPLICATE_RESOURCE: Repository already exists: https://github.com/existing/repo",
      "locations": [{"line": 1, "column": 1}],
      "path": ["createRepository"]
    }
  ]
}
```

### 6. Database Errors (500 Internal Server Error)

#### Database Connection Failure
**Request:** Any operation when database is unavailable
**Response:**
```json
{
  "error": "DATABASE_ERROR",
  "message": "Database operation failed: user lookup",
  "details": {
    "operation": "user_lookup",
    "original_error": "Connection timeout"
  }
}
```

### 7. External Service Errors (502 Bad Gateway)

#### GitHub OAuth Failure
**Request:** OAuth callback with GitHub service error
**Response:**
```json
{
  "error": "GITHUB_OAUTH_ERROR",
  "message": "GitHub OAuth failed",
  "details": {
    "service": "github_oauth",
    "original_error": "Network timeout"
  }
}
```

#### Missing OAuth Code
**Request:** OAuth callback without authorization code
**Response:**
```json
{
  "error": "VALIDATION_ERROR",
  "message": "Authorization code is required",
  "details": {
    "missing_parameter": "code"
  }
}
```

### 8. Health Check Errors (503 Service Unavailable)

#### Service Unhealthy
**Request:** GET `/health` when services are down
**Response:**
```json
{
  "status": "unhealthy",
  "error": "HEALTH_CHECK_ERROR",
  "message": "Health check failed",
  "details": {
    "error_type": "DatabaseConnectionError"
  }
}
```

## Error Logging

All errors are logged with appropriate levels:

- **ERROR**: 5xx server errors, database failures, unexpected exceptions
- **WARNING**: 4xx client errors, authentication failures, authorization violations
- **INFO**: Successful operations, user actions
- **DEBUG**: Detailed operation information (development only)

### Log Format

```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "ERROR",
  "message": "Database error during user lookup",
  "error_code": "DATABASE_ERROR",
  "details": {
    "operation": "user_lookup",
    "github_id": "123456"
  },
  "context": {
    "endpoint": "/auth/me",
    "method": "GET",
    "user_agent": "PostmanRuntime/7.32.3"
  }
}
```

## Testing Error Scenarios

### Using Postman Collection

Import the `postman_error_handling_examples.json` collection to test all error scenarios:

1. **Authentication Errors**: Test missing/invalid tokens
2. **Authorization Violations**: Test role-based access control
3. **Validation Errors**: Test input validation with invalid data
4. **Database Errors**: Test with database connectivity issues
5. **External Service Errors**: Test GitHub OAuth failures

### Environment Variables

Set these variables in your Postman environment:

- `base_url`: `http://localhost:8000`
- `mentor_token`: Valid JWT token for mentor user
- `student_token`: Valid JWT token for student user
- `valid_token_for_nonexistent_user`: Valid JWT format but non-existent user

### Test Scenarios

1. **Authentication Flow**:
   - Test missing Authorization header
   - Test invalid token formats
   - Test expired tokens
   - Test invalid signatures

2. **Authorization Flow**:
   - Test non-enrolled student login
   - Test cross-role access violations
   - Test insufficient permissions

3. **Input Validation**:
   - Test empty required fields
   - Test invalid formats (email, URL, ObjectId)
   - Test out-of-range values
   - Test negative numbers

4. **Resource Management**:
   - Test accessing non-existent resources
   - Test creating duplicate resources
   - Test database connectivity issues

## Error Handling Best Practices

### For Developers

1. **Always use structured exceptions** from `backend/exceptions.py`
2. **Log errors with context** using the `log_error` utility
3. **Provide meaningful error messages** that help users understand the issue
4. **Include relevant details** without exposing sensitive information
5. **Use appropriate HTTP status codes** for different error types

### For API Consumers

1. **Always check HTTP status codes** before processing responses
2. **Parse error responses** to get structured error information
3. **Handle different error types** appropriately in your application
4. **Log client-side errors** for debugging and monitoring
5. **Provide user-friendly error messages** based on error codes

### Error Recovery

1. **Authentication Errors**: Redirect to login or refresh tokens
2. **Authorization Errors**: Show access denied message or request permissions
3. **Validation Errors**: Highlight invalid fields and show correction hints
4. **Not Found Errors**: Show "resource not found" message or redirect
5. **Server Errors**: Show generic error message and retry option

## Monitoring and Alerting

### Key Metrics to Monitor

- **Error Rate**: Percentage of requests resulting in errors
- **Error Distribution**: Breakdown by error type and status code
- **Response Times**: Including error response times
- **Authentication Failures**: Rate of failed login attempts
- **Authorization Violations**: Potential security issues

### Alert Thresholds

- **Critical**: 5xx error rate > 5%
- **Warning**: 4xx error rate > 20%
- **Info**: Authentication failure rate > 10%

### Log Analysis

Use structured logging to analyze:
- Most common error types
- Error patterns by user role
- Geographic distribution of errors
- Time-based error trends