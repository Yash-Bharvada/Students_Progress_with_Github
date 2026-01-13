# Implementation Plan: Student Progress Backend

## Overview

Implementation of a production-ready FastAPI backend with Strawberry GraphQL, GitHub OAuth authentication, MongoDB Atlas persistence, strict role-based access control, and AI-powered code quality feedback system. The implementation follows the mandatory project structure and enforces critical access control rules where only mentors can enroll students.

## Tasks

- [x] 1. Set up project structure and dependencies
  - Create backend directory with mandatory structure including ai/ module
  - Set up requirements.txt with FastAPI, Strawberry, Motor, PyJWT, Google Generative AI dependencies
  - Create .env.example with required environment variables including Gemini API key
  - _Requirements: 10.2, 10.3_

- [x] 2. Implement configuration and database connection
  - [x] 2.1 Create config.py with environment variable validation
    - Load GitHub OAuth credentials, MongoDB connection string, JWT secret
    - Validate all required configuration on startup
    - _Requirements: 10.1, 10.4_

  - [x] 2.2 Implement database.py with Motor async MongoDB connection
    - Create Database class with async connection management
    - Set up collections for users, repositories, contribution_metrics, ai_feedback
    - Handle connection errors and provide proper error messages
    - _Requirements: 8.5, 9.3, 13.2_

- [x] 2.3 Create Postman collection setup
  - Create sample GraphQL queries and mutations for Postman testing
  - Include authentication examples with JWT tokens
  - _Requirements: 10.4_

- [x] 3. Implement authentication system
  - [x] 3.1 Create GitHub OAuth handler (auth/github_oauth.py)
    - Implement authorization URL generation for /auth/github/login
    - Implement authorization code exchange for /auth/github/callback
    - Fetch GitHub user profile (id, login, email)
    - _Requirements: 1.1, 1.2, 1.3_

  - [x] 3.2 Create JWT handler (auth/jwt_handler.py)
    - Implement JWT token creation with user claims
    - Implement token validation and user extraction
    - Handle invalid/expired tokens with proper error messages
    - _Requirements: 7.1, 7.2, 7.3, 7.4_

  - [x] 3.3 Create Postman authentication examples
    - Create sample OAuth flow testing steps
    - Provide JWT token extraction examples
    - _Requirements: 1.3, 1.4, 7.1, 7.2, 7.3_

- [x] 4. Implement user authentication and authorization logic
  - [x] 4.1 Create user validation logic in OAuth callback
    - Check if user exists in MongoDB
    - Issue JWT for existing users
    - Create mentor users if they don't exist
    - Deny access for non-enrolled students with 403 Forbidden
    - _Requirements: 1.4, 1.5, 1.6, 1.7_

  - [x] 4.2 Create Postman examples for user authentication
    - Provide sample mentor and student login scenarios
    - Include error case examples (403 Forbidden for non-enrolled students)
    - _Requirements: 1.5, 1.7, 2.4, 1.6_

- [x] 5. Create data models and GraphQL types
  - [x] 5.1 Create models.py with Pydantic models
    - Define User, Repository, ContributionMetrics models
    - Include proper field validation and types
    - Ensure ObjectId handling for MongoDB references
    - _Requirements: 8.1, 8.2, 8.3, 8.4_

  - [x] 5.2 Create GraphQL schema types (graphql/schema.py)
    - Define Strawberry types for User, Repository, ContributionMetrics
    - Create Role enum for MENTOR/STUDENT
    - Set up proper type annotations and field definitions
    - _Requirements: 2.1, 6.1, 6.2, 6.3, 6.4_

  - [x] 5.3 Create Postman examples for data models
    - Provide sample data creation and validation examples
    - Include ObjectId reference examples
    - _Requirements: 8.1, 8.2, 8.3, 8.4_

- [x] 6. Implement GraphQL permission classes and authorization
  - [x] 6.1 Create permission classes (graphql/permissions.py)
    - Implement IsAuthenticated, IsMentor, IsStudent permission classes
    - Validate JWT tokens and user roles in GraphQL context
    - _Requirements: 2.5, 6.6, 6.7_

  - [x] 6.2 Create GraphQL context management
    - Extract JWT tokens from Authorization headers
    - Set up user context for GraphQL resolvers
    - Handle authentication failures gracefully
    - _Requirements: 7.3, 9.1_

  - [x] 6.3 Create Postman examples for authorization testing
    - Provide role-based access control test scenarios
    - Include mentor vs student permission examples
    - _Requirements: 2.1, 2.5, 6.6, 6.7_

- [x] 7. Implement GraphQL queries
  - [x] 7.1 Create query resolvers (graphql/queries.py)
    - Implement getMe query for current user profile
    - Implement getRepositories with role-based filtering
    - Implement getMyContributionMetrics for students
    - Implement getAllContributionMetrics for mentors (repo-specific)
    - _Requirements: 6.1, 6.2, 6.3, 6.4_

  - [x] 7.2 Create Postman GraphQL query collection
    - Provide ready-to-use GraphQL queries for getMe, getRepositories, getMyContributionMetrics, getAllContributionMetrics
    - Include proper Authorization headers and variable examples
    - _Requirements: 6.1, 6.2, 6.3, 6.4_

- [x] 8. Implement GraphQL mutations
  - [x] 8.1 Create mutation resolvers (graphql/mutations.py)
    - Implement enrollStudent mutation (mentor-only)
    - Implement createRepository mutation (mentor-only)
    - Implement saveContributionMetrics mutation (student-only, self-data)
    - _Requirements: 3.1, 3.2, 4.1, 4.2, 5.1, 5.3_

  - [x] 8.2 Add authorization validation to mutations
    - Validate mentor permissions for enrollment and repository creation
    - Validate student permissions for metrics (self-only)
    - Handle duplicate enrollments gracefully
    - _Requirements: 3.3, 3.5, 4.4, 5.2, 5.5_

  - [x] 8.3 Create Postman GraphQL mutation collection
    - Provide ready-to-use mutations for enrollStudent, createRepository, saveContributionMetrics
    - Include sample payloads and expected responses
    - Add authorization examples for mentor-only and student-only operations
    - _Requirements: 3.1, 3.2, 3.4, 4.1, 4.2, 4.3, 4.5, 5.1, 5.3_

- [x] 9. Checkpoint - Core functionality complete
  - Ensure all tests pass, ask the user if questions arise.

- [x] 10. Implement FastAPI application setup
  - [x] 10.1 Create main.py with FastAPI app initialization
    - Set up FastAPI app with CORS configuration
    - Mount authentication routes at /auth prefix
    - Mount GraphQL endpoint at /graphql
    - Add database connection lifecycle management
    - _Requirements: 9.5, 10.5_

  - [x] 10.2 Create authentication routes
    - Implement /auth/github/login redirect endpoint
    - Implement /auth/github/callback OAuth handler
    - Integrate with user validation and JWT issuance
    - _Requirements: 1.1, 1.2, 1.4, 1.5, 1.6, 1.7_

  - [x] 10.3 Create Postman authentication endpoint collection
    - Provide ready-to-use requests for /auth/github/login and /auth/github/callback
    - Include OAuth flow testing steps and JWT extraction examples
    - _Requirements: 1.1, 1.2, 9.1_

- [x] 11. Implement comprehensive error handling
  - [x] 11.1 Add error handling throughout the application
    - Handle authentication failures with proper status codes
    - Handle authorization violations with 403 responses and logging
    - Handle database errors gracefully
    - Handle GraphQL input validation errors
    - _Requirements: 9.1, 9.2, 9.3, 9.4_

  - [x] 11.2 Create Postman error handling examples
    - Provide examples for authentication failures, authorization violations, database errors
    - Include expected error responses and status codes
    - _Requirements: 9.1, 9.2, 9.3, 9.4_

- [x] 12. Create comprehensive Postman collection for all operations
  - [x] 12.1 Organize complete Postman collection with folders
    - Authentication folder with OAuth and JWT examples
    - GraphQL Queries folder with all query operations
    - GraphQL Mutations folder with all mutation operations
    - Error Scenarios folder with various error cases
    - _Requirements: All requirements integration_

  - [x] 12.2 Add environment variables and pre-request scripts
    - Set up Postman environment with base URLs and tokens
    - Create pre-request scripts for automatic JWT token handling
    - Include variable examples for easy testing
    - _Requirements: 7.3, 9.1_

- [x] 13. Implement AI feedback system using Google Gemini API
  - [x] 13.1 Create AI feedback engine (ai/feedback_engine.py)
    - Implement GitHub repository data analysis
    - Create structured AI input from commit patterns and code indicators
    - Integrate with Google Gemini Flash API for fast feedback generation
    - Parse and validate Gemini Flash API responses safely
    - Handle Gemini API rate limits and error responses
    - Optimize prompts for Gemini Flash model's capabilities
    - _Requirements: 11.1, 11.2, 11.3_

  - [x] 13.2 Create AI prompt templates (ai/prompts.py)
    - Design educational and constructive prompt templates optimized for Gemini Flash
    - Ensure advisory tone and avoid absolute judgments
    - Create reusable prompt generation functions for Gemini Flash API format
    - Implement prompt engineering best practices for code analysis with Flash model
    - Optimize token usage for Flash model's efficiency
    - _Requirements: 11.5_

  - [x] 13.3 Add AIFeedback GraphQL types and resolvers
    - Create AIFeedback Strawberry type with quality score, strengths, issues, suggestions
    - Implement generateAIFeedback mutation with role-based authorization
    - Implement getMyAIFeedback query with proper access control
    - _Requirements: 12.1, 12.2, 12.3_

  - [x] 13.4 Create Postman AI feedback mutation collection
    - Provide ready-to-use generateAIFeedback mutation with sample payloads
    - Include role-based authorization examples (student vs mentor access)
    - Add sample repository IDs and expected Gemini Flash-generated AI feedback responses
    - Include error handling examples for Gemini Flash API failures
    - Test Flash model's fast response times and efficiency
    - _Requirements: 11.1, 11.2, 11.3, 12.1, 12.2, 12.4_

  - [x] 13.5 Create Postman AI feedback query collection
    - Provide ready-to-use getMyAIFeedback query with sample variables
    - Include examples for both student and mentor access patterns
    - Add sample responses showing Gemini Flash-generated quality scores, strengths, issues, and suggestions
    - Include comprehensive testing scenarios for Gemini Flash API integration
    - Validate Flash model's consistent and reliable feedback generation
    - _Requirements: 12.3, 13.1, 13.3_

- [x] 14. Final integration and testing
  - [x] 14.1 Create comprehensive integration tests
    - Test complete OAuth flow end-to-end
    - Test GraphQL operations with real JWT tokens
    - Test role-based access scenarios
    - Test AI feedback generation with real Gemini Flash API integration
    - Test error conditions and edge cases
    - _Requirements: All requirements integration_

  - [x] 14.2 Verify production readiness and create final Postman collection
    - Test with uvicorn server startup
    - Verify all environment variables are properly used
    - Test CORS configuration
    - Validate all GraphQL schema operations
    - Export complete Postman collection for distribution
    - _Requirements: 10.5, 9.5_

- [ ] 15. Final checkpoint - Production ready
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- All tasks focus on implementation and Postman testing preparation
- Each task references specific requirements for traceability
- Postman collections will be created for comprehensive API testing
- GraphQL mutations and queries will be ready-to-use in Postman
- All authentication and authorization logic must be thoroughly tested via Postman
- Database operations use Motor async driver throughout
- GraphQL operations enforce strict role-based permissions
- AI feedback system integrates cleanly with existing authorization rules using Google Gemini Flash API