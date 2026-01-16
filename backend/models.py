"""
Pydantic data models for the Student Progress Backend.
Defines data structures for users, repositories, metrics, and AI feedback.
"""

from datetime import datetime
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field, validator
from bson import ObjectId


class PyObjectId(ObjectId):
    """Custom ObjectId type for Pydantic models."""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v, handler=None):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)
    
    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")
        return field_schema


class Role(str, Enum):
    """User roles in the system."""
    MENTOR = "MENTOR"
    STUDENT = "STUDENT"


class SkillTag(BaseModel):
    """Technical skill tag with confidence and evidence."""
    
    name: str = Field(..., description="Technical skill name (e.g., 'FastAPI')")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score 0-1")
    evidence_file: str = Field(..., description="File path where skill was detected")
    
    class Config:
        populate_by_name = True


class UserSkillProfile(BaseModel):
    """User skill profile with verified skills and semantic embedding."""
    
    verified_skills: List[SkillTag] = Field(default_factory=list, description="List of verified technical skills")
    skill_embedding: Optional[List[float]] = Field(
        default=None,
        description="384-dimensional SentenceTransformers embedding vector"
    )
    last_scanned: Optional[datetime] = Field(default=None, description="Timestamp of last repository scan")
    
    @validator('skill_embedding')
    def validate_embedding_dimensions(cls, v):
        """Validate that embedding has exactly 384 dimensions."""
        if v is not None and len(v) != 384:
            raise ValueError("Embedding must be exactly 384 dimensions")
        return v
    
    class Config:
        populate_by_name = True


class User(BaseModel):
    """User data model."""
    
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    github_id: str = Field(..., description="GitHub user ID", alias="githubId")
    username: str = Field(..., description="GitHub username")
    email: Optional[str] = Field(None, description="User email address")
    role: Role = Field(..., description="User role (MENTOR or STUDENT)")
    is_enrolled: bool = Field(default=False, description="Whether student is enrolled", alias="isEnrolled")
    enrolled_by: Optional[str] = Field(None, description="GitHub ID of enrolling mentor", alias="enrolledBy")
    github_access_token: Optional[str] = Field(None, description="GitHub OAuth access token")
    created_at: datetime = Field(default_factory=datetime.utcnow, alias="createdAt")
    updated_at: datetime = Field(default_factory=datetime.utcnow, alias="updatedAt")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp", alias="lastLogin")
    skill_profile: Optional[UserSkillProfile] = Field(None, description="User skill profile with verified skills and embedding")
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class Repository(BaseModel):
    """Repository data model."""
    
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    repo_name: str = Field(..., description="Repository name", alias="repoName")
    repo_url: str = Field(..., description="Repository URL", alias="repoUrl")
    owner_github_id: str = Field(..., description="Repository owner's GitHub ID", alias="ownerGithubId")
    linked_students: List[str] = Field(default_factory=list, description="List of linked student GitHub IDs", alias="linkedStudents")
    created_at: datetime = Field(default_factory=datetime.utcnow, alias="createdAt")
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class ContributionMetrics(BaseModel):
    """Contribution metrics data model."""
    
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    repo_id: PyObjectId = Field(..., description="Repository ObjectId", alias="repoId")
    student_github_id: str = Field(..., description="Student's GitHub ID", alias="studentGithubId")
    commit_count: int = Field(default=0, description="Number of commits", alias="commitCount")
    pr_count: int = Field(default=0, description="Number of pull requests", alias="prCount")
    issue_count: int = Field(default=0, description="Number of issues", alias="issueCount")
    consistency_score: float = Field(default=0.0, description="Consistency score (0.0-1.0)", alias="consistencyScore")
    last_updated: datetime = Field(default_factory=datetime.utcnow, alias="lastUpdated")
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class AIFeedback(BaseModel):
    """AI feedback data model."""
    
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    repo_id: PyObjectId = Field(..., description="Repository ObjectId", alias="repoId")
    student_github_id: str = Field(..., description="Student's GitHub ID", alias="studentGithubId")
    quality_score: float = Field(..., description="Code quality score (0.0-10.0)", alias="qualityScore")
    strengths: List[str] = Field(default_factory=list, description="List of identified strengths")
    issues: List[str] = Field(default_factory=list, description="List of identified issues")
    suggestions: List[str] = Field(default_factory=list, description="List of improvement suggestions")
    generated_at: datetime = Field(default_factory=datetime.utcnow, alias="generatedAt")
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}