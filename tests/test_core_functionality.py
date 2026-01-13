"""
Core functionality tests for the Student Progress Backend.
Tests the essential components that have been implemented.
"""

import pytest
import asyncio
from backend.config import get_settings, validate_configuration
from backend.database import Database, DatabaseManager
from backend.auth.jwt_handler import JWTHandler, JWTError
from backend.auth.github_oauth import GitHubOAuth
from backend.models import Role


class TestCoreFunctionality:
    """Test core functionality that has been implemented."""
    
    def test_configuration_loading(self):
        """Test that configuration loads successfully."""
        settings = get_settings()
        assert settings is not None
        assert settings.mongodb_connection_string
        assert settings.github_client_id
        assert settings.jwt_secret_key
        
        # Test configuration validation
        validate_configuration()  # Should not raise exception
    
    def test_jwt_token_lifecycle(self):
        """Test JWT token creation and validation."""
        jwt_handler = JWTHandler()
        
        # Test token creation
        user_data = {
            "github_id": "12345",
            "username": "testuser",
            "email": "test@example.com",
            "role": Role.STUDENT.value
        }
        
        token = jwt_handler.create_token(user_data)
        assert token is not None
        assert isinstance(token, str)
        
        # Test token verification
        payload = jwt_handler.verify_token(token)
        assert payload["github_id"] == "12345"
        assert payload["username"] == "testuser"
        assert payload["role"] == Role.STUDENT.value
        
        # Test user extraction
        extracted_user = jwt_handler.extract_user_from_token(token)
        assert extracted_user["github_id"] == "12345"
        assert extracted_user["username"] == "testuser"
        
        # Test header extraction
        auth_header = f"Bearer {token}"
        extracted_token = jwt_handler.extract_token_from_header(auth_header)
        assert extracted_token == token
    
    def test_jwt_error_handling(self):
        """Test JWT error handling."""
        jwt_handler = JWTHandler()
        
        # Test invalid token
        with pytest.raises(JWTError):
            jwt_handler.verify_token("invalid.token.here")
        
        # Test missing required field
        with pytest.raises(JWTError, match="Required field"):
            jwt_handler.create_token({"username": "test"})  # Missing github_id
    
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
    
    @pytest.mark.asyncio
    async def test_database_connection(self):
        """Test database connection and basic operations."""
        try:
            async with DatabaseManager() as db:
                # Test connection
                assert db is not None
                
                # Test health check
                health = await db.health_check()
                assert health["status"] == "healthy"
                assert health["connected"] is True
                
                # Test collection accessors
                assert db.users is not None
                assert db.repositories is not None
                assert db.contribution_metrics is not None
                assert db.ai_feedback is not None
                
        except Exception as e:
            pytest.fail(f"Database connection test failed: {str(e)}")
    
    @pytest.mark.asyncio
    async def test_database_basic_operations(self):
        """Test basic database CRUD operations."""
        try:
            async with DatabaseManager() as db:
                # Test user insertion and retrieval
                test_user = {
                    "githubId": "test_12345",
                    "username": "testuser",
                    "email": "test@example.com",
                    "role": Role.STUDENT.value,
                    "isEnrolled": True,
                    "createdAt": "2024-01-01T00:00:00Z"
                }
                
                # Insert user
                result = await db.users.insert_one(test_user)
                assert result.inserted_id is not None
                
                # Retrieve user
                retrieved_user = await db.users.find_one({"githubId": "test_12345"})
                assert retrieved_user is not None
                assert retrieved_user["username"] == "testuser"
                
                # Clean up
                await db.users.delete_one({"_id": result.inserted_id})
                
        except Exception as e:
            pytest.fail(f"Database operations test failed: {str(e)}")
    
    def test_models_validation(self):
        """Test that data models work correctly."""
        from backend.models import User, Repository, ContributionMetrics, AIFeedback
        from datetime import datetime
        from bson import ObjectId
        
        # Test User model
        user = User(
            github_id="12345",
            username="testuser",
            email="test@example.com",
            role=Role.STUDENT,
            is_enrolled=True
        )
        assert user.github_id == "12345"
        assert user.role == Role.STUDENT
        
        # Test Repository model
        repo = Repository(
            repo_name="test-repo",
            repo_url="https://github.com/user/test-repo",
            owner_github_id="mentor123"
        )
        assert repo.repo_name == "test-repo"
        assert repo.linked_students == []
        
        # Test ContributionMetrics model
        metrics = ContributionMetrics(
            repo_id=ObjectId(),
            student_github_id="student123",
            commit_count=25,
            pr_count=5,
            consistency_score=0.85
        )
        assert metrics.commit_count == 25
        assert metrics.consistency_score == 0.85
    
    def test_role_enum(self):
        """Test Role enum functionality."""
        assert Role.MENTOR.value == "MENTOR"
        assert Role.STUDENT.value == "STUDENT"
        
        # Test enum comparison
        assert Role.MENTOR != Role.STUDENT
        assert Role.MENTOR == Role.MENTOR


if __name__ == "__main__":
    pytest.main([__file__, "-v"])