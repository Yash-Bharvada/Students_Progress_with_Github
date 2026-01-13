# Student Progress Backend - Final Testing Guide

## Production Readiness Verification

This guide provides comprehensive testing instructions for the Student Progress Backend API, including OAuth authentication, GraphQL operations, role-based access control, and AI feedback functionality.

## Prerequisites

### Environment Setup

1. **Environment Variables**: Ensure all required environment variables are set in `.env`:
   ```
   MONGODB_CONNECTION_STRING=mongodb+srv://...
   GITHUB_CLIENT_ID=your_github_client_id
   GITHUB_CLIENT_SECRET=your_github_client_secret
   GITHUB_REDIRECT_URI=http://localhost:8000/auth/github/callback
   JWT_SECRET_KEY=your_jwt_secret_key_32_chars_minimum
   GITHUB_API_TOKEN=your_github_api_token
   GEMINI_API_KEY=your_gemini_api_key
   ```

2. **Dependencies**: Install all required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. **Database**: Ensure MongoDB Atlas is accessible and configured

## Server Startup

### Development Server
```bash
# Start the development server
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Or use the built-in runner
python backend/main.py
```

### Production Server
```bash
# Start production server
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Testing with Postman

### Import Collections

1. Import the main collection: `postman_final_collection.json`
2. Import the environment: `postman_final_environment.json`
3. Set the environment as active in Postman

### Authentication Flow Testing

#### 1. GitHub OAuth Login
- **Request**: `GET /auth/github/login`
- **Expected**: 302 redirect to GitHub OAuth
- **Action**: Copy the redirect URL and complete OAuth in browser
- **Result**: Extract the `code` parameter from callback URL

#### 2. OAuth Callback
- **Request**: `GET /auth/github/callback?code={code}`
- **Expected**: 200 with JWT token and user info
- **Action**: Save the `access_token` to environment variables

#### 3. Verify Authentication
- **Request**: `GET /auth/me` with Bearer token
- **Expected**: 200 with current user information

### GraphQL Operations Testing

#### Queries

1. **Get Me**
   ```graphql
   query {
     getMe {
       id
       githubId
       username
       email
       role
       isEnrolled
       createdAt
     }
   }
   ```

2. **Get Repositories**
   ```graphql
   query {
     getRepositories {
       id
       repoName
       repoUrl
       ownerGithubId
       linkedStudents
       createdAt
     }
   }
   ```

3. **Get My Contribution Metrics** (Student)
   ```graphql
   query {
     getMyContributionMetrics {
       id
       repoId
       commitCount
       prCount
       issueCount
       consistencyScore
       lastUpdated
     }
   }
   ```

4. **Get All Contribution Metrics** (Mentor)
   ```graphql
   query GetAllMetrics($repoId: String!) {
     getAllContributionMetrics(repoId: $repoId) {
       id
       studentGithubId
       commitCount
       prCount
       issueCount
       consistencyScore
       lastUpdated
     }
   }
   ```

#### Mutations

1. **Enroll Student** (Mentor Only)
   ```graphql
   mutation EnrollStudent($input: EnrollStudentInput!) {
     enrollStudent(input: $input) {
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

2. **Create Repository** (Mentor Only)
   ```graphql
   mutation CreateRepository($input: CreateRepositoryInput!) {
     createRepository(input: $input) {
       id
       repoName
       repoUrl
       ownerGithubId
       linkedStudents
       createdAt
     }
   }
   ```

3. **Save Contribution Metrics** (Student Only)
   ```graphql
   mutation SaveMetrics($input: SaveContributionMetricsInput!) {
     saveContributionMetrics(input: $input) {
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

### AI Feedback Testing

1. **Generate AI Feedback**
   ```graphql
   mutation GenerateAIFeedback($input: GenerateAIFeedbackInput!) {
     generateAIFeedback(input: $input) {
       id
       repoId
       studentGithubId
       qualityScore
       strengths
       issues
       suggestions
       generatedAt
     }
   }
   ```

2. **Get My AI Feedback**
   ```graphql
   query {
     getMyAIFeedback {
       id
       repoId
       qualityScore
       strengths
       issues
       suggestions
       generatedAt
     }
   }
   ```

### Role-Based Access Control Testing

#### Test Scenarios

1. **Mentor Capabilities**
   - ✅ Can enroll students
   - ✅ Can create repositories
   - ✅ Can view all student metrics for their repositories
   - ✅ Can generate AI feedback for any repository
   - ✅ Can view all AI feedback

2. **Student Capabilities**
   - ✅ Can view their own profile
   - ✅ Can view repositories they're linked to
   - ✅ Can save their own contribution metrics
   - ✅ Can generate AI feedback for their repositories
   - ✅ Can view their own AI feedback
   - ❌ Cannot enroll other students
   - ❌ Cannot create repositories
   - ❌ Cannot view other students' metrics

3. **Unauthenticated Access**
   - ❌ Cannot access any GraphQL operations
   - ✅ Can access health endpoints
   - ✅ Can initiate OAuth flow

### Error Scenarios Testing

1. **Authentication Errors**
   - Invalid JWT token
   - Missing Authorization header
   - Expired token

2. **Authorization Errors**
   - Student trying to enroll another student
   - Student trying to create repository
   - Accessing other users' data

3. **Validation Errors**
   - Missing required fields
   - Invalid input formats
   - Invalid ObjectId references

4. **OAuth Errors**
   - Missing authorization code
   - Invalid authorization code
   - Non-enrolled student attempting login

## Health Check Endpoints

### Application Health
- **Endpoint**: `GET /health`
- **Expected**: System health status with database connectivity

### Authentication Health
- **Endpoint**: `GET /auth/health`
- **Expected**: Authentication service status

### Root Endpoint
- **Endpoint**: `GET /`
- **Expected**: API information and available endpoints

## Integration Testing

### Automated Tests
```bash
# Run integration tests
python -m pytest tests/test_integration.py -v

# Run production readiness tests
python -m pytest tests/test_production_readiness.py -v

# Run all tests
python -m pytest tests/ -v
```

### Manual Testing Workflow

1. **Setup Phase**
   - Start the server
   - Verify health endpoints
   - Import Postman collections

2. **Authentication Phase**
   - Complete OAuth flow for mentor user
   - Complete OAuth flow for student user
   - Verify JWT tokens are issued correctly

3. **Data Creation Phase**
   - Mentor enrolls a student
   - Mentor creates a repository
   - Student saves contribution metrics

4. **Query Phase**
   - Test all GraphQL queries with appropriate roles
   - Verify data filtering and access control

5. **AI Feedback Phase**
   - Generate AI feedback for repositories
   - Verify feedback quality and structure
   - Test role-based access to feedback

6. **Error Testing Phase**
   - Test all error scenarios
   - Verify proper error messages and status codes

## Performance Considerations

### Database Indexes
The system creates the following indexes for optimal performance:
- Users: `githubId` (unique), `role`, `enrolledBy`
- Repositories: `ownerGithubId`, `repoUrl` (unique), `linkedStudents`
- ContributionMetrics: `repoId + studentGithubId` (compound unique), `studentGithubId`, `repoId`
- AIFeedback: `repoId + studentGithubId` (compound), `studentGithubId`, `generatedAt`

### Rate Limiting
- GitHub API: Respect rate limits for repository analysis
- Gemini API: Handle rate limiting gracefully
- JWT: Implement reasonable token expiration

## Security Checklist

- ✅ JWT tokens are properly signed and validated
- ✅ Role-based access control is enforced
- ✅ CORS is properly configured
- ✅ Environment variables are used for secrets
- ✅ Input validation is implemented
- ✅ Error messages don't leak sensitive information
- ✅ Database connections are properly secured

## Deployment Verification

### Environment Variables
Verify all required environment variables are set in production:
```bash
# Check configuration
python -c "from backend.config import validate_configuration; validate_configuration()"
```

### Database Connectivity
```bash
# Test database connection
python -c "import asyncio; from backend.database import DatabaseManager; asyncio.run(DatabaseManager().__aenter__())"
```

### Service Dependencies
- MongoDB Atlas connectivity
- GitHub OAuth application configuration
- Gemini API key validity
- GitHub API token permissions

## Troubleshooting

### Common Issues

1. **Database Connection Failures**
   - Check MongoDB connection string
   - Verify network connectivity
   - Check IP whitelist in MongoDB Atlas

2. **OAuth Failures**
   - Verify GitHub OAuth app configuration
   - Check redirect URI matches exactly
   - Ensure client ID and secret are correct

3. **JWT Token Issues**
   - Verify JWT secret key is at least 32 characters
   - Check token expiration settings
   - Validate token format and claims

4. **GraphQL Errors**
   - Check schema validation
   - Verify input types match schema
   - Ensure proper authentication headers

5. **AI Feedback Issues**
   - Verify Gemini API key is valid
   - Check GitHub API token permissions
   - Ensure repository URLs are accessible

## Success Criteria

The system is production-ready when:

- ✅ All health endpoints return healthy status
- ✅ OAuth flow completes successfully for both roles
- ✅ All GraphQL operations work with proper authentication
- ✅ Role-based access control is enforced correctly
- ✅ AI feedback generation works with real repositories
- ✅ Error handling provides appropriate responses
- ✅ Database operations are performant with indexes
- ✅ All integration tests pass
- ✅ Postman collection covers all functionality
- ✅ Security measures are properly implemented