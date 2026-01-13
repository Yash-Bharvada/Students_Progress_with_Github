"""
Tests for configuration management and validation.
"""

import pytest
from backend.config import Settings, get_settings, validate_configuration


class TestConfiguration:
    """Test configuration loading and validation."""
    
    def test_settings_loading(self):
        """Test that settings load successfully."""
        settings = get_settings()
        assert settings is not None
        assert settings.mongodb_connection_string
        assert settings.github_client_id
        assert settings.jwt_secret_key
    
    def test_mongodb_connection_validation(self):
        """Test MongoDB connection string validation."""
        # Valid connection strings should pass
        valid_strings = [
            "mongodb://localhost:27017/test",
            "mongodb+srv://user:pass@cluster.mongodb.net/db"
        ]
        
        for conn_str in valid_strings:
            # This should not raise an exception
            Settings.validate_mongodb_connection(conn_str)
    
    def test_jwt_secret_validation(self):
        """Test JWT secret key validation."""
        # Valid secret (32+ characters)
        valid_secret = "a" * 32
        Settings.validate_jwt_secret(valid_secret)
        
        # Invalid secret (too short)
        with pytest.raises(ValueError, match="at least 32 characters"):
            Settings.validate_jwt_secret("short")
    
    def test_configuration_validation(self):
        """Test complete configuration validation."""
        # This should not raise an exception with current .env
        validate_configuration()