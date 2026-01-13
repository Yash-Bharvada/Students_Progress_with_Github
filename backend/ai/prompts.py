"""
AI prompt templates for Google Gemini Flash API.
Provides educational and constructive prompt templates optimized for code analysis.
"""

from typing import Dict, List, Optional, Any
from backend.models import ContributionMetrics


class GitHubAnalysisData:
    """Container for GitHub repository analysis data."""
    
    def __init__(self):
        self.repo_url: str = ""
        self.repo_name: str = ""
        self.commit_frequency: float = 0.0  # commits per day
        self.avg_commit_size: float = 0.0   # average lines changed per commit
        self.recent_commits: List[Dict] = []
        self.has_tests: bool = False
        self.has_documentation: bool = False
        self.has_readme: bool = False
        self.file_structure: List[str] = []
        self.languages: Dict[str, int] = {}
        self.total_commits: int = 0
        self.total_lines_added: int = 0
        self.total_lines_deleted: int = 0
        self.commit_messages: List[str] = []
        self.error_message: Optional[str] = None


class AIPrompts:
    """Centralized prompt templates for AI feedback generation using Gemini Flash API."""
    
    @staticmethod
    def get_code_quality_prompt(
        analysis_data: GitHubAnalysisData, 
        metrics: Optional[ContributionMetrics] = None
    ) -> str:
        """
        Generate a comprehensive code quality analysis prompt optimized for Gemini Flash.
        
        Args:
            analysis_data: GitHub repository analysis data
            metrics: Optional contribution metrics
            
        Returns:
            Formatted prompt string for Gemini Flash API
        """
        # Build context section efficiently for Flash model
        context = AIPrompts._build_repository_context(analysis_data, metrics)
        
        prompt = f"""You are an experienced software engineering mentor providing constructive feedback to a student developer. Your role is to help them learn and improve through specific, actionable guidance.

REPOSITORY ANALYSIS:
{context}

FEEDBACK GUIDELINES:
- Be educational and encouraging while honest about areas for improvement
- Focus on learning opportunities and growth
- Provide specific, actionable recommendations
- Maintain an advisory tone (suggestions, not commands)
- Avoid absolute judgments or guarantees
- Consider this is a learning environment, not production code review

RESPONSE FORMAT:
Quality Score: [Provide a score from 0-10 based on overall code quality, development practices, and learning progress]

Strengths:
- [List 2-4 specific positive aspects you observe]
- [Focus on good practices, effort, or improvement areas]

Issues:
- [List 2-4 areas that need attention]
- [Frame as learning opportunities, not failures]

Suggestions:
- [Provide 3-5 specific, actionable recommendations]
- [Include both immediate improvements and longer-term learning goals]
- [Suggest resources or practices when appropriate]

Remember: Your feedback should inspire continued learning and improvement. Be supportive while providing honest, constructive guidance."""

        return prompt
    
    @staticmethod
    def get_educational_feedback_prompt(context: Dict[str, Any]) -> str:
        """
        Generate an educational feedback prompt for specific learning scenarios.
        
        Args:
            context: Dictionary containing specific context for educational feedback
            
        Returns:
            Formatted educational prompt string
        """
        scenario = context.get('scenario', 'general')
        focus_areas = context.get('focus_areas', [])
        student_level = context.get('student_level', 'beginner')
        
        prompt = f"""You are a patient and encouraging programming mentor working with a {student_level} student developer. 

LEARNING SCENARIO: {scenario}

FOCUS AREAS: {', '.join(focus_areas) if focus_areas else 'General development practices'}

Your feedback should:
1. Acknowledge effort and progress made
2. Identify specific learning opportunities
3. Provide step-by-step guidance for improvement
4. Suggest appropriate resources for their level
5. Encourage continued learning and experimentation

Maintain a supportive, advisory tone that builds confidence while promoting growth. Frame challenges as exciting learning opportunities rather than problems to fix.

Please provide feedback that helps this student developer continue their learning journey with confidence and clear direction."""

        return prompt
    
    @staticmethod
    def get_commit_analysis_prompt(
        commit_messages: List[str], 
        commit_frequency: float,
        avg_commit_size: float
    ) -> str:
        """
        Generate a prompt focused on commit practices and development workflow.
        
        Args:
            commit_messages: List of recent commit messages
            commit_frequency: Commits per day
            avg_commit_size: Average lines changed per commit
            
        Returns:
            Formatted prompt for commit analysis
        """
        messages_text = '\n'.join([f"- {msg}" for msg in commit_messages[:8]]) if commit_messages else "No recent commits"
        
        prompt = f"""You are a software development mentor focusing on version control and development workflow practices.

COMMIT ANALYSIS DATA:
Commit Frequency: {commit_frequency:.2f} commits per day
Average Commit Size: {avg_commit_size:.1f} lines changed per commit

Recent Commit Messages:
{messages_text}

EVALUATION FOCUS:
- Commit message clarity and descriptiveness
- Commit frequency and consistency
- Commit size appropriateness
- Development workflow patterns

Provide educational feedback on:
1. Version control best practices
2. Commit message writing
3. Development workflow optimization
4. Consistency in development habits

Frame your feedback as learning opportunities to help improve their development workflow and collaboration skills. Be encouraging about progress while suggesting specific improvements."""

        return prompt
    
    @staticmethod
    def get_project_structure_prompt(
        file_structure: List[str],
        languages: Dict[str, int],
        has_tests: bool,
        has_documentation: bool,
        has_readme: bool
    ) -> str:
        """
        Generate a prompt focused on project organization and structure.
        
        Args:
            file_structure: List of files in the repository
            languages: Dictionary of languages and their usage
            has_tests: Whether tests are present
            has_documentation: Whether documentation exists
            has_readme: Whether README exists
            
        Returns:
            Formatted prompt for project structure analysis
        """
        files_text = ', '.join(file_structure[:15]) if file_structure else "No files detected"
        languages_text = ', '.join([f"{lang} ({bytes} bytes)" for lang, bytes in languages.items()]) if languages else "No languages detected"
        
        prompt = f"""You are a software architecture mentor helping a student learn about project organization and best practices.

PROJECT STRUCTURE ANALYSIS:
Files: {files_text}
Languages: {languages_text}
Has Tests: {has_tests}
Has Documentation: {has_documentation}
Has README: {has_readme}

EVALUATION FOCUS:
- Project organization and structure
- File naming conventions
- Presence of essential project files
- Code organization patterns
- Documentation practices

Provide constructive feedback on:
1. Project structure and organization
2. Essential files and documentation
3. Code organization best practices
4. Suggestions for improving project maintainability

Remember this is a learning environment - celebrate good organizational choices while gently guiding toward industry best practices. Provide specific, actionable suggestions for improvement."""

        return prompt
    
    @staticmethod
    def get_beginner_friendly_prompt(analysis_data: GitHubAnalysisData) -> str:
        """
        Generate a beginner-friendly prompt with simplified language and concepts.
        
        Args:
            analysis_data: GitHub repository analysis data
            
        Returns:
            Beginner-focused prompt string
        """
        prompt = f"""You are a friendly programming mentor working with a beginning developer. Use simple, encouraging language and focus on fundamental concepts.

STUDENT'S PROJECT: {analysis_data.repo_name}
Recent Activity: {analysis_data.total_commits} commits in the last 30 days
Project Files: {len(analysis_data.file_structure)} files

BEGINNER FOCUS AREAS:
- Basic coding practices
- Simple project organization
- Building good habits
- Encouraging continued learning

Your feedback should:
1. Use simple, non-technical language when possible
2. Celebrate small wins and progress
3. Provide one or two main areas to focus on
4. Suggest beginner-friendly resources
5. Encourage experimentation and learning

Keep suggestions simple and achievable. Focus on building confidence and establishing good development habits rather than advanced techniques."""

        return prompt
    
    @staticmethod
    def get_advanced_analysis_prompt(
        analysis_data: GitHubAnalysisData,
        metrics: ContributionMetrics
    ) -> str:
        """
        Generate an advanced analysis prompt for experienced developers.
        
        Args:
            analysis_data: GitHub repository analysis data
            metrics: Contribution metrics
            
        Returns:
            Advanced analysis prompt string
        """
        context = AIPrompts._build_repository_context(analysis_data, metrics)
        
        prompt = f"""You are a senior software engineer providing detailed technical feedback to an advanced student developer.

COMPREHENSIVE ANALYSIS:
{context}

ADVANCED EVALUATION CRITERIA:
- Code architecture and design patterns
- Performance considerations
- Scalability and maintainability
- Testing strategies and coverage
- Documentation quality and completeness
- Development workflow optimization
- Industry best practices adherence

Provide in-depth feedback covering:
1. Technical architecture and design decisions
2. Code quality and maintainability factors
3. Testing and quality assurance practices
4. Performance and scalability considerations
5. Professional development workflow suggestions

Your feedback should challenge the student to think about advanced concepts while providing specific, actionable guidance for reaching professional-level development practices."""

        return prompt
    
    @staticmethod
    def _build_repository_context(
        analysis_data: GitHubAnalysisData, 
        metrics: Optional[ContributionMetrics] = None
    ) -> str:
        """
        Build efficient repository context for Gemini Flash API.
        Optimizes token usage while providing comprehensive information.
        
        Args:
            analysis_data: GitHub repository analysis data
            metrics: Optional contribution metrics
            
        Returns:
            Formatted context string
        """
        # Build context efficiently to minimize tokens
        context_parts = []
        
        # Basic repository info
        context_parts.append(f"Repository: {analysis_data.repo_name}")
        
        # Activity metrics
        if analysis_data.total_commits > 0:
            context_parts.append(f"Recent Activity: {analysis_data.total_commits} commits ({analysis_data.commit_frequency:.1f}/day)")
            if analysis_data.avg_commit_size > 0:
                context_parts.append(f"Avg Commit Size: {analysis_data.avg_commit_size:.0f} lines")
        
        # Project structure
        structure_info = []
        if analysis_data.has_readme:
            structure_info.append("README")
        if analysis_data.has_tests:
            structure_info.append("Tests")
        if analysis_data.has_documentation:
            structure_info.append("Documentation")
        
        if structure_info:
            context_parts.append(f"Project Structure: {', '.join(structure_info)}")
        
        # Languages (top 3 to save tokens)
        if analysis_data.languages:
            top_languages = sorted(analysis_data.languages.items(), key=lambda x: x[1], reverse=True)[:3]
            lang_names = [lang for lang, _ in top_languages]
            context_parts.append(f"Languages: {', '.join(lang_names)}")
        
        # Recent commit messages (limited for token efficiency)
        if analysis_data.commit_messages:
            recent_messages = analysis_data.commit_messages[:5]  # Limit to 5 most recent
            context_parts.append("Recent Commits:")
            for i, msg in enumerate(recent_messages, 1):
                # Truncate long commit messages
                truncated_msg = msg[:80] + "..." if len(msg) > 80 else msg
                context_parts.append(f"  {i}. {truncated_msg}")
        
        # Additional metrics if available
        if metrics:
            context_parts.append(f"Contribution Metrics: {metrics.commit_count} total commits, {metrics.pr_count} PRs, {metrics.issue_count} issues")
            context_parts.append(f"Consistency Score: {metrics.consistency_score:.2f}/1.0")
        
        # File structure (limited to save tokens)
        if analysis_data.file_structure:
            file_count = len(analysis_data.file_structure)
            if file_count <= 10:
                context_parts.append(f"Files ({file_count}): {', '.join(analysis_data.file_structure)}")
            else:
                sample_files = analysis_data.file_structure[:8]
                context_parts.append(f"Files ({file_count}): {', '.join(sample_files)}, ... and {file_count - 8} more")
        
        return '\n'.join(context_parts)
    
    @staticmethod
    def get_error_fallback_prompt(error_message: str) -> str:
        """
        Generate a fallback prompt when repository analysis fails.
        
        Args:
            error_message: The error that occurred during analysis
            
        Returns:
            Fallback prompt string
        """
        prompt = f"""You are a supportive programming mentor. The automated analysis encountered an issue: {error_message}

Despite the technical difficulty, please provide encouraging feedback that:

1. Acknowledges that technical issues happen in software development
2. Encourages the student to continue their learning journey
3. Suggests general best practices for code development
4. Recommends checking repository accessibility and permissions
5. Provides motivation to keep coding and learning

Frame this as a learning opportunity about troubleshooting and problem-solving in software development. Be supportive and encouraging while providing general guidance that would benefit any developing programmer."""

        return prompt
    
    @staticmethod
    def validate_prompt_length(prompt: str, max_tokens: int = 2048) -> str:
        """
        Validate and potentially truncate prompt to fit within token limits.
        Optimized for Gemini Flash API efficiency.
        
        Args:
            prompt: The prompt to validate
            max_tokens: Maximum token limit (approximate)
            
        Returns:
            Validated prompt string
        """
        # Rough estimation: 1 token ≈ 4 characters for English text
        estimated_tokens = len(prompt) // 4
        
        if estimated_tokens <= max_tokens:
            return prompt
        
        # Truncate if too long, keeping the structure intact
        max_chars = max_tokens * 4
        if len(prompt) > max_chars:
            # Find a good truncation point (end of a line)
            truncation_point = prompt.rfind('\n', 0, max_chars - 100)
            if truncation_point > max_chars // 2:  # Only truncate if we keep at least half
                return prompt[:truncation_point] + "\n\n[Analysis truncated for efficiency - please provide feedback based on available information]"
            else:
                # If no good truncation point, just cut at max_chars with ellipsis
                return prompt[:max_chars - 50] + "\n\n[Analysis truncated for efficiency]"
        
        return prompt