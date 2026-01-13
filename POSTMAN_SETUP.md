# Postman Collection Setup Guide

This guide explains how to set up and use the Postman collection for testing the Student Progress Backend API.

## Files Included

- `postman_collection.json` - Complete API collection with all endpoints
- `postman_environment.json` - Environment variables for testing
- `POSTMAN_SETUP.md` - This setup guide

## Import Instructions

### 1. Import Collection
1. Open Postman
2. Click "Import" button
3. Select `postman_collection.json`
4. The collection "Student Progress Backend API" will be added

### 2. Import Environment
1. Click the gear icon (⚙️) in the top right
2. Select "Import"
3. Select `postman_environment.json`
4. Select "Student Progress Backend Environment" from the environment dropdown

## Collection Structure

### 📁 Authentication
- **GitHub OAuth Login** - Initiates OAuth flow
- **GitHub OAuth Callback** - Handles callback and extracts JWT token

### 📁 GraphQL Queries
- **Get Current User (getMe)** - Get authenticated user profile
- **Get Repositories** - Get repositories based on user role
- **Get My Contribution Metrics** - Student's own metrics
- **Get All Contribution Metrics** - All student metrics (mentor only)

### 📁 GraphQL Mutations
- **Enroll Student** - Enroll new student (mentor only)
- **Create Repository** - Create new repository (mentor only)
- **Save Contribution Metrics** - Save student metrics (student only)

### 📁 Error Scenarios
- **Unauthorized Request** - Test without JWT token
- **Invalid Token** - Test with invalid JWT
- **Student Trying Mentor Operation** - Test authorization violations

## OAuth Flow Testing Steps

### Complete OAuth 2.0 Authorization Code Flow

The collection provides a complete OAuth 2.0 flow implementation:

1. **Authorization Request** (`/auth/github/login`):
   - Generates GitHub authorization URL with proper scopes
   - Includes state parameter for CSRF protection
   - Redirects user to GitHub for authorization

2. **Authorization Grant** (User interaction):
   - User authorizes application on GitHub
   - GitHub redirects back with authorization code
   - Code is extracted from callback URL

3. **Access Token Request** (`/auth/github/callback`):
   - Exchanges authorization code for access token
   - Fetches user profile from GitHub API
   - Validates user against database
   - Issues JWT token for authenticated sessions

4. **Protected Resource Access**:
   - Uses JWT token for GraphQL API requests
   - Validates token on each request
   - Enforces role-based access control

### JWT Token Management Examples

#### Token Creation Response Format
```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "github_id": "12345",
    "username": "john_doe", 
    "email": "john@example.com",
    "role": "MENTOR"
  }
}
```

#### Token Usage in Requests
```http
POST /graphql
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
Content-Type: application/json

{
  "query": "query GetMe { getMe { id username role } }"
}
```

#### Token Validation Errors
```json
{
  "errors": [
    {
      "message": "Token has expired",
      "extensions": {
        "code": "UNAUTHENTICATED"
      }
    }
  ]
}
```

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `base_url` | API base URL | `http://localhost:8000` |
| `jwt_token` | Current user's JWT token | Auto-extracted from auth |
| `student_jwt_token` | Student JWT for testing | Manual entry |
| `mentor_jwt_token` | Mentor JWT for testing | Manual entry |
| `repository_id` | Repository ID for testing | Auto-extracted |
| `auth_code` | GitHub OAuth code | Manual entry |
| `github_username` | Test GitHub username | `test_student` |
| `student_email` | Test student email | `student@example.com` |
| `repo_name` | Test repository name | `Sample Project` |
| `repo_url` | Test repository URL | `https://github.com/mentor/sample-project` |

## Testing Workflow

### 1. Complete GitHub OAuth Authentication Flow

#### Step 1: Initiate OAuth Flow
1. **Start OAuth Request**:
   - Open "Authentication > Step 1: GitHub OAuth Login"
   - Send the request
   - The response will contain a redirect URL to GitHub

2. **Authorize on GitHub**:
   - Copy the authorization URL from the response
   - Open the URL in your browser
   - Click "Authorize" on GitHub's OAuth page
   - GitHub will redirect to: `http://localhost:8000/auth/github/callback?code=AUTHORIZATION_CODE`

3. **Extract Authorization Code**:
   - Copy the `code` parameter from the callback URL
   - Set the `auth_code` environment variable in Postman with this value

#### Step 2: Complete OAuth Flow and Extract JWT Token
1. **Exchange Code for Token**:
   - Open "Authentication > Step 2: GitHub OAuth Callback"
   - Ensure `{{auth_code}}` variable is properly set
   - Send the request

2. **Automatic JWT Token Extraction**:
   - The response will contain a JWT token
   - Post-response script automatically extracts and saves the token
   - Check the Postman console for confirmation messages:
     ```
     ✓ JWT token saved to environment variable: jwt_token
     ✓ User info saved - Role: MENTOR
     ```

3. **Validate Authentication**:
   - Open "Authentication > JWT Token Validation Test"
   - Send the request to confirm authentication is working
   - Should return your user profile information

#### Step 3: JWT Token Format and Structure

