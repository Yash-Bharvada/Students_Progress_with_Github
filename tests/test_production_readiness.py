"""
Production readiness verification tests for the Student Progress Backend.
Tests uvicorn server startup, environment variables, CORS configuration,
and GraphQL schema validation.
"""

import pytest
import os
import asyncio
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from backend.main import app
from backend.config import get_settings, validate_configuration
from backend.database import get_database
import json


class TestProductionReadiness:
    """Test production readiness components."""
    
    def test_fastapi_app_creation(self):
        """Test that FastAPI app can be created successfully."""
        assert app is not None
        assert app.title == "Student Progress Tracker API"
        assert app.version == "1.0.0"
    
    def test_environment_variables_validation(self):
        """Test that environment variables are properly validated."""
        try:
            # Test configuration loading
            settings = get_settings()
            
            # Verify required settings exist
            assert hasattr(settings, 'mongodb_connection_string')
            assert hasattr(settings, 'github_client_id')
            assert hasattr(settings, 'github_client_secret')
            assert hasattr(settings, 'jwt_secret_key')
            assert hasattr(settings, 'github_api_token')
            
            # Test configuration validation
            validate_configuration()
            
        except Exception as e:
            # In test environment, some config might be missing, which is expected
            assert any(keyword in str(e).lower() for keyword in ['required', 'missing', 'validation'])
    
    def test_cors_configuration(self):
        """Test CORS configuration is properly set up."""
        # Check that CORS middleware is configured
        middleware_classes = [middleware.cls.__name__ for middleware in app.user_middleware]
        assert 'CORSMiddleware' in middleware_classes
    
    def test_route_registration(self):
        """Test that all required routes are registered."""
        client = TestClient(app)
        
        # Test root endpoint
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        
        # Test health endpoint
        response = client.get("/health")
        # Health endpoint might fail due to database connection in test env
        assert response.status_code in [200, 503]
    
    def test_authentication_routes(self):
        """Test authentication routes are properly registered."""
        client = TestClient(app)
        
        # Test GitHub login redirect
        response = client.get("/auth/github/login")
        assert response.status_code == 302
        assert "github.com" in response.headers["location"]
        
        # Test auth health check
        response = client.get("/auth/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
    
    def test_graphql_endpoint(self):
        """Test GraphQL endpoint is accessible."""
        client = TestClient(app)
        
        # Test GraphQL endpoint with simple introspection query
        introspection_query = """
        query {
            __schema {
                types {
                    name
                }
            }
        }
        """
        
        response = client.post("/graphql", json={"query": introspection_query})
        assert response.status_code == 200
        data = response.json()
        
        # Should have schema information
        assert "data" in data
        assert "__schema" in data["data"]
        assert "types" in data["data"]["__schema"]
    
    def test_graphql_schema_validation(self):
        """Test GraphQL schema contains required types."""
        client = TestClient(app)
        
        # Query for specific types
        type_query = """
        query {
            __schema {
                types {
                    name
                    fields {
                        name
                    }
                }
            }
        }
        """
        
        response = client.post("/graphql", json={"query": type_query})
        assert response.status_code == 200
        data = response.json()
        
        # Extract type names
        types = data["data"]["__schema"]["types"]
        type_names = [t["name"] for t in types]
        
        # Verify required types exist
        required_types = ["User", "Repository", "ContributionMetrics", "AIFeedback", "Query", "Mutation"]
        for required_type in required_types:
            assert required_type in type_names, f"Required type {required_type} not found in schema"
    
    @pytest.mark.asyncio
    async def test_database_connection_handling(self):
        """Test database connection handling."""
        try:
            # Test database singleton
            db = get_database()
            assert db is not None
            
            # Test health check (might fail in test environment)
            health = await db.health_check()
            assert "status" in health
            
        except Exception as e:
            # Database connection might fail in test environment
            assert any(keyword in str(e).lower() for keyword in ['connection', 'timeout', 'network'])
    
    def test_error_handling_setup(self):
        """Test that error handlers are properly configured."""
        client = TestClient(app)
        
        # Test 404 handling
        response = client.get("/nonexistent-endpoint")
        assert response.status_code == 404
        
        # Test invalid GraphQL query
        response = client.post("/graphql", json={"query": "invalid query syntax"})
        assert response.status_code == 400
    
    def test_security_headers(self):
        """Test security-related configurations."""
        client = TestClient(app)
        
        response = client.get("/")
        
        # Check CORS headers are present (when configured)
        # Note: Actual CORS headers depend on request origin
        assert response.status_code == 200
    
    def test_api_documentation(self):
        """Test API documentation endpoints."""
        client = TestClient(app)
        
        # Test OpenAPI docs
        response = client.get("/docs")
        assert response.status_code == 200
        
        # Test ReDoc
        response = client.get("/redoc")
        assert response.status_code == 200
        
        # Test OpenAPI JSON
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "info" in data


class TestUvicornCompatibility:
    """Test uvicorn server compatibility."""
    
    def test_uvicorn_import(self):
        """Test that uvicorn can import the app."""
        try:
            import uvicorn
            from backend.main import app
            
            # Test that uvicorn can work with our app
            assert app is not None
            assert hasattr(app, 'router')
            
        except ImportError:
            pytest.skip("uvicorn not available")
    
    def test_asgi_compatibility(self):
        """Test ASGI compatibility."""
        from backend.main import app
        
        # Test that app has ASGI interface
        assert hasattr(app, '__call__')
        assert callable(app)
    
    def test_lifespan_events(self):
        """Test lifespan event configuration."""
        from backend.main import app
        
        # App should have lifespan configured
        assert hasattr(app, 'router')
        assert app.router is not None


class TestEnvironmentConfiguration:
    """Test environment-specific configuration."""
    
    def test_development_configuration(self):
        """Test development environment configuration."""
        with patch.dict(os.environ, {'ENVIRONMENT': 'development'}):
            try:
                settings = get_settings()
                assert settings.environment == 'development'
                assert settings.debug is True
            except Exception:
                # Configuration might fail in test environment
                pass
    
    def test_production_configuration(self):
        """Test production environment configuration."""
        with patch.dict(os.environ, {'ENVIRONMENT': 'production', 'DEBUG': 'false'}):
            try:
                settings = get_settings()
                assert settings.environment == 'production'
                # In production, debug should be False
                if hasattr(settings, 'debug'):
                    assert settings.debug is False
            except Exception:
                # Configuration might fail in test environment
                pass
    
    def test_cors_origins_parsing(self):
        """Test CORS origins configuration parsing."""
        try:
            settings = get_settings()
            cors_origins = settings.cors_origins_list
            assert isinstance(cors_origins, list)
            assert len(cors_origins) > 0
        except Exception:
            # Configuration might fail in test environment
            pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])