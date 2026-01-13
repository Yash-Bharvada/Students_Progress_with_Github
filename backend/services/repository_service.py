"""
Repository service for GitHub repository analysis and data collection.
Automatically retrieves and uses stored GitHub access tokens.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone, timedelta
from backend.services.user_service import user_service
from backend.auth.github_oauth import github_oauth, GitHubOAuthError
from backend.database import get_database


class RepositoryService:
    """Service for GitHub repository operations with automatic token management."""
    
    def __init__(self):
        self.db = get_database()
    
    async def get_user_repositories(self, github_id: str) -> Dict[str, Any]:
        """
        Get repositories for a user using their stored GitHub access token.
        
        Args:
            github_id: GitHub user ID
            
        Returns:
            Dictionary with repositories and metadata
        """
        try:
            # Get user's stored GitHub access token
            access_token = await user_service.get_user_github_token(github_id)
            if not access_token:
                return {
                    "success": False,
                    "error": "No GitHub access token found. User needs to re-authenticate.",
                    "repositories": []
                }
            
            # Get user info for username
            user = await user_service.find_user_by_github_id(github_id)
            if not user:
                return {
                    "success": False,
                    "error": "User not found",
                    "repositories": []
                }
            
            username = user["username"]
            
            # Fetch repositories using GitHub API
            repositories = await github_oauth.get_user_repositories(access_token, username)
            
            # Process repository data
            processed_repos = []
            for repo in repositories:
                processed_repos.append({
                    "name": repo["name"],
                    "description": repo["description"],
                    "language": repo["language"],
                    "stars": repo["stargazers_count"],
                    "forks": repo["forks_count"],
                    "size": repo["size"],
                    "private": repo["private"],
                    "created_at": repo["created_at"],
                    "updated_at": repo["updated_at"],
                    "clone_url": repo["clone_url"],
                    "html_url": repo["html_url"],
                    "default_branch": repo["default_branch"]
                })
            
            return {
                "success": True,
                "username": username,
                "total_repositories": len(repositories),
                "repositories": processed_repos,
                "fetched_at": datetime.now(timezone.utc).isoformat()
            }
            
        except GitHubOAuthError as e:
            return {
                "success": False,
                "error": f"GitHub API error: {str(e)}",
                "repositories": []
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Repository fetch failed: {str(e)}",
                "repositories": []
            }
    
    async def get_repository_commits(
        self, 
        github_id: str, 
        owner: str, 
        repo: str, 
        since: Optional[str] = None,
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        Get commits for a repository using user's stored GitHub access token.
        
        Args:
            github_id: GitHub user ID (for token retrieval)
            owner: Repository owner username
            repo: Repository name
            since: ISO 8601 date string to filter commits
            limit: Maximum number of commits to return
            
        Returns:
            Dictionary with commits and metadata
        """
        try:
            # Get user's stored GitHub access token
            access_token = await user_service.get_user_github_token(github_id)
            if not access_token:
                return {
                    "success": False,
                    "error": "No GitHub access token found. User needs to re-authenticate.",
                    "commits": []
                }
            
            # Fetch commits using GitHub API
            commits = await github_oauth.get_repository_commits(access_token, owner, repo, since)
            
            # Process commit data (limit results)
            processed_commits = []
            for commit in commits[:limit]:
                commit_data = commit["commit"]
                processed_commits.append({
                    "sha": commit["sha"][:8],  # Short SHA
                    "full_sha": commit["sha"],
                    "message": commit_data["message"],
                    "author": {
                        "name": commit_data["author"]["name"],
                        "email": commit_data["author"]["email"],
                        "date": commit_data["author"]["date"]
                    },
                    "committer": {
                        "name": commit_data["committer"]["name"],
                        "email": commit_data["committer"]["email"],
                        "date": commit_data["committer"]["date"]
                    },
                    "stats": commit.get("stats", {}),
                    "html_url": commit["html_url"],
                    "parents": [parent["sha"][:8] for parent in commit.get("parents", [])]
                })
            
            return {
                "success": True,
                "repository": f"{owner}/{repo}",
                "total_commits": len(commits),
                "showing": len(processed_commits),
                "since": since,
                "commits": processed_commits,
                "fetched_at": datetime.now(timezone.utc).isoformat()
            }
            
        except GitHubOAuthError as e:
            return {
                "success": False,
                "error": f"GitHub API error: {str(e)}",
                "commits": []
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Commit fetch failed: {str(e)}",
                "commits": []
            }
    
    async def analyze_repository_activity(self, github_id: str, owner: str, repo: str) -> Dict[str, Any]:
        """
        Analyze repository activity patterns for a student.
        
        Args:
            github_id: GitHub user ID
            owner: Repository owner username
            repo: Repository name
            
        Returns:
            Dictionary with activity analysis
        """
        try:
            # Get recent commits (last 30 days)
            since_date = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
            commit_data = await self.get_repository_commits(github_id, owner, repo, since_date)
            
            if not commit_data["success"]:
                return commit_data
            
            commits = commit_data["commits"]
            
            # Analyze commit patterns
            analysis = {
                "repository": f"{owner}/{repo}",
                "analysis_period": "Last 30 days",
                "total_commits": len(commits),
                "commit_frequency": len(commits) / 30,  # commits per day
                "authors": {},
                "commit_times": [],
                "message_patterns": {
                    "bug_fixes": 0,
                    "features": 0,
                    "documentation": 0,
                    "refactoring": 0,
                    "other": 0
                },
                "collaboration_indicators": {
                    "merge_commits": 0,
                    "multiple_authors": False,
                    "code_reviews": 0
                }
            }
            
            # Analyze each commit
            for commit in commits:
                author = commit["author"]["name"]
                
                # Count commits per author
                if author not in analysis["authors"]:
                    analysis["authors"][author] = 0
                analysis["authors"][author] += 1
                
                # Analyze commit times
                commit_time = datetime.fromisoformat(commit["author"]["date"].replace('Z', '+00:00'))
                analysis["commit_times"].append(commit_time.hour)
                
                # Analyze commit messages
                message = commit["message"].lower()
                if any(word in message for word in ["fix", "bug", "error", "issue"]):
                    analysis["message_patterns"]["bug_fixes"] += 1
                elif any(word in message for word in ["add", "feature", "implement", "new"]):
                    analysis["message_patterns"]["features"] += 1
                elif any(word in message for word in ["doc", "readme", "comment"]):
                    analysis["message_patterns"]["documentation"] += 1
                elif any(word in message for word in ["refactor", "clean", "optimize"]):
                    analysis["message_patterns"]["refactoring"] += 1
                else:
                    analysis["message_patterns"]["other"] += 1
                
                # Check for collaboration indicators
                if "merge" in message:
                    analysis["collaboration_indicators"]["merge_commits"] += 1
                
                if len(commit["parents"]) > 1:
                    analysis["collaboration_indicators"]["code_reviews"] += 1
            
            # Determine collaboration level
            analysis["collaboration_indicators"]["multiple_authors"] = len(analysis["authors"]) > 1
            
            # Calculate activity score (0-10)
            activity_score = min(10, (len(commits) / 10) * 5 + (len(analysis["authors"]) * 2))
            analysis["activity_score"] = round(activity_score, 1)
            
            # Calculate consistency score
            if len(commits) > 0:
                days_with_commits = len(set(
                    datetime.fromisoformat(commit["author"]["date"].replace('Z', '+00:00')).date()
                    for commit in commits
                ))
                consistency_score = min(1.0, days_with_commits / 30)
            else:
                consistency_score = 0.0
            
            analysis["consistency_score"] = round(consistency_score, 2)
            analysis["analyzed_at"] = datetime.now(timezone.utc).isoformat()
            
            return {
                "success": True,
                "analysis": analysis
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Repository analysis failed: {str(e)}",
                "analysis": {}
            }


# Global repository service instance
repository_service = RepositoryService()