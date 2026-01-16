"""
GraphQL context management for JWT authentication and user context.
Handles token extraction from Authorization headers and user context setup.
"""

from typing import Optional, Dict, Any
from dataclasses import dataclass
from fastapi import Request
from backend.auth.jwt_handler import jwt_handler, JWTError
import logging

# Set up logging
logger = logging.getLogger(__name__)


@dataclass
class GraphQLContext:
    """
    GraphQL context containing user information and request data.
    """
    user: Optional[Dict[str, Any]] = None
    request: Optional[Request] = None
    is_authenticated: bool = False
    authentication_error: Optional[str] = None


class ContextManager:
    """
    Manages GraphQL context creation and user authentication.
    """
    
    def __init__(self):
        self.jwt_handler = jwt_handler
    
    def extract_token_from_request(self, request: Request) -> Optional[str]:
        """
        Extract JWT token from request Authorization header.
        
        Args:
            request: FastAPI request object
            
        Returns:
            JWT token string or None if not found/invalid
        """
        try:
            # Get Authorization header
            authorization = request.headers.get("Authorization")
            if not authorization:
                return None
            
            # Extract token using JWT handler
            token = self.jwt_handler.extract_token_from_header(authorization)
            return token
            
        except Exception as e:
            logger.warning(f"Error extracting token from request: {str(e)}")
            return None
    
    def authenticate_user(self, token: str) -> tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Authenticate user using JWT token.
        
        Args:
            token: JWT token string
            
        Returns:
            Tuple of (user_data, error_message)
            user_data is None if authentication fails
            error_message is None if authentication succeeds
        """
        if not token:
            return None, "No token provided"
        
        try:
            # Extract user data from token
            user_data = self.jwt_handler.extract_user_from_token(token)
            
            # Validate required user fields
            required_fields = ['github_id', 'username', 'role']
            for field in required_fields:
                if not user_data.get(field):
                    return None, f"Invalid token: missing {field}"
            
            logger.info(f"User authenticated: {user_data['username']} ({user_data['role']})")
            return user_data, None
            
        except JWTError as e:
            error_msg = f"JWT authentication failed: {str(e)}"
            logger.warning(error_msg)
            return None, error_msg
        except Exception as e:
            error_msg = f"Unexpected authentication error: {str(e)}"
            logger.error(error_msg)
            return None, error_msg
    
    async def create_context(self, request: Request) -> GraphQLContext:
        """
        Create GraphQL context with user authentication.
        
        Args:
            request: FastAPI request object
            
        Returns:
            GraphQLContext with user information and authentication status
        """
        context = GraphQLContext(request=request)
        
        try:
            # Extract token from request
            token = self.extract_token_from_request(request)
            
            if token:
                # Authenticate user
                user_data, error = self.authenticate_user(token)
                
                if user_data:
                    context.user = user_data
                    context.is_authenticated = True
                    logger.debug(f"Context created for authenticated user: {user_data['username']}")
                else:
                    context.authentication_error = error
                    logger.debug(f"Authentication failed: {error}")
            else:
                logger.debug("No token found in request")
            
        except Exception as e:
            error_msg = f"Error creating GraphQL context: {str(e)}"
            logger.error(error_msg)
            context.authentication_error = error_msg
        
        return context
    
    def get_current_user(self, context: GraphQLContext) -> Optional[Dict[str, Any]]:
        """
        Get current authenticated user from context.
        
        Args:
            context: GraphQL context
            
        Returns:
            User data dictionary or None if not authenticated
        """
        return context.user if context.is_authenticated else None
    
    def require_authentication(self, context: GraphQLContext) -> Dict[str, Any]:
        """
        Require authentication and return user data.
        
        Args:
            context: GraphQL context
            
        Returns:
            User data dictionary
            
        Raises:
            Exception: If user is not authenticated
        """
        if not context.is_authenticated or not context.user:
            error_msg = context.authentication_error or "Authentication required"
            raise Exception(error_msg)
        
        return context.user
    
    def require_role(self, context: GraphQLContext, required_role: str) -> Dict[str, Any]:
        """
        Require specific role and return user data.
        
        Args:
            context: GraphQL context
            required_role: Required user role (MENTOR or STUDENT)
            
        Returns:
            User data dictionary
            
        Raises:
            Exception: If user doesn't have required role
        """
        user = self.require_authentication(context)
        
        if user.get('role') != required_role:
            raise Exception(f"Access denied. Required role: {required_role}")
        
        return user


# Global context manager instance
context_manager = ContextManager()


# Context factory function for Strawberry GraphQL
async def get_context(request: Request) -> GraphQLContext:
    """
    Context factory function for Strawberry GraphQL.
    
    Args:
        request: FastAPI request object
        
    Returns:
        GraphQL context with user authentication
    """
    return await context_manager.create_context(request)