"""
Tests for GraphQL schema, queries, and mutations.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from backend.graphql.queries import Query
from backend.graphql.mutations import Mutation
from backend.graphql.permissions import IsAuthenticated, IsMentor, IsStudent
from backend.models import Role
from datetime import datetime
from bson import ObjectId


class MockInfo:
    """Mock GraphQL Info object for testing."""
    
    def __init__(self, user_data=None):
        self.context = MagicMock()
        self.context.user = user_data


class TestGraphQLPermissions:
    """Test GraphQL permission classes."""
    
    def test_is_authenticated_with_user(self):
        """Test IsAuthenticated permission with valid user."""
        permission = IsAuthenticated()
        info = MockInfo(user_data={"github_id": "123", "role": "STUDENT"})
        
        assert permission.has_permission(None, info) is True
    
    def test_is_authenticated_without_user(self):
        """Test IsAuthenticated permission without user."""
        permission = IsAuthenticated()
        info = MockInfo(user_data=None)
        
        assert permission.has_permission(None, info) is False
    
    def test_is_mentor_with_mentor_user(self):
        """Test IsMentor permission with mentor user."""
        permission = IsMentor()
        info = MockInfo(user_data={"github_id": "123", "role": Role.MENTOR.value})
        
        assert permission.has_permission(None, info) is True
    
    def test_is_mentor_with_student_user(self):
        """Test IsMentor permission with student user."""
        permission = IsMentor()
        info = MockInfo(user_data={"github_id": "123", "role": Role.STUDENT.value})
        
        assert permission.has_permission(None, info) is False
    
    def test_is_student_with_student_user(self):
        """Test IsStudent permission with student user."""
        permission = IsStudent()
        info = MockInfo(user_data={"github_id": "123", "role": Role.STUDENT.value})
        
        assert permission.has_permission(None, info) is True
    
    def test_is_student_with_mentor_user(self):
        """Test IsStudent permission with mentor user."""
        permission = IsStudent()
        info = MockInfo(user_data={"github_id": "123", "role": Role.MENTOR.value})
        
        assert permission.has_permission(None, info) is False


class TestGraphQLQueries:
    """Test GraphQL query resolvers."""
    
    @pytest.mark.asyncio
    async def test_get_me_success(self, clean_database):
        """Test successful getMe query."""
        # Insert test user
        user_doc = {
            "_id": ObjectId(),
            "githubId": "12345",
            "username": "testuser",
            "email": "test@example.com",
            "role": Role.STUDENT.value,
            "isEnrolled": True,
            "createdAt": datetime.utcnow()
        }
        await clean_database.users.insert_one(user_doc)
        
        # Mock info with user context
        info = MockInfo(user_data={"github_id": "12345"})
        
        # Mock get_database to return our test database
        with pytest.mock.patch('backend.graphql.queries.get_database', return_value=clean_database):
            query = Query()
            result = await query.get_me(info)
            
            assert result.github_id == "12345"
            assert result.username == "testuser"
            assert result.role == Role.STUDENT
    
    @pytest.mark.asyncio
    async def test_get_me_no_user_context(self):
        """Test getMe query without user context."""
        info = MockInfo(user_data=None)
        
        query = Query()
        with pytest.raises(Exception, match="Authentication required"):
            await query.get_me(info)
    
    @pytest.mark.asyncio
    async def test_get_repositories_mentor(self, clean_database):
        """Test getRepositories query for mentor."""
        # Insert test repositories
        repo1 = {
            "_id": ObjectId(),
            "repoName": "repo1",
            "repoUrl": "https://github.com/mentor/repo1",
            "ownerGithubId": "mentor123",
            "linkedStudents": [],
            "createdAt": datetime.utcnow()
        }
        repo2 = {
            "_id": ObjectId(),
            "repoName": "repo2",
            "repoUrl": "https://github.com/mentor/repo2",
            "ownerGithubId": "mentor123",
            "linkedStudents": [],
            "createdAt": datetime.utcnow()
        }
        await clean_database.repositories.insert_many([repo1, repo2])
        
        # Mock mentor user context
        info = MockInfo(user_data={"github_id": "mentor123", "role": Role.MENTOR.value})
        
        with pytest.mock.patch('backend.graphql.queries.get_database', return_value=clean_database):
            query = Query()
            results = await query.get_repositories(info)
            
            assert len(results) == 2
            assert all(repo.owner_github_id == "mentor123" for repo in results)
    
    @pytest.mark.asyncio
    async def test_get_repositories_student(self, clean_database):
        """Test getRepositories query for student."""
        # Insert test repository with student linked
        repo = {
            "_id": ObjectId(),
            "repoName": "student-repo",
            "repoUrl": "https://github.com/mentor/student-repo",
            "ownerGithubId": "mentor123",
            "linkedStudents": ["student123"],
            "createdAt": datetime.utcnow()
        }
        await clean_database.repositories.insert_one(repo)
        
        # Mock student user context
        info = MockInfo(user_data={"github_id": "student123", "role": Role.STUDENT.value})
        
        with pytest.mock.patch('backend.graphql.queries.get_database', return_value=clean_database):
            query = Query()
            results = await query.get_repositories(info)
            
            assert len(results) == 1
            assert "student123" in results[0].linked_students


class TestGraphQLMutations:
    """Test GraphQL mutation resolvers."""
    
    @pytest.mark.asyncio
    async def test_enroll_student_success(self, clean_database):
        """Test successful student enrollment."""
        from backend.graphql.schema import EnrollStudentInput
        from backend.graphql.context import context_manager
        
        # Mock mentor context
        info = MockInfo(user_data={"github_id": "mentor123", "username": "mentor", "role": Role.MENTOR.value})
        
        # Mock context manager
        with pytest.mock.patch.object(context_manager, 'require_role', return_value=info.context.user):
            with pytest.mock.patch('backend.graphql.mutations.get_database', return_value=clean_database):
                mutation = Mutation()
                input_data = EnrollStudentInput(
                    github_username="newstudent",
                    email="student@example.com"
                )
                
                result = await mutation.enroll_student(info, input_data)
                
                assert result.username == "newstudent"
                assert result.role == Role.STUDENT
                assert result.is_enrolled is True
                assert result.enrolled_by == "mentor123"
    
    @pytest.mark.asyncio
    async def test_create_repository_success(self, clean_database):
        """Test successful repository creation."""
        from backend.graphql.schema import CreateRepositoryInput
        from backend.graphql.context import context_manager
        
        # Mock mentor context
        info = MockInfo(user_data={"github_id": "mentor123", "username": "mentor", "role": Role.MENTOR.value})
        
        with pytest.mock.patch.object(context_manager, 'require_role', return_value=info.context.user):
            with pytest.mock.patch('backend.graphql.mutations.get_database', return_value=clean_database):
                mutation = Mutation()
                input_data = CreateRepositoryInput(
                    repo_name="test-repo",
                    repo_url="https://github.com/mentor/test-repo"
                )
                
                result = await mutation.create_repository(info, input_data)
                
                assert result.repo_name == "test-repo"
                assert result.owner_github_id == "mentor123"
                assert result.linked_students == []
    
    @pytest.mark.asyncio
    async def test_save_contribution_metrics_success(self, clean_database):
        """Test successful contribution metrics saving."""
        from backend.graphql.schema import SaveContributionMetricsInput
        from backend.graphql.context import context_manager
        
        # First create a repository
        repo_id = ObjectId()
        repo = {
            "_id": repo_id,
            "repoName": "test-repo",
            "repoUrl": "https://github.com/mentor/test-repo",
            "ownerGithubId": "mentor123",
            "linkedStudents": [],
            "createdAt": datetime.utcnow()
        }
        await clean_database.repositories.insert_one(repo)
        
        # Mock student context
        info = MockInfo(user_data={"github_id": "student123", "username": "student", "role": Role.STUDENT.value})
        
        with pytest.mock.patch.object(context_manager, 'require_role', return_value=info.context.user):
            with pytest.mock.patch('backend.graphql.mutations.get_database', return_value=clean_database):
                mutation = Mutation()
                input_data = SaveContributionMetricsInput(
                    repo_id=str(repo_id),
                    commit_count=25,
                    pr_count=5,
                    issue_count=3,
                    consistency_score=0.85
                )
                
                result = await mutation.save_contribution_metrics(info, input_data)
                
                assert result.student_github_id == "student123"
                assert result.commit_count == 25
                assert result.consistency_score == 0.85