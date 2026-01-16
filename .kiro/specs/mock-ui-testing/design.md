# Design Document

## Overview

The Mock UI Testing Interface is a single-page HTML application that provides comprehensive testing capabilities for all backend functionality. It uses vanilla JavaScript with no build process, making it instantly runnable in any modern browser. The interface simulates authentication locally while making real API calls to the backend for all other operations.

## Architecture

### High-Level Architecture

```mermaid
graph TB
    A[Mock UI - Single HTML File] --> B[Mock Auth Layer]
    A --> C[GraphQL Client]
    A --> D[REST Client]
    
    B --> E[LocalStorage]
    C --> F[Backend GraphQL API]
    D --> G[Backend REST API]
    
    E --> H[User Credentials]
    E --> I[JWT Tokens]
    E --> J[Enrolled Students]
    
    F --> K[Queries]
    F --> L[Mutations]
    
    G --> M[/auth endpoints]
```

### Component Breakdown

1. **UI Layer**: HTML structure with CSS styling
2. **Mock Authentication**: Client-side credential management
3. **API Client Layer**: JavaScript functions for backend communication
4. **State Management**: LocalStorage for persistence
5. **Response Display**: Dynamic DOM manipulation for results

## Components and Interfaces

### 1. Authentication Component

**Purpose**: Manage real GitHub OAuth authentication flow with backend

**Interface**:
```javascript
class RealAuth {
  // Initiate GitHub OAuth login
  loginWithGitHub()
  
  // Handle OAuth callback and extract token
  handleOAuthCallback()
  
  // Get current user profile from backend
  async getCurrentUser()
  
  // Logout current user
  logout()
  
  // Check if user has role
  hasRole(role)
  
  // Get stored JWT token
  getToken()
  
  // Store JWT token
  setToken(token)
}
```

**Storage Schema**:
```javascript
// LocalStorage keys
{
  "auth_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "current_user": {
    "id": "507f1f77bcf86cd799439011",
    "username": "mentor1",
    "email": "mentor1@example.com",
    "role": "MENTOR",
    "githubId": "12345678",
    "isEnrolled": true,
    "createdAt": "2024-01-15T10:00:00Z"
  },
  "mock_backend_url": "http://localhost:8000"
}
```

### 2. GraphQL Client Component

**Purpose**: Execute GraphQL queries and mutations against the backend

**Interface**:
```javascript
class GraphQLClient {
  constructor(baseUrl, getToken)
  
  // Execute a GraphQL query
  async query(queryString, variables)
  
  // Execute a GraphQL mutation
  async mutate(mutationString, variables)
  
  // Predefined queries
  async getMe()
  async getRepositories()
  async getMyContributionMetrics()
  async getAllContributionMetrics(repoId)
  async getMyAIFeedback(repoId)
  async findCandidates(jobDescription)
  
  // Predefined mutations
  async enrollStudent(username, email)
  async createRepository(repoName, repoUrl)
  async saveContributionMetrics(repoId, metrics)
  async generateAIFeedback(repoId, studentGithubId)
}
```

### 3. REST Client Component

**Purpose**: Handle REST API calls for authentication endpoints

**Interface**:
```javascript
class RESTClient {
  constructor(baseUrl, getToken)
  
  // Call REST endpoints
  async get(endpoint)
  async post(endpoint, body)
  
  // Specific endpoints
  async getAuthMe()
  async healthCheck()
}
```

### 4. UI Manager Component

**Purpose**: Handle DOM manipulation and user interactions

**Interface**:
```javascript
class UIManager {
  // Initialize UI
  init()
  
  // Update authentication UI
  updateAuthUI(user)
  
  // Show/hide sections based on role
  updateRoleBasedUI(role)
  
  // Display API responses
  displayResponse(data, isError)
  
  // Clear response area
  clearResponse()
  
  // Show loading state
  showLoading(message)
  
  // Hide loading state
  hideLoading()
  
  // Display enrolled students (mentor only)
  displayEnrolledStudents(students)
}
```

## Data Models

