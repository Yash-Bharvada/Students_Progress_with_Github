#!/usr/bin/env python3
"""
Minimal FastAPI server for testing OAuth authentication flow.
This is a temporary test server to verify our authentication system works.
"""

import sys
sys.path.append('backend')

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from backend.auth.github_oauth import github_oauth, GitHubOAuthError
from backend.auth.jwt_handler import jwt_handler, JWTError
from backend.services.user_service import user_service
from backend.services.repository_service import repository_service
from backend.models import Role
from backend.config import get_settings

# Initialize FastAPI app
app = FastAPI(
    title="Student Progress Backend - Test Server",
    description="Test server for OAuth authentication flow",
    version="1.0.0"
)

# Get settings
settings = get_settings()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint with basic info."""
    return {
        "message": "Student Progress Backend - Automatic Token Management",
        "status": "running",
        "oauth_scopes": ["user:email", "repo"],
        "features": {
            "automatic_token_storage": True,
            "secure_database_storage": True,
            "no_manual_tokens_required": True
        },
        "endpoints": {
            "auth": {
                "login": "/auth/github/login",
                "callback": "/auth/github/callback"
            },
            "testing": {
                "validate_token": "/test/validate-token",
                "user_repositories": "/test/repositories/{username}",
                "repository_commits": "/test/commits/{owner}/{repo}",
                "repository_analysis": "/test/analyze/{owner}/{repo}",
                "health": "/health"
            }
        },
        "instructions": [
            "1. Authenticate via /auth/github/login (grants repository access)",
            "2. GitHub access token is stored securely in database",
            "3. Use JWT token for all API calls - no manual token management needed",
            "4. Example: /test/repositories/Yash-Bharvada",
            "5. Example: /test/analyze/Yash-Bharvada/repo-name"
        ]
    }


@app.get("/auth/github/login")
async def github_login():
    """
    Initiate GitHub OAuth flow.
    Redirects user to GitHub for authorization.
    """
    try:
        # Generate authorization URL with state for CSRF protection
        auth_url = github_oauth.get_authorization_url(state="test_oauth_state")
        
        # Return redirect response
        return RedirectResponse(url=auth_url)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OAuth initialization failed: {str(e)}")


@app.get("/auth/github/callback")
async def github_callback(code: str = None, state: str = None, error: str = None):
    """
    Handle GitHub OAuth callback with automatic token storage.
    Exchanges authorization code for access token and stores it securely.
    """
    try:
        # Check for OAuth errors
        if error:
            raise HTTPException(status_code=400, detail=f"OAuth error: {error}")
        
        if not code:
            raise HTTPException(status_code=400, detail="Authorization code is required")
        
        # Verify state parameter (basic CSRF protection)
        if state not in ["test_oauth_state", "repo_access_test", "browser_test"]:
            raise HTTPException(status_code=400, detail="Invalid state parameter")
        
        # Complete OAuth flow and get access token
        access_token = await github_oauth.exchange_code_for_token(code, state)
        
        # Get user profile
        github_user = await github_oauth.get_user_profile(access_token)
        
        # Validate user access and determine role
        access_validation = await user_service.validate_user_access(str(github_user.id))
        
        if not access_validation["has_access"]:
            raise HTTPException(
                status_code=403, 
                detail=f"Access denied: {access_validation['reason']}"
            )
        
        # Create or update user with GitHub access token (stored securely in database)
        user_doc = await user_service.create_or_update_user(
            github_user, 
            access_token, 
            access_validation["role"]
        )
        
        # Create JWT token (without access token - it's stored in database)
        jwt_user_data = {
            "github_id": str(github_user.id),
            "username": github_user.login,
            "email": github_user.email,
            "role": access_validation["role"].value
        }
        
        jwt_token = jwt_handler.create_token(jwt_user_data)
        
        # Return success response
        return JSONResponse(
            status_code=200,
            content={
                "message": "Authentication successful",
                "token": jwt_token,
                "user": {
                    "github_id": str(github_user.id),
                    "username": github_user.login,
                    "email": github_user.email,
                    "role": access_validation["role"].value
                },
                "repository_access": True,
                "scopes": ["user:email", "repo"],
                "token_stored": True,  # Indicates token is stored securely
                "is_new_user": access_validation["is_new_user"]
            }
        )
        
    except GitHubOAuthError as e:
        raise HTTPException(status_code=400, detail=f"OAuth error: {str(e)}")
    except JWTError as e:
        raise HTTPException(status_code=500, detail=f"Token creation error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Authentication failed: {str(e)}")


@app.get("/test/repositories/{username}")
async def test_user_repositories(username: str, request: Request):
    """
    Test endpoint to fetch real GitHub repositories using stored access token.
    No manual token required - automatically uses stored token.
    """
    try:
        # Extract and validate JWT token
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            raise HTTPException(status_code=401, detail="Authorization header required")
        
        token = jwt_handler.extract_token_from_header(auth_header)
        if not token:
            raise HTTPException(status_code=401, detail="Invalid Authorization header format")
        
        # Get user info from JWT
        user_info = jwt_handler.extract_user_from_token(token)
        github_id = user_info["github_id"]
        
        # Fetch repositories using stored access token
        repo_data = await repository_service.get_user_repositories(github_id)
        
        if not repo_data["success"]:
            raise HTTPException(status_code=400, detail=repo_data["error"])
        
        return {
            "message": f"Successfully fetched repositories for {username}",
            "username": repo_data["username"],
            "total_repositories": repo_data["total_repositories"],
            "showing": min(10, len(repo_data["repositories"])),
            "repositories": repo_data["repositories"][:10],  # Limit to 10 for display
            "fetched_at": repo_data["fetched_at"],
            "token_source": "stored_securely"
        }
        
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Repository fetch failed: {str(e)}")


@app.get("/test/commits/{owner}/{repo}")
async def test_repository_commits(owner: str, repo: str, request: Request, since: str = None):
    """
    Test endpoint to fetch real commit data using stored access token.
    No manual token required - automatically uses stored token.
    """
    try:
        # Extract and validate JWT token
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            raise HTTPException(status_code=401, detail="Authorization header required")
        
        token = jwt_handler.extract_token_from_header(auth_header)
        if not token:
            raise HTTPException(status_code=401, detail="Invalid Authorization header format")
        
        # Get user info from JWT
        user_info = jwt_handler.extract_user_from_token(token)
        github_id = user_info["github_id"]
        
        # Fetch commits using stored access token
        commit_data = await repository_service.get_repository_commits(
            github_id, owner, repo, since, limit=20
        )
        
        if not commit_data["success"]:
            raise HTTPException(status_code=400, detail=commit_data["error"])
        
        return {
            "message": f"Successfully fetched commits for {owner}/{repo}",
            "repository": commit_data["repository"],
            "total_commits": commit_data["total_commits"],
            "showing": commit_data["showing"],
            "since": commit_data["since"],
            "commits": commit_data["commits"],
            "fetched_at": commit_data["fetched_at"],
            "token_source": "stored_securely"
        }
        
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Commit fetch failed: {str(e)}")


@app.get("/test/analyze/{owner}/{repo}")
async def test_repository_analysis(owner: str, repo: str, request: Request):
    """
    Test endpoint for advanced repository analysis using stored access token.
    Provides detailed activity patterns and collaboration metrics.
    """
    try:
        # Extract and validate JWT token
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            raise HTTPException(status_code=401, detail="Authorization header required")
        
        token = jwt_handler.extract_token_from_header(auth_header)
        if not token:
            raise HTTPException(status_code=401, detail="Invalid Authorization header format")
        
        # Get user info from JWT
        user_info = jwt_handler.extract_user_from_token(token)
        github_id = user_info["github_id"]
        
        # Analyze repository using stored access token
        analysis_data = await repository_service.analyze_repository_activity(github_id, owner, repo)
        
        if not analysis_data["success"]:
            raise HTTPException(status_code=400, detail=analysis_data["error"])
        
        return {
            "message": f"Successfully analyzed repository {owner}/{repo}",
            "analysis": analysis_data["analysis"],
            "token_source": "stored_securely"
        }
        
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Repository analysis failed: {str(e)}")


@app.get("/test/validate-token")
async def validate_token(request: Request):
    """
    Test endpoint to validate JWT tokens.
    Requires Authorization: Bearer <token> header.
    """
    try:
        # Extract token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            raise HTTPException(status_code=401, detail="Authorization header required")
        
        token = jwt_handler.extract_token_from_header(auth_header)
        if not token:
            raise HTTPException(status_code=401, detail="Invalid Authorization header format")
        
        # Validate token and extract user info
        user_info = jwt_handler.extract_user_from_token(token)
        
        return {
            "message": "Token is valid",
            "user": user_info,
            "token_valid": True
        }
        
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Token validation failed: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "oauth_configured": bool(settings.github_client_id and settings.github_client_secret),
        "jwt_configured": bool(settings.jwt_secret_key),
        "environment": settings.environment
    }


if __name__ == "__main__":
    print("🚀 Starting Student Progress Backend Test Server...")
    print(f"📍 Server will be available at: http://localhost:8000")
    print(f"🔐 OAuth Login URL: http://localhost:8000/auth/github/login")
    print(f"🏥 Health Check: http://localhost:8000/health")
    print(f"🧪 Token Validation: http://localhost:8000/test/validate-token")
    print("\n" + "="*60)
    print("TESTING INSTRUCTIONS:")
    print("1. Open http://localhost:8000/auth/github/login in your browser")
    print("2. Complete GitHub OAuth authorization")
    print("3. Copy the JWT token from the callback response")
    print("4. Test token validation with Postman or curl")
    print("="*60 + "\n")
    
    uvicorn.run(
        "test_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )