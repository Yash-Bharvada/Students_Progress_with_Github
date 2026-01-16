# Implementation Plan: Mock UI Testing Interface

## Overview

Create a single-page HTML application with embedded CSS and JavaScript that provides comprehensive testing capabilities for all backend functionality. The implementation will be done incrementally, building from basic structure to complete functionality.

## Tasks

- [x] 1. Create basic HTML structure and styling
  - Create `mock-ui.html` file in project root
  - Add HTML5 boilerplate with proper meta tags
  - Create main container with header showing title and backend URL configuration
  - Add embedded CSS for layout, colors, and responsive design
  - Implement section containers for all major features
  - Add loading spinner and response display area
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [x] 2. Implement real GitHub OAuth authentication
  - [x] 2.1 Create RealAuth class for authentication management
    - Implement loginWithGitHub() method that redirects to /auth/github/login
    - Implement handleOAuthCallback() to extract JWT token from URL or response
    - Implement getCurrentUser() method that calls /auth/me endpoint
    - Implement logout() method with state cleanup
    - Implement getToken() and setToken() helper methods
    - Implement hasRole() helper method
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7_

  - [x] 2.2 Create authentication UI components
    - Add "Login with GitHub" button
    - Add manual token entry text area for testing
    - Add "Use Token" button for manual token entry
    - Add current user display with role, email, GitHub ID, and token
    - Add logout button
    - Wire up button clicks to RealAuth methods
    - Handle OAuth callback on page load
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6_

  - [x] 2.3 Implement LocalStorage persistence
    - Save JWT token to "auth_token" key
    - Save current user profile to "current_user" key
    - Load and restore session on page load
    - Call /auth/me to validate token on page load
    - Clear storage on logout
    - _Requirements: 2.3, 2.4, 2.6_

- [x] 3. Implement GraphQL client
  - [x] 3.1 Create GraphQLClient class
    - Implement constructor with baseUrl and token getter
    - Implement query() method for executing GraphQL queries
    - Implement mutate() method for executing GraphQL mutations
    - Add error handling for network and GraphQL errors
    - _Requirements: 3.1, 3.2, 3.5, 3.6_

  - [x] 3.2 Add predefined query methods
    - Implement getMe() query
    - Implement getRepositories() query
    - Implement getMyContributionMetrics() query
    - Implement getAllContributionMetrics(repoId) query
    - Implement getMyAIFeedback(repoId) query
    - Implement findCandidates(jobDescription) query
    - _Requirements: 3.1, 3.2, 3.3, 3.4_

  - [x] 3.3 Add predefined mutation methods
    - Implement enrollStudent(username, email) mutation
    - Implement createRepository(repoName, repoUrl) mutation
    - Implement saveContributionMetrics(repoId, metrics) mutation
    - Implement generateAIFeedback(repoId, studentGithubId) mutation
    - _Requirements: 3.1, 3.2_

- [x] 4. Implement student enrollment interface
  - Add enrollment form with GitHub username and email fields
  - Add "Enroll Student" button with click handler
  - Implement validation for required fields
  - Call GraphQL enrollStudent mutation on submit
  - Display enrolled student information on success
  - Add "Refresh List" button to fetch enrolled students from backend
  - Implement getEnrolledStudents() method to query backend for students enrolled by current mentor
  - Display enrolled students list with GitHub username, GitHub ID, and email
  - Show message that students can now login via GitHub OAuth
  - Add error display for enrollment failures
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8_

- [x] 5. Implement repository management interface
  - Add repository creation form with name and URL fields
  - Add "Create Repository" button with click handler
  - Implement validation for required fields and URL format
  - Call GraphQL createRepository mutation on submit
  - Display created repository information including ID
  - Add error display for creation failures
  - Show/hide section based on MENTOR role
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7_

- [x] 6. Implement contribution metrics interface
  - Add metrics form with repo ID, commit count, PR count, issue count, and consistency score fields
  - Add "Save Contribution Metrics" button with click handler
  - Implement validation for numeric fields and consistency score range (0.0-1.0)
  - Call GraphQL saveContributionMetrics mutation on submit
  - Display saved metrics information
  - Add error display for save failures
  - Show/hide section based on STUDENT role
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6_

- [x] 7. Implement mentor metrics query interface
  - Add repo ID input field for mentor metrics query
  - Add "Get All Contribution Metrics (Mentor)" button with click handler
  - Implement validation for repo ID
  - Call GraphQL getAllContributionMetrics query on submit
  - Display all student metrics for the repository
  - Add error display for query failures
  - Show/hide section based on MENTOR role
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6_

