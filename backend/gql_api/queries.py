"""
GraphQL query resolvers for the Student Progress Backend.
Implements getMe, getRepositories, getMyContributionMetrics, and getAllContributionMetrics queries
with proper role-based authorization, data filtering, and comprehensive error handling.
"""

from typing import List, Optional
import strawberry
from strawberry.types import Info
from bson import ObjectId
from backend.gql_api.schema import User, Repository, ContributionMetrics, AIFeedback, Role, SkillTag, CandidateResult
from backend.gql_api.permissions import IsAuthenticated, IsMentor, IsStudent
from backend.database import get_database
from backend.services.recommendation import RecommendationService
from backend.models import Role as ModelRole
from backend.exceptions import (
    AuthenticationError,
    AuthorizationError,
    DatabaseError,
    NotFoundError,
    ValidationError,
    InvalidInputError,
    InsufficientPermissionsError,
    RepositoryNotFoundError,
    UserNotFoundError,
    log_error,
    handle_database_error
)
import logging

# Set up logging
logger = logging.getLogger(__name__)


@strawberry.type
class Query:
    """GraphQL Query type with all query resolvers."""
    
    @strawberry.field(permission_classes=[IsAuthenticated])
    async def get_me(self, info: Info) -> User:
        """
        Get current user profile information with comprehensive error handling.
        
        Returns:
            Current user's profile data
            
        Raises:
            Exception: If user is not authenticated or not found in database
        """
        try:
            # Get current user from context
            current_user = info.context.user
            if not current_user:
                raise AuthenticationError(
                    message="Authentication required",
                    details={"context": "GraphQL get_me query"}
                )
            
            github_id = current_user.get('github_id')
            if not github_id:
                raise AuthenticationError(
                    message="Invalid user context: missing github_id",
                    details={"user_context": current_user}
                )
            
            logger.debug(f"Getting profile for user: {github_id}")
            
            # Get database connection
            db = get_database()
            
            # Find user in database
            user_doc = await db.users.find_one({"githubId": github_id})
            if not user_doc:
                raise UserNotFoundError(
                    identifier=github_id,
                    details={"context": "get_me query"}
                )
            
            logger.debug(f"Successfully retrieved user profile: {user_doc['username']}")
            
            # Convert to GraphQL User type
            return User(
                id=str(user_doc["_id"]),
                github_id=user_doc["githubId"],
                username=user_doc["username"],
                email=user_doc.get("email"),
                role=Role(user_doc["role"]),
                is_enrolled=user_doc.get("isEnrolled", False),
                enrolled_by=user_doc.get("enrolledBy"),
                created_at=user_doc["createdAt"]
            )
            
        except (AuthenticationError, UserNotFoundError) as e:
            log_error(e, {"query": "get_me", "github_id": github_id if 'github_id' in locals() else None})
            raise Exception(f"{e.error_code}: {e.message}")
        except Exception as e:
            db_error = handle_database_error(e, "user profile retrieval")
            log_error(db_error, {"query": "get_me"})
            raise Exception(f"Failed to get user profile: {db_error.message}")
    
    @strawberry.field(permission_classes=[IsAuthenticated])
    async def get_repositories(self, info: Info) -> List[Repository]:
        """
        Get repositories based on user role and permissions with comprehensive error handling.
        - Mentors: Get all repositories they own
        - Students: Get repositories they are linked to
        
        Returns:
            List of repositories accessible to the current user
            
        Raises:
            Exception: If user is not authenticated or database error occurs
        """
        try:
            # Get current user from context
            current_user = info.context.user
            if not current_user:
                raise AuthenticationError(
                    message="Authentication required",
                    details={"context": "GraphQL get_repositories query"}
                )
            
            github_id = current_user.get('github_id')
            role = current_user.get('role')
            
            if not github_id or not role:
                raise AuthenticationError(
                    message="Invalid user context",
                    details={"github_id": bool(github_id), "role": bool(role)}
                )
            
            logger.debug(f"Getting repositories for user: {github_id} ({role})")
            
            # Get database connection
            db = get_database()
            
            repositories = []
            
            if role == ModelRole.MENTOR.value:
                # Mentors get all repositories they own
                cursor = db.repositories.find({"ownerGithubId": github_id})
                async for repo_doc in cursor:
                    repositories.append(Repository(
                        id=str(repo_doc["_id"]),
                        repo_name=repo_doc["repoName"],
                        repo_url=repo_doc["repoUrl"],
                        owner_github_id=repo_doc["ownerGithubId"],
                        linked_students=repo_doc.get("linkedStudents", []),
                        created_at=repo_doc["createdAt"]
                    ))
            
            elif role == ModelRole.STUDENT.value:
                # Students get repositories they are linked to
                cursor = db.repositories.find({"linkedStudents": github_id})
                async for repo_doc in cursor:
                    repositories.append(Repository(
                        id=str(repo_doc["_id"]),
                        repo_name=repo_doc["repoName"],
                        repo_url=repo_doc["repoUrl"],
                        owner_github_id=repo_doc["ownerGithubId"],
                        linked_students=repo_doc.get("linkedStudents", []),
                        created_at=repo_doc["createdAt"]
                    ))
            else:
                raise AuthorizationError(
                    message=f"Invalid user role: {role}",
                    details={"role": role, "valid_roles": ["MENTOR", "STUDENT"]}
                )
            
            logger.info(f"Retrieved {len(repositories)} repositories for user {github_id} ({role})")
            return repositories
            
        except (AuthenticationError, AuthorizationError) as e:
            log_error(e, {
                "query": "get_repositories",
                "github_id": github_id if 'github_id' in locals() else None,
                "role": role if 'role' in locals() else None
            })
            raise Exception(f"{e.error_code}: {e.message}")
        except Exception as e:
            db_error = handle_database_error(e, "repository retrieval")
            log_error(db_error, {"query": "get_repositories"})
            raise Exception(f"Failed to get repositories: {db_error.message}")
    
    @strawberry.field(permission_classes=[IsStudent])
    async def get_my_contribution_metrics(self, info: Info) -> List[ContributionMetrics]:
        """
        Get contribution metrics for the current student with comprehensive error handling.
        Only students can access this query and only their own metrics.
        
        Returns:
            List of contribution metrics for the current student
            
        Raises:
            Exception: If user is not a student or database error occurs
        """
        try:
            # Get current user from context
            current_user = info.context.user
            if not current_user:
                raise AuthenticationError(
                    message="Authentication required",
                    details={"context": "GraphQL get_my_contribution_metrics query"}
                )
            
            github_id = current_user.get('github_id')
            role = current_user.get('role')
            
            if not github_id:
                raise AuthenticationError(
                    message="Invalid user context: missing github_id",
                    details={"user_context": current_user}
                )
            
            if role != ModelRole.STUDENT.value:
                raise InsufficientPermissionsError(
                    operation="get_my_contribution_metrics",
                    required_role="STUDENT",
                    details={"current_role": role}
                )
            
            logger.debug(f"Getting contribution metrics for student: {github_id}")
            
            # Get database connection
            db = get_database()
            
            # Find all contribution metrics for this student
            metrics = []
            cursor = db.contribution_metrics.find({"studentGithubId": github_id})
            
            async for metrics_doc in cursor:
                metrics.append(ContributionMetrics(
                    id=str(metrics_doc["_id"]),
                    repo_id=str(metrics_doc["repoId"]),
                    student_github_id=metrics_doc["studentGithubId"],
                    commit_count=metrics_doc.get("commitCount", 0),
                    pr_count=metrics_doc.get("prCount", 0),
                    issue_count=metrics_doc.get("issueCount", 0),
                    consistency_score=metrics_doc.get("consistencyScore", 0.0),
                    last_updated=metrics_doc["lastUpdated"]
                ))
            
            logger.info(f"Retrieved {len(metrics)} contribution metrics for student {github_id}")
            return metrics
            
        except (AuthenticationError, InsufficientPermissionsError) as e:
            log_error(e, {
                "query": "get_my_contribution_metrics",
                "github_id": github_id if 'github_id' in locals() else None,
                "role": role if 'role' in locals() else None
            })
            raise Exception(f"{e.error_code}: {e.message}")
        except Exception as e:
            db_error = handle_database_error(e, "contribution metrics retrieval")
            log_error(db_error, {"query": "get_my_contribution_metrics"})
            raise Exception(f"Failed to get contribution metrics: {db_error.message}")
    
    @strawberry.field(permission_classes=[IsMentor])
    async def get_all_contribution_metrics(self, info: Info, repo_id: str) -> List[ContributionMetrics]:
        """
        Get all contribution metrics for a specific repository with comprehensive error handling.
        Only mentors can access this query and only for repositories they own.
        
        Args:
            repo_id: Repository ID to get metrics for
            
        Returns:
            List of all contribution metrics for the specified repository
            
        Raises:
            Exception: If user is not a mentor, doesn't own the repository, or database error occurs
        """
        try:
            # Get current user from context
            current_user = info.context.user
            if not current_user:
                raise AuthenticationError(
                    message="Authentication required",
                    details={"context": "GraphQL get_all_contribution_metrics query"}
                )
            
            github_id = current_user.get('github_id')
            role = current_user.get('role')
            
            if not github_id:
                raise AuthenticationError(
                    message="Invalid user context: missing github_id",
                    details={"user_context": current_user}
                )
            
            if role != ModelRole.MENTOR.value:
                raise InsufficientPermissionsError(
                    operation="get_all_contribution_metrics",
                    required_role="MENTOR",
                    details={"current_role": role}
                )
            
            # Validate repo_id format
            if not repo_id or not repo_id.strip():
                raise InvalidInputError(
                    field="repo_id",
                    reason="Repository ID is required and cannot be empty"
                )
            
            if not ObjectId.is_valid(repo_id):
                raise InvalidInputError(
                    field="repo_id",
                    reason=f"Invalid repository ID format: {repo_id}"
                )
            
            logger.debug(f"Getting all contribution metrics for repository {repo_id} by mentor {github_id}")
            
            # Get database connection
            db = get_database()
            
            # Verify mentor owns the repository
            repo_doc = await db.repositories.find_one({
                "_id": ObjectId(repo_id),
                "ownerGithubId": github_id
            })
            
            if not repo_doc:
                raise RepositoryNotFoundError(
                    repo_id=repo_id,
                    details={
                        "mentor": github_id,
                        "reason": "Repository not found or access denied"
                    }
                )
            
            # Find all contribution metrics for this repository
            metrics = []
            cursor = db.contribution_metrics.find({"repoId": ObjectId(repo_id)})
            
            async for metrics_doc in cursor:
                metrics.append(ContributionMetrics(
                    id=str(metrics_doc["_id"]),
                    repo_id=str(metrics_doc["repoId"]),
                    student_github_id=metrics_doc["studentGithubId"],
                    commit_count=metrics_doc.get("commitCount", 0),
                    pr_count=metrics_doc.get("prCount", 0),
                    issue_count=metrics_doc.get("issueCount", 0),
                    consistency_score=metrics_doc.get("consistencyScore", 0.0),
                    last_updated=metrics_doc["lastUpdated"]
                ))
            
            logger.info(f"Retrieved {len(metrics)} contribution metrics for repository {repo_id} by mentor {github_id}")
            return metrics
            
        except (AuthenticationError, InsufficientPermissionsError, InvalidInputError, RepositoryNotFoundError) as e:
            log_error(e, {
                "query": "get_all_contribution_metrics",
                "mentor": github_id if 'github_id' in locals() else None,
                "repo_id": repo_id,
                "role": role if 'role' in locals() else None
            })
            raise Exception(f"{e.error_code}: {e.message}")
        except Exception as e:
            db_error = handle_database_error(e, "repository contribution metrics retrieval")
            log_error(db_error, {"query": "get_all_contribution_metrics", "repo_id": repo_id})
            raise Exception(f"Failed to get repository contribution metrics: {db_error.message}")
    
    @strawberry.field(permission_classes=[IsAuthenticated])
    async def get_my_ai_feedback(self, info: Info, repo_id: Optional[str] = None) -> List[AIFeedback]:
        """
        Get AI feedback for the current user with proper access control.
        - Students: Get only their own AI feedback
        - Mentors: Get AI feedback for all students in their repositories
        
        Args:
            repo_id: Optional repository ID to filter feedback
            
        Returns:
            List of AI feedback accessible to the current user
            
        Raises:
            Exception: If user is not authenticated or database error occurs
        """
        try:
            # Get current user from context
            current_user = info.context.user
            if not current_user:
                raise AuthenticationError(
                    message="Authentication required",
                    details={"context": "GraphQL get_my_ai_feedback query"}
                )
            
            github_id = current_user.get('github_id')
            role = current_user.get('role')
            
            if not github_id or not role:
                raise AuthenticationError(
                    message="Invalid user context",
                    details={"github_id": bool(github_id), "role": bool(role)}
                )
            
            # Validate repo_id format if provided
            if repo_id and not ObjectId.is_valid(repo_id):
                raise InvalidInputError(
                    field="repo_id",
                    reason=f"Invalid repository ID format: {repo_id}"
                )
            
            logger.debug(f"Getting AI feedback for user: {github_id} ({role})")
            
            # Get database connection
            db = get_database()
            
            feedback_list = []
            
            if role == ModelRole.STUDENT.value:
                # Students get only their own AI feedback
                query = {"studentGithubId": github_id}
                if repo_id:
                    query["repoId"] = ObjectId(repo_id)
                
                cursor = db.ai_feedback.find(query).sort("generatedAt", -1)
                async for feedback_doc in cursor:
                    feedback_list.append(AIFeedback(
                        id=str(feedback_doc["_id"]),
                        repo_id=str(feedback_doc["repoId"]),
                        student_github_id=feedback_doc["studentGithubId"],
                        quality_score=feedback_doc.get("qualityScore", 0.0),
                        strengths=feedback_doc.get("strengths", []),
                        issues=feedback_doc.get("issues", []),
                        suggestions=feedback_doc.get("suggestions", []),
                        generated_at=feedback_doc["generatedAt"]
                    ))
            
            elif role == ModelRole.MENTOR.value:
                # Mentors get AI feedback for all students in their repositories
                if repo_id:
                    # Verify mentor owns the repository
                    repo_doc = await db.repositories.find_one({
                        "_id": ObjectId(repo_id),
                        "ownerGithubId": github_id
                    })
                    
                    if not repo_doc:
                        raise RepositoryNotFoundError(
                            repo_id=repo_id,
                            details={
                                "mentor": github_id,
                                "reason": "Repository not found or access denied"
                            }
                        )
                    
                    # Get feedback for this specific repository
                    cursor = db.ai_feedback.find({"repoId": ObjectId(repo_id)}).sort("generatedAt", -1)
                else:
                    # Get feedback for all repositories owned by this mentor
                    mentor_repos = []
                    repo_cursor = db.repositories.find({"ownerGithubId": github_id})
                    async for repo_doc in repo_cursor:
                        mentor_repos.append(repo_doc["_id"])
                    
                    if mentor_repos:
                        cursor = db.ai_feedback.find({"repoId": {"$in": mentor_repos}}).sort("generatedAt", -1)
                    else:
                        cursor = db.ai_feedback.find({"_id": {"$exists": False}})  # Empty cursor
                
                async for feedback_doc in cursor:
                    feedback_list.append(AIFeedback(
                        id=str(feedback_doc["_id"]),
                        repo_id=str(feedback_doc["repoId"]),
                        student_github_id=feedback_doc["studentGithubId"],
                        quality_score=feedback_doc.get("qualityScore", 0.0),
                        strengths=feedback_doc.get("strengths", []),
                        issues=feedback_doc.get("issues", []),
                        suggestions=feedback_doc.get("suggestions", []),
                        generated_at=feedback_doc["generatedAt"]
                    ))
            else:
                raise AuthorizationError(
                    message=f"Invalid user role: {role}",
                    details={"role": role, "valid_roles": ["MENTOR", "STUDENT"]}
                )
            
            logger.info(f"Retrieved {len(feedback_list)} AI feedback entries for user {github_id} ({role})")
            return feedback_list
            
        except (AuthenticationError, AuthorizationError, InvalidInputError, RepositoryNotFoundError) as e:
            log_error(e, {
                "query": "get_my_ai_feedback",
                "github_id": github_id if 'github_id' in locals() else None,
                "role": role if 'role' in locals() else None,
                "repo_id": repo_id
            })
            raise Exception(f"{e.error_code}: {e.message}")
        except Exception as e:
            db_error = handle_database_error(e, "AI feedback retrieval")
            log_error(db_error, {"query": "get_my_ai_feedback", "repo_id": repo_id})
            raise Exception(f"Failed to get AI feedback: {db_error.message}")
    
    @strawberry.field(permission_classes=[IsAuthenticated])
    async def find_candidates(self, info: Info, job_description: str) -> List[CandidateResult]:
        """
        Find students matching a job description using AI-powered skill matching.
        
        Uses local SentenceTransformers for embedding generation and scikit-learn
        for cosine similarity calculations. Returns top 5 candidates with match scores > 0.6.
        
        Args:
            job_description: Text describing job requirements and desired skills
            
        Returns:
            List of CandidateResult objects with student information and match scores,
            sorted by match score in descending order
            
        Raises:
            Exception: If user is not authenticated or search fails
        """
        try:
            # Get current user from context
            current_user = info.context.user
            if not current_user:
                raise AuthenticationError(
                    message="Authentication required",
                    details={"context": "GraphQL find_candidates query"}
                )
            
            github_id = current_user.get('github_id')
            if not github_id:
                raise AuthenticationError(
                    message="Invalid user context: missing github_id",
                    details={"user_context": current_user}
                )
            
            # Validate job description
            if not job_description or not job_description.strip():
                raise InvalidInputError(
                    field="job_description",
                    reason="Job description is required and cannot be empty"
                )
            
            logger.info(f"Finding candidates for job description by user {github_id}")
            
            # Get database connection
            db = get_database()
            
            # Initialize recommendation service
            recommendation_service = RecommendationService(db)
            
            # Find matching students
            matches = await recommendation_service.find_matching_students(job_description)
            
            # Transform to GraphQL CandidateResult types
            results = []
            for match in matches:
                user_doc = match.user
                
                # Extract verified skills from skill profile
                verified_skills = []
                if 'skill_profile' in user_doc and 'verified_skills' in user_doc['skill_profile']:
                    for skill in user_doc['skill_profile']['verified_skills']:
                        verified_skills.append(SkillTag(
                            name=skill['name'],
                            confidence=skill['confidence'],
                            evidence_file=skill['evidence_file']
                        ))
                
                results.append(CandidateResult(
                    id=str(user_doc['_id']),
                    username=user_doc['username'],
                    email=user_doc.get('email'),
                    match_score=match.match_score,
                    verified_skills=verified_skills
                ))
            
            logger.info(f"Returning {len(results)} candidates for user {github_id}")
            return results
            
        except (AuthenticationError, InvalidInputError) as e:
            log_error(e, {
                "query": "find_candidates",
                "github_id": github_id if 'github_id' in locals() else None
            })
            raise Exception(f"{e.error_code}: {e.message}")
        except ValueError as e:
            # Handle validation errors from recommendation service
            error = InvalidInputError(
                field="job_description",
                reason=str(e)
            )
            log_error(error, {"query": "find_candidates"})
            raise Exception(f"{error.error_code}: {error.message}")
        except Exception as e:
            db_error = handle_database_error(e, "candidate search")
            log_error(db_error, {"query": "find_candidates"})
            raise Exception(f"Failed to find candidates: {db_error.message}")