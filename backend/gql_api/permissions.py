"""
GraphQL permission classes for role-based access control.
Implements IsAuthenticated, IsMentor, and IsStudent permission classes
that validate JWT tokens and user roles in GraphQL context.
"""

from typing import Any
import strawberry
from strawberry.permission import BasePermission
from strawberry.types import Info
from backend.models import Role


class IsAuthenticated(BasePermission):
    """
    Permission class that requires user authentication.
    Validates that a valid JWT token was provided and user context exists.
    """
    
    message = "Authentication required. Please provide a valid JWT token."
    
    def has_permission(self, source: Any, info: Info, **kwargs) -> bool:
        """
        Check if user is authenticated.
        
        Args:
            source: GraphQL source object
            info: GraphQL info object containing context
            **kwargs: Additional arguments
            
        Returns:
            True if user is authenticated, False otherwise
        """
        # Check if user context exists and has required fields
        user = getattr(info.context, 'user', None)
        if not user:
            return False
        
        # Validate that user has required authentication fields
        required_fields = ['github_id', 'username', 'role']
        for field in required_fields:
            if not user.get(field):
                return False
        
        return True


class IsMentor(BasePermission):
    """
    Permission class that requires mentor role.
    Validates that user is authenticated and has MENTOR role.
    """
    
    message = "Mentor access required. This operation is restricted to mentors only."
    
    def has_permission(self, source: Any, info: Info, **kwargs) -> bool:
        """
        Check if user is authenticated and has mentor role.
        
        Args:
            source: GraphQL source object
            info: GraphQL info object containing context
            **kwargs: Additional arguments
            
        Returns:
            True if user is authenticated mentor, False otherwise
        """
        # First check if user is authenticated
        if not IsAuthenticated().has_permission(source, info, **kwargs):
            return False
        
        # Check if user has mentor role
        user = getattr(info.context, 'user', None)
        return user and user.get('role') == Role.MENTOR.value


class IsStudent(BasePermission):
    """
    Permission class that requires student role.
    Validates that user is authenticated and has STUDENT role.
    """
    
    message = "Student access required. This operation is restricted to students only."
    
    def has_permission(self, source: Any, info: Info, **kwargs) -> bool:
        """
        Check if user is authenticated and has student role.
        
        Args:
            source: GraphQL source object
            info: GraphQL info object containing context
            **kwargs: Additional arguments
            
        Returns:
            True if user is authenticated student, False otherwise
        """
        # First check if user is authenticated
        if not IsAuthenticated().has_permission(source, info, **kwargs):
            return False
        
        # Check if user has student role
        user = getattr(info.context, 'user', None)
        return user and user.get('role') == Role.STUDENT.value


class IsOwnerOrMentor(BasePermission):
    """
    Permission class that allows access to resource owners or mentors.
    Useful for operations where students can access their own data or mentors can access all data.
    """
    
    message = "Access denied. You can only access your own data or you must be a mentor."
    
    def has_permission(self, source: Any, info: Info, **kwargs) -> bool:
        """
        Check if user is authenticated and either owns the resource or is a mentor.
        
        Args:
            source: GraphQL source object
            info: GraphQL info object containing context
            **kwargs: Additional arguments (should include resource_owner_id for ownership check)
            
        Returns:
            True if user is resource owner or mentor, False otherwise
        """
        # First check if user is authenticated
        if not IsAuthenticated().has_permission(source, info, **kwargs):
            return False
        
        user = getattr(info.context, 'user', None)
        if not user:
            return False
        
        # Allow if user is mentor
        if user.get('role') == Role.MENTOR.value:
            return True
        
        # Allow if user is student and owns the resource
        if user.get('role') == Role.STUDENT.value:
            resource_owner_id = kwargs.get('resource_owner_id')
            if resource_owner_id and user.get('github_id') == resource_owner_id:
                return True
        
        return False