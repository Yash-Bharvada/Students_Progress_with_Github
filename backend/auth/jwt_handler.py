"""
JWT handler for token creation, validation, and user extraction.
Handles JWT token lifecycle and integrates with GraphQL context.
"""

import jwt
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional
from pydantic import BaseModel
from backend.config import get_settings


class JWTError(Exception):
    """Custom exception for JWT-related errors."""
    pass


class TokenData(BaseModel):
    """JWT token payload data model."""
    github_id: str
    username: str
    email: Optional[str]
    role: str
    exp: int
    iat: int


class JWTHandler:
    """JWT handler for token creation and validation."""
    
    def __init__(self):
        self.settings = get_settings()
        self.secret_key = self.settings.jwt_secret_key
        self.algorithm = self.settings.jwt_algorithm
        self.expiration_hours = self.settings.jwt_expiration_hours
    
    def create_token(self, user_data: Dict[str, Any]) -> str:
        """
        Create JWT token with user claims.
        
        Args:
            user_data: Dictionary containing user information
                Required keys: github_id, username, role
                Optional keys: email
        
        Returns:
            Encoded JWT token string
            
        Raises:
            JWTError: If token creation fails or required data is missing
        """
        try:
            # Validate required fields
            required_fields = ["github_id", "username", "role"]
            for field in required_fields:
                if field not in user_data or not user_data[field]:
                    raise JWTError(f"Required field '{field}' is missing or empty")
            
            # Create token payload
            now = datetime.now(timezone.utc)
            expiration = now + timedelta(hours=self.expiration_hours)
            
            payload = {
                "github_id": str(user_data["github_id"]),
                "username": user_data["username"],
                "email": user_data.get("email"),
                "role": user_data["role"],
                "iat": int(now.timestamp()),
                "exp": int(expiration.timestamp()),
                "iss": "student-progress-tracker",  # Issuer
                "aud": "student-progress-api"       # Audience
            }
            
            # Encode token
            token = jwt.encode(
                payload,
                self.secret_key,
                algorithm=self.algorithm
            )
            
            return token
            
        except jwt.PyJWTError as e:
            raise JWTError(f"Failed to create JWT token: {str(e)}")
        except Exception as e:
            raise JWTError(f"Unexpected error creating JWT token: {str(e)}")
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verify and decode JWT token.
        
        Args:
            token: JWT token string to verify
            
        Returns:
            Decoded token payload as dictionary
            
        Raises:
            JWTError: If token is invalid, expired, or verification fails
        """
        if not token:
            raise JWTError("Token is required")
        
        try:
            # Decode and verify token
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                audience="student-progress-api",
                issuer="student-progress-tracker"
            )
            
            # Validate required claims
            required_claims = ["github_id", "username", "role", "exp", "iat"]
            for claim in required_claims:
                if claim not in payload:
                    raise JWTError(f"Missing required claim: {claim}")
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise JWTError("Token has expired")
        except jwt.InvalidTokenError as e:
            raise JWTError(f"Invalid token: {str(e)}")
        except jwt.InvalidSignatureError:
            raise JWTError("Invalid token signature")
        except jwt.InvalidAudienceError:
            raise JWTError("Invalid token audience")
        except jwt.InvalidIssuerError:
            raise JWTError("Invalid token issuer")
        except Exception as e:
            raise JWTError(f"Unexpected error verifying token: {str(e)}")
    
    def extract_token_from_header(self, authorization_header: Optional[str]) -> Optional[str]:
        """
        Extract JWT token from Authorization Bearer header.
        
        Args:
            authorization_header: Authorization header value (e.g., "Bearer <token>")
            
        Returns:
            JWT token string or None if header is invalid
        """
        if not authorization_header:
            return None
        
        # Check for Bearer token format
        parts = authorization_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return None
        
        return parts[1]
    
    def extract_user_from_token(self, token: str) -> Dict[str, Any]:
        """
        Extract user information from JWT token.
        
        Args:
            token: JWT token string
            
        Returns:
            Dictionary containing user information
            
        Raises:
            JWTError: If token is invalid or user extraction fails
        """
        payload = self.verify_token(token)
        
        return {
            "github_id": payload["github_id"],
            "username": payload["username"],
            "email": payload.get("email"),
            "role": payload["role"]
        }
    
    def refresh_token(self, token: str) -> str:
        """
        Refresh an existing JWT token with new expiration.
        
        Args:
            token: Current JWT token
            
        Returns:
            New JWT token with refreshed expiration
            
        Raises:
            JWTError: If token refresh fails
        """
        try:
            # Verify current token (this will raise if expired)
            payload = self.verify_token(token)
            
            # Create new token with same user data
            user_data = {
                "github_id": payload["github_id"],
                "username": payload["username"],
                "email": payload.get("email"),
                "role": payload["role"]
            }
            
            return self.create_token(user_data)
            
        except JWTError:
            raise  # Re-raise JWT errors
        except Exception as e:
            raise JWTError(f"Unexpected error refreshing token: {str(e)}")
    
    def get_token_expiration(self, token: str) -> datetime:
        """
        Get expiration datetime from JWT token.
        
        Args:
            token: JWT token string
            
        Returns:
            Token expiration datetime
            
        Raises:
            JWTError: If token is invalid
        """
        payload = self.verify_token(token)
        return datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    
    def is_token_expired(self, token: str) -> bool:
        """
        Check if JWT token is expired.
        
        Args:
            token: JWT token string
            
        Returns:
            True if token is expired, False otherwise
        """
        try:
            expiration = self.get_token_expiration(token)
            return datetime.now(timezone.utc) > expiration
        except JWTError:
            return True  # Consider invalid tokens as expired


# Global JWT handler instance
jwt_handler = JWTHandler()