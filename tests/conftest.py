"""
Pytest configuration and fixtures for the Student Progress Backend tests.
"""

import pytest
import asyncio
from typing import AsyncGenerator
from backend.database import Database
from backend.config import get_settings


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_database() -> AsyncGenerator[Database, None]:
    """Create a test database connection."""
    # Use test database
    settings = get_settings()
    test_connection_string = settings.mongodb_connection_string.replace(
        "student_progress", "student_progress_test"
    )
    
    db = Database(test_connection_string)
    await db.connect()
    
    yield db
    
    # Cleanup: Drop test database
    await db.client.drop_database("student_progress_test")
    await db.disconnect()


@pytest.fixture
async def clean_database(test_database: Database):
    """Clean database before each test."""
    # Clear all collections
    await test_database.users.delete_many({})
    await test_database.repositories.delete_many({})
    await test_database.contribution_metrics.delete_many({})
    await test_database.ai_feedback.delete_many({})
    
    yield test_database