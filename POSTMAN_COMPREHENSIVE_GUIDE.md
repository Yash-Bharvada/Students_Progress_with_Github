# Student Progress Backend - Comprehensive Postman Collection Guide

## Overview

This comprehensive Postman collection provides complete testing capabilities for the Student Progress Backend API, including GitHub OAuth authentication, GraphQL operations, role-based authorization testing, error scenarios, and AI-powered feedback system testing.

## Collection Structure

### 1. Authentication Folder
Complete GitHub OAuth 2.0 Authorization Code Flow implementation with comprehensive testing scenarios:

- **OAuth Flow Steps**: Login redirect, callback handling, token extraction
- **Success Scenarios**: Mentor auto-creation, enrolled student login
- **Error Scenarios**: Non-enrolled student denial, invalid codes, missing parameters
- **JWT Management**: Token validation, expiration handling, manual token setup

### 2. GraphQL Queries Folder
Role-based GraphQL query operations with proper authorization:

- **getMe**: Current user profile (IsAuthenticated)
- **getRepositories**: Role-filtered repository access (IsAuthenticated)
- **getMyContributionMetrics**: Student's own metrics (IsStudent)
- **getAllContributionMetrics**: All student metrics for repository (IsMentor)
- **Authorization Tests**: Cross-role access denial validation

### 3. GraphQL Mutations Folder
Role-restricted GraphQL mutation operations with comprehensive validation:

- **enrollStudent**: Student enrollment by mentors (IsMentor)
- **createRepository**: Repository creation by mentors (IsMentor)
- **saveContributionMetrics**: Student metrics saving (IsStudent)
- **Input Validation**: Error handling for invalid data
- **Authorization Tests**: Cross-role operation denial validation

### 4. Authorization Testing Folder
Comprehensive permission class validation:

- **IsAuthenticated**: Valid/invalid token testing
- **IsMentor**: Mentor-only operation validation
- **IsStudent**: Student-only operation validation
- **IsOwnerOrMentor**: Data access control validation
- **Role-Based Summary**: Complete authorization validation

### 5. Error Scenarios Folder
Complete error handling and edge case testing:

- **Authentication Errors**: Missing, invalid, expired tokens
- **Authorization Errors**: Role-based access violations
- **OAuth Errors**: Invalid codes, missing parameters
- **System Errors**: Database connectivity, service health

### 6. AI Feedback System Folder
AI-powered code quality feedback with LLM integration:

- **generateAIFeedback**: AI feedback generation (role-based access)
- **getMyAIFeedback**: Student's own feedback history (IsStudent)
- **getAllAIFeedback**: All student feedback access (IsMentor)
- **Authorization Tests**: AI feedback access control validation
- **Error Handling**: Invalid repository, AI service failure testing

## Environment Variables

### Authentication Variables
- `jwt_token`: General JWT token for authenticated requests
- `mentor_jwt_token`: Mentor-specific JWT token
- `student_jwt_token`: Student-specific JWT token
- `expired_jwt_token`: Expired token for testing expiration handling

### OAuth Variables
- `auth_code`: Authorization code from GitHub callback
- `student_auth_code`: Auth code for enrolled student testing
- `non_enrolled_student_code`: Auth code for non-enrolled student (403 test)
- `oauth_state`: State parameter for CSRF protection

### Data Variables (Auto-populated)
- `repository_id`: Repository ID from createRepository mutation
- `enrolled_student_github_id`: Student GitHub ID from enrollStudent mutation
- `contribution_metrics_id`: Metrics ID from saveContributionMetrics mutation
- `ai_feedback_id`: AI feedback ID from generateAIFeedback mutation

### User Context Variables (Auto-populated)
- `current_user_github_id`: Current user's GitHub ID
- `current_user_role`: Current user's role (MENTOR/STUDENT)

