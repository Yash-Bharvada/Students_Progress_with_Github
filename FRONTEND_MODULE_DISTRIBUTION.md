# Frontend Module Distribution for Student Progress Tracker

## Overview
This document provides a complete module-based distribution of the backend API, mapping each backend module to the frontend components and features required to consume it.

---

## 1. Authentication Module (`/auth`)

### Backend Endpoints
- `GET /auth/github/login` - Initiate GitHub OAuth
- `GET /auth/github/callback` - Handle OAuth callback
- `GET /auth/me` - Get current user info
- `POST /auth/logout` - Logout endpoint
- `GET /auth/health` - Auth service health check

### Frontend Requirements

#### 1.1 Login/Authentication Flow
**Components Needed:**
- `LoginPage` - Landing page with "Login with GitHub" button
- `AuthCallback` - Handle OAuth redirect and token extraction
- `AuthContext` - Global authentication state management
- `ProtectedRoute` - Route wrapper for authenticated pages

**Features:**
- GitHub OAuth button that redirects to `/auth/github/login`
- Callback handler to extract token from URL query params
- Store JWT token in localStorage/sessionStorage
- Automatic token refresh/validation
- Redirect logic (enrolled students → dashboard, non-enrolled → error page)

**State Management:**
```typescript
interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}
```

#### 1.2 User Profile Display
**Components Needed:**
- `UserProfile` - Display current user information
- `UserAvatar` - GitHub avatar display
- `RoleBadge` - Visual indicator for MENTOR/STUDENT role

**Data to Display:**
- Username
- Email
- Role (MENTOR/STUDENT)
- Enrollment status
- Created date
- Last login

---

## 2. User Management Module (GraphQL)

### Backend Operations
- `getMe` - Get current user profile
- `enrollStudent` (Mutation) - Enroll a new student

### Frontend Requirements

#### 2.1 Student Enrollment (Mentor Only)
**Components Needed:**
- `EnrollStudentForm` - Form to enroll new students
- `EnrollStudentModal` - Modal dialog for enrollment
- `StudentList` - Display enrolled students

**Form Fields:**
- GitHub username (required)
- Email address (required)
- Submit button
- Validation messages

**Features:**
- Role-based access (only show to mentors)
- Form validation (email format, required fields)
- Success/error notifications
- Duplicate student handling

**API Integration:**
```graphql
mutation EnrollStudent($input: EnrollStudentInput!) {
  enrollStudent(input: $input) {
    id
    username
    email
    role
    isEnrolled
    enrolledBy
  }
}
```

#### 2.2 User Profile Management
**Components Needed:**
- `ProfileCard` - Display user profile
- `ProfileSettings` - Edit profile settings (if applicable)

---

## 3. Repository Management Module (GraphQL)

### Backend Operations
- `getRepositories` - Get user's repositories
- `createRepository` (Mutation) - Create new repository record

### Frontend Requirements

#### 3.1 Repository List View
**Components Needed:**
- `RepositoryList` - Display all repositories
- `RepositoryCard` - Individual repository card
- `RepositoryFilters` - Filter/search repositories
- `EmptyRepositoryState` - Empty state when no repos

**Data to Display per Repository:**
- Repository name
- Repository URL (clickable link to GitHub)
- Owner GitHub ID
- Linked students (for mentors)
- Created date
- Number of linked students

**Features:**
- Different views for mentors vs students
  - Mentors: See repositories they own
  - Students: See repositories they're linked to
- Search/filter functionality
- Sort by name, date, student count
- Click to view repository details

#### 3.2 Create Repository (Mentor Only)
**Components Needed:**
- `CreateRepositoryForm` - Form to add repository
- `CreateRepositoryModal` - Modal dialog
- `RepositoryUrlValidator` - Validate GitHub URLs

**Form Fields:**
- Repository name (required)
- Repository URL (required, must be valid GitHub URL)
- Submit button
- Validation messages

**Validation Rules:**
- URL must start with http:// or https://
- GitHub URLs must include owner and repo name
- Check for duplicate URLs
- Display error messages for invalid input

