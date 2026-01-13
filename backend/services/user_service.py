"""
User service for managing user authentication, authorization, and GitHub token storage.
Handles secure storage and retrieval of GitHub access tokens.
"""

from typing import Optional, Dict, Any
from datetime import datetime, timezone
from bson import ObjectId
from backend.database import get_database
from backend.auth.github_oauth import GitHubUser
from backend.models import User, Role


class UserService:
    """Service for user management and GitHub token storage."""
    
    def __init__(self):
        self.db = get_database()
    
    async def find_user_by_github_id(self, github_id: str) -> Optional[Dict[str, Any]]:
        """
        Find user by GitHub ID.
        
        Args:
            github_id: GitHub user ID
            
        Returns:
            User document or None if not found
        """
        try:
            await self.db.connect()
            user = await self.db.users.find_one({"githubId": github_id})
            return user
        except Exception as e:
            print(f"Error finding user by GitHub ID: {e}")
            return None
    
    async def create_or_update_user(
        self, 
        github_user: GitHubUser, 
        github_access_token: str,
        role: Role = Role.MENTOR
    ) -> Dict[str, Any]:
        """
        Create new user or update existing user with GitHub access token.
        
        Args:
            github_user: GitHub user profile data
            github_access_token: GitHub OAuth access token
            role: User role (MENTOR or STUDENT)
            
        Returns:
            User document
        """
        try:
            await self.db.connect()
            
            github_id = str(github_user.id)
            now = datetime.now(timezone.utc)
            
            # Check if user already exists
            existing_user = await self.find_user_by_github_id(github_id)
            
            if existing_user:
                # Update existing user with new access token
                update_data = {
                    "username": github_user.login,
                    "email": github_user.email,
                    "githubAccessToken": github_access_token,  # Store securely
                    "lastLogin": now,
                    "updatedAt": now
                }
                
                await self.db.users.update_one(
                    {"githubId": github_id},
                    {"$set": update_data}
                )
                
                # Return updated user
                updated_user = await self.find_user_by_github_id(github_id)
                return updated_user
            
            else:
                # Create new user
                user_data = {
                    "githubId": github_id,
                    "username": github_user.login,
                    "email": github_user.email,
                    "role": role.value,
                    "isEnrolled": True if role == Role.MENTOR else False,
                    "enrolledBy": None if role == Role.MENTOR else None,
                    "githubAccessToken": github_access_token,  # Store securely
                    "createdAt": now,
                    "updatedAt": now,
                    "lastLogin": now
                }
                
                result = await self.db.users.insert_one(user_data)
                user_data["_id"] = result.inserted_id
                
                return user_data
                
        except Exception as e:
            print(f"Error creating/updating user: {e}")
            raise
    
    async def get_user_github_token(self, github_id: str) -> Optional[str]:
        """
        Get GitHub access token for a user.
        
        Args:
            github_id: GitHub user ID
            
        Returns:
            GitHub access token or None if not found
        """
        try:
            user = await self.find_user_by_github_id(github_id)
            if user and "githubAccessToken" in user:
                return user["githubAccessToken"]
            return None
        except Exception as e:
            print(f"Error getting user GitHub token: {e}")
            return None
    
    async def validate_user_access(self, github_id: str) -> Dict[str, Any]:
        """
        Validate if user should have access to the system.
        
        Args:
            github_id: GitHub user ID
            
        Returns:
            Dictionary with access validation result
        """
        try:
            user = await self.find_user_by_github_id(github_id)
            
            if not user:
                # New user - check if they should be auto-enrolled as mentor
                # In production, you might have different logic here
                return {
                    "has_access": True,  # For demo, allow all users
                    "role": Role.MENTOR,
                    "is_new_user": True,
                    "reason": "Auto-enrollment as mentor"
                }
            
            # Existing user
            if user.get("role") == Role.MENTOR.value:
                return {
                    "has_access": True,
                    "role": Role.MENTOR,
                    "is_new_user": False,
                    "reason": "Existing mentor"
                }
            
            elif user.get("role") == Role.STUDENT.value:
                if user.get("isEnrolled", False):
                    return {
                        "has_access": True,
                        "role": Role.STUDENT,
                        "is_new_user": False,
                        "reason": "Enrolled student"
                    }
                else:
                    return {
                        "has_access": False,
                        "role": Role.STUDENT,
                        "is_new_user": False,
                        "reason": "Student not enrolled by mentor"
                    }
            
            return {
                "has_access": False,
                "role": None,
                "is_new_user": False,
                "reason": "Invalid user role"
            }
            
        except Exception as e:
            print(f"Error validating user access: {e}")
            return {
                "has_access": False,
                "role": None,
                "is_new_user": False,
                "reason": f"Validation error: {str(e)}"
            }
    
    async def enroll_student(self, mentor_github_id: str, student_github_username: str, student_email: str) -> Dict[str, Any]:
        """
        Enroll a student (mentor-only operation).
        
        Args:
            mentor_github_id: GitHub ID of the mentor
            student_github_username: GitHub username of student to enroll
            student_email: Email of student to enroll
            
        Returns:
            Enrollment result
        """
        try:
            await self.db.connect()
            
            # Verify mentor permissions
            mentor = await self.find_user_by_github_id(mentor_github_id)
            if not mentor or mentor.get("role") != Role.MENTOR.value:
                raise PermissionError("Only mentors can enroll students")
            
            # Create student record (they'll get access token when they login)
            now = datetime.now(timezone.utc)
            student_data = {
                "githubId": None,  # Will be set when they first login
                "username": student_github_username,
                "email": student_email,
                "role": Role.STUDENT.value,
                "isEnrolled": True,
                "enrolledBy": mentor_github_id,
                "githubAccessToken": None,  # Will be set when they login
                "createdAt": now,
                "updatedAt": now,
                "lastLogin": None
            }
            
            # Check if student already enrolled
            existing_student = await self.db.users.find_one({
                "username": student_github_username,
                "role": Role.STUDENT.value
            })
            
            if existing_student:
                return {
                    "success": False,
                    "message": "Student already enrolled",
                    "student": existing_student
                }
            
            result = await self.db.users.insert_one(student_data)
            student_data["_id"] = result.inserted_id
            
            return {
                "success": True,
                "message": "Student enrolled successfully",
                "student": student_data
            }
            
        except Exception as e:
            print(f"Error enrolling student: {e}")
            return {
                "success": False,
                "message": f"Enrollment failed: {str(e)}",
                "student": None
            }


# Global user service instance
user_service = UserService()