### System Variables
- `base_url`: API base URL (default: http://localhost:8000)
- `request_timestamp`: Current request timestamp
- `last_response_timestamp`: Last response timestamp

## Pre-Request Scripts

### Automatic JWT Token Management
The collection includes comprehensive pre-request scripts that:

1. **Token Validation**: Automatically checks JWT token expiration
2. **User Context**: Extracts and sets user information from tokens
3. **Token Selection**: Automatically uses appropriate token (mentor/student/general)
4. **Environment Setup**: Auto-populates missing environment variables
5. **Request Logging**: Logs request details for debugging

### Token Expiration Handling
- Automatically detects expired JWT tokens
- Provides clear warnings and instructions for re-authentication
- Extracts user information from valid tokens

## Post-Response Scripts

### Automatic Data Extraction
The collection includes global post-response scripts that:

1. **Token Extraction**: Automatically saves JWT tokens from OAuth callbacks
2. **ID Extraction**: Auto-saves important IDs (repository, student, metrics, feedback)
3. **User Context**: Sets user context variables from authentication responses
4. **Error Logging**: Logs GraphQL errors with detailed information
5. **Performance Monitoring**: Tracks response times and logs slow requests

### GraphQL Response Validation
- Validates GraphQL response format
- Logs operation success/failure
- Extracts and logs GraphQL errors

## Usage Instructions

### 1. Initial Setup
1. Import the collection and environment files into Postman
2. Set the `base_url` environment variable (default: http://localhost:8000)
3. Ensure the backend server is running

### 2. Authentication Flow
1. **Start OAuth Flow**: Run "Step 1: GitHub OAuth Login"
2. **Complete OAuth**: Follow redirect URL in browser, authorize application
3. **Extract Code**: Copy authorization code from callback URL
4. **Complete Login**: Run appropriate callback request (mentor/student)
5. **Verify Tokens**: JWT tokens are automatically saved to environment

### 3. Testing Workflow
1. **Authentication**: Complete OAuth flow for both mentor and student users
2. **Data Setup**: Use mentor token to enroll students and create repositories
3. **Student Operations**: Use student token to save contribution metrics
4. **AI Feedback**: Generate and retrieve AI feedback with appropriate roles
5. **Authorization Testing**: Run cross-role access tests to verify security
6. **Error Testing**: Test various error scenarios and edge cases

### 4. Role-Based Testing
- **Mentor Operations**: Use `{{mentor_jwt_token}}` for mentor-only operations
- **Student Operations**: Use `{{student_jwt_token}}` for student-only operations
- **General Operations**: Use `{{jwt_token}}` for general authenticated operations

## Requirements Coverage

### Authentication & Authorization (Requirements 1, 2, 7)
- ✅ GitHub OAuth complete flow testing
- ✅ JWT token management and validation
- ✅ Role-based access control enforcement
- ✅ Non-enrolled student access denial

### GraphQL Operations (Requirements 3, 4, 5, 6)
- ✅ Student enrollment by mentors
- ✅ Repository management by mentors
- ✅ Contribution metrics by students
- ✅ Role-based query access control

### Data Management (Requirements 8, 9)
- ✅ MongoDB data persistence validation
- ✅ Error handling and security measures
- ✅ Input validation and data integrity

### System Configuration (Requirements 10)
- ✅ Environment variable management
- ✅ Production deployment configuration testing

### AI Feedback System (Requirements 11, 12, 13)
- ✅ AI feedback generation and analysis
- ✅ Role-based AI feedback authorization
- ✅ AI feedback data management and integrity

## Testing Best Practices

### 1. Sequential Testing
Run requests in logical order:
1. Authentication → Data Setup → Operations → Validation

### 2. Environment Management
- Use separate environments for development/staging/production
- Keep sensitive tokens secure
- Regularly refresh expired tokens

### 3. Error Validation
- Always test both success and failure scenarios
- Verify proper error messages and status codes
- Test authorization boundaries thoroughly

### 4. Data Cleanup
- Use test data that can be safely created/modified
- Consider cleanup procedures for test environments
- Avoid using production data for testing

## Troubleshooting

### Common Issues

1. **Missing JWT Token**
   - Ensure OAuth flow is completed successfully
   - Check that tokens are saved to environment variables
   - Verify token hasn't expired

2. **Authorization Denied**
   - Verify using correct token type (mentor vs student)
   - Check user role matches operation requirements
   - Ensure user is properly enrolled (for students)

3. **GraphQL Errors**
   - Check request body format and variables
   - Verify required fields are provided
   - Review GraphQL schema for correct field names

4. **Environment Variables**
   - Ensure all required variables are set
   - Check variable names match exactly
   - Verify base_url points to correct server

### Debug Information
The collection provides extensive logging:
- Request/response details
- Token validation status
- User context information
- Performance metrics
- Error details

## Security Considerations

### Token Management
- JWT tokens are marked as secret in environment
- Tokens are automatically validated for expiration
- Clear warnings for security issues

### Authorization Testing
- Comprehensive cross-role access testing
- Proper error message validation
- Security boundary verification

### Data Protection
- Student data access restrictions validated
- Mentor-only operations properly protected
- Self-only data access enforced for students

## Integration with Development Workflow

### Continuous Testing
- Use collection runner for automated testing
- Integrate with CI/CD pipelines
- Monitor API changes and compatibility

### Documentation
- Collection serves as living API documentation
- Examples provide implementation guidance
- Error scenarios help with error handling

### Collaboration
- Shared environment for team testing
- Consistent testing procedures
- Standardized error validation

This comprehensive Postman collection ensures thorough testing of all Student Progress Backend functionality while providing clear documentation and automated workflows for efficient development and testing processes.