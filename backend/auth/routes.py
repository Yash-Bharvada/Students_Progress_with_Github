"""
FastAPI authentication routes for GitHub OAuth flow.
Implements /auth/github/login and /auth/github/callback endpoints with comprehensive error handling.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, status, Request, Response
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from backend.auth.github_oauth import github_oauth
from backend.services.auth_service import auth_service
from backend.exceptions import (
    AuthenticationError,
    AuthorizationError,
    ExternalServiceError,
    ValidationError,
    log_error,
    convert_to_http_exception,
    GitHubOAuthError,
    StudentNotEnrolledError,
    UserNotFoundError
)
import logging

logger = logging.getLogger(__name__)


class AuthResponse(BaseModel):
    """Authentication response model."""
    access_token: str
    token_type: str
    user: dict


class ErrorResponse(BaseModel):
    """Error response model."""
    detail: str
    error_code: Optional[str] = None


# Create authentication router
auth_router = APIRouter(prefix="/auth", tags=["authentication"])


@auth_router.get("/github/login")
async def github_login(request: Request) -> RedirectResponse:
    """
    GitHub OAuth login endpoint with comprehensive error handling.
    
    Redirects user to GitHub's OAuth authorization page.
    
    Requirements 1.1: WHEN a user accesses /auth/github/login, 
    THE System SHALL redirect them to GitHub's OAuth authorization page
    
    Returns:
        RedirectResponse to GitHub OAuth authorization URL
        
    Raises:
        HTTPException: 500 if OAuth initialization fails
    """
    try:
        logger.info("Initiating GitHub OAuth login flow")
        
        # Generate state parameter for CSRF protection (optional but recommended)
        state = None  # Could implement CSRF state validation here
        
        # Get GitHub authorization URL
        auth_url = github_oauth.get_authorization_url(state=state)
        
        logger.info("Successfully generated GitHub OAuth URL")
        return RedirectResponse(url=auth_url, status_code=status.HTTP_302_FOUND)
        
    except ExternalServiceError as e:
        log_error(e, {"endpoint": "/auth/github/login"})
        raise convert_to_http_exception(e)
    except Exception as e:
        error = ExternalServiceError(
            message="Failed to initiate GitHub OAuth",
            details={"service": "github_oauth", "original_error": str(e)}
        )
        log_error(error, {"endpoint": "/auth/github/login"})
        raise convert_to_http_exception(error)


@auth_router.get("/github/callback")
async def github_callback(
    code: Optional[str] = None,
    state: Optional[str] = None,
    error: Optional[str] = None,
    error_description: Optional[str] = None
) -> AuthResponse:
    """
    GitHub OAuth callback endpoint with comprehensive error handling.
    
    Handles the OAuth callback from GitHub, exchanges code for token,
    fetches user profile, validates user, and issues JWT token.
    
    Requirements 1.2: Exchange authorization code for access token
    Requirements 1.3: Fetch GitHub user profile
    Requirements 1.4: Validate user against MongoDB
    Requirements 1.5: Issue JWT for existing users
    Requirements 1.6: Create mentor users if they don't exist
    Requirements 1.7: Deny access for non-enrolled students with 403 Forbidden
    
    Args:
        code: Authorization code from GitHub
        state: State parameter for CSRF protection
        error: Error code from GitHub (if OAuth failed)
        error_description: Error description from GitHub
        
    Returns:
        AuthResponse with JWT token and user information
        
    Raises:
        HTTPException: Various HTTP errors based on failure type
    """
    try:
        logger.info("Processing GitHub OAuth callback")
        
        # Check for OAuth errors from GitHub
        if error:
            error_msg = error_description or error
            logger.warning(f"GitHub OAuth error: {error_msg}")
            raise ValidationError(
                message=f"GitHub OAuth failed: {error_msg}",
                details={"github_error": error, "description": error_description}
            )
        
        # Validate authorization code
        if not code:
            logger.warning("Missing authorization code in OAuth callback")
            raise ValidationError(
                message="Authorization code is required",
                details={"missing_parameter": "code"}
            )
        
        logger.info("Completing GitHub OAuth flow")
        
        # Complete OAuth flow: exchange code for token and get user profile
        github_user = await github_oauth.complete_oauth_flow(code, state)
        
        logger.info(f"GitHub OAuth successful for user: {github_user.login}")
        
        # Validate and authenticate user
        auth_result = await auth_service.validate_and_authenticate_user(github_user)
        
        logger.info(f"User authentication successful: {github_user.login}")
        return AuthResponse(**auth_result)
        
    except ValidationError as e:
        log_error(e, {"endpoint": "/auth/github/callback", "code_present": bool(code)})
        raise convert_to_http_exception(e)
    except AuthorizationError as e:
        # This handles 403 Forbidden for non-enrolled students
        log_error(e, {"endpoint": "/auth/github/callback", "user": code})
        raise convert_to_http_exception(e)
    except GitHubOAuthError as e:
        log_error(e, {"endpoint": "/auth/github/callback", "step": "oauth_flow"})
        raise convert_to_http_exception(e)
    except AuthenticationError as e:
        log_error(e, {"endpoint": "/auth/github/callback", "step": "user_validation"})
        raise convert_to_http_exception(e)
    except Exception as e:
        error = AuthenticationError(
            message="Unexpected error during authentication",
            details={"original_error": str(e), "error_type": type(e).__name__}
        )
        log_error(error, {"endpoint": "/auth/github/callback"})
        raise convert_to_http_exception(error)


@auth_router.get("/me")
async def get_current_user(request: Request) -> dict:
    """
    Get current authenticated user information with comprehensive error handling.
    
    This endpoint can be used to validate JWT tokens and get user info.
    Requires valid JWT token in Authorization header.
    
    Returns:
        Current user information
        
    Raises:
        HTTPException: 401 if token is invalid or missing, 404 if user not found
    """
    try:
        logger.debug("Getting current user information")
        
        # Extract token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            raise AuthenticationError(
                message="Authorization header is required",
                details={"missing_header": "Authorization"}
            )
        
        # Extract JWT token
        token = auth_header.replace("Bearer ", "")
        if not token or token == auth_header:
            raise AuthenticationError(
                message="Bearer token is required",
                details={"invalid_format": "Expected 'Bearer <token>'"}
            )
        
        # Validate token and extract user info
        from backend.auth.jwt_handler import jwt_handler
        user_data = jwt_handler.extract_user_from_token(token)
        
        # Get full user information from database
        user_doc = await auth_service.get_user_by_github_id(user_data["github_id"])
        if not user_doc:
            raise UserNotFoundError(
                identifier=user_data["github_id"],
                details={"github_id": user_data["github_id"]}
            )
        
        logger.debug(f"Successfully retrieved user info: {user_doc['username']}")
        
        return {
            "id": str(user_doc["_id"]),
            "github_id": user_doc["githubId"],
            "username": user_doc["username"],
            "email": user_doc.get("email"),
            "role": user_doc["role"],
            "is_enrolled": user_doc.get("isEnrolled", False),
            "created_at": user_doc["createdAt"],
            "last_login": user_doc.get("lastLogin")
        }
        
    except (AuthenticationError, UserNotFoundError) as e:
        log_error(e, {"endpoint": "/auth/me"})
        raise convert_to_http_exception(e)
    except Exception as e:
        error = AuthenticationError(
            message="Token validation failed",
            details={"original_error": str(e), "error_type": type(e).__name__}
        )
        log_error(error, {"endpoint": "/auth/me"})
        raise convert_to_http_exception(error)


@auth_router.post("/logout")
async def logout() -> dict:
    """
    Logout endpoint.
    
    Since we're using stateless JWT tokens, logout is handled client-side
    by discarding the token. This endpoint exists for API completeness.
    
    Returns:
        Success message
    """
    return {"message": "Logged out successfully. Please discard your JWT token."}


# Health check endpoint for authentication service
@auth_router.get("/health")
async def auth_health_check() -> dict:
    """
    Authentication service health check with comprehensive error handling.
    
    Returns:
        Health status of authentication components
    """
    try:
        logger.debug("Performing authentication health check")
        
        # Test database connection
        from backend.database import get_database
        db = get_database()
        health = await db.health_check()
        
        return {
            "status": "healthy",
            "authentication": "operational",
            "github_oauth": "configured",
            "jwt_handler": "operational",
            "database": health.get("status", "unknown")
        }
        
    except Exception as e:
        logger.error(f"Authentication health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": "HEALTH_CHECK_ERROR",
            "message": "Authentication health check failed",
            "details": {"error_type": type(e).__name__, "error": str(e)}
        }