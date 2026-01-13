# Data Models Guide

## Overview

This guide provides comprehensive examples and validation patterns for the Student Progress Backend data models, including Pydantic models for MongoDB persistence and Strawberry GraphQL types for API interface.

## Pydantic Models (backend/models.py)

### User Model

The User model represents both mentors and students in the system with role-based field validation.

```python
class User(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    github_id: str = Field(..., description="GitHub user ID", alias="githubId")
    username: str = Field(..., description="GitHub username")
    email: Optional[str] = Field(None, description="User email address")
    role: Role = Field(..., description="User role (MENTOR or STUDENT)")
    is_enrolled: bool = Field(default=False, description="Whether student is enrolled", alias="isEnrolled")
    enrolled_by: Optional[str] = Field(None, description="GitHub ID of enrolling mentor", alias="enrolledBy")
    created_at: datetime = Field(default_factory=datetime.utcnow, alias="createdAt")
```

**Sample Data:**
```json
{
  "_id": "507f1f77bcf86cd799439011",
  "githubId": "12345",
  "username": "john_doe",
  "email": "john@example.com",
  "role": "MENTOR",
  "isEnrolled": true,
  "enrolledBy": null,
  "createdAt": "2024-01-15T10:30:00Z"
}
```

**Validation Rules:**
- `githubId` must be unique across all users
- `role` must be either "MENTOR" or "STUDENT"
- `enrolledBy` should be null for mentors, required for students
- `isEnrolled` should be true for mentors by default

### Repository Model

The Repository model represents code repositories managed by mentors with linked students.

```python
class Repository(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    repo_name: str = Field(..., description="Repository name", alias="repoName")
    repo_url: str = Field(..., description="Repository URL", alias="repoUrl")
    owner_github_id: str = Field(..., description="Repository owner's GitHub ID", alias="ownerGithubId")
    linked_students: List[str] = Field(default_factory=list, description="List of linked student GitHub IDs", alias="linkedStudents")
    created_at: datetime = Field(default_factory=datetime.utcnow, alias="createdAt")
```

**Sample Data:**
```json
{
  "_id": "507f1f77bcf86cd799439013",
  "repoName": "Student Portfolio Project",
  "repoUrl": "https://github.com/mentor/student-portfolio",
  "ownerGithubId": "12345",
  "linkedStudents": ["67890", "11111", "22222"],
  "createdAt": "2024-01-15T12:00:00Z"
}
```

**Validation Rules:**
- `repoUrl` must be unique across all repositories
- `ownerGithubId` must reference an existing mentor
- `linkedStudents` array contains GitHub IDs of enrolled students

### ContributionMetrics Model

The ContributionMetrics model tracks student performance metrics for specific repositories.

```python
class ContributionMetrics(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    repo_id: PyObjectId = Field(..., description="Repository ObjectId", alias="repoId")
    student_github_id: str = Field(..., description="Student's GitHub ID", alias="studentGithubId")
    commit_count: int = Field(default=0, description="Number of commits", alias="commitCount")
    pr_count: int = Field(default=0, description="Number of pull requests", alias="prCount")
    issue_count: int = Field(default=0, description="Number of issues", alias="issueCount")
    consistency_score: float = Field(default=0.0, description="Consistency score (0.0-1.0)", alias="consistencyScore")
    last_updated: datetime = Field(default_factory=datetime.utcnow, alias="lastUpdated")
```

**Sample Data:**
```json
{
  "_id": "507f1f77bcf86cd799439014",
  "repoId": "507f1f77bcf86cd799439013",
  "studentGithubId": "67890",
  "commitCount": 25,
  "prCount": 5,
  "issueCount": 3,
  "consistencyScore": 0.85,
  "lastUpdated": "2024-01-15T15:30:00Z"
}
```

**ObjectId Reference:**
- `repoId` references the Repository document's `_id`
- This creates a relationship between metrics and repositories
- Enables efficient MongoDB queries and aggregations

### AIFeedback Model

The AIFeedback model stores AI-generated code quality feedback for student repositories.

