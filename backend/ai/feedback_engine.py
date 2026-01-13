"""
AI feedback generation engine for analyzing GitHub repository data.
Integrates with Google Gemini Flash API for fast feedback generation.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import httpx
from bson import ObjectId

from backend.models import AIFeedback, Repository, ContributionMetrics
from backend.config import get_settings
from backend.database import Database
from backend.ai.gemini_client import get_gemini_client
from backend.ai.prompts import AIPrompts, GitHubAnalysisData

logger = logging.getLogger(__name__)


class AIFeedbackEngine:
    """AI-powered feedback generation engine."""
    
    def __init__(self, database: Database):
        """Initialize feedback engine with database connection."""
        self.database = database
        self.settings = get_settings()
        
        # Initialize Gemini client only if API key is available
        try:
            self.gemini_client = get_gemini_client()
        except ValueError as e:
            if "Gemini API key is required" in str(e):
                # For testing or when API key is not available
                self.gemini_client = None
                logger.warning("Gemini API key not available - AI feedback will use fallback responses")
            else:
                raise
        
    async def analyze_repository(self, repo_id: str, student_github_id: str) -> AIFeedback:
        """
        Analyze repository and generate AI feedback.
        
        Args:
            repo_id: Repository ObjectId as string
            student_github_id: Student's GitHub ID
            
        Returns:
            AIFeedback object with generated feedback
            
        Raises:
            ValueError: If repository not found or access denied
            Exception: If analysis or AI generation fails
        """
        try:
            logger.info(f"Starting AI analysis for repo {repo_id}, student {student_github_id}")
            
            # Get repository information
            repo = await self._get_repository(repo_id)
            if not repo:
                raise ValueError(f"Repository {repo_id} not found")
            
            # Fetch GitHub data for analysis
            analysis_data = await self.fetch_github_data(repo.repo_url, student_github_id)
            
            # Get contribution metrics if available
            metrics = await self._get_contribution_metrics(repo_id, student_github_id)
            
            # Generate AI feedback
            feedback = await self.generate_feedback(analysis_data, metrics)
            
            # Store feedback in database
            feedback.repoId = ObjectId(repo_id)
            feedback.studentGithubId = student_github_id
            
            await self.store_feedback(feedback)
            
            logger.info(f"Successfully generated AI feedback for repo {repo_id}")
            return feedback
            
        except Exception as e:
            logger.error(f"Error analyzing repository {repo_id}: {str(e)}")
            raise
    
    async def fetch_github_data(self, repo_url: str, student_github_id: str) -> GitHubAnalysisData:
        """
        Fetch and analyze GitHub repository data.
        
        Args:
            repo_url: Repository URL
            student_github_id: Student's GitHub ID for filtering commits
            
        Returns:
            GitHubAnalysisData with analyzed repository information
        """
        analysis_data = GitHubAnalysisData()
        analysis_data.repo_url = repo_url
        
        try:
            # Extract owner and repo name from URL
            repo_parts = repo_url.replace("https://github.com/", "").split("/")
            if len(repo_parts) < 2:
                raise ValueError(f"Invalid GitHub repository URL: {repo_url}")
            
            owner, repo_name = repo_parts[0], repo_parts[1]
            analysis_data.repo_name = repo_name
            
            # GitHub API headers
            headers = {
                "Authorization": f"token {self.settings.github_api_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            async with httpx.AsyncClient() as client:
                # Get repository information
                repo_response = await client.get(
                    f"https://api.github.com/repos/{owner}/{repo_name}",
                    headers=headers
                )
                
                if repo_response.status_code == 404:
                    analysis_data.error_message = "Repository not found or not accessible"
                    return analysis_data
                elif repo_response.status_code != 200:
                    analysis_data.error_message = f"GitHub API error: {repo_response.status_code}"
                    return analysis_data
                
                repo_info = repo_response.json()
                
                # Get commits by the student (last 30 days)
                since_date = (datetime.utcnow() - timedelta(days=30)).isoformat()
                commits_response = await client.get(
                    f"https://api.github.com/repos/{owner}/{repo_name}/commits",
                    headers=headers,
                    params={
                        "author": student_github_id,
                        "since": since_date,
                        "per_page": 100
                    }
                )
                
                if commits_response.status_code == 200:
                    commits = commits_response.json()
                    analysis_data.recent_commits = commits
                    analysis_data.total_commits = len(commits)
                    
                    # Calculate commit frequency (commits per day)
                    if commits:
                        analysis_data.commit_frequency = len(commits) / 30.0
                        
                        # Extract commit messages
                        analysis_data.commit_messages = [
                            commit.get("commit", {}).get("message", "")
                            for commit in commits[:10]  # Last 10 commits
                        ]
                        
                        # Calculate average commit size (approximate)
                        total_changes = 0
                        for commit in commits[:20]:  # Analyze last 20 commits for performance
                            commit_detail = await client.get(
                                commit["url"],
                                headers=headers
                            )
                            if commit_detail.status_code == 200:
                                commit_data = commit_detail.json()
                                stats = commit_data.get("stats", {})
                                total_changes += stats.get("total", 0)
                        
                        if total_changes > 0:
                            analysis_data.avg_commit_size = total_changes / min(len(commits), 20)
                
                # Get repository contents to analyze structure
                contents_response = await client.get(
                    f"https://api.github.com/repos/{owner}/{repo_name}/contents",
                    headers=headers
                )
                
                if contents_response.status_code == 200:
                    contents = contents_response.json()
                    analysis_data.file_structure = [
                        item["name"] for item in contents if item["type"] == "file"
                    ]
                    
                    # Check for common files
                    file_names = [f.lower() for f in analysis_data.file_structure]
                    analysis_data.has_readme = any(
                        name.startswith("readme") for name in file_names
                    )
                    analysis_data.has_tests = any(
                        "test" in name or name.endswith(".test.js") or name.endswith("_test.py")
                        for name in file_names
                    )
                    analysis_data.has_documentation = any(
                        name in ["docs", "documentation"] or name.endswith(".md")
                        for name in file_names
                    )
                
                # Get language statistics
                languages_response = await client.get(
                    f"https://api.github.com/repos/{owner}/{repo_name}/languages",
                    headers=headers
                )
                
                if languages_response.status_code == 200:
                    analysis_data.languages = languages_response.json()
                
        except Exception as e:
            logger.error(f"Error fetching GitHub data for {repo_url}: {str(e)}")
            analysis_data.error_message = f"Failed to fetch repository data: {str(e)}"
        
        return analysis_data
    
    async def generate_feedback(self, analysis_data: GitHubAnalysisData, metrics: Optional[ContributionMetrics] = None) -> AIFeedback:
        """
        Generate AI feedback using Gemini Flash API.
        
        Args:
            analysis_data: GitHub repository analysis data
            metrics: Optional contribution metrics
            
        Returns:
            AIFeedback object with generated feedback
        """
        try:
            # Check if we have an error in data fetching
            if analysis_data.error_message:
                # Use error fallback prompt
                error_prompt = AIPrompts.get_error_fallback_prompt(analysis_data.error_message)
                
                if self.gemini_client:
                    try:
                        feedback_response = await self.gemini_client.generate_feedback(error_prompt)
                    except Exception:
                        # If AI generation fails, use static fallback
                        feedback_response = {
                            "quality_score": 0.0,
                            "strengths": [],
                            "issues": [f"Unable to analyze repository: {analysis_data.error_message}"],
                            "suggestions": ["Please ensure the repository is public and accessible", "Check repository permissions and try again"]
                        }
                else:
                    feedback_response = {
                        "quality_score": 0.0,
                        "strengths": [],
                        "issues": [f"Unable to analyze repository: {analysis_data.error_message}"],
                        "suggestions": ["Please ensure the repository is public and accessible", "Configure Gemini API key for detailed AI feedback"]
                    }
                
                return AIFeedback(
                    repoId=ObjectId(),  # Will be set by caller
                    studentGithubId="",  # Will be set by caller
                    qualityScore=feedback_response.get("quality_score", 0.0),
                    strengths=feedback_response.get("strengths", []),
                    issues=feedback_response.get("issues", []),
                    suggestions=feedback_response.get("suggestions", [])
                )
            
            # Generate prompt using AIPrompts with context awareness
            prompt = self.get_contextual_prompt(analysis_data, metrics)
            
            # Validate prompt length for Gemini Flash efficiency
            prompt = AIPrompts.validate_prompt_length(prompt)
            
            # Generate feedback using Gemini Flash (if available)
            if self.gemini_client:
                feedback_response = await self.gemini_client.generate_feedback(prompt)
            else:
                # Fallback response when Gemini client is not available
                logger.warning("Gemini client not available - using fallback feedback")
                feedback_response = {
                    "quality_score": 6.0,
                    "strengths": ["Code structure appears organized", "Repository contains multiple files"],
                    "issues": ["Unable to perform detailed analysis without AI service"],
                    "suggestions": ["Configure Gemini API key for detailed AI feedback", "Consider adding more documentation"]
                }
            
            # Create AIFeedback object
            feedback = AIFeedback(
                repoId=ObjectId(),  # Will be set by caller
                studentGithubId="",  # Will be set by caller
                qualityScore=feedback_response.get("quality_score", 5.0),
                strengths=feedback_response.get("strengths", []),
                issues=feedback_response.get("issues", []),
                suggestions=feedback_response.get("suggestions", [])
            )
            
            return feedback
            
        except Exception as e:
            logger.error(f"Error generating AI feedback: {str(e)}")
            # Return fallback feedback
            return AIFeedback(
                repoId=ObjectId(),
                studentGithubId="",
                qualityScore=5.0,
                strengths=["Code analysis attempted"],
                issues=[f"AI feedback generation failed: {str(e)}"],
                suggestions=["Please try again later or contact support"]
            )
    
    async def store_feedback(self, feedback: AIFeedback) -> str:
        """
        Store AI feedback in database.
        
        Args:
            feedback: AIFeedback object to store
            
        Returns:
            String ID of stored feedback
        """
        try:
            # Convert to dict for MongoDB storage
            feedback_dict = feedback.dict(by_alias=True)
            
            # Insert into database
            result = await self.database.ai_feedback.insert_one(feedback_dict)
            
            logger.info(f"Stored AI feedback with ID: {result.inserted_id}")
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Error storing AI feedback: {str(e)}")
            raise
    
    async def get_feedback_history(self, student_github_id: str, repo_id: Optional[str] = None) -> List[AIFeedback]:
        """
        Get AI feedback history for a student.
        
        Args:
            student_github_id: Student's GitHub ID
            repo_id: Optional repository ID to filter by
            
        Returns:
            List of AIFeedback objects
        """
        try:
            query = {"studentGithubId": student_github_id}
            if repo_id:
                query["repoId"] = ObjectId(repo_id)
            
            cursor = self.database.ai_feedback.find(query).sort("generatedAt", -1)
            feedback_list = []
            
            async for doc in cursor:
                feedback = AIFeedback(**doc)
                feedback_list.append(feedback)
            
            return feedback_list
            
        except Exception as e:
            logger.error(f"Error getting feedback history: {str(e)}")
            return []
    
    def get_contextual_prompt(
        self, 
        analysis_data: GitHubAnalysisData, 
        metrics: Optional[ContributionMetrics] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Get contextual prompt based on analysis data and additional context.
        
        Args:
            analysis_data: GitHub repository analysis data
            metrics: Optional contribution metrics
            context: Optional context for specialized prompts
            
        Returns:
            Appropriate prompt string for the context
        """
        if context:
            prompt_type = context.get('type', 'default')
            
            if prompt_type == 'beginner':
                return AIPrompts.get_beginner_friendly_prompt(analysis_data)
            elif prompt_type == 'advanced' and metrics:
                return AIPrompts.get_advanced_analysis_prompt(analysis_data, metrics)
            elif prompt_type == 'commit_focus':
                return AIPrompts.get_commit_analysis_prompt(
                    analysis_data.commit_messages,
                    analysis_data.commit_frequency,
                    analysis_data.avg_commit_size
                )
            elif prompt_type == 'structure_focus':
                return AIPrompts.get_project_structure_prompt(
                    analysis_data.file_structure,
                    analysis_data.languages,
                    analysis_data.has_tests,
                    analysis_data.has_documentation,
                    analysis_data.has_readme
                )
            elif prompt_type == 'educational':
                return AIPrompts.get_educational_feedback_prompt(context)
        
        # Default to comprehensive code quality prompt
        return AIPrompts.get_code_quality_prompt(analysis_data, metrics)
    
    async def _get_repository(self, repo_id: str) -> Optional[Repository]:
        """Get repository by ID."""
        try:
            doc = await self.database.repositories.find_one({"_id": ObjectId(repo_id)})
            if doc:
                return Repository(**doc)
            return None
        except Exception as e:
            logger.error(f"Error getting repository {repo_id}: {str(e)}")
            return None
    
    async def _get_contribution_metrics(self, repo_id: str, student_github_id: str) -> Optional[ContributionMetrics]:
        """Get contribution metrics for student and repository."""
        try:
            doc = await self.database.contribution_metrics.find_one({
                "repoId": ObjectId(repo_id),
                "studentGithubId": student_github_id
            })
            if doc:
                return ContributionMetrics(**doc)
            return None
        except Exception as e:
            logger.error(f"Error getting contribution metrics: {str(e)}")
            return None