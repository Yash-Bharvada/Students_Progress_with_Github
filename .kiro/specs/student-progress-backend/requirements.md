# Requirements Document

## Introduction

A production-ready backend system for tracking student project progress and performance using FastAPI, GraphQL (Strawberry), MongoDB Atlas, and GitHub OAuth authentication. The system enforces strict role-based access control with only two roles: MENTOR and STUDENT, where students cannot self-register and must be enrolled by mentors.

## Glossary

- **System**: The Student Project Progress & Performance Tracking Backend
- **Mentor**: A user with MENTOR role who can enroll students and create repositories
- **Student**: A user with STUDENT role who can only login if pre-enrolled and track their own metrics
- **GitHub_OAuth**: GitHub Authorization Code Flow authentication mechanism
- **JWT_Handler**: JSON Web Token authentication and authorization system
- **MongoDB_Atlas**: Cloud MongoDB database service using Motor async driver
- **GraphQL_API**: API interface using Strawberry GraphQL framework
- **Contribution_Metrics**: Student performance data including commits, PRs, issues, and consistency scores
- **AI_Feedback**: AI-generated code quality analysis and improvement suggestions for student repositories
- **LLM_Service**: Large Language Model service (Google Gemini Flash API) for generating educational feedback

## Requirements

### Requirement 1: GitHub OAuth Authentication

**User Story:** As a system user, I want to authenticate using GitHub OAuth, so that I can securely access the system using my existing GitHub credentials.

#### Acceptance Criteria

1. WHEN a user accesses /auth/github/login, THE System SHALL redirect them to GitHub's OAuth authorization page
2. WHEN GitHub redirects back to /auth/github/callback with an authorization code, THE System SHALL exchange the code for an access token
3. WHEN the System receives a valid GitHub access token, THE System SHALL fetch the user's GitHub profile including id, login, and email
4. WHEN the System successfully retrieves GitHub profile data, THE System SHALL validate the user against the MongoDB user collection
5. IF the user exists in MongoDB, THE System SHALL issue a JWT token for authentication
6. IF the user does NOT exist and has MENTOR role potential, THE System SHALL create a new user record and issue a JWT token
7. IF the user does NOT exist and would be a STUDENT, THE System SHALL deny access with 403 Forbidden status

### Requirement 2: Role-Based Access Control

**User Story:** As a system administrator, I want strict role-based access control, so that only authorized users can perform specific operations based on their assigned roles.

#### Acceptance Criteria

1. THE System SHALL support exactly two roles: MENTOR and STUDENT
2. WHEN a student attempts to register themselves, THE System SHALL prevent the registration and maintain system security
3. WHEN a mentor enrolls a student using GitHub username, THE System SHALL create a student record with isEnrolled=true
4. WHEN a student attempts to login via GitHub OAuth, THE System SHALL only allow login if the student was pre-enrolled by a mentor
5. WHEN any user attempts to access protected GraphQL operations, THE System SHALL validate their JWT token and role permissions

### Requirement 3: Student Enrollment Management

**User Story:** As a mentor, I want to enroll students using their GitHub username, so that I can grant them access to track their project progress.

#### Acceptance Criteria

1. WHEN a mentor provides a valid GitHub username and email for enrollment, THE System SHALL create a new student record
2. WHEN creating a student record, THE System SHALL set isEnrolled=true and record the enrolling mentor's GitHub ID
3. WHEN a mentor attempts to enroll a student, THE System SHALL validate the mentor's authorization before proceeding
4. WHEN student enrollment is successful, THE System SHALL return the student's id, username, and role information
5. IF a mentor attempts to enroll an already enrolled student, THE System SHALL handle the duplicate gracefully

### Requirement 4: Repository Management

**User Story:** As a mentor, I want to create and manage repositories, so that I can track student contributions across different projects.

#### Acceptance Criteria

1. WHEN a mentor provides repository name and URL, THE System SHALL create a new repository record
2. WHEN creating a repository, THE System SHALL record the mentor's GitHub ID as the owner
3. WHEN a repository is created, THE System SHALL initialize an empty linkedStudents array for future student associations
4. WHEN a mentor attempts to create a repository, THE System SHALL validate the mentor's authorization
5. THE System SHALL store repository creation timestamp for audit purposes

### Requirement 5: Contribution Metrics Tracking

**User Story:** As a student, I want to save my contribution metrics, so that I can track my project progress and performance over time.

#### Acceptance Criteria

1. WHEN a student provides valid contribution data for a repository, THE System SHALL save the metrics to their record
2. WHEN saving contribution metrics, THE System SHALL validate that the student is authorized to update only their own metrics
3. WHEN contribution metrics are saved, THE System SHALL update commitCount, prCount, issueCount, and consistencyScore
4. WHEN metrics are updated, THE System SHALL record the lastUpdated timestamp
5. THE System SHALL prevent students from modifying other students' contribution metrics

### Requirement 6: GraphQL API Interface

**User Story:** As a frontend developer, I want a stable GraphQL API, so that I can build user interfaces without worrying about API changes.

#### Acceptance Criteria