```python
class AIFeedback(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    repo_id: PyObjectId = Field(..., description="Repository ObjectId", alias="repoId")
    student_github_id: str = Field(..., description="Student's GitHub ID", alias="studentGithubId")
    quality_score: float = Field(..., description="Code quality score (0.0-10.0)", alias="qualityScore")
    strengths: List[str] = Field(default_factory=list, description="List of identified strengths")
    issues: List[str] = Field(default_factory=list, description="List of identified issues")
    suggestions: List[str] = Field(default_factory=list, description="List of improvement suggestions")
    generated_at: datetime = Field(default_factory=datetime.utcnow, alias="generatedAt")
```

**Sample Data:**
```json
{
  "_id": "507f1f77bcf86cd799439015",
  "repoId": "507f1f77bcf86cd799439013",
  "studentGithubId": "67890",
  "qualityScore": 7.5,
  "strengths": [
    "Consistent commit messages",
    "Good code organization",
    "Proper use of Git branches"
  ],
  "issues": [
    "Limited test coverage",
    "Some functions lack documentation"
  ],
  "suggestions": [
    "Add unit tests for core functions",
    "Include JSDoc comments for public methods",
    "Consider using a linter for code consistency"
  ],
  "generatedAt": "2024-01-15T16:00:00Z"
}
```

## GraphQL Types (backend/graphql/schema.py)

### Strawberry Type Definitions

The GraphQL schema uses Strawberry to define types that map from Pydantic models:

```python
@strawberry.enum
class Role(Enum):
    MENTOR = "MENTOR"
    STUDENT = "STUDENT"

@strawberry.type
class User:
    id: str = strawberry.field(description="User ID")
    github_id: str = strawberry.field(description="GitHub user ID")
    username: str = strawberry.field(description="GitHub username")
    email: Optional[str] = strawberry.field(description="User email address")
    role: Role = strawberry.field(description="User role (MENTOR or STUDENT)")
    is_enrolled: bool = strawberry.field(description="Whether student is enrolled")
    enrolled_by: Optional[str] = strawberry.field(description="GitHub ID of enrolling mentor")
    created_at: datetime = strawberry.field(description="Account creation timestamp")
```

### Type Mapping Patterns

| Pydantic Type | GraphQL Type | Notes |
|---------------|--------------|-------|
| `PyObjectId` | `String` | ObjectIds become string IDs in GraphQL |
| `Optional[str]` | `String` (nullable) | Optional fields are nullable in GraphQL |
| `List[str]` | `[String!]!` | Non-null array of non-null strings |
| `datetime` | `DateTime` | ISO 8601 formatted datetime strings |
| `Role` enum | `Role` enum | Direct enum mapping |
| `float` | `Float` | Direct numeric mapping |
| `int` | `Int` | Direct numeric mapping |

### Input Types for Mutations

```python
@strawberry.input
class EnrollStudentInput:
    github_username: str = strawberry.field(description="Student's GitHub username")
    email: str = strawberry.field(description="Student's email address")

@strawberry.input
class CreateRepositoryInput:
    repo_name: str = strawberry.field(description="Repository name")
    repo_url: str = strawberry.field(description="Repository URL")

@strawberry.input
class SaveContributionMetricsInput:
    repo_id: str = strawberry.field(description="Repository ID")
    commit_count: int = strawberry.field(description="Number of commits")
    pr_count: int = strawberry.field(description="Number of pull requests")
    issue_count: int = strawberry.field(description="Number of issues")
    consistency_score: float = strawberry.field(description="Consistency score (0.0-1.0)")
```

## ObjectId Reference Patterns

### Primary Keys and References

1. **User Collection**: Uses `githubId` (string) as the primary business identifier
2. **Repository Collection**: Uses MongoDB `_id` (ObjectId) as primary key
3. **ContributionMetrics Collection**: References repositories via `repoId` (ObjectId)
4. **AIFeedback Collection**: References repositories via `repoId` (ObjectId)

### Reference Examples

```python
# Repository reference in ContributionMetrics
{
  "repoId": ObjectId("507f1f77bcf86cd799439013"),  # References Repository._id
  "studentGithubId": "67890"  # References User.githubId
}

# Multiple references in Repository
{
  "ownerGithubId": "12345",  # References mentor User.githubId
  "linkedStudents": ["67890", "11111"]  # References student User.githubId
}
```

