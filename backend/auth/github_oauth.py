"""
GitHub OAuth handler implementing Authorization Code Flow.
Handles authorization URL generation, code exchange, and user profile fetching with comprehensive error handling.
"""

import httpx
from typing import Dict, Any, Optional, List
from urllib.parse import urlencode
from pydantic import BaseModel
from backend.config import get_settings
from backend.exceptions import (
    ExternalServiceError,
    ValidationError,
    log_error,
    handle_external_service_error
)
import logging

logger = logging.getLogger(__name__)


class GitHubUser(BaseModel):
    """GitHub user profile data model."""
    id: int
    login: str
    email: Optional[str]
    name: Optional[str]
    avatar_url: Optional[str]


class GitHubOAuthError(ExternalServiceError):
    """Custom exception for GitHub OAuth errors."""
    
    def __init__(self, message: str = "GitHub OAuth failed", **kwargs):
        super().__init__(message, error_code="GITHUB_OAUTH_ERROR", **kwargs)


class GitHubOAuth:
    """GitHub OAuth handler for Authorization Code Flow."""
    
    def __init__(self):
        self.settings = get_settings()
        self.client_id = self.settings.github_client_id
        self.client_secret = self.settings.github_client_secret
        self.redirect_uri = self.settings.github_redirect_uri
        
        # GitHub OAuth endpoints
        self.auth_url = "https://github.com/login/oauth/authorize"
        self.token_url = "https://github.com/login/oauth/access_token"
        self.user_api_url = "https://api.github.com/user"
    
    def get_authorization_url(self, state: Optional[str] = None) -> str:
        """
        Generate GitHub OAuth authorization URL for /auth/github/login.
        
        Args:
            state: Optional state parameter for CSRF protection
            
        Returns:
            Complete authorization URL for GitHub OAuth
        """
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": "user:email repo",  # Request access to user profile, email, and repositories
            "response_type": "code"
        }
        
        if state:
            params["state"] = state
        
        return f"{self.auth_url}?{urlencode(params)}"
    
    async def exchange_code_for_token(self, code: str, state: Optional[str] = None) -> str:
        """
        Exchange authorization code for access token at /auth/github/callback with comprehensive error handling.
        
        Args:
            code: Authorization code from GitHub callback
            state: Optional state parameter for validation
            
        Returns:
            GitHub access token
            
        Raises:
            GitHubOAuthError: If token exchange fails
        """
        if not code:
            raise ValidationError(
                message="Authorization code is required",
                details={"parameter": "code"}
            )
        
        token_data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "redirect_uri": self.redirect_uri
        }
        
        headers = {
            "Accept": "application/json",
            "User-Agent": "StudentProgressTracker/1.0"
        }
        
        try:
            logger.debug("Exchanging authorization code for access token")
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.token_url,
                    data=token_data,
                    headers=headers,
                    timeout=30.0
                )
                
                if response.status_code != 200:
                    error_msg = f"Token exchange failed with status {response.status_code}: {response.text}"
                    logger.error(error_msg)
                    raise GitHubOAuthError(
                        message="GitHub token exchange failed",
                        details={
                            "status_code": response.status_code,
                            "response": response.text[:500]  # Limit response size
                        }
                    )
                
                token_response = response.json()
                
                if "error" in token_response:
                    error_description = token_response.get('error_description', token_response['error'])
                    logger.error(f"GitHub OAuth error: {error_description}")
                    raise GitHubOAuthError(
                        message=f"GitHub OAuth error: {error_description}",
                        details=token_response
                    )
                
                access_token = token_response.get("access_token")
                if not access_token:
                    logger.error("No access token received from GitHub")
                    raise GitHubOAuthError(
                        message="No access token received from GitHub",
                        details={"response": token_response}
                    )
                
                logger.info("Successfully exchanged authorization code for access token")
                return access_token
                
        except httpx.RequestError as e:
            error = handle_external_service_error(e, "GitHub OAuth")
            log_error(error, {"operation": "token_exchange"})
            raise GitHubOAuthError(
                message="Network error during token exchange",
                details={"original_error": str(e)}
            )
        except GitHubOAuthError:
            raise
        except Exception as e:
            error = handle_external_service_error(e, "GitHub OAuth")
            log_error(error, {"operation": "token_exchange"})
            raise GitHubOAuthError(
                message="Unexpected error during token exchange",
                details={"original_error": str(e)}
            )
    
    async def get_user_profile(self, access_token: str) -> GitHubUser:
        """
        Fetch GitHub user profile including id, login, and email.
        
        Args:
            access_token: Valid GitHub access token
            
        Returns:
            GitHubUser object with profile data
            
        Raises:
            GitHubOAuthError: If profile fetch fails
        """
        if not access_token:
            raise GitHubOAuthError("Access token is required")
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "StudentProgressTracker/1.0"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                # Fetch user profile
                user_response = await client.get(
                    self.user_api_url,
                    headers=headers,
                    timeout=30.0
                )
                
                if user_response.status_code != 200:
                    raise GitHubOAuthError(
                        f"Failed to fetch user profile with status {user_response.status_code}: {user_response.text}"
                    )
                
                user_data = user_response.json()
                
                # Fetch user emails if email is not public
                email = user_data.get("email")
                if not email:
                    email_response = await client.get(
                        "https://api.github.com/user/emails",
                        headers=headers,
                        timeout=30.0
                    )
                    
                    if email_response.status_code == 200:
                        emails = email_response.json()
                        # Find primary email
                        for email_obj in emails:
                            if email_obj.get("primary", False):
                                email = email_obj.get("email")
                                break
                
                # Validate required fields
                if not user_data.get("id"):
                    raise GitHubOAuthError("GitHub user ID not found in profile")
                
                if not user_data.get("login"):
                    raise GitHubOAuthError("GitHub username not found in profile")
                
                return GitHubUser(
                    id=user_data["id"],
                    login=user_data["login"],
                    email=email,
                    name=user_data.get("name"),
                    avatar_url=user_data.get("avatar_url")
                )
                
        except httpx.RequestError as e:
            raise GitHubOAuthError(f"Network error during profile fetch: {str(e)}")
        except Exception as e:
            if isinstance(e, GitHubOAuthError):
                raise
            raise GitHubOAuthError(f"Unexpected error during profile fetch: {str(e)}")
    
    async def complete_oauth_flow(self, code: str, state: Optional[str] = None) -> GitHubUser:
        """
        Complete the full OAuth flow: exchange code for token and fetch user profile.
        
        Args:
            code: Authorization code from GitHub callback
            state: Optional state parameter for validation
            
        Returns:
            GitHubUser object with complete profile data
            
        Raises:
            GitHubOAuthError: If any step of the OAuth flow fails
        """
        # Exchange code for access token
        access_token = await self.exchange_code_for_token(code, state)
        
        # Fetch user profile with the access token
        user_profile = await self.get_user_profile(access_token)
        
        return user_profile


    async def get_user_repositories(self, access_token: str, username: str) -> List[Dict[str, Any]]:
        """
        Get user's repositories using GitHub API.
        
        Args:
            access_token: Valid GitHub access token with repo scope
            username: GitHub username
            
        Returns:
            List of repository data
            
        Raises:
            GitHubOAuthError: If repository fetch fails
        """
        if not access_token:
            raise GitHubOAuthError("Access token is required")
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "StudentProgressTracker/1.0"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://api.github.com/users/{username}/repos",
                    headers=headers,
                    params={
                        "type": "all",
                        "sort": "updated",
                        "per_page": 100
                    },
                    timeout=30.0
                )
                
                if response.status_code != 200:
                    raise GitHubOAuthError(
                        f"Failed to fetch repositories with status {response.status_code}: {response.text}"
                    )
                
                return response.json()
                
        except httpx.RequestError as e:
            raise GitHubOAuthError(f"Network error during repository fetch: {str(e)}")
        except Exception as e:
            if isinstance(e, GitHubOAuthError):
                raise
            raise GitHubOAuthError(f"Unexpected error during repository fetch: {str(e)}")

    async def get_repository_commits(self, access_token: str, owner: str, repo: str, since: str = None) -> List[Dict[str, Any]]:
        """
        Get commits for a specific repository.
        
        Args:
            access_token: Valid GitHub access token with repo scope
            owner: Repository owner username
            repo: Repository name
            since: ISO 8601 date string to filter commits
            
        Returns:
            List of commit data
            
        Raises:
            GitHubOAuthError: If commit fetch fails
        """
        if not access_token:
            raise GitHubOAuthError("Access token is required")
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "StudentProgressTracker/1.0"
        }
        
        params = {"per_page": 100}
        if since:
            params["since"] = since
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://api.github.com/repos/{owner}/{repo}/commits",
                    headers=headers,
                    params=params,
                    timeout=30.0
                )
                
                if response.status_code != 200:
                    raise GitHubOAuthError(
                        f"Failed to fetch commits with status {response.status_code}: {response.text}"
                    )
                
                return response.json()
                
        except httpx.RequestError as e:
            raise GitHubOAuthError(f"Network error during commit fetch: {str(e)}")
        except Exception as e:
            if isinstance(e, GitHubOAuthError):
                raise
            raise GitHubOAuthError(f"Unexpected error during commit fetch: {str(e)}")


# Global OAuth handler instance
github_oauth = GitHubOAuth()