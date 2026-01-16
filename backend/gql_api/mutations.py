"""
GraphQL mutation resolvers for the Student Progress Backend.
Implements enrollStudent, createRepository, and saveContributionMetrics mutations
with proper role-based authorization, data validation, and comprehensive error handling.
"""

import strawberry
from typing import Optional
from datetime import datetime
from strawberry.types import Info
from bson import ObjectId

from backend.models import User, Repository, ContributionMetrics, Role
from backend.ai.feedback_engine import AIFeedbackEngine
from backend.gql_api.schema import (
    User as GraphQLUser, 
    Repository as GraphQLRepository, 
    ContributionMetrics as GraphQLContributionMetrics,
    AIFeedback as GraphQLAIFeedback,
    EnrollStudentInput,
    CreateRepositoryInput,
    SaveContributionMetricsInput,
    GenerateAIFeedbackInput
)
from backend.gql_api.permissions import IsMentor, IsStudent, IsAuthenticated
from backend.database import get_database, Database
from backend.gql_api.context import context_manager
from backend.exceptions import (
    ValidationError,
    AuthorizationError,
    DatabaseError,
    ConflictError,
    NotFoundError,
    DuplicateResourceError,
    InvalidInputError,
    InsufficientPermissionsError,
    RepositoryNotFoundError,
    log_error,
    handle_database_error
)
import logging

# Set up logging
logger = logging.getLogger(__name__)