1. THE System SHALL provide a getMe query that returns the current user's profile information
2. THE System SHALL provide a getRepositories query that returns repositories based on user role and permissions
3. THE System SHALL provide a getMyContributionMetrics query for students to view their own metrics
4. THE System SHALL provide a getAllContributionMetrics query for mentors to view all student metrics for a repository
5. THE System SHALL provide enrollStudent, createRepository, and saveContributionMetrics mutations with proper authorization
6. WHEN any GraphQL operation is called, THE System SHALL require valid JWT authentication
7. WHEN GraphQL operations are executed, THE System SHALL enforce role-based authorization rules

### Requirement 7: JWT Token Management

**User Story:** As a system user, I want secure token-based authentication, so that my session remains secure and my identity is properly validated.

#### Acceptance Criteria

1. WHEN a user successfully authenticates via GitHub OAuth, THE System SHALL issue a JWT token containing user identification
2. WHEN a JWT token is issued, THE System SHALL include necessary claims for user identification and role validation
3. WHEN GraphQL requests are made, THE System SHALL extract and validate JWT tokens from Authorization Bearer headers
4. WHEN a JWT token is invalid or expired, THE System SHALL reject the request with appropriate error messages
5. THE System SHALL use secure JWT signing algorithms and proper token expiration policies

### Requirement 8: MongoDB Data Persistence

**User Story:** As a system administrator, I want reliable data storage, so that user information and metrics are persistently maintained.

#### Acceptance Criteria

1. THE System SHALL store user data in a User collection with githubId, username, email, role, isEnrolled, enrolledBy, and createdAt fields
2. THE System SHALL store repository data in a Repository collection with repoName, repoUrl, ownerGithubId, linkedStudents, and createdAt fields
3. THE System SHALL store contribution data in a ContributionMetrics collection with repoId, studentGithubId, metrics, and lastUpdated fields
4. WHEN data is stored, THE System SHALL use proper MongoDB ObjectId types for document references
5. THE System SHALL use Motor async driver for all database operations to maintain performance

### Requirement 9: Error Handling and Security

**User Story:** As a system administrator, I want comprehensive error handling and security measures, so that the system remains stable and secure in production.

#### Acceptance Criteria

1. WHEN authentication failures occur, THE System SHALL return appropriate HTTP status codes and error messages
2. WHEN authorization violations are detected, THE System SHALL log the attempt and return 403 Forbidden responses
3. WHEN database operations fail, THE System SHALL handle exceptions gracefully and provide meaningful error responses
4. WHEN invalid input is provided to GraphQL operations, THE System SHALL validate and reject with clear error messages
5. THE System SHALL implement proper CORS policies and security headers for production deployment

### Requirement 10: Production Deployment Configuration

**User Story:** As a DevOps engineer, I want proper configuration management, so that the system can be deployed securely in different environments.

#### Acceptance Criteria

1. THE System SHALL use environment variables for all sensitive configuration including database URLs and OAuth secrets
2. THE System SHALL provide a comprehensive requirements.txt file with all necessary Python dependencies
3. THE System SHALL include a .env.example file showing required environment variables
4. WHEN the system starts, THE System SHALL validate that all required configuration is present
5. THE System SHALL be runnable using uvicorn with proper async support and reload capabilities for development

### Requirement 11: AI-Powered Code Quality Feedback

**User Story:** As a student, I want AI-generated feedback on my code quality, so that I can learn and improve my programming practices through actionable suggestions.

#### Acceptance Criteria

1. WHEN a user requests AI feedback for a repository, THE System SHALL analyze GitHub contribution data and generate structured feedback using Google Gemini Flash API
2. WHEN generating AI feedback, THE System SHALL collect commit frequency, average commit size, presence of tests/documentation, and recent commit messages
3. WHEN AI analysis is complete, THE System SHALL generate a quality score (0-10), strengths list, issues list, and improvement suggestions using Gemini Flash's fast natural language capabilities
4. WHEN AI feedback is generated, THE System SHALL store the results in an AIFeedback collection with repoId, studentGithubId, and timestamp
5. THE System SHALL ensure AI feedback is constructive, educational, and clearly states suggestions are advisory

### Requirement 12: AI Feedback Authorization and Access

**User Story:** As a mentor, I want to generate and view AI feedback for student repositories, so that I can provide better guidance based on automated analysis.

#### Acceptance Criteria

1. WHEN a student requests AI feedback generation, THE System SHALL only allow generation for repositories they have access to
2. WHEN a mentor requests AI feedback generation, THE System SHALL allow generation for any student repository
3. WHEN viewing AI feedback, students SHALL only access their own feedback while mentors SHALL access all student feedback
4. WHEN AI feedback is requested for a repository, THE System SHALL validate user authorization before processing
5. THE System SHALL integrate AI feedback operations into existing GraphQL authorization rules

### Requirement 13: AI Feedback Data Management

**User Story:** As a system administrator, I want reliable storage and retrieval of AI feedback data, so that feedback history is maintained and accessible.

#### Acceptance Criteria

1. THE System SHALL store AI feedback in an AIFeedback collection with _id, repoId, studentGithubId, qualityScore, strengths, issues, suggestions, and generatedAt fields
2. WHEN storing AI feedback, THE System SHALL use proper MongoDB ObjectId types for document references
3. WHEN AI feedback is generated, THE System SHALL include timestamp information for audit and history tracking
4. THE System SHALL handle Gemini Flash API service failures gracefully and provide meaningful error responses
5. THE System SHALL maintain AI feedback data integrity and prevent unauthorized modifications