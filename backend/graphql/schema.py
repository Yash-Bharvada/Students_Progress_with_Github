"""
GraphQL schema and type definitions using Strawberry GraphQL.
Defines GraphQL types for User, Repository, ContributionMetrics, and AIFeedback.
"""

import strawberry
from datetime import datetime
from typing import Optional, List
from enum import Enum
from backend.graphql.context import get_context


@strawberry.enum
class Role(Enum):
    """User roles in the system."""
    MENTOR = "MENTOR"
    STUDENT = "STUDENT"


@strawberry.type
class User:
    """GraphQL User type."""
    
    id: str = strawberry.field(description="User ID")
    github_id: str = strawberry.field(description="GitHub user ID")
    username: str = strawberry.field(description="GitHub username")
    email: Optional[str] = strawberry.field(description="User email address")
    role: Role = strawberry.field(description="User role (MENTOR or STUDENT)")
    is_enrolled: bool = strawberry.field(description="Whether student is enrolled")
    enrolled_by: Optional[str] = strawberry.field(description="GitHub ID of enrolling mentor")
    created_at: datetime = strawberry.field(description="Account creation timestamp")


@strawberry.type
class Repository:
    """GraphQL Repository type."""
    
    id: str = strawberry.field(description="Repository ID")
    repo_name: str = strawberry.field(description="Repository name")
    repo_url: str = strawberry.field(description="Repository URL")
    owner_github_id: str = strawberry.field(description="Repository owner's GitHub ID")
    linked_students: List[str] = strawberry.field(description="List of linked student GitHub IDs")
    created_at: datetime = strawberry.field(description="Repository creation timestamp")


@strawberry.type
class ContributionMetrics:
    """GraphQL ContributionMetrics type."""
    
    id: str = strawberry.field(description="Metrics ID")
    repo_id: str = strawberry.field(description="Repository ID")
    student_github_id: str = strawberry.field(description="Student's GitHub ID")
    commit_count: int = strawberry.field(description="Number of commits")
    pr_count: int = strawberry.field(description="Number of pull requests")
    issue_count: int = strawberry.field(description="Number of issues")
    consistency_score: float = strawberry.field(description="Consistency score (0.0-1.0)")
    last_updated: datetime = strawberry.field(description="Last update timestamp")


@strawberry.type
class AIFeedback:
    """GraphQL AIFeedback type."""
    
    id: str = strawberry.field(description="Feedback ID")
    repo_id: str = strawberry.field(description="Repository ID")
    student_github_id: str = strawberry.field(description="Student's GitHub ID")
    quality_score: float = strawberry.field(description="Code quality score (0.0-10.0)")
    strengths: List[str] = strawberry.field(description="List of identified strengths")
    issues: List[str] = strawberry.field(description="List of identified issues")
    suggestions: List[str] = strawberry.field(description="List of improvement suggestions")
    generated_at: datetime = strawberry.field(description="Feedback generation timestamp")


# Input types for mutations
@strawberry.input
class EnrollStudentInput:
    """Input type for enrolling a student."""
    github_username: str = strawberry.field(description="Student's GitHub username")
    email: str = strawberry.field(description="Student's email address")


@strawberry.input
class CreateRepositoryInput:
    """Input type for creating a repository."""
    repo_name: str = strawberry.field(description="Repository name")
    repo_url: str = strawberry.field(description="Repository URL")


@strawberry.input
class SaveContributionMetricsInput:
    """Input type for saving contribution metrics."""
    repo_id: str = strawberry.field(description="Repository ID")
    commit_count: int = strawberry.field(description="Number of commits")
    pr_count: int = strawberry.field(description="Number of pull requests")
    issue_count: int = strawberry.field(description="Number of issues")
    consistency_score: float = strawberry.field(description="Consistency score (0.0-1.0)")


@strawberry.input
class GenerateAIFeedbackInput:
    """Input type for generating AI feedback."""
    repo_id: str = strawberry.field(description="Repository ID")
    student_github_id: Optional[str] = strawberry.field(
        description="Student's GitHub ID (optional, defaults to current user for students)",
        default=None
    )


# Import actual Query and Mutation classes
from backend.graphql.queries import Query
from backend.graphql.mutations import Mutation


# Create the GraphQL schema
schema = strawberry.Schema(
    query=Query, 
    mutation=Mutation
)