- [x] 8. Implement AI feedback generation interface
  - Add form with repo ID and optional student GitHub ID fields
  - Add "Generate AI Feedback" button with click handler
  - Implement validation for repo ID
  - Call GraphQL generateAIFeedback mutation on submit
  - Display quality score, strengths, issues, and suggestions
  - Add error display for generation failures
  - Show help text explaining student GitHub ID requirement for mentors
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6_

- [x] 9. Implement candidate search interface
  - Add text area for job description input
  - Add "Find Candidates" button with click handler
  - Implement validation for non-empty job description
  - Call GraphQL findCandidates query on submit
  - Display candidate results with username, email, match score, and verified skills
  - Show "No candidates found" message when results are empty
  - Add error display for search failures
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6_

- [x] 10. Implement response display and error handling
  - [x] 10.1 Create UIManager class for DOM manipulation
    - Implement displayResponse(data, isError) method
    - Implement clearResponse() method
    - Implement showLoading(message) and hideLoading() methods
    - Implement updateAuthUI(user) method
    - Implement updateRoleBasedUI(role) method
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

  - [x] 10.2 Add response formatting
    - Format JSON responses with proper indentation
    - Add syntax highlighting for JSON (optional)
    - Style error messages in red
    - Style success messages in green
    - Add "Clear Results" button
    - _Requirements: 10.2, 10.3, 10.4, 10.5_

- [x] 11. Implement configuration management
  - Add backend URL input field in header
  - Add "Update" button to save backend URL
  - Persist backend URL to LocalStorage ("mock_backend_url" key)
  - Load backend URL from LocalStorage on page load
  - Default to "http://localhost:8000" if not set
  - Display current backend URL prominently
  - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5_

- [x] 12. Implement token management features
  - Add text area for displaying current JWT token
  - Add text area for manually editing JWT token
  - Add "Copy Token" button to copy token to clipboard
  - Persist manually entered tokens to LocalStorage
  - Update token display when authentication state changes
  - _Requirements: 12.1, 12.2, 12.3, 12.4_

- [x] 13. Add GraphQL query visibility and editing
  - Add "Show GraphQL Query" toggle for each GraphQL operation
  - Display GraphQL query/mutation text in editable text area when toggled
  - Use edited query when operation is executed
  - Add "Reset to Default" button to restore original queries
  - Store custom queries in memory (not persisted)
  - _Requirements: 14.1, 14.2, 14.3, 14.4, 14.5_

- [x] 14. Implement role-based UI visibility
  - Hide student enrollment section for non-mentors
  - Hide repository creation section for non-mentors
  - Hide contribution metrics section for non-students
  - Hide mentor metrics query section for non-mentors
  - Update UI visibility on login/logout
  - Add role indicators on restricted sections
  - _Requirements: 2.1, 2.2, 2.3, 4.7, 5.7, 6.6, 7.6_

- [x] 15. Add help documentation and examples
  - Add collapsible help sections for each feature
  - Include step-by-step testing instructions
  - Add example values for all input fields
  - Document role requirements for each feature
  - Add "Quick Start" section at the top
  - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5_

- [x] 16. Implement enrolled students display from backend
  - Create getEnrolledStudents() GraphQL query method
  - Implement displayEnrolledStudents() method in UIManager
  - Fetch students from backend where enrolledBy matches current mentor's githubId
  - Display student list with GitHub username, GitHub ID, and email
  - Show OAuth login status for each student
  - Update list when new students are enrolled
  - Show empty state when no students are enrolled
  - Add "Refresh List" button to manually update the list
  - _Requirements: 4.8_

- [x] 17. Add REST API client for health checks
  - Create RESTClient class with get() and post() methods
  - Implement healthCheck() method calling /health endpoint
  - Implement getAuthMe() method calling /auth/me endpoint
  - Add "Health Check" button to test backend connectivity
  - Display health check results in response area
  - _Requirements: 11.1_

- [x] 18. Final integration and testing
  - Test GitHub OAuth login flow (mentor and student)
  - Test manual token entry for testing scenarios
  - Test complete mentor workflow (login → enroll → create repo → view metrics)
  - Test complete student workflow (login → save metrics → view feedback)
  - Test all error scenarios (invalid token, invalid data, backend offline)
  - Test role-based access (student trying mentor operations, etc.)
  - Test token management (manual token entry, copy token)
  - Test backend URL configuration
  - Verify all GraphQL queries and mutations work correctly
  - Test OAuth callback handling
  - Test token expiration and refresh
  - Test in Chrome, Firefox, and Safari
  - _Requirements: All_

## Notes

- All tasks build incrementally on previous tasks
- Each task should be tested before moving to the next
- The UI should remain functional after each task completion
- Focus on simplicity and clarity over advanced features
- **Authentication uses real GitHub OAuth - identical to production**
- **No mock authentication - all auth goes through backend**
- Students must be enrolled by mentors before they can login
- Use browser console for debugging during development
- The authentication system requires no changes for production deployment
