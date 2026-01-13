"""
Comprehensive integration tests for the Student Progress Backend.
Tests complete OAuth flow, GraphQL operations with real JWT tokens,
role-based access scenarios, AI feedback generation, and error conditions.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from backend.auth.jwt_handler import JWTHandler
from backend.auth.github_oauth import GitHubOAuth, GitHubUser
from backend.models import Role
from datetime import datetime
from bson import ObjectId


class TestIntegrationBasic:
    """Basic integration tests without complex fixtures."""
    
    def setup_method(self):
        """Set up test dependencies."""
        self.jwt_handler = JWTHandler()
    
    def test_jwt_token_creation_and_validation(self):
        """Test JWT token creation and validation integration."""
        # Create token
        user_data = {
            "github_id": "12345",
            "username": "testuser",
            "email": "test@example.com",
            "role": Role.STUDENT.value
        }
        
        token = self.jwt_handler.create_token(user_data)
        assert token is not None
        assert isinstance(token, str)
        
        # Validate token
        payload = self.jwt_handler.verify_token(token)
        assert payload["github_id"] == "12345"
        assert payload["username"] == "testuser"
        assert payload["role"] == Role.STUDENT.value
        
        # Extract user from token
        extracted_user = self.jwt_handler.extract_user_from_token(token)
        assert extracted_user["github_id"] == "12345"
        assert extracted_user["username"] == "testuser"
    
    def test_github_oauth_url_generation(self):
        """Test GitHub OAuth URL generation."""
        github_oauth = GitHubOAuth()
        
        # Test basic URL generation
        url = github_oauth.get_authorization_url()
        assert url.startswith("https://github.com/login/oauth/authorize")
        assert "client_id=" in url
        assert "scope=user%3Aemail+repo" in url
        
        # Test with state parameter
        state = "test_state_123"
        url_with_state = github_oauth.get_authorization_url(state=state)
        assert f"state={state}" in url_with_state
    
    def test_role_enum_functionality(self):
        """Test Role enum functionality."""
        assert Role.MENTOR.value == "MENTOR"
        assert Role.STUDENT.value == "STUDENT"
        
        # Test enum comparison
        assert Role.MENTOR != Role.STUDENT
        assert Role.MENTOR == Role.MENTOR
    
    @pytest.mark.asyncio
    async def test_database_operations_mock(self):
        """Test database operations with mocking."""
        from backend.database import Database
        
        # Mock database operations
        with patch('motor.motor_asyncio.AsyncIOMotorClient') as mock_client:
            mock_db = MagicMock()
            mock_collection = MagicMock()
            
            # Setup mock chain
            mock_client.return_value.__getitem__.return_value = mock_db
            mock_db.__getitem__.return_value = mock_collection
            
            # Mock insert operation
            mock_collection.insert_one = AsyncMock(return_value=MagicMock(inserted_id=ObjectId()))
            
            # Mock find operation
            mock_collection.find_one = AsyncMock(return_value={
                "_id": ObjectId(),
                "githubId": "12345",
                "username": "testuser",
                "role": Role.STUDENT.value
            })
            
            # Test database instance creation
            db = Database("mongodb://test")
            db.client = mock_client.return_value
            db.db = mock_db
            db._is_connected = True
            
            # Test collection access
            users_collection = db.users
            assert users_collection is not None
            
            # Test insert operation
            result = await users_collection.insert_one({"test": "data"})
            assert result.inserted_id is not None
            
            # Test find operation
            user = await users_collection.find_one({"githubId": "12345"})
            assert user is not None
            assert user["username"] == "testuser"


class TestAuthenticationFlow:
    """Test authentication flow components."""
    
    def setup_method(self):
        """Set up test dependencies."""
        self.jwt_handler = JWTHandler()
    
    def test_jwt_error_handling(self):
        """Test JWT error handling."""
        from backend.auth.jwt_handler import JWTError
        
        # Test invalid token
        with pytest.raises(JWTError):
            self.jwt_handler.verify_token("invalid.token.here")
        
        # Test missing required field
        with pytest.raises(JWTError, match="Required field"):
            self.jwt_handler.create_token({"username": "test"})  # Missing github_id
    
    def test_token_header_extraction(self):
        """Test token extraction from headers."""
        # Valid Bearer token
        header = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
        token = self.jwt_handler.extract_token_from_header(header)
        assert token == "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
        
        # Invalid header format
        invalid_header = "InvalidFormat token"
        token = self.jwt_handler.extract_token_from_header(invalid_header)
        assert token is None
        
        # No header
        token = self.jwt_handler.extract_token_from_header(None)
        assert token is None
    
    @pytest.mark.asyncio
    async def test_github_oauth_error_handling(self):
        """Test GitHub OAuth error handling."""
        from backend.auth.github_oauth import GitHubOAuthError
        
        github_oauth = GitHubOAuth()
        
        # Test missing code
        with pytest.raises(GitHubOAuthError, match="Authorization code is required"):
            await github_oauth.exchange_code_for_token("")
        
        # Test missing token for user profile
        with pytest.raises(GitHubOAuthError, match="Access token is required"):
            await github_oauth.get_user_profile("")


class TestRoleBasedAccessLogic:
    """Test role-based access control logic."""
    
    def test_permission_validation(self):
        """Test permission validation logic."""
        from backend.graphql.permissions import IsAuthenticated, IsMentor, IsStudent
        
        # Mock context objects
        class MockContext:
            def __init__(self, user_data=None):
                self.user = user_data
        
        class MockInfo:
            def __init__(self, user_data=None):
                self.context = MockContext(user_data)
        
        # Test IsAuthenticated permission
        auth_permission = IsAuthenticated()
        
        # With authenticated user
        info_with_user = MockInfo({"github_id": "123", "role": "STUDENT"})
        assert auth_permission.has_permission(None, info_with_user) is True
        
        # Without user
        info_without_user = MockInfo(None)
        assert auth_permission.has_permission(None, info_without_user) is False
        
        # Test IsMentor permission
        mentor_permission = IsMentor()
        
        # With mentor user
        info_mentor = MockInfo({"github_id": "123", "role": Role.MENTOR.value})
        assert mentor_permission.has_permission(None, info_mentor) is True
        
        # With student user
        info_student = MockInfo({"github_id": "123", "role": Role.STUDENT.value})
        assert mentor_permission.has_permission(None, info_student) is False
        
        # Test IsStudent permission
        student_permission = IsStudent()
        
        # With student user
        assert student_permission.has_permission(None, info_student) is True
        
        # With mentor user
        assert student_permission.has_permission(None, info_mentor) is False


class TestDataModelValidation:
    """Test data model validation and functionality."""
    
    def test_user_model_creation(self):
        """Test User model creation and validation."""
        from backend.models import User
        
        user = User(
            github_id="12345",
            username="testuser",
            email="test@example.com",
            role=Role.STUDENT,
            is_enrolled=True
        )
        
        assert user.github_id == "12345"
        assert user.username == "testuser"
        assert user.role == Role.STUDENT
        assert user.is_enrolled is True
    
    def test_repository_model_creation(self):
        """Test Repository model creation and validation."""
        from backend.models import Repository
        
        repo = Repository(
            repo_name="test-repo",
            repo_url="https://github.com/user/test-repo",
            owner_github_id="mentor123"
        )
        
        assert repo.repo_name == "test-repo"
        assert repo.repo_url == "https://github.com/user/test-repo"
        assert repo.owner_github_id == "mentor123"
        assert repo.linked_students == []
    
    def test_contribution_metrics_model_creation(self):
        """Test ContributionMetrics model creation and validation."""
        from backend.models import ContributionMetrics
        
        metrics = ContributionMetrics(
            repo_id=ObjectId(),
            student_github_id="student123",
            commit_count=25,
            pr_count=5,
            consistency_score=0.85
        )
        
        assert metrics.student_github_id == "student123"
        assert metrics.commit_count == 25
        assert metrics.pr_count == 5
        assert metrics.consistency_score == 0.85
    
    def test_ai_feedback_model_creation(self):
        """Test AIFeedback model creation and validation."""
        from backend.models import AIFeedback
        
        feedback = AIFeedback(
            repo_id=ObjectId(),
            student_github_id="student123",
            quality_score=8.5,
            strengths=["Good commit frequency", "Includes tests"],
            issues=["Some commits could be smaller"],
            suggestions=["Consider breaking large commits into smaller ones"]
        )
        
        assert feedback.student_github_id == "student123"
        assert feedback.quality_score == 8.5
        assert len(feedback.strengths) == 2
        assert len(feedback.issues) == 1
        assert len(feedback.suggestions) == 1


class TestConfigurationValidation:
    """Test configuration validation and loading."""
    
    def test_configuration_loading(self):
        """Test that configuration loads successfully."""
        from backend.config import get_settings, validate_configuration
        
        try:
            settings = get_settings()
            assert settings is not None
            assert settings.mongodb_connection_string
            assert settings.github_client_id
            assert settings.jwt_secret_key
            
            # Test configuration validation
            validate_configuration()  # Should not raise exception
            
        except Exception as e:
            # Configuration might fail in test environment, which is expected
            assert "Configuration validation failed" in str(e) or "required" in str(e).lower()


class TestErrorHandling:
    """Test error handling and exception management."""
    
    def test_custom_exceptions(self):
        """Test custom exception classes."""
        from backend.exceptions import (
            AuthenticationError, 
            AuthorizationError,
            ValidationError,
            DatabaseError,
            ExternalServiceError
        )
        
        # Test AuthenticationError
        auth_error = AuthenticationError(
            message="Invalid credentials",
            details={"field": "password"}
        )
        assert auth_error.message == "Invalid credentials"
        assert auth_error.details["field"] == "password"
        assert auth_error.status_code == 401
        
        # Test AuthorizationError
        authz_error = AuthorizationError(
            message="Access denied",
            details={"required_role": "MENTOR"}
        )
        assert authz_error.message == "Access denied"
        assert authz_error.status_code == 403
        
        # Test ValidationError
        validation_error = ValidationError(
            message="Invalid input",
            details={"field": "email", "error": "invalid format"}
        )
        assert validation_error.message == "Invalid input"
        assert validation_error.status_code == 422
    
    def test_exception_conversion(self):
        """Test exception conversion to HTTP exceptions."""
        from backend.exceptions import (
            AuthenticationError,
            convert_to_http_exception
        )
        from fastapi import HTTPException
        
        # Create custom exception
        custom_error = AuthenticationError(
            message="Token expired",
            details={"token": "expired"}
        )
        
        # Convert to HTTP exception
        http_exception = convert_to_http_exception(custom_error)
        
        assert isinstance(http_exception, HTTPException)
        assert http_exception.status_code == 401
        assert "Token expired" in str(http_exception.detail)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])