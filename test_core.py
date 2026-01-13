#!/usr/bin/env python3
"""
Simple test script to verify core functionality.
"""

def test_configuration():
    """Test configuration loading."""
    print("Testing configuration...")
    from backend.config import get_settings, validate_configuration
    
    settings = get_settings()
    print(f"✓ MongoDB: {settings.mongodb_connection_string[:20]}...")
    print(f"✓ GitHub OAuth: {settings.github_client_id[:10]}...")
    print(f"✓ JWT Secret: {len(settings.jwt_secret_key)} chars")
    
    validate_configuration()
    print("✓ Configuration validation passed")


def test_jwt_functionality():
    """Test JWT token creation and validation."""
    print("\nTesting JWT functionality...")
    from backend.auth.jwt_handler import JWTHandler
    from backend.models import Role
    
    jwt_handler = JWTHandler()
    user_data = {
        "github_id": "12345",
        "username": "testuser",
        "email": "test@example.com",
        "role": Role.STUDENT.value
    }
    
    # Create token
    token = jwt_handler.create_token(user_data)
    print(f"✓ JWT token created: {token[:20]}...")
    
    # Verify token
    payload = jwt_handler.verify_token(token)
    print(f"✓ JWT token verified: {payload['username']}")
    
    # Extract user
    extracted_user = jwt_handler.extract_user_from_token(token)
    print(f"✓ User extracted: {extracted_user['username']}")


def test_github_oauth():
    """Test GitHub OAuth URL generation."""
    print("\nTesting GitHub OAuth...")
    from backend.auth.github_oauth import GitHubOAuth
    
    github_oauth = GitHubOAuth()
    auth_url = github_oauth.get_authorization_url()
    print(f"✓ OAuth URL generated: {auth_url[:50]}...")
    
    # Test with state
    auth_url_with_state = github_oauth.get_authorization_url(state="test123")
    print("✓ OAuth URL with state generated")


def test_database_connection():
    """Test database connection."""
    print("\nTesting database connection...")
    import asyncio
    from backend.database import DatabaseManager
    
    async def test_db():
        try:
            async with DatabaseManager() as db:
                health = await db.health_check()
                print(f"✓ Database connection: {health['status']}")
                print(f"✓ Database name: {health.get('database_name', 'unknown')}")
                return True
        except Exception as e:
            print(f"✗ Database connection failed: {str(e)}")
            return False
    
    return asyncio.run(test_db())


def test_models():
    """Test data models."""
    print("\nTesting data models...")
    from backend.models import Role
    
    # Test Role enum
    assert Role.MENTOR.value == "MENTOR"
    assert Role.STUDENT.value == "STUDENT"
    print("✓ Role enum working")
    
    # Test model imports
    from backend.models import User, Repository, ContributionMetrics, AIFeedback
    print("✓ All models imported successfully")


def main():
    """Run all tests."""
    print("🧪 Running core functionality tests...\n")
    
    try:
        test_configuration()
        test_jwt_functionality()
        test_github_oauth()
        test_models()
        
        # Test database connection (may fail if MongoDB not available)
        db_success = test_database_connection()
        
        print("\n" + "="*50)
        if db_success:
            print("✅ All core functionality tests passed!")
        else:
            print("⚠️  Core functionality tests passed (database connection issue)")
        print("="*50)
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()