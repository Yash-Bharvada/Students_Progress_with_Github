# Requirements Document

## Introduction

A comprehensive mock web UI for testing all backend functionality of the Student Progress Tracker system. This UI provides a single-page interface to test authentication, user management, repository management, contribution metrics, AI feedback generation, and skill-based candidate search without requiring a production frontend.

## Glossary

- **Mock_UI**: A simple HTML/JavaScript testing interface for backend validation
- **Test_Interface**: Single-page application for exercising all backend endpoints
- **Backend_API**: The FastAPI + GraphQL backend system being tested
- **Auth_Flow**: Real GitHub OAuth authentication workflow using backend /auth endpoints
- **GraphQL_Client**: JavaScript code for making GraphQL queries and mutations
- **REST_Client**: JavaScript code for making REST API calls to /auth endpoints
- **Test_Scenario**: A specific user workflow being validated through the UI
- **Response_Display**: Visual feedback showing API responses and errors

## Requirements

### Requirement 1: Single-Page Mock UI Structure

**User Story:** As a developer, I want a single HTML page with all testing features, so that I can quickly test backend functionality without complex setup.

#### Acceptance Criteria

1. THE Mock_UI SHALL be a single HTML file with embedded CSS and JavaScript
2. THE Mock_UI SHALL be runnable by opening the file directly in a web browser
3. THE Mock_UI SHALL include sections for Authentication, User Management, Repository Management, Metrics, AI Feedback, and Candidate Search
4. THE Mock_UI SHALL display a clear header indicating this is a testing interface
5. THE Mock_UI SHALL use a clean, organized layout with labeled sections and buttons

### Requirement 2: Real Backend Authentication Integration

**User Story:** As a developer, I want to use the real GitHub OAuth authentication flow, so that the authentication system works identically to production and requires no changes when deploying.

#### Acceptance Criteria

1. THE Mock_UI SHALL provide a "Login with GitHub" button that redirects to /auth/github/login
2. WHEN GitHub OAuth callback returns to the UI, THE System SHALL extract the JWT token from the URL or response
3. WHEN a JWT token is received, THE System SHALL store it in browser localStorage
4. WHEN a JWT token is stored, THE System SHALL call /auth/me to get user profile information
5. WHEN user profile is retrieved, THE System SHALL display username, role, email, and enrollment status
6. WHEN a user clicks "Logout", THE System SHALL clear the stored JWT token and update the UI
7. THE Mock_UI SHALL handle OAuth errors gracefully and display error messages

### Requirement 3: GraphQL Query Testing Interface

**User Story:** As a developer, I want to test GraphQL queries, so that I can verify data retrieval works correctly for different user roles.

#### Acceptance Criteria

1. THE Mock_UI SHALL provide a "Get My Profile (GraphQL)" button that executes the getMe query
2. THE Mock_UI SHALL provide a "Get My Repositories" button that executes the getRepositories query
3. THE Mock_UI SHALL provide a "Get My Contribution Metrics" button that executes the getMyContributionMetrics query (student only)
4. THE Mock_UI SHALL provide a "Get My AI Feedback" button that executes the getMyAIFeedback query
5. WHEN any GraphQL query is executed, THE System SHALL include the JWT token in the Authorization header
6. WHEN query responses are received, THE System SHALL display the full JSON response in a formatted text area

### Requirement 4: Student Enrollment Testing Interface

**User Story:** As a developer testing mentor functionality, I want to enroll students, so that I can verify the enrollment workflow and create student accounts in the backend.

#### Acceptance Criteria

1. THE Mock_UI SHALL provide input fields for GitHub username and email for student enrollment
2. THE Mock_UI SHALL provide an "Enroll Student" button that executes the enrollStudent GraphQL mutation
3. WHEN the enroll button is clicked, THE System SHALL validate that all required fields are filled
4. WHEN enrollment is successful, THE System SHALL display the created student's information including their GitHub username
5. WHEN enrollment is successful, THE System SHALL inform the mentor that the student can now login via GitHub OAuth
6. WHEN enrollment fails, THE System SHALL display the error message clearly
7. THE Mock_UI SHALL indicate that this feature requires MENTOR role
8. THE Mock_UI SHALL maintain a list of enrolled students retrieved from the backend

### Requirement 5: Repository Creation Testing Interface

**User Story:** As a developer testing mentor functionality, I want to create repositories, so that I can verify repository management works.

#### Acceptance Criteria

1. THE Mock_UI SHALL provide input fields for repository name and URL
2. THE Mock_UI SHALL provide a "Create Repository" button that executes the createRepository mutation
3. WHEN the create button is clicked, THE System SHALL validate that required fields are filled
4. WHEN repository creation is successful, THE System SHALL display the created repository's information including ID
5. WHEN repository creation fails, THE System SHALL display the error message clearly
6. THE Mock_UI SHALL indicate that this feature requires MENTOR role

### Requirement 6: Contribution Metrics Testing Interface

**User Story:** As a developer testing student functionality, I want to save contribution metrics, so that I can verify metrics tracking works.

#### Acceptance Criteria

1. THE Mock_UI SHALL provide input fields for repository ID, commit count, PR count, issue count, and consistency score
2. THE Mock_UI SHALL provide a "Save Contribution Metrics" button that executes the saveContributionMetrics mutation
3. WHEN the save button is clicked, THE System SHALL validate that all numeric fields contain valid numbers
4. WHEN metrics are saved successfully, THE System SHALL display the saved metrics information
5. WHEN saving fails, THE System SHALL display the error message clearly
6. THE Mock_UI SHALL indicate that this feature requires STUDENT role

### Requirement 7: Mentor Metrics Query Testing Interface

