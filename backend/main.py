"""
FastAPI application entry point with GraphQL, authentication, and database integration.
Production-ready setup with CORS, middleware, and comprehensive error handling.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from strawberry.fastapi import GraphQLRouter
from backend.config import get_settings, validate_configuration
from backend.database import connect_database, disconnect_database, get_database
from backend.auth.routes import auth_router
from backend.graphql.schema import schema
from backend.graphql.context import get_context


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for database connection lifecycle.
    Handles startup and shutdown events for proper resource management.
    """
    logger.info("🚀 Starting Student Progress Tracker API...")
    
    try:
        # Validate configuration on startup
        validate_configuration()
        
        # Connect to database
        await connect_database()
        
        # Test database connection
        db = get_database()
        health = await db.health_check()
        if health["status"] == "healthy":
            logger.info("✅ Database connection established successfully")
        else:
            logger.error(f"❌ Database health check failed: {health}")
            raise Exception("Database connection failed")
        
        logger.info("✅ Application startup complete")
        
        yield  # Application runs here
        
    except Exception as e:
        logger.error(f"❌ Application startup failed: {e}")
        raise
    finally:
        # Cleanup on shutdown
        logger.info("🔄 Shutting down Student Progress Tracker API...")
        await disconnect_database()
        logger.info("✅ Application shutdown complete")


# Create FastAPI application with lifespan management
app = FastAPI(
    title="Student Progress Tracker API",
    description="Production-ready backend for tracking student project progress and performance",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Get application settings
settings = get_settings()

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# Import custom exceptions
from backend.exceptions import (
    BaseApplicationError, 
    AuthenticationError, 
    AuthorizationError,
    ValidationError,
    DatabaseError,
    ExternalServiceError,
    log_error,
    convert_to_http_exception
)

# Global exception handlers for comprehensive error handling

@app.exception_handler(BaseApplicationError)
async def application_exception_handler(request: Request, exc: BaseApplicationError):
    """Handle custom application exceptions with proper logging and responses."""
    log_error(exc, {"path": request.url.path, "method": request.method})
    
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_dict()
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle FastAPI HTTP exceptions with enhanced logging."""
    logger.warning(f"HTTP exception: {exc.status_code} - {exc.detail}", extra={
        "status_code": exc.status_code,
        "path": request.url.path,
        "method": request.method
    })
    
    # Ensure detail is properly formatted
    if isinstance(exc.detail, dict):
        detail = exc.detail
    else:
        detail = {
            "error": "HTTP_ERROR",
            "message": str(exc.detail),
            "details": {}
        }
    
    return JSONResponse(
        status_code=exc.status_code,
        content=detail
    )

@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    """Handle validation errors with detailed field information."""
    log_error(exc, {"path": request.url.path, "method": request.method})
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "VALIDATION_ERROR",
            "message": "Input validation failed",
            "details": exc.details
        }
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors."""
    log_error(exc, {"path": request.url.path, "method": request.method})
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred",
            "details": {
                "error_type": type(exc).__name__,
                "path": request.url.path
            }
        }
    )


# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Application health check endpoint with comprehensive error handling.
    Returns overall system health including database status.
    """
    try:
        # Check database health
        db = get_database()
        db_health = await db.health_check()
        
        return {
            "status": "healthy" if db_health["status"] == "healthy" else "unhealthy",
            "version": "1.0.0",
            "environment": settings.environment,
            "database": db_health,
            "services": {
                "authentication": "operational",
                "graphql": "operational",
                "ai_feedback": "operational"
            }
        }
        
    except DatabaseError as e:
        logger.error(f"Database health check failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "error": "DATABASE_ERROR",
                "message": "Database health check failed",
                "details": e.details
            }
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "error": "HEALTH_CHECK_ERROR",
                "message": "Health check failed",
                "details": {"error_type": type(e).__name__}
            }
        )


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Student Progress Tracker API",
        "version": "1.0.0",
        "docs": "/docs",
        "graphql": "/graphql",
        "authentication": "/auth"
    }


# Mount authentication routes at /auth prefix
app.include_router(auth_router, prefix="/auth", tags=["authentication"])

# Create GraphQL router with context
graphql_app = GraphQLRouter(
    schema,
    context_getter=get_context,
    graphiql=settings.debug  # Enable GraphiQL in development
)

# Mount GraphQL endpoint at /graphql
app.add_route("/graphql", graphql_app)
app.add_websocket_route("/graphql", graphql_app)  # For subscriptions if needed


if __name__ == "__main__":
    import uvicorn
    
    # Run with uvicorn for development
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )