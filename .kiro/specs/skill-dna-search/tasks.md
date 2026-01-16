# Implementation Plan: Skill DNA & Headhunter Search

## Overview

Implementation of an AI-powered skill extraction and job matching system that scans local code repositories, generates semantic embeddings using local SentenceTransformers, and performs local vector search using scikit-learn. The system uses Google Gemini Flash for code analysis (with rate limiting) and local HuggingFace models for embeddings, extending the existing student-progress-backend with new AI capabilities while maintaining compatibility with existing infrastructure.

## Tasks

- [x] 1. Update project dependencies
  - Add scikit-learn, numpy, google-generativeai, sentence-transformers to requirements.txt
  - Verify compatibility with existing dependencies
  - Update .env.example with GEMINI_API_KEY
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 11.4_

- [x] 2. Extend data models for skill profiles
  - [x] 2.1 Create SkillTag and UserSkillProfile Pydantic models in backend/models.py
    - Define SkillTag with name, confidence, evidence_file fields
    - Define UserSkillProfile with verified_skills, skill_embedding, last_scanned
    - Add embedding dimension validator (must be 384 for SentenceTransformers)
    - _Requirements: 2.1, 2.2, 2.4_

  - [ ]* 2.2 Write property test for embedding dimension validation
    - **Property 1: Embedding Dimension Consistency**
    - **Validates: Requirements 2.4, 4.2, 4.3, 12.2**

  - [x] 2.3 Extend User model with optional skill_profile field
    - Add skill_profile: Optional[UserSkillProfile] to User model
    - Ensure backward compatibility with existing user documents
    - _Requirements: 2.3_

- [-] 3. Implement Skill Engine AI module
  - [x] 3.1 Create backend/ai/skill_engine.py with SkillEngine class
    - Implement __init__ to load Gemini Flash model
    - Create analyze_code_file method for code analysis using Gemini Flash
    - Create generate_embedding method for 384-dim vector generation using local SentenceTransformers
    - Load SentenceTransformers model globally (all-MiniLM-L6-v2)
    - Add error handling for API failures
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.6, 4.1, 4.2, 4.4, 4.5, 11.2_

  - [ ]* 3.2 Write property test for code analysis output
    - **Property 2: Code Analysis Returns Structured Skills**
    - **Validates: Requirements 3.3**

  - [ ]* 3.3 Write unit tests for Skill Engine error handling
    - Test API failure scenarios
    - Test rate limit handling
    - Test invalid API key errors
    - _Requirements: 3.4, 4.4, 12.1_

- [x] 4. Create repository scanning utility
  - [x] 4.1 Create scan_local_repo.py script in project root
    - Implement command-line argument parsing (--directory, --github-id)
    - Create RepositoryScanner class with pymongo connection
    - Implement recursive directory traversal for .py files
    - Add file filtering logic (skip venv, __pycache__, .git, node_modules)
    - _Requirements: 5.1, 5.2, 5.5, 10.1, 10.2_

  - [x] 4.2 Implement skill extraction and aggregation
    - Batch analyze all found Python files using SkillEngine
    - Implement 12-second delay between Gemini API calls (5 RPM limit)
    - Aggregate skills from all files into summary string
    - Generate master embedding from aggregated skills using local SentenceTransformers
    - _Requirements: 5.3, 5.4, 6.1, 3.6_

  - [ ]* 4.3 Write property test for repository scanning completeness
    - **Property 3: Repository Scanning Completeness**
    - **Validates: Requirements 5.2, 5.3, 5.4, 5.5, 3.6**

  - [x] 4.3 Implement MongoDB profile updates
    - Update User document with UserSkillProfile
    - Set verified_skills, skill_embedding, last_scanned fields
    - Add progress reporting and confirmation output
    - _Requirements: 6.2, 6.3, 6.4, 10.4_

  - [ ]* 4.4 Write property test for skill profile update integrity
    - **Property 4: Skill Profile Update Integrity**
    - **Validates: Requirements 6.1, 6.2, 6.3, 6.4**

  - [ ]* 4.5 Write unit tests for edge cases
    - Test empty directory handling
    - Test no Python files found
    - Test MongoDB connection failures
    - _Requirements: 12.3, 12.4_