**API Integration:**
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

#### 3.3 Repository Details View
**Components Needed:**
- `RepositoryDetails` - Full repository information
- `LinkedStudentsList` - Students linked to repository
- `RepositoryMetrics` - Overview metrics

---

## 4. Contribution Metrics Module (GraphQL)

### Backend Operations
- `getMyContributionMetrics` - Get student's own metrics
- `getAllContributionMetrics` - Get all metrics for a repo (mentor only)
- `saveContributionMetrics` (Mutation) - Save/update metrics

### Frontend Requirements

#### 4.1 Student Metrics Dashboard
**Components Needed:**
- `MetricsDashboard` - Overview of all metrics
- `MetricsCard` - Individual metric display
- `MetricsChart` - Visual charts (line, bar, pie)
- `MetricsTrend` - Show trends over time

**Metrics to Display:**
- Commit count
- PR count
- Issue count
- Consistency score (0.0-1.0)
- Last updated timestamp

**Visualizations:**
- Bar chart: Commits, PRs, Issues comparison
- Line chart: Consistency score over time
- Progress indicators for each metric
- Color coding (green = good, yellow = moderate, red = needs improvement)

**API Integration:**
```graphql
query GetMyContributionMetrics {
  getMyContributionMetrics {
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

#### 4.2 Mentor Metrics View (All Students)
**Components Needed:**
- `StudentMetricsTable` - Table view of all students
- `StudentMetricsComparison` - Compare students
- `MetricsExport` - Export metrics to CSV/PDF

**Features:**
- View metrics for all students in a repository
- Sort by any metric column
- Filter by student name
- Compare multiple students side-by-side
- Export functionality

**API Integration:**
```graphql
query GetAllContributionMetrics($repoId: String!) {
  getAllContributionMetrics(repoId: $repoId) {
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

#### 4.3 Save/Update Metrics (Student Only)
**Components Needed:**
- `UpdateMetricsForm` - Form to update metrics
- `MetricsInputFields` - Input fields with validation

**Form Fields:**
- Repository selector (dropdown)
- Commit count (number, >= 0)
- PR count (number, >= 0)
- Issue count (number, >= 0)
- Consistency score (slider, 0.0-1.0)
- Submit button

**Validation:**
- All counts must be non-negative
- Consistency score must be between 0.0 and 1.0
- Repository must exist

---

## 5. AI Feedback Module (GraphQL)

### Backend Operations
- `getMyAiFeedback` - Get AI feedback (role-based)
- `generateAiFeedback` (Mutation) - Generate new feedback

### Frontend Requirements

#### 5.1 AI Feedback Display
**Components Needed:**
- `FeedbackCard` - Display single feedback entry
- `FeedbackList` - List all feedback entries
- `FeedbackTimeline` - Timeline view of feedback
- `QualityScoreGauge` - Visual quality score display

**Data to Display:**
- Quality score (0.0-10.0) with visual gauge
- Strengths (list with icons)
- Issues (list with warning icons)
- Suggestions (list with lightbulb icons)
- Generated timestamp
- Repository name
- Student name (for mentors)

**Visualizations:**
- Quality score gauge (0-10 scale)
- Color-coded sections:
  - Strengths: Green
  - Issues: Red/Orange
  - Suggestions: Blue
- Timeline view showing feedback history

#### 5.2 Generate AI Feedback
**Components Needed:**
- `GenerateFeedbackButton` - Trigger feedback generation
- `GenerateFeedbackModal` - Modal with options
- `FeedbackLoadingState` - Loading indicator during generation

**Features:**
- Button to trigger AI analysis
- For mentors: Select student from dropdown
- For students: Automatically use their own ID
- Loading state during generation (can take time)
- Success notification with link to view feedback
- Error handling for failed generation

**API Integration:**
```graphql
mutation GenerateAiFeedback($input: GenerateAIFeedbackInput!) {
  generateAiFeedback(input: $input) {
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

#### 5.3 Feedback History
**Components Needed:**
- `FeedbackHistory` - Historical feedback view
- `FeedbackComparison` - Compare feedback over time
- `FeedbackTrends` - Show quality score trends

**Features:**
- View all past feedback for a repository
- Filter by date range
- Compare quality scores over time
- Show improvement trends

---

## 6. Skill DNA Search Module (GraphQL)

### Backend Operations
- `findCandidates` - Search for students by job description

### Frontend Requirements

#### 6.1 Job Search Interface
**Components Needed:**
- `JobSearchForm` - Input job description
- `JobDescriptionTextarea` - Multi-line text input
- `SearchButton` - Trigger search

**Form Fields:**
- Job description (required, multi-line textarea)
- Search button
- Clear button

**Features:**
- Rich text input for job descriptions
- Character count indicator
- Validation (non-empty)
- Search history (optional)

#### 6.2 Candidate Results Display
**Components Needed:**
- `CandidateList` - List of matching candidates
- `CandidateCard` - Individual candidate card
- `MatchScoreIndicator` - Visual match score
- `SkillTagList` - Display verified skills

**Data to Display per Candidate:**
- Username
- Email
- Match score (0.0-1.0) with visual indicator
- Verified skills with confidence scores
- Evidence files for each skill

**Visualizations:**
- Match score as percentage bar
- Color-coded match quality:
  - > 0.8: Excellent (green)
  - 0.6-0.8: Good (blue)
  - < 0.6: Fair (yellow)
- Skill tags with confidence badges
- Sort by match score (descending)

**API Integration:**
```graphql
query FindCandidates($jobDescription: String!) {
  findCandidates(jobDescription: $jobDescription) {
    id
    username
    email
    matchScore
    verifiedSkills {
      name
      confidence
      evidenceFile
    }
  }
}
```

#### 6.3 Candidate Details View
**Components Needed:**
- `CandidateProfile` - Full candidate profile
- `SkillBreakdown` - Detailed skill analysis
- `ContactButton` - Contact candidate (email)

---

## 7. Health Check & Monitoring

### Backend Endpoints
- `GET /health` - Application health check
- `GET /auth/health` - Auth service health check

### Frontend Requirements

#### 7.1 System Status Dashboard (Admin/Mentor)
**Components Needed:**
- `SystemHealthDashboard` - Overall system status
- `ServiceStatusCard` - Individual service status
- `HealthIndicator` - Visual health indicator

**Data to Display:**
- Overall status (healthy/unhealthy)
- Database status
- Authentication service status
- GraphQL service status
- AI feedback service status
- Environment info

**Features:**
- Auto-refresh every 30 seconds
- Color-coded status indicators
- Alert notifications for unhealthy services

---

## 8. Common/Shared Components

### 8.1 Layout Components
- `AppLayout` - Main application layout
- `Sidebar` - Navigation sidebar
- `Header` - Top navigation bar
- `Footer` - Footer with links

### 8.2 Navigation Components
- `NavMenu` - Main navigation menu
- `NavItem` - Individual nav item
- `RoleBasedNav` - Show/hide based on role

**Navigation Structure:**
```
Mentor:
- Dashboard
- Students (Enroll, View All)
- Repositories (Create, View All)
- Metrics (View All Students)
- AI Feedback (Generate, View All)
- Job Search (Find Candidates)
- Profile

Student:
- Dashboard
- My Repositories
- My Metrics (View, Update)
- My Feedback
- Profile
```

### 8.3 UI Components
- `Button` - Reusable button component
- `Input` - Form input fields
- `Select` - Dropdown select
- `Modal` - Modal dialog
- `Card` - Card container
- `Table` - Data table
- `Chart` - Chart wrapper (Chart.js/Recharts)
- `Badge` - Status badges
- `Alert` - Notification alerts
- `Loader` - Loading spinner
- `EmptyState` - Empty state placeholder
- `ErrorBoundary` - Error handling

### 8.4 Utility Components
- `DateFormatter` - Format dates consistently
- `ScoreIndicator` - Visual score display
- `ProgressBar` - Progress indicator
- `Tooltip` - Hover tooltips
- `Pagination` - Paginate lists
- `SearchBar` - Search input

---

## 9. State Management Architecture

### 9.1 Global State (Context/Redux)
```typescript
interface AppState {
  auth: AuthState;
  user: UserState;
  repositories: RepositoryState;
  metrics: MetricsState;
  feedback: FeedbackState;
  candidates: CandidateState;
  ui: UIState;
}
```

### 9.2 API Client Configuration
```typescript
// GraphQL Client Setup
const graphqlClient = new ApolloClient({
  uri: '/graphql',
  headers: {
    Authorization: `Bearer ${token}`
  }
});

// REST Client Setup (for auth)
const restClient = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    Authorization: `Bearer ${token}`
  }
});
```

---

## 10. Page Structure

### 10.1 Public Pages
- `/` - Landing page
- `/login` - Login page (redirects to GitHub OAuth)
- `/auth/callback` - OAuth callback handler
- `/error` - Error page (403, 404, 500)

### 10.2 Mentor Pages
- `/dashboard` - Mentor dashboard
- `/students` - Student management
- `/students/enroll` - Enroll new student
- `/repositories` - Repository list
- `/repositories/create` - Create repository
- `/repositories/:id` - Repository details
- `/metrics/:repoId` - View all student metrics
- `/feedback` - AI feedback management
- `/feedback/:repoId` - Repository feedback
- `/search` - Job candidate search
- `/profile` - User profile

### 10.3 Student Pages
- `/dashboard` - Student dashboard
- `/repositories` - My repositories
- `/repositories/:id` - Repository details
- `/metrics` - My metrics
- `/metrics/update` - Update metrics
- `/feedback` - My feedback
- `/profile` - User profile

---

## 11. Error Handling

### 11.1 Error Types to Handle
- Authentication errors (401)
- Authorization errors (403)
- Not found errors (404)
- Validation errors (422)
- Server errors (500)
- Network errors
- GraphQL errors

### 11.2 Error Display Components
- `ErrorPage` - Full page error
- `ErrorAlert` - Inline error alert
- `ErrorToast` - Toast notification
- `ValidationError` - Form validation errors

---

## 12. Responsive Design Requirements

### 12.1 Breakpoints
- Mobile: < 768px
- Tablet: 768px - 1024px
- Desktop: > 1024px

### 12.2 Mobile-Specific Components
- `MobileNav` - Mobile navigation drawer
- `MobileTable` - Mobile-friendly table view
- `MobileCard` - Optimized card layout

---

## 13. Performance Considerations

### 13.1 Optimization Strategies
- Lazy loading for routes
- Code splitting by role (mentor/student)
- Memoization for expensive computations
- Virtual scrolling for long lists
- Debounced search inputs
- Cached GraphQL queries
- Optimistic UI updates

### 13.2 Loading States
- Skeleton screens for initial load
- Spinners for actions
- Progress bars for long operations
- Shimmer effects for loading content

---

## 14. Testing Requirements

### 14.1 Component Tests
- Unit tests for all components
- Integration tests for forms
- Snapshot tests for UI components

### 14.2 E2E Tests
- Login flow
- Student enrollment flow
- Repository creation flow
- Metrics update flow
- AI feedback generation flow
- Job search flow

---

## 15. Deployment Considerations

### 15.1 Environment Variables
```
REACT_APP_API_URL=http://localhost:8000
REACT_APP_GRAPHQL_URL=http://localhost:8000/graphql
REACT_APP_GITHUB_CLIENT_ID=your_client_id
```

### 15.2 Build Configuration
- Production build optimization
- Environment-specific configs
- CDN for static assets
- Service worker for offline support (optional)

---

## Summary

This frontend requires:
- **~50-60 React components**
- **8-10 pages/routes**
- **GraphQL client** (Apollo Client recommended)
- **REST client** (Axios for auth endpoints)
- **State management** (Context API or Redux)
- **Chart library** (Chart.js or Recharts)
- **UI framework** (Material-UI, Ant Design, or Tailwind CSS)
- **Form library** (React Hook Form or Formik)
- **Routing** (React Router)

**Estimated Development Time:** 4-6 weeks for a full-featured frontend with all modules.