The JWT token follows this structure:
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJnaXRodWJfaWQiOiIxMjM0NSIsInVzZXJuYW1lIjoiam9obl9kb2UiLCJlbWFpbCI6ImpvaG5AZXhhbXBsZS5jb20iLCJyb2xlIjoiTUVOVE9SIiwiaWF0IjoxNjQwOTk1MjAwLCJleHAiOjE2NDA5OTg4MDB9.signature
```

**Token Claims:**
- `github_id`: User's GitHub ID
- `username`: GitHub username
- `email`: User's email address
- `role`: MENTOR or STUDENT
- `iat`: Issued at timestamp
- `exp`: Expiration timestamp (24 hours default)
- `iss`: Issuer (student-progress-tracker)
- `aud`: Audience (student-progress-api)

### 2. JWT Token Extraction Examples

#### Automatic Token Extraction Script
The collection includes this post-response script for automatic token handling:

```javascript
// Extract JWT token from OAuth callback response
if (pm.response.code === 200) {
    const responseJson = pm.response.json();
    if (responseJson.token) {
        pm.environment.set('jwt_token', responseJson.token);
        console.log('✓ JWT token saved to environment variable: jwt_token');
        
        // Also save user info for reference
        if (responseJson.user) {
            pm.environment.set('current_user_role', responseJson.user.role);
            pm.environment.set('current_user_github_id', responseJson.user.github_id);
            console.log('✓ User info saved - Role:', responseJson.user.role);
        }
    }
} else {
    console.log('❌ Authentication failed:', pm.response.text());
}
```

#### Manual Token Setup
For testing with existing tokens:

1. **Set Token Manually**:
   - Go to Environment variables
   - Set `jwt_token` to your existing JWT token
   - Or use "Authentication > Manual JWT Token Setup" request

2. **Token Validation**:
   - Use "JWT Token Validation Test" to verify token is valid
   - Check token expiration and claims

### 3. Test User Operations
1. **Get Current User**:
   - Run "Get Current User (getMe)"
   - Verify user profile information

2. **Test Role-Based Operations**:
   - If mentor: Test repository creation and student enrollment
   - If student: Test contribution metrics saving

### 3. Test Authorization
1. **Test Without Token**:
   - Run "Unauthorized Request (No Token)"
   - Should return authentication error

2. **Test Invalid Token**:
   - Run "Invalid Token"
   - Should return token validation error

3. **Test Role Violations**:
   - Use student token for mentor operations
   - Should return 403 Forbidden

## GraphQL Query Examples

### Get Current User
```graphql
query GetMe {
  getMe {
    id
    githubId
    username
    email
    role
    isEnrolled
    enrolledBy
    createdAt
  }
}
```

### Enroll Student (Mentor Only)
```graphql
mutation EnrollStudent($githubUsername: String!, $email: String!) {
  enrollStudent(githubUsername: $githubUsername, email: $email) {
    id
    githubId
    username
    email
    role
    isEnrolled
    enrolledBy
    createdAt
  }
}
```

### Save Contribution Metrics (Student Only)
```graphql
mutation SaveContributionMetrics(
  $repoId: String!,
  $commitCount: Int!,
  $prCount: Int!,
  $issueCount: Int!,
  $consistencyScore: Float!
) {
  saveContributionMetrics(
    repoId: $repoId,
    commitCount: $commitCount,
    prCount: $prCount,
    issueCount: $issueCount,
    consistencyScore: $consistencyScore
  ) {
    id
    repoId
    studentGithubId
    commitCount
    prCount
    issueCount
    consistencyScore
    lastUpdated
  }
}
```

## Pre-Request Scripts

The collection includes automatic scripts that:
- Extract JWT tokens from authentication responses
- Save repository IDs for use in other requests
- Validate token availability before requests

## Testing Tips

1. **Multiple User Testing**:
   - Save different JWT tokens in separate environment variables
   - Switch tokens to test different user roles

2. **Error Testing**:
   - Use the Error Scenarios folder to test edge cases
   - Verify proper error messages and status codes

3. **Data Flow Testing**:
   - Create repository → Save metrics → Query metrics
   - Test the complete data flow for each user type

4. **Authorization Testing**:
   - Test each operation with different user roles
   - Verify proper access control enforcement

## Troubleshooting

### Common Issues

1. **"No JWT token found"**:
   - Complete the authentication flow first
   - Check that `jwt_token` environment variable is set

2. **"Database not connected"**:
   - Ensure MongoDB is running and accessible
   - Check connection string in `.env` file

3. **"GitHub OAuth failed"**:
   - Verify GitHub OAuth app configuration
   - Check client ID and secret in `.env` file

4. **GraphQL validation errors**:
   - Check query syntax and variable types
   - Ensure all required fields are provided

### Environment Setup

Make sure your `.env` file contains all required variables:
```env
MONGODB_CONNECTION_STRING=mongodb+srv://...
GITHUB_CLIENT_ID=your_client_id
GITHUB_CLIENT_SECRET=your_client_secret
GITHUB_REDIRECT_URI=http://localhost:8000/auth/github/callback
JWT_SECRET_KEY=your_secret_key_minimum_32_characters
GITHUB_API_TOKEN=your_github_token
# ... other variables
```

## Support

For issues with the API or Postman collection:
1. Check the server logs for detailed error messages
2. Verify environment variable configuration
3. Test database connectivity
4. Validate JWT token format and expiration