# Student Progress & Performance Tracking Backend

A comprehensive, production-ready FastAPI backend system for tracking student project progress and performance. Built with modern Python technologies including Strawberry GraphQL, GitHub OAuth authentication, MongoDB Atlas persistence, strict role-based access control, and AI-powered code quality feedback using Google Gemini Flash API.

## 🚀 Features

### Core Functionality
- **GitHub OAuth Authentication** - Secure authentication using GitHub accounts
- **Role-Based Access Control** - Strict MENTOR/STUDENT role separation
- **GraphQL API** - Modern API with Strawberry GraphQL framework
- **MongoDB Atlas Integration** - Cloud-native database with async Motor driver
- **AI-Powered Feedback** - Code quality analysis using Google Gemini Flash API
- **Production-Ready** - Comprehensive error handling, logging, and security measures

### Key Capabilities
- **Student Enrollment Management** - Only mentors can enroll students
- **Repository Tracking** - Monitor student contributions across projects
- **Contribution Metrics** - Track commits, PRs, issues, and consistency scores
- **AI Code Analysis** - Automated feedback on code quality and best practices
- **Comprehensive Testing** - Unit tests, integration tests, and property-based testing
- **API Documentation** - Auto-generated OpenAPI/Swagger documentation

## 🏗️ Architecture

### System Overview
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend API    │    │   External      │
│   Application   │◄──►│   (FastAPI +     │◄──►│   Services      │
│                 │    │   GraphQL)       │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │                         │
                              ▼                         ▼
                    ┌──────────────────┐    ┌─────────────────┐
                    │   MongoDB Atlas  │    │ • GitHub OAuth  │
                    │   Database       │    │ • GitHub API    │
                    │                  │    │ • Gemini Flash  │
                    └──────────────────┘    └─────────────────┘
```

### Project Structure
```
backend/
├── __init__.py
├── main.py                    # FastAPI application entry point with lifespan management
├── config.py                  # Environment configuration with validation
├── database.py                # MongoDB connection with Motor async driver
├── models.py                  # Pydantic data models with validation
├── exceptions.py              # Custom exception classes and error handling
├── auth/                      # Authentication module
│   ├── __init__.py
│   ├── github_oauth.py        # GitHub OAuth Authorization Code Flow
│   ├── jwt_handler.py         # JWT token creation and validation
│   └── routes.py              # Authentication REST endpoints
├── graphql/                   # GraphQL module
│   ├── __init__.py
│   ├── schema.py              # GraphQL schema and type definitions
│   ├── queries.py             # GraphQL query resolvers
│   ├── mutations.py           # GraphQL mutation resolvers
│   ├── permissions.py         # Role-based permission classes
│   └── context.py             # GraphQL context management
├── services/                  # Business logic services
│   ├── __init__.py
│   ├── auth_service.py        # Authentication business logic
│   ├── user_service.py        # User management operations
│   └── repository_service.py # Repository management operations
└── ai/                        # AI feedback module
    ├── __init__.py
    ├── feedback_engine.py     # AI feedback generation engine
    ├── gemini_client.py       # Google Gemini Flash API client
    └── prompts.py             # AI prompt templates and engineering

tests/                         # Comprehensive test suite
├── __init__.py
├── conftest.py               # Pytest configuration and fixtures
├── test_auth.py              # Authentication component tests
├── test_core_functionality.py # Core system functionality tests
├── test_database.py          # Database operations tests
├── test_graphql.py           # GraphQL schema and resolver tests
├── test_integration.py       # End-to-end integration tests
└── test_production_readiness.py # Production deployment verification

.kiro/specs/student-progress-backend/  # Specification documents
├── requirements.md           # Detailed system requirements (EARS format)
├── design.md                # System design and architecture
└── tasks.md                 # Implementation task breakdown
```

## 🛠️ Technology Stack

### Backend Framework
- **FastAPI** - Modern, fast web framework for building APIs
- **Strawberry GraphQL** - Python GraphQL library with type annotations
- **Pydantic** - Data validation using Python type annotations
- **Motor** - Async MongoDB driver for Python

### Authentication & Security
- **GitHub OAuth** - OAuth 2.0 Authorization Code Flow
- **JWT (JSON Web Tokens)** - Stateless authentication tokens
- **CORS** - Cross-Origin Resource Sharing configuration
- **Input Validation** - Comprehensive request validation

### Database & Storage
- **MongoDB Atlas** - Cloud-native MongoDB database
- **Async Operations** - Non-blocking database operations
- **Indexing Strategy** - Optimized database indexes for performance

### AI & External Services
- **Google Gemini Flash API** - Fast AI model for code analysis
- **GitHub API** - Repository data fetching and analysis
- **Rate Limiting** - Graceful handling of API rate limits

### Development & Testing
- **Pytest** - Comprehensive testing framework
- **Property-Based Testing** - Automated test case generation
- **Integration Testing** - End-to-end system testing
- **Postman Collections** - API testing and documentation

## 📋 Prerequisites

### System Requirements
- **Python 3.10+** - Modern Python version with async support
- **MongoDB Atlas Account** - Cloud database service
- **GitHub OAuth Application** - For authentication
- **Google Cloud Account** - For Gemini Flash API access

### Development Tools
- **Git** - Version control
- **Postman** - API testing (optional but recommended)
- **VS Code/PyCharm** - IDE with Python support

## 🚀 Quick Start

### 1. Clone and Setup
```bash
# Clone the repository
git clone <repository-url>
cd student-progress-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your configuration
nano .env  # or use your preferred editor
```

### 3. Configure Environment Variables
Edit `.env` file with the following required variables:

```env
# Database Configuration
MONGODB_CONNECTION_STRING=mongodb+srv://username:password@cluster.mongodb.net/student_progress

# GitHub OAuth Configuration
GITHUB_CLIENT_ID=your_github_oauth_client_id
GITHUB_CLIENT_SECRET=your_github_oauth_client_secret
GITHUB_REDIRECT_URI=http://localhost:8000/auth/github/callback
GITHUB_API_TOKEN=your_github_personal_access_token

# JWT Configuration
JWT_SECRET_KEY=your_jwt_secret_key_minimum_32_characters
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Google Gemini API Configuration
GEMINI_API_KEY=your_google_gemini_api_key
GEMINI_MODEL=gemini-1.5-flash
GEMINI_TEMPERATURE=0.3
GEMINI_MAX_OUTPUT_TOKENS=1024

# Application Configuration
ENVIRONMENT=development
DEBUG=true
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
LOG_LEVEL=INFO
```

### 4. Database Setup
```bash
# Verify database connection
python -c "from backend.config import validate_configuration; validate_configuration()"

# Test database connectivity
python -c "import asyncio; from backend.database import DatabaseManager; asyncio.run(DatabaseManager().__aenter__())"
```

### 5. Run the Application
```bash
# Development server with auto-reload
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Or use the built-in runner
python backend/main.py

# Production server
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 6. Verify Installation
```bash
# Check application health
curl http://localhost:8000/health

# Check authentication health
curl http://localhost:8000/auth/health

# Access API documentation
open http://localhost:8000/docs
```

## 🔐 Authentication Flow

### GitHub OAuth Setup

1. **Create GitHub OAuth App**:
   - Go to GitHub Settings → Developer settings → OAuth Apps
   - Create new OAuth App with:
     - Application name: "Student Progress Tracker"
     - Homepage URL: `http://localhost:8000`
     - Authorization callback URL: `http://localhost:8000/auth/github/callback`

2. **Authentication Process**:
   ```
   User → /auth/github/login → GitHub OAuth → /auth/github/callback → JWT Token
   ```

3. **Role Assignment**:
   - **New users**: Automatically assigned MENTOR role
   - **Students**: Must be enrolled by a mentor before they can login
   - **Access Control**: Strict role-based permissions on all operations

### JWT Token Management
- **Token Creation**: Includes user ID, role, and expiration
- **Token Validation**: Verified on every GraphQL request
- **Token Extraction**: From Authorization Bearer header
- **Security**: Signed with configurable secret key

## 📊 Data Models

### User Model
```python
class User(BaseModel):
    github_id: str              # GitHub user ID (unique)
    username: str               # GitHub username
    email: Optional[str]        # User email address
    role: Role                  # MENTOR or STUDENT
    is_enrolled: bool           # Enrollment status
    enrolled_by: Optional[str]  # Enrolling mentor's GitHub ID
    created_at: datetime        # Account creation timestamp
```

### Repository Model
```python
class Repository(BaseModel):
    repo_name: str              # Repository name
    repo_url: str               # GitHub repository URL (unique)
    owner_github_id: str        # Repository owner's GitHub ID
    linked_students: List[str]  # List of linked student GitHub IDs
    created_at: datetime        # Repository creation timestamp
```

### ContributionMetrics Model
```python
class ContributionMetrics(BaseModel):
    repo_id: ObjectId           # Repository reference
    student_github_id: str      # Student's GitHub ID
    commit_count: int           # Number of commits
    pr_count: int               # Number of pull requests
    issue_count: int            # Number of issues
    consistency_score: float    # Consistency score (0.0-1.0)
    last_updated: datetime      # Last update timestamp
```

