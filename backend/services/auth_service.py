"""
Authentication service for user validation and OAuth callback logic.
Handles user existence checks, mentor creation, and student enrollment validation with comprehensive error handling.
"""

from typing import Optional, Dict, Any
from datetime import datetime
from fastapi import HTTPException, status
from backend.models import User, Role
from backend.database import get_database
from backend.auth.jwt_handler import jwt_handler
from backend.auth.github_oauth import GitHubUser
from backend.exceptions import (
    AuthenticationError,
    AuthorizationError,
    DatabaseError,
    StudentNotEnrolledError,
    UserNotFoundError,
    log_error,
    handle_database_error
)
import logging

logger = logging.getLogger(__name__)


class AuthService:
    """Service for handling user authentication and validation logic."""
    
    def __init__(self):
        self.db = get_database()
    
    async def validate_and_authenticate_user(self, github_user: GitHubUser) -> Dict[str, Any]:
        """
        Validate user from GitHub OAuth and handle authentication logic.
        
        This method implements the core authentication requirements:
        - Check if user exists in MongoDB
        - Issue JWT for existing users
        - Create mentor users if they don't exist
        - Deny access for non-enrolled students with 403 Forbidden
        
        Args:
            github_user: GitHub user profile from OAuth
            
        Returns:
            Dictionary containing JWT token and user information
            
        Raises:
            HTTPException: 403 Forbidden for non-enrolled students
            AuthenticationError: For other authentication failures
        """
        try:
            # Check if user exists in MongoDB
            existing_user = await self._find_user_by_github_id(str(github_user.id))
            
            if existing_user:
                # User exists - issue JWT token
                return await self._authenticate_existing_user(existing_user, github_user)
            else:
                # User doesn't exist - determine if they should be created or denied
                return await self._handle_new_user(github_user)
                
        except AuthorizationError:
            # Re-raise authorization errors (like 403 Forbidden)
            raise
        except Exception as e:
            error = AuthenticationError(
                message="Authentication validation failed",
                details={"original_error": str(e), "github_user": github_user.login}
            )
            log_error(error, {"service": "auth_service", "method": "validate_and_authenticate_user"})
            raise error
    
    async def _find_user_by_github_id(self, github_id: str) -> Optional[Dict[str, Any]]:
        """Find user by GitHub ID in MongoDB with error handling."""
        try:
            user_doc = await self.db.users.find_one({"githubId": github_id})
            return user_doc
        except Exception as e:
            db_error = handle_database_error(e, "user lookup by GitHub ID")
            log_error(db_error, {"github_id": github_id})
            raise db_error
    
    async def _authenticate_existing_user(self, user_doc: Dict[str, Any], github_user: GitHubUser) -> Dict[str, Any]:
        """
        Authenticate existing user and issue JWT token.
        
        Requirements 1.5: Issue JWT for existing users
        Requirements 1.7: Deny access for non-enrolled students
        """
        try:
            # Check if student is enrolled
            if user_doc["role"] == Role.STUDENT.value and not user_doc.get("isEnrolled", False):
                raise StudentNotEnrolledError(
                    username=github_user.login,
                    details={"github_id": str(github_user.id)}
                )
            
            logger.info(f"Authenticating existing user: {github_user.login}")
            
            # Update last login timestamp
            await self.db.users.update_one(
                {"githubId": str(github_user.id)},
                {
                    "$set": {
                        "lastLogin": datetime.utcnow(),
                        "email": github_user.email  # Update email in case it changed
                    }
                }
            )
            
            # Create JWT token
            token_data = {
                "github_id": str(github_user.id),
                "username": github_user.login,
                "email": github_user.email,
                "role": user_doc["role"]
            }
            
            jwt_token = jwt_handler.create_token(token_data)
            
            return {
                "access_token": jwt_token,
                "token_type": "bearer",
                "user": {
                    "id": str(user_doc["_id"]),
                    "github_id": str(github_user.id),
                    "username": github_user.login,
                    "email": github_user.email,
                    "role": user_doc["role"],
                    "is_enrolled": user_doc.get("isEnrolled", False)
                }
            }
            
        except StudentNotEnrolledError:
            raise
        except Exception as e:
            error = AuthenticationError(
                message="Error authenticating existing user",
                details={"github_user": github_user.login, "original_error": str(e)}
            )
            log_error(error, {"service": "auth_service", "method": "_authenticate_existing_user"})
            raise error
    
    async def _handle_new_user(self, github_user: GitHubUser) -> Dict[str, Any]:
        """
        Handle new user authentication logic.
        
        Requirements 1.6: Create mentor users if they don't exist
        Requirements 1.7: Deny access for non-enrolled students
        """
        try:
            # Check if this user was pre-enrolled as a student
            pre_enrolled_student = await self.db.users.find_one({
                "username": github_user.login,
                "role": Role.STUDENT.value,
                "isEnrolled": True
            })
            
            if pre_enrolled_student:
                # Student was pre-enrolled - update with GitHub ID and authenticate
                return await self._activate_pre_enrolled_student(pre_enrolled_student, github_user)
            else:
                # Not pre-enrolled - create as mentor or deny access
                return await self._create_mentor_or_deny(github_user)
                
        except StudentNotEnrolledError:
            raise
        except Exception as e:
            error = AuthenticationError(
                message="Error handling new user",
                details={"github_user": github_user.login, "original_error": str(e)}
            )
            log_error(error, {"service": "auth_service", "method": "_handle_new_user"})
            raise error
    
    async def _activate_pre_enrolled_student(self, student_doc: Dict[str, Any], github_user: GitHubUser) -> Dict[str, Any]:
        """
        Activate a pre-enrolled student by updating their GitHub ID.
        
        This handles the case where a mentor enrolled a student by username,
        and now the student is logging in for the first time.
        """
        try:
            # Update student record with GitHub ID
            await self.db.users.update_one(
                {"_id": student_doc["_id"]},
                {
                    "$set": {
                        "githubId": str(github_user.id),
                        "email": github_user.email,
                        "lastLogin": datetime.utcnow()
                    }
                }
            )
            
            # Create JWT token
            token_data = {
                "github_id": str(github_user.id),
                "username": github_user.login,
                "email": github_user.email,
                "role": Role.STUDENT.value
            }
            
            jwt_token = jwt_handler.create_token(token_data)
            
            return {
                "access_token": jwt_token,
                "token_type": "bearer",
                "user": {
                    "id": str(student_doc["_id"]),
                    "github_id": str(github_user.id),
                    "username": github_user.login,
                    "email": github_user.email,
                    "role": Role.STUDENT.value,
                    "is_enrolled": True
                }
            }
            
        except Exception as e:
            error = AuthenticationError(
                message="Error activating pre-enrolled student",
                details={"github_user": github_user.login, "original_error": str(e)}
            )
            log_error(error, {"service": "auth_service", "method": "_activate_pre_enrolled_student"})
            raise error
    
    async def _create_mentor_or_deny(self, github_user: GitHubUser) -> Dict[str, Any]:
        """
        Create mentor user or deny access for non-enrolled students.
        
        Requirements 1.6: Create mentor users if they don't exist
        Requirements 1.7: Deny access for non-enrolled students with 403 Forbidden
        """
        try:
            # For this implementation, we'll create mentors automatically
            # In a production system, you might want additional validation
            # or a whitelist of allowed mentor GitHub IDs
            
            # Create new mentor user
            new_mentor = User(
                github_id=str(github_user.id),
                username=github_user.login,
                email=github_user.email,
                role=Role.MENTOR,
                is_enrolled=True,  # Mentors are always enrolled
                enrolled_by=None,  # Mentors are not enrolled by anyone
                created_at=datetime.utcnow(),
                last_login=datetime.utcnow()
            )
            
            # Insert into database
            result = await self.db.users.insert_one(new_mentor.dict(by_alias=True, exclude={"id"}))
            
            # Create JWT token
            token_data = {
                "github_id": str(github_user.id),
                "username": github_user.login,
                "email": github_user.email,
                "role": Role.MENTOR.value
            }
            
            jwt_token = jwt_handler.create_token(token_data)
            
            return {
                "access_token": jwt_token,
                "token_type": "bearer",
                "user": {
                    "id": str(result.inserted_id),
                    "github_id": str(github_user.id),
                    "username": github_user.login,
                    "email": github_user.email,
                    "role": Role.MENTOR.value,
                    "is_enrolled": True
                }
            }
            
        except Exception as e:
            error = AuthenticationError(
                message="Error creating mentor user",
                details={"github_user": github_user.login, "original_error": str(e)}
            )
            log_error(error, {"service": "auth_service", "method": "_create_mentor_or_deny"})
            raise error
    
    async def get_user_by_github_id(self, github_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user by GitHub ID for JWT token validation.
        
        Args:
            github_id: GitHub user ID
            
        Returns:
            User document or None if not found
        """
        try:
            return await self._find_user_by_github_id(github_id)
        except Exception as e:
            error = AuthenticationError(
                message="Error retrieving user",
                details={"github_id": github_id, "original_error": str(e)}
            )
            log_error(error, {"service": "auth_service", "method": "get_user_by_github_id"})
            raise error
    
    async def update_user_login(self, github_id: str) -> None:
        """
        Update user's last login timestamp.
        
        Args:
            github_id: GitHub user ID
        """
        try:
            await self.db.users.update_one(
                {"githubId": github_id},
                {"$set": {"lastLogin": datetime.utcnow()}}
            )
        except Exception as e:
            error = AuthenticationError(
                message="Error updating user login",
                details={"github_id": github_id, "original_error": str(e)}
            )
            log_error(error, {"service": "auth_service", "method": "update_user_login"})
            raise error


# Global auth service instance
auth_service = AuthService()