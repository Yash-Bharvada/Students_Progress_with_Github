"""
Tests for database connection and operations.
"""

import pytest
from backend.database import Database, DatabaseManager
from backend.models import User, Repository, ContributionMetrics, Role
from datetime import datetime
from bson import ObjectId


class TestDatabase:
    """Test database connection and operations."""
    
    @pytest.mark.asyncio
    async def test_database_connection(self, test_database: Database):
        """Test database connection and health check."""
        health = await test_database.health_check()
        assert health["status"] == "healthy"
        assert health["connected"] is True
        assert "database_name" in health
    
    @pytest.mark.asyncio
    async def test_database_collections(self, test_database: Database):
        """Test database collection accessors."""
        # Test collection properties
        assert test_database.users is not None
        assert test_database.repositories is not None
        assert test_database.contribution_metrics is not None
        assert test_database.ai_feedback is not None
    
    @pytest.mark.asyncio
    async def test_user_operations(self, clean_database: Database):
        """Test user CRUD operations."""
        db = clean_database
        
        # Create user
        user_data = {
            "githubId": "12345",
            "username": "testuser",
            "email": "test@example.com",
            "role": Role.STUDENT.value,
            "isEnrolled": True,
            "enrolledBy": "mentor123",
            "createdAt": datetime.utcnow()
        }
        
        result = await db.users.insert_one(user_data)
        assert result.inserted_id is not None
        
        # Read user
        user = await db.users.find_one({"githubId": "12345"})
        assert user is not None
        assert user["username"] == "testuser"
        assert user["role"] == Role.STUDENT.value
        
        # Update user
        await db.users.update_one(
            {"_id": user["_id"]},
            {"$set": {"email": "updated@example.com"}}
        )
        
        updated_user = await db.users.find_one({"_id": user["_id"]})
        assert updated_user["email"] == "updated@example.com"
        
        # Delete user
        await db.users.delete_one({"_id": user["_id"]})
        deleted_user = await db.users.find_one({"_id": user["_id"]})
        assert deleted_user is None
    
    @pytest.mark.asyncio
    async def test_repository_operations(self, clean_database: Database):
        """Test repository CRUD operations."""
        db = clean_database
        
        # Create repository
        repo_data = {
            "repoName": "test-repo",
            "repoUrl": "https://github.com/user/test-repo",
            "ownerGithubId": "mentor123",
            "linkedStudents": ["student1", "student2"],
            "createdAt": datetime.utcnow()
        }
        
        result = await db.repositories.insert_one(repo_data)
        assert result.inserted_id is not None
        
        # Read repository
        repo = await db.repositories.find_one({"repoName": "test-repo"})
        assert repo is not None
        assert repo["ownerGithubId"] == "mentor123"
        assert len(repo["linkedStudents"]) == 2
    
    @pytest.mark.asyncio
    async def test_contribution_metrics_operations(self, clean_database: Database):
        """Test contribution metrics CRUD operations."""
        db = clean_database
        
        # First create a repository to reference
        repo_result = await db.repositories.insert_one({
            "repoName": "test-repo",
            "repoUrl": "https://github.com/user/test-repo",
            "ownerGithubId": "mentor123",
            "linkedStudents": [],
            "createdAt": datetime.utcnow()
        })
        repo_id = repo_result.inserted_id
        
        # Create contribution metrics
        metrics_data = {
            "repoId": repo_id,
            "studentGithubId": "student123",
            "commitCount": 25,
            "prCount": 5,
            "issueCount": 3,
            "consistencyScore": 0.85,
            "lastUpdated": datetime.utcnow()
        }
        
        result = await db.contribution_metrics.insert_one(metrics_data)
        assert result.inserted_id is not None
        
        # Read metrics
        metrics = await db.contribution_metrics.find_one({"studentGithubId": "student123"})
        assert metrics is not None
        assert metrics["commitCount"] == 25
        assert metrics["consistencyScore"] == 0.85
    
    @pytest.mark.asyncio
    async def test_database_manager_context(self):
        """Test DatabaseManager context manager."""
        async with DatabaseManager() as db:
            assert db is not None
            health = await db.health_check()
            assert health["status"] == "healthy"