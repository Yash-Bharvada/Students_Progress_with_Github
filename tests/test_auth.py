"""
Tests for authentication components (JWT and GitHub OAuth).
"""

import pytest
from unittest.mock import AsyncMock, patch
from backend.auth.jwt_handler import JWTHandler, JWTError
from backend.auth.github_oauth import GitHubOAuth, GitHubUser, GitHubOAuthError
from backend.models import Role


class TestJWTHandler:
    """Test JWT token creation and validation."""
    
    def setup_method(self):
        """Set up test JWT handler."""
        self.jwt_handler = JWTHandler()
    
    def test_create_token_success(self):
        """Test successful JWT token creation."""
        user_data = {
            "github_id": "12345",
            "username": "testuser",
            "email": "test@example.com",
            "role": Role.STUDENT.value
        }
        
        token = self.jwt_handler.create_token(user_data)
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_create_token_missing_required_field(self):
        """Test token creation with missing required field."""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "role": Role.STUDENT.value
            # Missing github_id
        }
        
        with pytest.raises(JWTError, match="Required field 'github_id'"):
            self.jwt_handler.create_token(user_data)
    
    def test_verify_token_success(self):
        """Test successful token verification."""
        user_data = {
            "github_id": "12345",
            "username": "testuser",
            "email": "test@example.com",
            "role": Role.STUDENT.value
        }
        
        token = self.jwt_handler.create_token(user_data)
        payload = self.jwt_handler.verify_token(token)
        
        assert payload["github_id"] == "12345"
        assert payload["username"] == "testuser"
        assert payload["role"] == Role.STUDENT.value
    
    def test_verify_invalid_token(self):
        """Test verification of invalid token."""
        with pytest.raises(JWTError, match="Invalid token"):
            self.jwt_handler.verify_token("invalid.token.here")
    
    def test_extract_token_from_header(self):
        """Test token extraction from Authorization header."""
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
    
    def test_extract_user_from_token(self):
        """Test user extraction from token."""
        user_data = {
            "github_id": "12345",
            "username": "testuser",
            "email": "test@example.com",
            "role": Role.MENTOR.value
        }
        
        token = self.jwt_handler.create_token(user_data)
        extracted_user = self.jwt_handler.extract_user_from_token(token)
        
        assert extracted_user["github_id"] == "12345"
        assert extracted_user["username"] == "testuser"
        assert extracted_user["role"] == Role.MENTOR.value


class TestGitHubOAuth:
    """Test GitHub OAuth functionality."""
    
    def setup_method(self):
        """Set up test GitHub OAuth handler."""
        self.github_oauth = GitHubOAuth()
    
    def test_get_authorization_url(self):
        """Test authorization URL generation."""
        url = self.github_oauth.get_authorization_url()
        
        assert url.startswith("https://github.com/login/oauth/authorize")
        assert "client_id=" in url
        assert "scope=user%3Aemail+repo" in url
        assert "response_type=code" in url
    
    def test_get_authorization_url_with_state(self):
        """Test authorization URL generation with state parameter."""
        state = "test_state_123"
        url = self.github_oauth.get_authorization_url(state=state)
        
        assert f"state={state}" in url
    
    @pytest.mark.asyncio
    async def test_exchange_code_for_token_missing_code(self):
        """Test token exchange with missing code."""
        with pytest.raises(GitHubOAuthError, match="Authorization code is required"):
            await self.github_oauth.exchange_code_for_token("")
    
    @pytest.mark.asyncio
    @patch('httpx.AsyncClient.post')
    async def test_exchange_code_for_token_success(self, mock_post):
        """Test successful token exchange."""
        # Mock successful response
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"access_token": "test_token_123"}
        mock_post.return_value = mock_response
        
        token = await self.github_oauth.exchange_code_for_token("test_code")
        assert token == "test_token_123"
    
    @pytest.mark.asyncio
    @patch('httpx.AsyncClient.get')
    async def test_get_user_profile_success(self, mock_get):
        """Test successful user profile fetch."""
        # Mock user profile response
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": 12345,
            "login": "testuser",
            "email": "test@example.com",
            "name": "Test User",
            "avatar_url": "https://github.com/avatar.jpg"
        }
        mock_get.return_value = mock_response
        
        user = await self.github_oauth.get_user_profile("test_token")
        
        assert isinstance(user, GitHubUser)
        assert user.id == 12345
        assert user.login == "testuser"
        assert user.email == "test@example.com"
    
    @pytest.mark.asyncio
    async def test_get_user_profile_missing_token(self):
        """Test user profile fetch with missing token."""
        with pytest.raises(GitHubOAuthError, match="Access token is required"):
            await self.github_oauth.get_user_profile("")