- [ ] 5. Checkpoint - Core scanning functionality complete
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 6. Implement recommendation service
  - [x] 6.1 Create backend/services/recommendation.py with RecommendationService class
    - Implement find_matching_students method
    - Generate job embedding from job description using local SentenceTransformers
    - Load SentenceTransformers model globally for efficiency
    - Retrieve all users with skill_embedding from MongoDB using motor
    - Calculate cosine similarity using sklearn.metrics.pairwise.cosine_similarity
    - Filter results by threshold (>0.6) and return top 5
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 8.1, 8.2, 8.4_

  - [ ]* 6.2 Write property test for candidate search workflow
    - **Property 5: Candidate Search Workflow**
    - **Validates: Requirements 7.1, 7.2, 7.3, 7.4, 8.2, 8.4**

  - [ ]* 6.3 Write unit tests for edge cases
    - Test no users with embeddings (empty list)
    - Test all scores below threshold
    - Test cosine similarity calculation failures
    - _Requirements: 8.5, 12.5_

- [x] 7. Extend GraphQL schema for candidate search
  - [x] 7.1 Add SkillTag, UserSkillProfile, CandidateResult types to backend/graphql/schema.py
    - Define Strawberry types matching Pydantic models
    - Add match_score field to CandidateResult
    - _Requirements: 9.4_

  - [x] 7.2 Implement findCandidates query in backend/graphql/queries.py
    - Add findCandidates query accepting jobDescription parameter
    - Validate authentication using existing JWT validation
    - Call RecommendationService.find_matching_students
    - Transform results to CandidateResult GraphQL types
    - _Requirements: 9.1, 9.2, 9.3, 9.5_

  - [ ]* 7.3 Write property test for GraphQL candidate query integration
    - **Property 6: GraphQL Candidate Query Integration**
    - **Validates: Requirements 9.2, 9.3**

  - [ ]* 7.4 Write property test for authentication enforcement
    - **Property 7: Authentication Enforcement**
    - **Validates: Requirements 9.5**

  - [ ]* 7.5 Write unit tests for GraphQL integration
    - Test query with valid authentication
    - Test query without authentication
    - Test result transformation
    - _Requirements: 9.1, 9.5_

- [x] 8. Update configuration module
  - [x] 8.1 Add GEMINI_API_KEY to backend/config.py
    - Add GEMINI_API_KEY field with environment variable binding
    - Add validator to ensure key is set and not placeholder
    - _Requirements: 11.1, 11.2_

  - [ ]* 8.2 Write property test for Skill Engine initialization
    - **Property 8: Skill Engine Initialization**
    - **Validates: Requirements 11.2**

  - [ ]* 8.3 Write unit test for missing API key error
    - Test configuration error when GEMINI_API_KEY is missing
    - _Requirements: 11.3_

- [ ] 9. Checkpoint - All components implemented
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 10. Integration and end-to-end testing
  - [ ] 10.1 Create integration test for complete scanning workflow
    - Test scan_local_repo.py with sample repository
    - Verify skill extraction and profile updates
    - Validate embedding generation and storage
    - _Requirements: All scanning requirements_

  - [ ] 10.2 Create integration test for complete search workflow
    - Test findCandidates GraphQL query end-to-end
    - Verify job embedding generation
    - Validate similarity calculations and ranking
    - Test with multiple users and various job descriptions
    - _Requirements: All search requirements_

  - [ ]* 10.3 Write property test for scanner progress reporting
    - **Property 9: Scanner Progress Reporting**
    - **Validates: Requirements 10.4**

  - [ ] 10.4 Test script executability
    - Verify scan_local_repo.py runs from command line
    - Test with various directory paths and GitHub IDs
    - Validate error messages for invalid inputs
    - _Requirements: 10.5_

- [ ] 11. Documentation and deployment preparation
  - [ ] 11.1 Update README with skill search feature documentation
    - Document scan_local_repo.py usage
    - Document findCandidates GraphQL query
    - Add examples of job matching queries
    - _Requirements: All requirements_

  - [ ] 11.2 Create usage examples
    - Example: Scanning a local repository
    - Example: GraphQL query for finding candidates
    - Example: Interpreting match scores
    - _Requirements: All requirements_

- [ ] 12. Final checkpoint - Production ready
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
- Integration tests verify end-to-end workflows
- The system integrates with existing student-progress-backend infrastructure
- AI operations use Google Gemini Flash for code analysis (5 RPM limit with 12s delays)
- Embeddings use local SentenceTransformers all-MiniLM-L6-v2 (384-dim, unlimited, free)
- Search uses local scikit-learn cosine similarity (no cloud vector database)
