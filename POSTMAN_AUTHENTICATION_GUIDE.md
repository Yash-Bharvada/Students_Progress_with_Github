# Postman Authentication Guide

## Overview

This guide provides comprehensive instructions for testing the Student Progress Backend authentication system using Postman. The authentication system implements GitHub OAuth 2.0 Authorization Code Flow with strict role-based access control.

## Authentication Flow Requirements

The system enforces the following authentication rules:

- **Requirements 1.5**: Issue JWT for existing users
- **Requirements 1.6**: Create mentor users if they don't exist  
- **Requirements 1.7**: Deny access for non-enrolled students with 403 Forbidden
- **Requirements 2.4**: Prevent student self-registration

## Test Scenarios

### 1. Mentor Authentication Success

**Scenario**: New or existing mentor logs in via GitHub OAuth

**Steps**:
1. Use "Step 1: GitHub OAuth Login" to get authorization URL
2. Complete OAuth flow in browser
3. Use "Step 2: Mentor Login Success" with authorization code
4. Verify JWT token is issued and mentor role is assigned

**Expected Outcome**:
- Status: 200 OK
- JWT token issued
- User role: MENTOR
- is_enrolled: true

### 2. Enrolled Student Authentication Success

**Scenario**: Student who was pre-enrolled by a mentor logs in

**Prerequisites**: 
- Student must be enrolled by mentor using `enrollStudent` mutation
- Student GitHub username must match enrollment record

**Steps**:
1. Ensure student is enrolled (use enrollStudent mutation)
2. Complete OAuth flow for enrolled student
3. Use "Step 3: Enrolled Student Login Success" with authorization code
4. Verify JWT token is issued for student

**Expected Outcome**:
- Status: 200 OK
- JWT token issued
- User role: STUDENT
- is_enrolled: true

### 3. Non-Enrolled Student Access Denial

**Scenario**: Student who was NOT pre-enrolled attempts to login

**Steps**:
1. Use GitHub account that has NOT been enrolled by any mentor
2. Complete OAuth flow
3. Use "Step 4: Non-Enrolled Student Login (403 Forbidden)" with authorization code
4. Verify access is denied with 403 Forbidden

**Expected Outcome**:
- Status: 403 Forbidden
- Error message: "Access denied. Student is not enrolled. Please contact a mentor for enrollment."

## Error Scenarios

### OAuth Errors

1. **Invalid Authorization Code**
   - Request: "OAuth Error - Invalid Code"
   - Expected: 400 Bad Request with OAuth error message

2. **Missing Authorization Code**
   - Request: "OAuth Error - Missing Code"  
   - Expected: 400 Bad Request with "Authorization code is required"

### JWT Token Errors

1. **Invalid JWT Token**
   - Request: "Invalid JWT Token"
   - Expected: 401 Unauthorized with token validation error

2. **Expired JWT Token**
   - Request: "Expired JWT Token"
   - Expected: 401 Unauthorized with "Token has expired"

### Authorization Errors

1. **Student Attempting Mentor Operation**
   - Request: "Student Trying Mentor Operation (403 Forbidden)"
   - Expected: GraphQL error with "User must be a mentor"

2. **Mentor Attempting Student Operation**
   - Request: "Mentor Trying Student-Only Operation"
   - Expected: GraphQL error with "User must be a student"

## Environment Variables

Set these variables in your Postman environment:

### Required Variables
- `base_url`: API base URL (default: http://localhost:8000)
- `auth_code`: Authorization code from GitHub OAuth callback
- `student_auth_code`: Auth code for enrolled student testing
- `non_enrolled_student_code`: Auth code for non-enrolled student testing

### Auto-Populated Variables
- `jwt_token`: Current JWT token (auto-set from OAuth success)
- `mentor_jwt_token`: Mentor JWT token (auto-set)
- `student_jwt_token`: Student JWT token (auto-set)
- `current_user_role`: Current user's role (auto-set)
- `current_user_github_id`: Current user's GitHub ID (auto-set)

### Optional Variables
- `oauth_state`: State parameter for CSRF protection
- `expired_jwt_token`: Expired token for testing expiration handling

## Testing Workflow

### Complete Authentication Test

1. **Setup Phase**
   ```
   1. Start with "Step 1: GitHub OAuth Login"
   2. Complete OAuth in browser for mentor account
   3. Run "Step 2: Mentor Login Success"
   4. Verify mentor JWT token is saved
   ```

2. **Student Enrollment Phase**
   ```
   1. Use mentor JWT to run "Enroll Student" mutation
   2. Enroll a test student with their GitHub username
   3. Verify enrollment success
   ```

3. **Student Authentication Phase**
   ```
   1. Complete OAuth flow for enrolled student
   2. Run "Step 3: Enrolled Student Login Success"
   3. Verify student JWT token is saved
   ```

4. **Error Testing Phase**
   ```
   1. Test non-enrolled student with "Step 4: Non-Enrolled Student Login"
   2. Test invalid codes with OAuth error scenarios
   3. Test authorization violations with role-based error scenarios
   ```

### JWT Token Validation

Use "JWT Token Validation Test" to verify any JWT token:
- Tests token validity
- Returns user profile information
- Validates token claims and expiration

## Common Issues and Solutions

### Issue: OAuth Code Expired
**Solution**: OAuth codes expire quickly (usually 10 minutes). Generate a new code by repeating the OAuth flow.

### Issue: Student Not Enrolled Error
**Solution**: Ensure the student was properly enrolled by a mentor using the `enrollStudent` mutation before attempting login.

### Issue: Invalid JWT Token
**Solution**: 
1. Check token format (should start with "eyJ")
2. Verify token hasn't expired
3. Ensure proper Authorization header format: "Bearer <token>"

### Issue: Role-Based Access Denied
**Solution**: Verify you're using the correct JWT token for the operation:
- Use `mentor_jwt_token` for mentor operations
- Use `student_jwt_token` for student operations

## Security Considerations

1. **JWT Token Security**: Tokens contain sensitive user information. Store securely and don't log in production.

2. **OAuth State Parameter**: Use the `oauth_state` parameter to prevent CSRF attacks in production.

3. **Token Expiration**: JWT tokens expire after the configured time (default: 24 hours). Implement token refresh in production applications.

4. **Role Validation**: Always validate user roles on the server side. Client-side role checks are insufficient for security.

## API Endpoints Reference

### Authentication Endpoints
- `GET /auth/github/login` - Initiate OAuth flow
- `GET /auth/github/callback` - Handle OAuth callback
- `GET /auth/me` - Get current user profile
- `POST /auth/logout` - Logout (client-side token disposal)
- `GET /auth/health` - Authentication service health check

### GraphQL Endpoint
- `POST /graphql` - All GraphQL queries and mutations

## Requirements Validation Matrix

| Requirement | Test Scenario | Postman Request |
|-------------|---------------|-----------------|
| 1.1 | OAuth login redirect | Step 1: GitHub OAuth Login |
| 1.2 | Code exchange | Step 2: Mentor Login Success |
| 1.3 | User profile fetch | Step 2: Mentor Login Success |
| 1.4 | User validation | Step 2: Mentor Login Success |
| 1.5 | JWT for existing users | Step 2: Mentor Login Success |
| 1.6 | Mentor auto-creation | Step 2: Mentor Login Success |
| 1.7 | Non-enrolled student denial | Step 4: Non-Enrolled Student Login |
| 2.4 | Student self-registration prevention | Step 4: Non-Enrolled Student Login |
| 7.1-7.4 | JWT token management | JWT Token Validation Test |
| 9.1-9.2 | Error handling | Error Scenarios folder |

This comprehensive test suite validates all authentication requirements and provides examples for both success and error scenarios.