**User Story:** As a developer testing mentor functionality, I want to query all contribution metrics for a repository, so that I can verify mentor access works.

#### Acceptance Criteria

1. THE Mock_UI SHALL provide an input field for repository ID
2. THE Mock_UI SHALL provide a "Get All Contribution Metrics (Mentor)" button that executes the getAllContributionMetrics query
3. WHEN the query button is clicked, THE System SHALL validate that repository ID is provided
4. WHEN metrics are retrieved successfully, THE System SHALL display all student metrics for that repository
5. WHEN the query fails, THE System SHALL display the error message clearly
6. THE Mock_UI SHALL indicate that this feature requires MENTOR role

### Requirement 8: AI Feedback Generation Testing Interface

**User Story:** As a developer, I want to generate AI feedback, so that I can verify the AI feedback system works for both students and mentors.

#### Acceptance Criteria

1. THE Mock_UI SHALL provide input fields for repository ID and optional student GitHub ID
2. THE Mock_UI SHALL provide a "Generate AI Feedback" button that executes the generateAIFeedback mutation
3. WHEN the generate button is clicked, THE System SHALL validate that repository ID is provided
4. WHEN AI feedback is generated successfully, THE System SHALL display the quality score, strengths, issues, and suggestions
5. WHEN generation fails, THE System SHALL display the error message clearly
6. THE Mock_UI SHALL indicate that student GitHub ID is required for mentors but optional for students

### Requirement 9: Candidate Search Testing Interface

**User Story:** As a developer, I want to search for candidates by job description, so that I can verify the skill DNA search functionality works.

#### Acceptance Criteria

1. THE Mock_UI SHALL provide a text area for entering job descriptions
2. THE Mock_UI SHALL provide a "Find Candidates" button that executes the findCandidates query
3. WHEN the search button is clicked, THE System SHALL validate that job description is not empty
4. WHEN candidates are found, THE System SHALL display each candidate's username, email, match score, and verified skills
5. WHEN no candidates are found, THE System SHALL display a "No candidates found" message
6. WHEN the search fails, THE System SHALL display the error message clearly

### Requirement 10: Response Display and Error Handling

**User Story:** As a developer, I want clear visual feedback for all operations, so that I can quickly identify issues and verify correct behavior.

#### Acceptance Criteria

1. WHEN any API call is made, THE Mock_UI SHALL display a loading indicator
2. WHEN an API call succeeds, THE Mock_UI SHALL display the response in a formatted, readable way
3. WHEN an API call fails, THE Mock_UI SHALL display the error message in red text
4. WHEN displaying JSON responses, THE Mock_UI SHALL use proper indentation and syntax highlighting
5. THE Mock_UI SHALL provide a "Clear Results" button to reset the response display area

### Requirement 11: Configuration and Setup

**User Story:** As a developer, I want easy configuration of the backend URL, so that I can test against different environments.

#### Acceptance Criteria

1. THE Mock_UI SHALL include a configuration section at the top with an input field for backend URL
2. THE Mock_UI SHALL default to http://localhost:8000 as the backend URL
3. WHEN the backend URL is changed, THE System SHALL use the new URL for all subsequent API calls
4. THE Mock_UI SHALL persist the backend URL in browser localStorage
5. THE Mock_UI SHALL display the current backend URL prominently

### Requirement 12: Token Management

**User Story:** As a developer, I want to manually manage JWT tokens, so that I can test with different user tokens and scenarios.

#### Acceptance Criteria

1. THE Mock_UI SHALL provide a text area for manually entering or editing JWT tokens
2. THE Mock_UI SHALL persist the JWT token in browser localStorage
3. WHEN a token is manually entered, THE System SHALL use it for all authenticated requests
4. THE Mock_UI SHALL provide a "Copy Token" button to copy the current token to clipboard
5. THE Mock_UI SHALL display token expiration warnings if the token format can be decoded

### Requirement 13: Test Scenario Documentation

**User Story:** As a developer, I want inline documentation of test scenarios, so that I understand how to test each feature properly.

#### Acceptance Criteria

1. THE Mock_UI SHALL include collapsible help sections for each feature
2. WHEN a help section is expanded, THE System SHALL display step-by-step testing instructions
3. THE Mock_UI SHALL include example values for all input fields
4. THE Mock_UI SHALL document which features require MENTOR vs STUDENT roles
5. THE Mock_UI SHALL include a "Quick Start" section explaining the basic testing workflow

### Requirement 14: GraphQL Request Builder

**User Story:** As a developer, I want to see and edit GraphQL queries before sending them, so that I can customize tests and learn the API.

#### Acceptance Criteria

1. THE Mock_UI SHALL provide a "Show GraphQL Query" toggle for each GraphQL operation
2. WHEN the toggle is enabled, THE System SHALL display the GraphQL query/mutation text in an editable text area
3. WHEN a query is edited, THE System SHALL use the edited version when the operation is executed
4. THE Mock_UI SHALL provide "Reset to Default" buttons to restore original queries
5. THE Mock_UI SHALL validate GraphQL syntax before sending requests

### Requirement 15: Batch Testing and Automation

**User Story:** As a developer, I want to run multiple tests in sequence, so that I can quickly validate end-to-end workflows.

#### Acceptance Criteria

1. THE Mock_UI SHALL provide a "Run Full Test Suite" button
2. WHEN the test suite runs, THE System SHALL execute a predefined sequence of operations
3. WHEN running the test suite, THE System SHALL display progress and results for each step
4. THE Mock_UI SHALL include test scenarios for both MENTOR and STUDENT workflows
5. WHEN the test suite completes, THE System SHALL display a summary of passed and failed operations