### User Model (From Backend)
```javascript
{
  id: string,  // MongoDB ObjectId
  username: string,
  email: string,
  githubId: string,  // From GitHub OAuth
  role: "MENTOR" | "STUDENT",
  isEnrolled: boolean,
  enrolledBy?: string,  // For students only
  createdAt: string  // ISO timestamp
}
```

### Current Session Model
```javascript
{
  id: string,
  username: string,
  email: string,
  role: "MENTOR" | "STUDENT",
  githubId: string,
  isEnrolled: boolean,
  token: string  // Real JWT token from backend
}
```

### GraphQL Query/Mutation Models

These match the backend schema exactly:

```graphql
# Queries
type Query {
  getMe: User
  getRepositories: [Repository]
  getMyContributionMetrics: [ContributionMetrics]
  getAllContributionMetrics(repoId: String!): [ContributionMetrics]
  getMyAIFeedback(repoId: String): [AIFeedback]
  findCandidates(jobDescription: String!): [CandidateResult]
}

# Mutations
type Mutation {
  enrollStudent(input: EnrollStudentInput!): User
  createRepository(input: CreateRepositoryInput!): Repository
  saveContributionMetrics(input: SaveContributionMetricsInput!): ContributionMetrics
  generateAIFeedback(input: GenerateAIFeedbackInput!): AIFeedback
}
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Authentication State Consistency
*For any* user session, if a user is logged in, then the JWT token in localStorage must be valid and the current user object must match the /auth/me response from the backend.
**Validates: Requirements 2.3, 2.4, 2.5**

### Property 2: Role-Based UI Visibility
*For any* logged-in user, the UI sections displayed must match their role permissions (mentor-only features hidden for students, student-only features hidden for mentors).
**Validates: Requirements 3.1, 3.2**

### Property 3: Token Inclusion in API Calls
*For any* authenticated API call, the request must include the JWT token in the Authorization header with "Bearer" prefix.
**Validates: Requirements 3.5**

### Property 4: Student Enrollment Backend Integration
*For any* successful student enrollment by a mentor, the student record must be created in the backend database and the student must be able to login via GitHub OAuth.
**Validates: Requirements 4.4, 4.5, 4.6**

### Property 5: API Response Display
*For any* API call (success or failure), the response must be displayed in the response area with appropriate formatting and error styling.
**Validates: Requirements 10.2, 10.3**

### Property 6: Input Validation Before API Calls
*For any* form submission, all required fields must be validated before making the API call.
**Validates: Requirements 4.3, 5.3, 6.3, 7.3, 8.3, 9.3**

### Property 7: GraphQL Query Structure
*For any* GraphQL operation, the request must include a valid query/mutation string and variables object matching the backend schema.
**Validates: Requirements 3.5, 14.3**

### Property 8: Backend URL Configuration Persistence
*For any* backend URL change, the new URL must be persisted to localStorage and used for all subsequent API calls.
**Validates: Requirements 11.3, 11.4**

### Property 9: Logout State Cleanup
*For any* logout operation, the JWT token and current user object must be cleared from localStorage and the UI must update to logged-out state.
**Validates: Requirements 2.6**

### Property 10: Enrolled Students List from Backend
*For any* mentor viewing enrolled students, the displayed list must be fetched from the backend via GraphQL query and show all students enrolled by that mentor.
**Validates: Requirements 4.8**

## Error Handling

### Client-Side Errors

1. **Validation Errors**
   - Empty required fields
   - Invalid email format
   - Invalid numeric values
   - Display: Red text below input field

2. **Authentication Errors**
   - Invalid credentials
   - User not found
   - Role mismatch
   - Display: Alert message with error details

3. **Storage Errors**
   - LocalStorage quota exceeded
   - LocalStorage disabled
   - Display: Warning banner at top of page

### Backend API Errors

1. **Network Errors**
   - Backend not reachable
   - Timeout
   - Display: "Backend connection failed" message

2. **GraphQL Errors**
   - Query syntax errors
   - Authorization errors
   - Validation errors
   - Display: Full error response in response area

3. **HTTP Errors**
   - 401 Unauthorized
   - 403 Forbidden
   - 404 Not Found
   - 500 Internal Server Error
   - Display: Status code and error message

### Error Display Format

```javascript
{
  error: true,
  status: 403,
  message: "Insufficient permissions",
  details: {
    operation: "enrollStudent",
    required_role: "MENTOR"
  }
}
```

## Testing Strategy

### Unit Testing Approach

Since this is a single HTML file with embedded JavaScript, traditional unit testing frameworks are not used. Instead, testing is manual and interactive:

1. **Authentication Flow Testing**
   - Test mentor signup with valid/invalid data
   - Test mentor login with correct/incorrect credentials
   - Test student login with enrolled/non-enrolled accounts
   - Test logout and state cleanup

2. **GraphQL Query Testing**
   - Test each query with valid authentication
   - Test queries without authentication
   - Test queries with wrong role
   - Verify response formatting

3. **GraphQL Mutation Testing**
   - Test each mutation with valid data
   - Test mutations with invalid data
   - Test mutations with wrong role
   - Verify database updates

4. **UI State Testing**
   - Test role-based UI visibility
   - Test response display for success/error
   - Test loading states
   - Test form validation

5. **Integration Testing**
   - Test complete mentor workflow: signup → enroll student → create repo → view metrics
   - Test complete student workflow: login → save metrics → view feedback
   - Test candidate search workflow
   - Test error recovery

### Manual Test Checklist

**Mentor Workflow:**
- [ ] Sign up as mentor
- [ ] Login as mentor
- [ ] Enroll a student
- [ ] Create a repository
- [ ] View all repositories
- [ ] View all contribution metrics for a repo
- [ ] Generate AI feedback for a student
- [ ] View AI feedback
- [ ] Search for candidates
- [ ] Logout

**Student Workflow:**
- [ ] Login as enrolled student
- [ ] View my profile
- [ ] View my repositories
- [ ] Save contribution metrics
- [ ] View my contribution metrics
- [ ] Generate AI feedback for myself
- [ ] View my AI feedback
- [ ] Logout

**Error Scenarios:**
- [ ] Try to login with wrong credentials
- [ ] Try student operations as mentor
- [ ] Try mentor operations as student
- [ ] Try operations without authentication
- [ ] Test with backend offline
- [ ] Test with invalid repository IDs
- [ ] Test with invalid input data

### Browser Compatibility

The mock UI should be tested in:
- Chrome/Edge (Chromium-based)
- Firefox
- Safari

Minimum browser versions:
- Chrome 90+
- Firefox 88+
- Safari 14+

## UI Layout Design

### Page Structure

```
┌─────────────────────────────────────────────────────────────┐
│  Mock UI Testing Interface - Student Progress Tracker       │
│  Backend URL: [http://localhost:8000] [Update]              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  AUTHENTICATION                                              │
│  Status: Not logged in                                       │
│  [Login with GitHub]                                         │
│                                                              │
│  OR (for testing with existing token):                      │
│  Paste JWT Token: [________________________________]         │
│  [Use Token]                                                 │
│                                                              │
│  Current User: mentor1 (MENTOR) [Logout]                   │
│  GitHub ID: 12345678                                        │
│  Email: mentor1@example.com                                 │
│  Token: eyJhbGc... [Copy]                                   │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  STUDENT ENROLLMENT (Mentor Only)                           │
│  GitHub Username: [________] Email: [________]              │
│  [Enroll Student]                                           │
│                                                              │
│  Enrolled Students (from backend):                          │
│  • student1 (github_student1) - student1@example.com       │
│    Status: Can login via GitHub OAuth                      │
│  • student2 (github_student2) - student2@example.com       │
│    Status: Can login via GitHub OAuth                      │
│  [Refresh List]                                             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  REPOSITORY MANAGEMENT (Mentor Only)                        │
│  Repo Name: [________] Repo URL: [________]                 │
│  [Create Repository]                                        │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  GRAPHQL QUERIES                                            │
│  [Get My Profile] [Get Repositories] [Get My Metrics]      │
│  [Get My AI Feedback]                                       │
│                                                              │
│  Mentor Only:                                               │
│  Repo ID: [________] [Get All Metrics for Repo]            │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  CONTRIBUTION METRICS (Student Only)                        │
│  Repo ID: [________]                                        │
│  Commits: [___] PRs: [___] Issues: [___]                   │
│  Consistency Score: [___] (0.0 - 1.0)                      │
│  [Save Metrics]                                             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  AI FEEDBACK GENERATION                                     │
│  Repo ID: [________]                                        │
│  Student GitHub ID: [________] (Required for mentors)      │
│  [Generate AI Feedback]                                     │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  CANDIDATE SEARCH                                           │
│  Job Description:                                           │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ Looking for a Python developer with FastAPI...      │
│  │                                                       │
│  └─────────────────────────────────────────────────────┘  │
│  [Find Candidates]                                          │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  RESPONSE / RESULTS                                         │
│  [Clear Results]                                            │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ {                                                     │
│  │   "data": {                                           │
│  │     "getMe": {                                        │
│  │       "username": "mentor1",                          │
│  │       "role": "MENTOR"                                │
│  │     }                                                 │
│  │   }                                                   │
│  │ }                                                     │
│  └─────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Color Scheme

- **Background**: #f5f5f5 (light gray)
- **Sections**: #ffffff (white) with subtle shadow
- **Primary Buttons**: #4CAF50 (green)
- **Secondary Buttons**: #2196F3 (blue)
- **Danger Buttons**: #f44336 (red)
- **Success Text**: #4CAF50 (green)
- **Error Text**: #f44336 (red)
- **Code/Response**: #263238 (dark gray) background with #00ff00 (green) text

### Responsive Design

- Minimum width: 800px
- Maximum width: 1200px
- Center-aligned on larger screens
- Sections stack vertically
- Mobile-friendly (scales down to 600px)

## Implementation Notes

### Technology Stack

- **HTML5**: Structure
- **CSS3**: Styling (embedded in `<style>` tag)
- **Vanilla JavaScript**: Logic (embedded in `<script>` tag)
- **LocalStorage API**: Data persistence
- **Fetch API**: HTTP requests

### No External Dependencies

The entire application is self-contained in a single HTML file with no external libraries or frameworks. This ensures:
- Instant loading
- No build process
- No dependency management
- Easy distribution
- Works offline (except for API calls)

### Security Considerations

**Production-Ready Authentication:**
- Uses real GitHub OAuth flow via backend /auth endpoints
- Real JWT tokens issued by backend
- Token validation handled by backend
- Secure token storage in browser localStorage
- HTTPS required for production deployment (OAuth callback URLs)

**Testing Features:**
- Manual token entry for testing with pre-generated tokens
- Token copy functionality for sharing between test sessions
- Clear token display for debugging

**Important Notes:**
- This UI is for TESTING purposes but uses PRODUCTION authentication
- The authentication system is identical to what a production frontend would use
- No mock authentication - all auth goes through the real backend
- Students must be enrolled by mentors before they can login via GitHub OAuth

### Browser Storage Limits

LocalStorage has a 5-10MB limit per origin. For testing purposes, this is sufficient for:
- JWT tokens (typically < 1KB each)
- User profile data
- Configuration data
- No need to store user credentials (handled by backend)

If storage limits are reached, the UI will display a warning and suggest clearing old data.

## Future Enhancements (Out of Scope)

These features are NOT included in the initial implementation but could be added later:

1. **Export/Import Test Data**: Save and load test scenarios
2. **Request History**: View past API calls and responses
3. **Performance Metrics**: Track API response times
4. **Automated Test Runner**: Script common test scenarios
5. **Dark Mode**: Alternative color scheme
6. **GraphQL Query Builder**: Visual query construction
7. **WebSocket Support**: Test real-time features
8. **Multi-Tab Sync**: Sync state across browser tabs