### AIFeedback Model
```python
class AIFeedback(BaseModel):
    repo_id: ObjectId           # Repository reference
    student_github_id: str      # Student's GitHub ID
    quality_score: float        # Code quality score (0.0-10.0)
    strengths: List[str]        # List of identified strengths
    issues: List[str]           # List of identified issues
    suggestions: List[str]      # List of improvement suggestions
    generated_at: datetime      # Feedback generation timestamp
```

## 🔍 GraphQL API

### Schema Overview
The API provides a comprehensive GraphQL schema with queries and mutations for all system operations.

### Queries

#### Get Current User
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

#### Get Repositories
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

#### Get Contribution Metrics (Student)
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

#### Get All Contribution Metrics (Mentor)
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

### Mutations

#### Enroll Student (Mentor Only)
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

#### Create Repository (Mentor Only)
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

#### Save Contribution Metrics (Student Only)
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

### AI Feedback Operations

#### Generate AI Feedback
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

#### Get AI Feedback
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

## 🤖 AI-Powered Code Quality Feedback

### Google Gemini Flash Integration
The system uses Google's Gemini Flash API for fast, intelligent code quality analysis:

- **Repository Analysis**: Analyzes commit patterns, code structure, and development practices
- **Quality Scoring**: Provides numerical quality scores (0.0-10.0)
- **Structured Feedback**: Identifies strengths, issues, and actionable suggestions
- **Educational Focus**: Feedback designed to help students learn and improve

### Feedback Categories
1. **Strengths**: Positive aspects of the code and development practices
2. **Issues**: Areas that need improvement or potential problems
3. **Suggestions**: Specific, actionable recommendations for improvement

### Analysis Metrics
- **Commit Frequency**: Consistency of contributions over time
- **Commit Size**: Average size and scope of commits
- **Code Quality Indicators**: Presence of tests, documentation, and best practices
- **Development Patterns**: Analysis of commit messages and code organization

## 🛡️ Security & Access Control

### Role-Based Access Control (RBAC)

#### Mentor Capabilities
- ✅ Enroll new students
- ✅ Create and manage repositories
- ✅ View all student metrics for their repositories
- ✅ Generate AI feedback for any repository
- ✅ Access comprehensive analytics and reports

#### Student Capabilities
- ✅ View their own profile and enrollment status
- ✅ Access repositories they're linked to
- ✅ Submit their own contribution metrics
- ✅ Generate AI feedback for their repositories
- ✅ View their own AI feedback and progress
- ❌ Cannot enroll other students
- ❌ Cannot create repositories
- ❌ Cannot access other students' private data

### Security Measures
- **JWT Authentication**: Secure, stateless authentication
- **Input Validation**: Comprehensive request validation using Pydantic
- **SQL Injection Prevention**: MongoDB with parameterized queries
- **CORS Configuration**: Proper cross-origin resource sharing setup
- **Rate Limiting**: Protection against API abuse
- **Error Handling**: Secure error messages that don't leak sensitive information

## 🧪 Testing

### Test Suite Overview
The project includes a comprehensive testing strategy with multiple types of tests:

### Unit Tests
```bash
# Run authentication tests
python -m pytest tests/test_auth.py -v

# Run database tests
python -m pytest tests/test_database.py -v

# Run GraphQL tests
python -m pytest tests/test_graphql.py -v
```

### Integration Tests
```bash
# Run integration tests
python -m pytest tests/test_integration.py -v

# Run production readiness tests
python -m pytest tests/test_production_readiness.py -v
```

### All Tests
```bash
# Run complete test suite
python -m pytest tests/ -v --cov=backend

# Run tests with coverage report
python -m pytest tests/ --cov=backend --cov-report=html
```

### Property-Based Testing
The system includes property-based tests that automatically generate test cases to verify system correctness across a wide range of inputs.

### Postman Testing
Comprehensive Postman collections are provided for manual and automated API testing:

```bash
# Import collections
postman_final_collection.json       # Complete API test suite
postman_final_environment.json      # Environment variables
```

## 📚 API Documentation

### Interactive Documentation
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

### GraphQL Playground
- **GraphiQL**: Available in development mode at `/graphql`
- **Schema Introspection**: Full schema exploration capabilities
- **Query Testing**: Interactive query and mutation testing

## 🚀 Deployment

### Production Configuration
```env
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING
CORS_ORIGINS=https://yourdomain.com
```

