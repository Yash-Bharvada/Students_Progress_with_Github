"""
Configuration management with environment variable validation.
Loads and validates all required configuration on startup.
"""

import os
from typing import Optional
from pydantic import field_validator, Field, ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable validation."""
    
    # Database Configuration
    mongodb_connection_string: str
    
    # GitHub OAuth Configuration
    github_client_id: str
    github_client_secret: str
    github_redirect_uri: str
    
    # JWT Configuration
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    
    # AI/LLM Service Configuration
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4"
    
    # Google Gemini API Configuration
    gemini_api_key: Optional[str] = None
    gemini_model: str = "gemini-1.5-flash"
    gemini_temperature: float = 0.3
    gemini_max_output_tokens: int = 1024
    
    # AWS Bedrock Configuration (Alternative to OpenAI)
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_region: str = "us-east-1"
    bedrock_model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0"
    
    # Application Configuration
    environment: str = "development"
    debug: bool = True
    cors_origins: str = "http://localhost:3000,http://localhost:3001"
    frontend_url: Optional[str] = None  # Frontend URL for OAuth redirects
    
    # GitHub API Configuration (for repository analysis)
    github_api_token: str
    
    # Logging Configuration
    log_level: str = "INFO"
    
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )
    
    @field_validator('mongodb_connection_string')
    @classmethod
    def validate_mongodb_connection(cls, v):
        """Validate MongoDB connection string format."""
        if not v:
            raise ValueError("MongoDB connection string is required")
        if not v.startswith(('mongodb://', 'mongodb+srv://')):
            raise ValueError("MongoDB connection string must start with mongodb:// or mongodb+srv://")
        return v
    
    @field_validator('github_client_id', 'github_client_secret', 'github_redirect_uri')
    @classmethod
    def validate_github_oauth(cls, v):
        """Validate GitHub OAuth configuration."""
        if not v:
            raise ValueError("GitHub OAuth configuration is required")
        return v
    
    @field_validator('jwt_secret_key')
    @classmethod
    def validate_jwt_secret(cls, v):
        """Validate JWT secret key strength."""
        if not v:
            raise ValueError("JWT secret key is required")
        if len(v) < 32:
            raise ValueError("JWT secret key must be at least 32 characters long")
        return v
    
    @field_validator('github_api_token')
    @classmethod
    def validate_github_api_token(cls, v):
        """Validate GitHub API token."""
        if not v:
            raise ValueError("GitHub API token is required for repository analysis")
        return v
    
    @field_validator('gemini_api_key')
    @classmethod
    def validate_gemini_api_key(cls, v):
        """Validate Gemini API key is set and not a placeholder."""
        if v and v in ['your_gemini_api_key_here', 'your_gemini_api_key']:
            raise ValueError(
                "GEMINI_API_KEY must be set to a valid API key, not a placeholder. "
                "Get your API key from: https://makersuite.google.com/app/apikey"
            )
        return v
    
    def validate_llm_configuration(self) -> None:
        """Validate that at least one LLM service is configured."""
        has_openai = bool(self.openai_api_key)
        has_bedrock = bool(self.aws_access_key_id and self.aws_secret_access_key)
        has_gemini = bool(self.gemini_api_key)
        
        if not has_openai and not has_bedrock and not has_gemini:
            raise ValueError(
                "At least one LLM service must be configured: "
                "either OpenAI (OPENAI_API_KEY), AWS Bedrock (AWS_ACCESS_KEY_ID + AWS_SECRET_ACCESS_KEY), "
                "or Google Gemini (GEMINI_API_KEY)"
            )
    
    @property
    def cors_origins_list(self) -> list[str]:
        """Convert CORS origins string to list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"


# Global settings instance
settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get application settings singleton."""
    global settings
    if settings is None:
        settings = Settings()
        # Validate LLM configuration after initialization
        settings.validate_llm_configuration()
    return settings


def validate_configuration() -> None:
    """
    Validate all required configuration on startup.
    Raises ValueError if any required configuration is missing or invalid.
    """
    try:
        settings = get_settings()
        print(f"✓ Configuration loaded successfully for environment: {settings.environment}")
        print(f"✓ Database: {settings.mongodb_connection_string.split('@')[1] if '@' in settings.mongodb_connection_string else 'Local MongoDB'}")
        print(f"✓ GitHub OAuth: Client ID configured")
        print(f"✓ JWT: Secret key configured ({len(settings.jwt_secret_key)} characters)")
        
        # Check LLM configuration
        if settings.openai_api_key:
            print(f"✓ OpenAI: API key configured, model: {settings.openai_model}")
        if settings.aws_access_key_id and settings.aws_secret_access_key:
            print(f"✓ AWS Bedrock: Credentials configured, region: {settings.aws_region}")
        if settings.gemini_api_key:
            print(f"✓ Google Gemini: API key configured, model: {settings.gemini_model}")
        
        print(f"✓ GitHub API: Token configured")
        print(f"✓ CORS Origins: {settings.cors_origins_list}")
        
    except Exception as e:
        print(f"❌ Configuration validation failed: {e}")
        raise


if __name__ == "__main__":
    # Test configuration validation
    validate_configuration()