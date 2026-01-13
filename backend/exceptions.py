"""
Custom exception classes for comprehensive error handling.
Provides structured error types with proper HTTP status codes and logging.
"""

from typing import Optional, Dict, Any
from fastapi import HTTPException, status
import logging

logger = logging.getLogger(__name__)


class BaseApplicationError(Exception):
    """Base exception class for all application errors."""
    
    def __init__(
        self, 
        message: str, 
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for JSON responses."""
        return {
            "error": self.error_code,
            "message": self.message,
            "details": self.details
        }


class AuthenticationError(BaseApplicationError):
    """Authentication-related errors (401 Unauthorized)."""
    
    def __init__(self, message: str = "Authentication failed", **kwargs):
        super().__init__(message, **kwargs)
        self.status_code = status.HTTP_401_UNAUTHORIZED


class AuthorizationError(BaseApplicationError):
    """Authorization-related errors (403 Forbidden)."""
    
    def __init__(self, message: str = "Access denied", **kwargs):
        super().__init__(message, **kwargs)
        self.status_code = status.HTTP_403_FORBIDDEN


class ValidationError(BaseApplicationError):
    """Input validation errors (400 Bad Request)."""
    
    def __init__(self, message: str = "Invalid input", **kwargs):
        super().__init__(message, **kwargs)
        self.status_code = status.HTTP_400_BAD_REQUEST


class NotFoundError(BaseApplicationError):
    """Resource not found errors (404 Not Found)."""
    
    def __init__(self, message: str = "Resource not found", **kwargs):
        super().__init__(message, **kwargs)
        self.status_code = status.HTTP_404_NOT_FOUND


class ConflictError(BaseApplicationError):
    """Resource conflict errors (409 Conflict)."""
    
    def __init__(self, message: str = "Resource conflict", **kwargs):
        super().__init__(message, **kwargs)
        self.status_code = status.HTTP_409_CONFLICT


class DatabaseError(BaseApplicationError):
    """Database operation errors (500 Internal Server Error)."""
    
    def __init__(self, message: str = "Database operation failed", **kwargs):
        super().__init__(message, **kwargs)
        self.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR


class ExternalServiceError(BaseApplicationError):
    """External service errors (502 Bad Gateway)."""
    
    def __init__(self, message: str = "External service error", **kwargs):
        super().__init__(message, **kwargs)
        self.status_code = status.HTTP_502_BAD_GATEWAY


class RateLimitError(BaseApplicationError):
    """Rate limiting errors (429 Too Many Requests)."""
    
    def __init__(self, message: str = "Rate limit exceeded", **kwargs):
        super().__init__(message, **kwargs)
        self.status_code = status.HTTP_429_TOO_MANY_REQUESTS


# Specific application errors

class GitHubOAuthError(ExternalServiceError):
    """GitHub OAuth specific errors."""
    
    def __init__(self, message: str = "GitHub OAuth failed", **kwargs):
        super().__init__(message, error_code="GITHUB_OAUTH_ERROR", **kwargs)


class JWTError(AuthenticationError):
    """JWT token specific errors."""
    
    def __init__(self, message: str = "JWT token error", **kwargs):
        super().__init__(message, error_code="JWT_ERROR", **kwargs)


class UserNotFoundError(NotFoundError):
    """User not found specific error."""
    
    def __init__(self, identifier: str, **kwargs):
        message = f"User not found: {identifier}"
        super().__init__(message, error_code="USER_NOT_FOUND", **kwargs)


class StudentNotEnrolledError(AuthorizationError):
    """Student not enrolled specific error."""
    
    def __init__(self, username: str, **kwargs):
        message = f"Student '{username}' is not enrolled. Please contact a mentor for enrollment."
        super().__init__(message, error_code="STUDENT_NOT_ENROLLED", **kwargs)


class RepositoryNotFoundError(NotFoundError):
    """Repository not found specific error."""
    
    def __init__(self, repo_id: str, **kwargs):
        message = f"Repository not found: {repo_id}"
        super().__init__(message, error_code="REPOSITORY_NOT_FOUND", **kwargs)


class DuplicateResourceError(ConflictError):
    """Duplicate resource specific error."""
    
    def __init__(self, resource_type: str, identifier: str, **kwargs):
        message = f"{resource_type} already exists: {identifier}"
        super().__init__(message, error_code="DUPLICATE_RESOURCE", **kwargs)


class InsufficientPermissionsError(AuthorizationError):
    """Insufficient permissions specific error."""
    
    def __init__(self, operation: str, required_role: str, **kwargs):
        message = f"Insufficient permissions for '{operation}'. Required role: {required_role}"
        super().__init__(message, error_code="INSUFFICIENT_PERMISSIONS", **kwargs)


class InvalidInputError(ValidationError):
    """Invalid input specific error."""
    
    def __init__(self, field: str, reason: str, **kwargs):
        message = f"Invalid {field}: {reason}"
        super().__init__(message, error_code="INVALID_INPUT", **kwargs)


# Error handler utilities

def log_error(error: Exception, context: Optional[Dict[str, Any]] = None) -> None:
    """
    Log error with appropriate level and context.
    
    Args:
        error: Exception to log
        context: Additional context information
    """
    context = context or {}
    
    if isinstance(error, BaseApplicationError):
        # Application errors - log with context
        if error.status_code >= 500:
            logger.error(f"{error.error_code}: {error.message}", extra={
                "error_code": error.error_code,
                "details": error.details,
                "context": context
            })
        elif error.status_code >= 400:
            logger.warning(f"{error.error_code}: {error.message}", extra={
                "error_code": error.error_code,
                "details": error.details,
                "context": context
            })
    else:
        # Unexpected errors - always log as error
        logger.error(f"Unexpected error: {str(error)}", exc_info=True, extra={
            "error_type": type(error).__name__,
            "context": context
        })


def convert_to_http_exception(error: Exception) -> HTTPException:
    """
    Convert application error to FastAPI HTTPException.
    
    Args:
        error: Exception to convert
        
    Returns:
        HTTPException with appropriate status code and detail
    """
    if isinstance(error, BaseApplicationError):
        return HTTPException(
            status_code=error.status_code,
            detail={
                "error": error.error_code,
                "message": error.message,
                "details": error.details
            }
        )
    elif isinstance(error, HTTPException):
        return error
    else:
        # Unexpected error - return 500
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred",
                "details": {}
            }
        )


def handle_database_error(error: Exception, operation: str) -> DatabaseError:
    """
    Handle database errors with proper logging and conversion.
    
    Args:
        error: Database exception
        operation: Description of the database operation
        
    Returns:
        DatabaseError with appropriate message
    """
    error_msg = f"Database error during {operation}: {str(error)}"
    log_error(error, {"operation": operation})
    
    return DatabaseError(
        message=f"Database operation failed: {operation}",
        details={"operation": operation, "original_error": str(error)}
    )


def handle_external_service_error(error: Exception, service: str) -> ExternalServiceError:
    """
    Handle external service errors with proper logging and conversion.
    
    Args:
        error: External service exception
        service: Name of the external service
        
    Returns:
        ExternalServiceError with appropriate message
    """
    error_msg = f"External service error ({service}): {str(error)}"
    log_error(error, {"service": service})
    
    return ExternalServiceError(
        message=f"External service unavailable: {service}",
        details={"service": service, "original_error": str(error)}
    )