### Docker Deployment (Optional)
```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY backend/ ./backend/
EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Health Checks
- **Application Health**: `GET /health`
- **Authentication Health**: `GET /auth/health`
- **Database Connectivity**: Included in health endpoints

### Performance Optimization
- **Database Indexes**: Optimized indexes for all query patterns
- **Async Operations**: Non-blocking I/O throughout the application
- **Connection Pooling**: Efficient database connection management
- **Caching Strategy**: Configurable caching for frequently accessed data

## 🔧 Configuration

### Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `MONGODB_CONNECTION_STRING` | Yes | - | MongoDB Atlas connection string |
| `GITHUB_CLIENT_ID` | Yes | - | GitHub OAuth application client ID |
| `GITHUB_CLIENT_SECRET` | Yes | - | GitHub OAuth application client secret |
| `GITHUB_REDIRECT_URI` | Yes | - | OAuth callback URL |
| `GITHUB_API_TOKEN` | Yes | - | GitHub personal access token |
| `JWT_SECRET_KEY` | Yes | - | JWT signing secret (min 32 chars) |
| `JWT_ALGORITHM` | No | HS256 | JWT signing algorithm |
| `JWT_EXPIRATION_HOURS` | No | 24 | JWT token expiration time |
| `GEMINI_API_KEY` | Yes | - | Google Gemini Flash API key |
| `GEMINI_MODEL` | No | gemini-1.5-flash | Gemini model to use |
| `GEMINI_TEMPERATURE` | No | 0.3 | AI response creativity (0.0-1.0) |
| `GEMINI_MAX_OUTPUT_TOKENS` | No | 1024 | Maximum AI response length |
| `ENVIRONMENT` | No | development | Application environment |
| `DEBUG` | No | true | Enable debug mode |
| `CORS_ORIGINS` | No | localhost:3000 | Allowed CORS origins |
| `LOG_LEVEL` | No | INFO | Logging level |

## 🐛 Troubleshooting

### Common Issues

#### Database Connection Issues
```bash
# Test MongoDB connection
python -c "from backend.config import get_settings; print(get_settings().mongodb_connection_string)"

# Verify network connectivity
ping cluster0.mongodb.net
```

#### Authentication Problems
```bash
# Verify GitHub OAuth configuration
curl -X GET "https://api.github.com/user" -H "Authorization: token YOUR_GITHUB_TOKEN"

# Test JWT token generation
python -c "from backend.auth.jwt_handler import JWTHandler; print(JWTHandler().create_token({'github_id': 'test'}))"
```

#### AI Feedback Issues
```bash
# Test Gemini API connectivity
python -c "from backend.ai.gemini_client import GeminiClient; client = GeminiClient(); print('Gemini client initialized')"
```

### Debug Mode
Enable detailed logging and error information:
```env
DEBUG=true
LOG_LEVEL=DEBUG
```

### Health Check Endpoints
Monitor system health:
```bash
# Application health
curl http://localhost:8000/health

# Authentication service health
curl http://localhost:8000/auth/health
```

## 📈 Performance & Monitoring

### Database Performance
- **Indexes**: Optimized for all query patterns
- **Connection Pooling**: Efficient connection management
- **Async Operations**: Non-blocking database operations

### API Performance
- **Response Times**: Optimized GraphQL resolvers
- **Rate Limiting**: Protection against abuse
- **Caching**: Strategic caching of frequently accessed data

### Monitoring Recommendations
- **Application Logs**: Structured logging with correlation IDs
- **Health Endpoints**: Regular health check monitoring
- **Database Metrics**: MongoDB Atlas monitoring
- **API Metrics**: Request/response time tracking

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

### Code Standards
- **Type Hints**: All functions must include type annotations
- **Documentation**: Comprehensive docstrings for all modules
- **Testing**: Minimum 80% test coverage for new code
- **Linting**: Code must pass flake8 and black formatting

### Testing Requirements
- Unit tests for all new functions
- Integration tests for new endpoints
- Property-based tests for complex logic
- Postman collection updates for API changes

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **FastAPI** - Modern Python web framework
- **Strawberry GraphQL** - Excellent GraphQL library
- **MongoDB Atlas** - Reliable cloud database
- **Google Gemini** - Powerful AI capabilities
- **GitHub** - Authentication and repository hosting

## 📞 Support

For support and questions:
- Create an issue in the GitHub repository
- Check the troubleshooting section above
- Review the comprehensive testing guide: `FINAL_TESTING_GUIDE.md`

---

**Built with ❤️ using modern Python technologies for educational excellence.**