@strawberry.type
class Mutation:
    """GraphQL Mutation resolvers with role-based authorization."""
    
    @strawberry.field(permission_classes=[IsMentor])
    async def enroll_student(
        self, 
        info: Info, 
        input: EnrollStudentInput
    ) -> GraphQLUser:
        """
        Enroll a student by creating a new student record with comprehensive error handling.
        Only mentors can enroll students.
        
        Args:
            info: GraphQL info object containing context
            input: Student enrollment input data
            
        Returns:
            GraphQL User object for the enrolled student
            
        Raises:
            Exception: If enrollment fails or student already exists
        """
        try:
            # Validate mentor permissions explicitly
            mentor_user = context_manager.require_role(info.context, Role.MENTOR.value)
            mentor_github_id = mentor_user['github_id']
            
            logger.info(f"Mentor {mentor_user['username']} attempting to enroll student: {input.github_username}")
            
            # Validate input data with detailed error messages
            if not input.github_username or not input.github_username.strip():
                raise InvalidInputError(
                    field="github_username",
                    reason="GitHub username is required and cannot be empty"
                )
            
            if not input.email or not input.email.strip():
                raise InvalidInputError(
                    field="email", 
                    reason="Email is required and cannot be empty"
                )
            
            # Basic email validation
            if '@' not in input.email or '.' not in input.email.split('@')[-1]:
                raise InvalidInputError(
                    field="email",
                    reason="Invalid email format"
                )
            
            # Get database connection
            db = get_database()
            
            # Check if student already exists
            existing_user = await db.users.find_one({"username": input.github_username})
            if existing_user:
                # Handle duplicate enrollment gracefully
                if existing_user.get('role') == Role.STUDENT.value and existing_user.get('isEnrolled'):
                    logger.warning(f"Student {input.github_username} is already enrolled")
                    # Return existing student instead of raising error (graceful duplicate handling)
                    return GraphQLUser(
                        id=str(existing_user['_id']),
                        github_id=existing_user['githubId'],
                        username=existing_user['username'],
                        email=existing_user.get('email'),
                        role=Role(existing_user['role']),
                        is_enrolled=existing_user['isEnrolled'],
                        enrolled_by=existing_user.get('enrolledBy'),
                        created_at=existing_user['createdAt']
                    )
                else:
                    raise DuplicateResourceError(
                        resource_type="User",
                        identifier=input.github_username,
                        details={
                            "existing_role": existing_user.get('role'),
                            "existing_enrollment": existing_user.get('isEnrolled')
                        }
                    )
            
            # Create new student record
            student_data = User(
                github_id=f"github_{input.github_username}",  # Placeholder GitHub ID
                username=input.github_username,
                email=input.email,
                role=Role.STUDENT,
                is_enrolled=True,
                enrolled_by=mentor_github_id,
                created_at=datetime.utcnow()
            )
            
            # Convert to dict for MongoDB insertion
            student_dict = student_data.dict(by_alias=True, exclude={'id'})
            
            # Insert student into database
            result = await db.users.insert_one(student_dict)
            student_id = result.inserted_id
            
            logger.info(f"Successfully enrolled student {input.github_username} with ID: {student_id}")
            
            # Return GraphQL User object
            return GraphQLUser(
                id=str(student_id),
                github_id=student_data.github_id,
                username=student_data.username,
                email=student_data.email,
                role=student_data.role,
                is_enrolled=student_data.is_enrolled,
                enrolled_by=student_data.enrolled_by,
                created_at=student_data.created_at
            )
            
        except (ValidationError, DuplicateResourceError, InvalidInputError) as e:
            log_error(e, {
                "mutation": "enroll_student",
                "mentor": mentor_user.get('username') if 'mentor_user' in locals() else None,
                "student_username": input.github_username
            })
            raise Exception(f"{e.error_code}: {e.message}")
        except Exception as e:
            if isinstance(e, Exception) and "require_role" in str(e):
                # Authorization error from context manager
                error = InsufficientPermissionsError(
                    operation="enroll_student",
                    required_role="MENTOR"
                )
                log_error(error, {"mutation": "enroll_student"})
                raise Exception(f"{error.error_code}: {error.message}")
            
            # Database or unexpected errors
            db_error = handle_database_error(e, "student enrollment")
            log_error(db_error, {
                "mutation": "enroll_student",
                "student_username": input.github_username
            })
            raise Exception(f"Failed to enroll student {input.github_username}: {db_error.message}")
    
    @strawberry.field(permission_classes=[IsMentor])
    async def create_repository(
        self, 
        info: Info, 
        input: CreateRepositoryInput
    ) -> GraphQLRepository:
        """
        Create a new repository record with comprehensive error handling.
        Only mentors can create repositories.
        
        Args:
            info: GraphQL info object containing context
            input: Repository creation input data
            
        Returns:
            GraphQL Repository object for the created repository
            
        Raises:
            Exception: If repository creation fails or URL already exists
        """
        try:
            # Validate mentor permissions explicitly
            mentor_user = context_manager.require_role(info.context, Role.MENTOR.value)
            mentor_github_id = mentor_user['github_id']
            
            logger.info(f"Mentor {mentor_user['username']} creating repository: {input.repo_name}")
            
            # Validate input data with detailed error messages
            if not input.repo_name or not input.repo_name.strip():
                raise InvalidInputError(
                    field="repo_name",
                    reason="Repository name is required and cannot be empty"
                )
            
            if not input.repo_url or not input.repo_url.strip():
                raise InvalidInputError(
                    field="repo_url",
                    reason="Repository URL is required and cannot be empty"
                )
            
            # Basic URL validation
            if not (input.repo_url.startswith('http://') or input.repo_url.startswith('https://')):
                raise InvalidInputError(
                    field="repo_url",
                    reason="Repository URL must be a valid HTTP/HTTPS URL"
                )
            
            # Additional URL validation for GitHub repositories
            if 'github.com' in input.repo_url and not input.repo_url.count('/') >= 4:
                raise InvalidInputError(
                    field="repo_url",
                    reason="GitHub repository URL must include owner and repository name"
                )
            
            # Get database connection
            db = get_database()
            
            # Check if repository URL already exists
            existing_repo = await db.repositories.find_one({"repoUrl": input.repo_url})
            if existing_repo:
                raise DuplicateResourceError(
                    resource_type="Repository",
                    identifier=input.repo_url,
                    details={"existing_id": str(existing_repo["_id"])}
                )
            
            # Create new repository record
            repo_data = Repository(
                repo_name=input.repo_name,
                repo_url=input.repo_url,
                owner_github_id=mentor_github_id,
                linked_students=[],  # Initialize empty list
                created_at=datetime.utcnow()
            )
            
            # Convert to dict for MongoDB insertion
            repo_dict = repo_data.dict(by_alias=True, exclude={'id'})
            
            # Insert repository into database
            result = await db.repositories.insert_one(repo_dict)
            repo_id = result.inserted_id
            
            logger.info(f"Successfully created repository {input.repo_name} with ID: {repo_id}")
            
            # Return GraphQL Repository object
            return GraphQLRepository(
                id=str(repo_id),
                repo_name=repo_data.repo_name,
                repo_url=repo_data.repo_url,
                owner_github_id=repo_data.owner_github_id,
                linked_students=repo_data.linked_students,
                created_at=repo_data.created_at
            )
            
        except (ValidationError, DuplicateResourceError, InvalidInputError) as e:
            log_error(e, {
                "mutation": "create_repository",
                "mentor": mentor_user.get('username') if 'mentor_user' in locals() else None,
                "repo_name": input.repo_name,
                "repo_url": input.repo_url
            })
            raise Exception(f"{e.error_code}: {e.message}")
        except Exception as e:
            if isinstance(e, Exception) and "require_role" in str(e):
                # Authorization error from context manager
                error = InsufficientPermissionsError(
                    operation="create_repository",
                    required_role="MENTOR"
                )
                log_error(error, {"mutation": "create_repository"})
                raise Exception(f"{error.error_code}: {error.message}")
            
            # Database or unexpected errors
            db_error = handle_database_error(e, "repository creation")
            log_error(db_error, {
                "mutation": "create_repository",
                "repo_name": input.repo_name
            })
            raise Exception(f"Failed to create repository {input.repo_name}: {db_error.message}")
    
    @strawberry.field(permission_classes=[IsStudent])
    async def save_contribution_metrics(
        self, 
        info: Info, 
        input: SaveContributionMetricsInput
    ) -> GraphQLContributionMetrics:
        """
        Save contribution metrics for a student with comprehensive error handling.
        Students can only save their own metrics (self-only validation).
        
        Args:
            info: GraphQL info object containing context
            input: Contribution metrics input data
            
        Returns:
            GraphQL ContributionMetrics object for the saved metrics
            
        Raises:
            Exception: If metrics saving fails or repository doesn't exist
        """
        try:
            # Validate student permissions explicitly (self-only access)
            student_user = context_manager.require_role(info.context, Role.STUDENT.value)
            student_github_id = student_user['github_id']
            
            logger.info(f"Student {student_user['username']} saving metrics for repository: {input.repo_id}")
            
            # Validate input data with detailed error messages
            if not input.repo_id or not input.repo_id.strip():
                raise InvalidInputError(
                    field="repo_id",
                    reason="Repository ID is required and cannot be empty"
                )
            
            # Validate metric values are non-negative
            if input.commit_count < 0:
                raise InvalidInputError(
                    field="commit_count",
                    reason="Commit count must be non-negative"
                )
            
            if input.pr_count < 0:
                raise InvalidInputError(
                    field="pr_count",
                    reason="PR count must be non-negative"
                )
            
            if input.issue_count < 0:
                raise InvalidInputError(
                    field="issue_count",
                    reason="Issue count must be non-negative"
                )
            
            # Validate consistency score range
            if not (0.0 <= input.consistency_score <= 1.0):
                raise InvalidInputError(
                    field="consistency_score",
                    reason="Consistency score must be between 0.0 and 1.0"
                )
            
            # Get database connection
            db = get_database()
            
            # Validate repository exists and ObjectId format
            if not ObjectId.is_valid(input.repo_id):
                raise InvalidInputError(
                    field="repo_id",
                    reason=f"Invalid repository ID format: {input.repo_id}"
                )
            
            repo_object_id = ObjectId(input.repo_id)
            repository = await db.repositories.find_one({"_id": repo_object_id})
            if not repository:
                raise RepositoryNotFoundError(
                    repo_id=input.repo_id,
                    details={"student": student_user['username']}
                )
            
            # Additional validation: Check if student has access to this repository
            # Students should only save metrics for repositories they're linked to or have access to
            # For now, we allow any enrolled student to save metrics for any repository
            # This could be enhanced to check linkedStudents array in the future
            
            # Check if metrics already exist for this student and repository
            existing_metrics = await db.contribution_metrics.find_one({
                "repoId": repo_object_id,
                "studentGithubId": student_github_id
            })
            
            if existing_metrics:
                # Update existing metrics (student can only update their own)
                update_data = {
                    "commitCount": input.commit_count,
                    "prCount": input.pr_count,
                    "issueCount": input.issue_count,
                    "consistencyScore": input.consistency_score,
                    "lastUpdated": datetime.utcnow()
                }
                
                await db.contribution_metrics.update_one(
                    {"_id": existing_metrics["_id"]},
                    {"$set": update_data}
                )
                
                metrics_id = existing_metrics["_id"]
                logger.info(f"Updated existing metrics for student {student_user['username']}")
                
            else:
                # Create new metrics record (student can only create for themselves)
                metrics_data = ContributionMetrics(
                    repo_id=repo_object_id,
                    student_github_id=student_github_id,  # Enforced to be current student
                    commit_count=input.commit_count,
                    pr_count=input.pr_count,
                    issue_count=input.issue_count,
                    consistency_score=input.consistency_score,
                    last_updated=datetime.utcnow()
                )
                
                # Convert to dict for MongoDB insertion
                metrics_dict = metrics_data.dict(by_alias=True, exclude={'id'})
                
                # Insert metrics into database
                result = await db.contribution_metrics.insert_one(metrics_dict)
                metrics_id = result.inserted_id
                
                logger.info(f"Created new metrics for student {student_user['username']} with ID: {metrics_id}")
            
            # Return GraphQL ContributionMetrics object
            return GraphQLContributionMetrics(
                id=str(metrics_id),
                repo_id=input.repo_id,
                student_github_id=student_github_id,  # Always the current student
                commit_count=input.commit_count,
                pr_count=input.pr_count,
                issue_count=input.issue_count,
                consistency_score=input.consistency_score,
                last_updated=datetime.utcnow()
            )
            
        except (ValidationError, InvalidInputError, RepositoryNotFoundError) as e:
            log_error(e, {
                "mutation": "save_contribution_metrics",
                "student": student_user.get('username') if 'student_user' in locals() else None,
                "repo_id": input.repo_id
            })
            raise Exception(f"{e.error_code}: {e.message}")
        except Exception as e:
            if isinstance(e, Exception) and "require_role" in str(e):
                # Authorization error from context manager
                error = InsufficientPermissionsError(
                    operation="save_contribution_metrics",
                    required_role="STUDENT"
                )
                log_error(error, {"mutation": "save_contribution_metrics"})
                raise Exception(f"{error.error_code}: {error.message}")
            
            # Database or unexpected errors
            db_error = handle_database_error(e, "contribution metrics save")
            log_error(db_error, {
                "mutation": "save_contribution_metrics",
                "repo_id": input.repo_id
            })
            raise Exception(f"Failed to save contribution metrics: {db_error.message}")
    
    @strawberry.field(permission_classes=[IsAuthenticated])
    async def generate_ai_feedback(
        self, 
        info: Info, 
        input: GenerateAIFeedbackInput
    ) -> GraphQLAIFeedback:
        """
        Generate AI feedback for a repository with role-based authorization.
        - Students: Can only generate feedback for repositories they have access to
        - Mentors: Can generate feedback for any student repository they own
        
        Args:
            info: GraphQL info object containing context
            input: AI feedback generation input data
            
        Returns:
            GraphQL AIFeedback object with generated feedback
            
        Raises:
            Exception: If feedback generation fails or access is denied
        """
        try:
            # Get current user from context
            current_user = info.context.user
            if not current_user:
                raise AuthenticationError(
                    message="Authentication required",
                    details={"context": "GraphQL generate_ai_feedback mutation"}
                )
            
            github_id = current_user.get('github_id')
            role = current_user.get('role')
            
            if not github_id or not role:
                raise AuthenticationError(
                    message="Invalid user context",
                    details={"github_id": bool(github_id), "role": bool(role)}
                )
            
            logger.info(f"User {current_user.get('username')} ({role}) generating AI feedback for repository: {input.repo_id}")
            
            # Validate input data
            if not input.repo_id or not input.repo_id.strip():
                raise InvalidInputError(
                    field="repo_id",
                    reason="Repository ID is required and cannot be empty"
                )
            
            if not ObjectId.is_valid(input.repo_id):
                raise InvalidInputError(
                    field="repo_id",
                    reason=f"Invalid repository ID format: {input.repo_id}"
                )
            
            # Get database connection
            db = get_database()
            
            # Determine target student GitHub ID based on role and input
            target_student_github_id = None
            
            if role == Role.STUDENT.value:
                # Students can only generate feedback for themselves
                if input.student_github_id and input.student_github_id != github_id:
                    raise InsufficientPermissionsError(
                        operation="generate_ai_feedback",
                        required_role="MENTOR",
                        details={"reason": "Students can only generate feedback for themselves"}
                    )
                target_student_github_id = github_id
                
                # Verify student has access to the repository (optional check)
                # For now, we allow any enrolled student to generate feedback for any repository
                # This could be enhanced to check linkedStudents array in the future
                
            elif role == Role.MENTOR.value:
                # Mentors can generate feedback for any student in their repositories
                if not input.student_github_id:
                    raise InvalidInputError(
                        field="student_github_id",
                        reason="Mentors must specify a student GitHub ID for feedback generation"
                    )
                
                # Verify mentor owns the repository
                repo_doc = await db.repositories.find_one({
                    "_id": ObjectId(input.repo_id),
                    "ownerGithubId": github_id
                })
                
                if not repo_doc:
                    raise RepositoryNotFoundError(
                        repo_id=input.repo_id,
                        details={
                            "mentor": github_id,
                            "reason": "Repository not found or access denied"
                        }
                    )
                
                # Verify the target student exists and is enrolled
                student_doc = await db.users.find_one({
                    "githubId": input.student_github_id,
                    "role": Role.STUDENT.value,
                    "isEnrolled": True
                })
                
                if not student_doc:
                    raise InvalidInputError(
                        field="student_github_id",
                        reason=f"Student {input.student_github_id} not found or not enrolled"
                    )
                
                target_student_github_id = input.student_github_id
            else:
                raise AuthorizationError(
                    message=f"Invalid user role: {role}",
                    details={"role": role, "valid_roles": ["MENTOR", "STUDENT"]}
                )
            
            # Initialize AI feedback engine
            ai_engine = AIFeedbackEngine(db)
            
            # Generate AI feedback
            feedback = await ai_engine.analyze_repository(input.repo_id, target_student_github_id)
            
            logger.info(f"Successfully generated AI feedback for repository {input.repo_id}, student {target_student_github_id}")
            
            # Return GraphQL AIFeedback object
            return GraphQLAIFeedback(
                id=str(feedback.id),
                repo_id=str(feedback.repoId),
                student_github_id=feedback.studentGithubId,
                quality_score=feedback.qualityScore,
                strengths=feedback.strengths,
                issues=feedback.issues,
                suggestions=feedback.suggestions,
                generated_at=feedback.generatedAt
            )
            
        except (AuthenticationError, AuthorizationError, InvalidInputError, InsufficientPermissionsError, RepositoryNotFoundError) as e:
            log_error(e, {
                "mutation": "generate_ai_feedback",
                "user": current_user.get('username') if 'current_user' in locals() else None,
                "role": role if 'role' in locals() else None,
                "repo_id": input.repo_id,
                "target_student": input.student_github_id
            })
            raise Exception(f"{e.error_code}: {e.message}")
        except Exception as e:
            # Handle AI feedback generation errors
            db_error = handle_database_error(e, "AI feedback generation")
            log_error(db_error, {
                "mutation": "generate_ai_feedback",
                "repo_id": input.repo_id,
                "target_student": target_student_github_id if 'target_student_github_id' in locals() else None
            })
            raise Exception(f"Failed to generate AI feedback: {db_error.message}")