### MongoDB Indexes

Based on the design document, these indexes should be created:

```javascript
// User collection indexes
db.users.createIndex({ "githubId": 1 }, { unique: true })
db.users.createIndex({ "role": 1 })
db.users.createIndex({ "enrolledBy": 1 })

// Repository collection indexes
db.repositories.createIndex({ "ownerGithubId": 1 })
db.repositories.createIndex({ "repoUrl": 1 }, { unique: true })
db.repositories.createIndex({ "linkedStudents": 1 })

// ContributionMetrics collection indexes
db.contribution_metrics.createIndex({ "repoId": 1, "studentGithubId": 1 }, { unique: true })
db.contribution_metrics.createIndex({ "studentGithubId": 1 })
db.contribution_metrics.createIndex({ "repoId": 1 })

// AIFeedback collection indexes
db.ai_feedback.createIndex({ "repoId": 1, "studentGithubId": 1 })
db.ai_feedback.createIndex({ "studentGithubId": 1 })
db.ai_feedback.createIndex({ "generatedAt": 1 })
```

## Validation Examples

### Pydantic Model Validation

```python
from backend.models import User, Repository, ContributionMetrics, Role

# Valid mentor user
mentor = User(
    githubId="12345",
    username="mentor_user",
    email="mentor@example.com",
    role=Role.MENTOR,
    isEnrolled=True,
    enrolledBy=None
)

# Valid student user
student = User(
    githubId="67890",
    username="student_user",
    email="student@example.com",
    role=Role.STUDENT,
    isEnrolled=True,
    enrolledBy="12345"  # Mentor's GitHub ID
)

# Valid repository
repo = Repository(
    repoName="Sample Project",
    repoUrl="https://github.com/mentor/sample-project",
    ownerGithubId="12345",
    linkedStudents=["67890"]
)

# Valid contribution metrics
metrics = ContributionMetrics(
    repoId=repo.id,
    studentGithubId="67890",
    commitCount=25,
    prCount=5,
    issueCount=3,
    consistencyScore=0.85
)
```

### GraphQL Query Examples

```graphql
# Get user profile
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

# Get repositories with linked students
query GetRepositories {
  getRepositories {
    id
    repoName
    repoUrl
    ownerGithubId
    linkedStudents
    createdAt
  }
}

# Get contribution metrics
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

### Mutation Examples

```graphql
# Enroll a student (mentor only)
mutation EnrollStudent($githubUsername: String!, $email: String!) {
  enrollStudent(githubUsername: $githubUsername, email: $email) {
    id
    githubId
    username
    email
    role
    isEnrolled
    enrolledBy
  }
}

# Create a repository (mentor only)
mutation CreateRepository($repoName: String!, $repoUrl: String!) {
  createRepository(repoName: $repoName, repoUrl: $repoUrl) {
    id
    repoName
    repoUrl
    ownerGithubId
    linkedStudents
    createdAt
  }
}

# Save contribution metrics (student only)
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

## Requirements Validation

This data model implementation validates the following requirements:

- **8.1**: User collection with githubId, username, email, role, isEnrolled, enrolledBy, and createdAt fields
- **8.2**: Repository collection with repoName, repoUrl, ownerGithubId, linkedStudents, and createdAt fields
- **8.3**: ContributionMetrics collection with repoId, studentGithubId, metrics, and lastUpdated fields
- **8.4**: Proper MongoDB ObjectId types for document references
- **2.1**: Role enum for MENTOR/STUDENT values
- **6.1-6.4**: GraphQL types for User, Repository, ContributionMetrics with proper field definitions

## Testing with Postman

Use the provided `postman_data_models_examples.json` collection to test:

1. **Model Validation**: Send sample data to validation endpoints
2. **GraphQL Types**: Query the GraphQL schema for type definitions
3. **ObjectId References**: Test relationships between documents
4. **Field Validation**: Verify required fields and data types
5. **Enum Values**: Test Role enum validation

The Postman collection includes comprehensive examples for all data models with proper validation scenarios and expected responses.