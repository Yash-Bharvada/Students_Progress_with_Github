#!/usr/bin/env python3
"""
Repository Scanner - Standalone CLI utility for scanning local code repositories.

Scans local directories for code files (Python, JavaScript, TypeScript, Java, C++, Go, etc.),
extracts technical skills using AI, generates semantic embeddings, and updates user skill 
profiles in MongoDB.

Usage:
    python scan_local_repo.py --directory <path> --github-id <id>

Example:
    python scan_local_repo.py --directory ./my-project --github-id john-doe
"""

import argparse
import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Set
import pymongo
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

# Add backend to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.config import get_settings
from backend.ai.skill_engine import SkillEngine
from backend.models import SkillTag, UserSkillProfile


class RepositoryScanner:
    """
    Scans local code repositories for technical skills.
    
    Recursively traverses directories, analyzes code files (Python, JavaScript, 
    TypeScript, Java, C++, Go, Rust, etc.) using AI, aggregates skills, generates 
    embeddings, and updates MongoDB profiles.
    """
    
    # Directories to skip during traversal
    IGNORE_DIRS = {
        'venv', 'env', '.venv', '.env',
        '__pycache__', '.pytest_cache',
        'node_modules', '.git', '.svn', '.hg',
        'dist', 'build', '.tox', '.eggs',
        '.mypy_cache', '.ruff_cache', 'target',
        'bin', 'obj', '.gradle', '.idea', '.vscode'
    }
    
    # File extensions to analyze (common programming languages)
    VALID_EXTENSIONS = {
        # Python
        '.py',
        # JavaScript/TypeScript
        '.js', '.jsx', '.ts', '.tsx', '.mjs', '.cjs',
        # Java/Kotlin
        '.java', '.kt', '.kts',
        # C/C++
        '.c', '.cpp', '.cc', '.cxx', '.h', '.hpp',
        # C#
        '.cs',
        # Go
        '.go',
        # Rust
        '.rs',
        # Ruby
        '.rb',
        # PHP
        '.php',
        # Swift
        '.swift',
        # Scala
        '.scala',
        # R
        '.r', '.R',
        # Shell scripts
        '.sh', '.bash',
        # SQL
        '.sql',
        # Other
        '.dart', '.lua', '.perl', '.pl'
    }
    
    def __init__(self, db_connection_string: str, gemini_api_key: str):
        """
        Initialize Repository Scanner.
        
        Args:
            db_connection_string: MongoDB connection string
            gemini_api_key: Google Gemini API key
            
        Raises:
            ConnectionError: If MongoDB connection fails
            ValueError: If API key is invalid
        """
        print("🔧 Initializing Repository Scanner...")
        
        # Initialize Skill Engine
        try:
            self.skill_engine = SkillEngine(api_key=gemini_api_key)
            print("✅ Skill Engine initialized")
        except Exception as e:
            raise ValueError(f"Failed to initialize Skill Engine: {e}")
        
        # Connect to MongoDB using pymongo (synchronous)
        try:
            self.db_client = pymongo.MongoClient(
                db_connection_string,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=10000
            )
            
            # Extract database name
            db_name = self._extract_database_name(db_connection_string)
            self.db = self.db_client[db_name]
            
            # Test connection
            self.db_client.admin.command('ping')
            print(f"✅ Connected to MongoDB database: {db_name}")
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            raise ConnectionError(f"Failed to connect to MongoDB: {e}")
    
    def _extract_database_name(self, connection_string: str) -> str:
        """Extract database name from MongoDB connection string."""
        try:
            if '/' in connection_string:
                db_part = connection_string.split('/')[-1]
                db_name = db_part.split('?')[0]
                if db_name:
                    return db_name
            return "student_progress"
        except Exception:
            return "student_progress"
    
    def scan_directory(self, directory_path: str) -> List[str]:
        """
        Recursively scan directory for code files.
        
        Args:
            directory_path: Target directory to scan
            
        Returns:
            List of absolute file paths to analyze
            
        Raises:
            FileNotFoundError: If directory doesn't exist
            ValueError: If directory is not accessible
        """
        directory = Path(directory_path).resolve()
        
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")
        
        if not directory.is_dir():
            raise ValueError(f"Path is not a directory: {directory}")
        
        print(f"\n📂 Scanning directory: {directory}")
        print(f"🔍 Looking for code files...")
        
        code_files = []
        
        # Recursively walk directory tree
        for root, dirs, files in os.walk(directory):
            # Filter out ignored directories (modify dirs in-place)
            dirs[:] = [d for d in dirs if d not in self.IGNORE_DIRS]
            
            # Find code files
            for file in files:
                if Path(file).suffix in self.VALID_EXTENSIONS:
                    file_path = os.path.join(root, file)
                    code_files.append(file_path)
        
        print(f"✅ Found {len(code_files)} code file(s)")
        
        if not code_files:
            print("⚠️  No code files found in directory")
        
        return code_files

    
    async def extract_skills_from_files(self, file_paths: List[str]) -> List[SkillTag]:
        """
        Analyze all files and extract skills with evidence.
        Implements 12-second delay between API calls to respect 5 RPM limit.
        
        Args:
            file_paths: List of file paths to analyze
            
        Returns:
            List of SkillTag objects with name, confidence, evidence_file
        """
        if not file_paths:
            return []
        
        print(f"\n🤖 Analyzing {len(file_paths)} file(s) with AI...")
        
        all_skills: Dict[str, SkillTag] = {}  # skill_name -> SkillTag
        
        for idx, file_path in enumerate(file_paths, 1):
            try:
                # Read file content
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Skip empty files
                if not content.strip():
                    continue
                
                # Analyze code with Skill Engine
                filename = Path(file_path).name
                print(f"  [{idx}/{len(file_paths)}] Analyzing: {filename}")
                skills_text = await self.skill_engine.analyze_code_file(filename, content)
                
                if skills_text:
                    # Parse skills from comma-separated string
                    skill_names = [s.strip() for s in skills_text.split(',') if s.strip()]
                    
                    # Create or update SkillTag objects
                    for skill_name in skill_names:
                        # Calculate relative path, or use absolute if outside project
                        try:
                            relative_path = str(Path(file_path).relative_to(Path.cwd()))
                        except ValueError:
                            # File is outside project directory, use absolute path
                            relative_path = str(Path(file_path))
                        
                        if skill_name in all_skills:
                            # Skill already exists, increase confidence
                            all_skills[skill_name].confidence = min(
                                1.0,
                                all_skills[skill_name].confidence + 0.1
                            )
                        else:
                            # New skill
                            all_skills[skill_name] = SkillTag(
                                name=skill_name,
                                confidence=0.8,  # Initial confidence
                                evidence_file=relative_path
                            )
                    
                    print(f"      Found: {skills_text}")
                
                # CRITICAL FIX: Respect Gemini Free Tier (5 Requests Per Minute)
                # 60 seconds / 5 requests = 12 seconds delay required
                if idx < len(file_paths):  # Don't delay after last file
                    print("   ⏳ Cooling down (12s) for API Rate Limit...")
                    await asyncio.sleep(12)
                
            except Exception as e:
                print(f"  ⚠️  Error analyzing {Path(file_path).name}: {e}")
                continue
        
        skill_list = list(all_skills.values())
        print(f"✅ Extracted {len(skill_list)} unique skill(s)")
        
        return skill_list
    
    async def aggregate_skills_summary(self, skills: List[SkillTag]) -> str:
        """
        Aggregate skills into a summary string for embedding generation.
        
        Args:
            skills: List of SkillTag objects
            
        Returns:
            Aggregated skill summary string
        """
        if not skills:
            return ""
        
        # Create summary with skill names and confidence
        skill_descriptions = []
        for skill in skills:
            skill_descriptions.append(f"{skill.name} (confidence: {skill.confidence:.2f})")
        
        summary = "Technical Skills: " + ", ".join([s.name for s in skills])
        return summary
    
    async def generate_master_embedding(self, skill_summary: str) -> List[float]:
        """
        Generate master embedding from aggregated skills using local SentenceTransformers.
        
        Args:
            skill_summary: Aggregated skill summary text
            
        Returns:
            384-dimensional embedding vector
            
        Raises:
            Exception: If embedding generation fails
        """
        print("\n🧠 Generating skill embedding (local, no API calls)...")
        
        try:
            embedding = self.skill_engine.generate_embedding(skill_summary)
            print(f"✅ Generated {len(embedding)}-dimensional embedding")
            return embedding
        except Exception as e:
            raise Exception(f"Failed to generate embedding: {e}")
    
    def update_user_profile(
        self,
        github_id: str,
        skills: List[SkillTag],
        embedding: List[float]
    ) -> None:
        """
        Update user document in MongoDB with skill profile.
        
        Args:
            github_id: User's GitHub ID
            skills: List of extracted SkillTag objects
            embedding: 768-dimensional embedding vector
            
        Raises:
            ValueError: If user not found
            Exception: If database update fails
        """
        print(f"\n💾 Updating skill profile for user: {github_id}")
        
        try:
            # Find user by GitHub ID
            user = self.db.users.find_one({"githubId": github_id})
            
            if not user:
                raise ValueError(f"User not found with GitHub ID: {github_id}")
            
            # Create UserSkillProfile
            skill_profile = UserSkillProfile(
                verified_skills=skills,
                skill_embedding=embedding,
                last_scanned=datetime.utcnow()
            )
            
            # Update user document
            result = self.db.users.update_one(
                {"githubId": github_id},
                {
                    "$set": {
                        "skill_profile": skill_profile.dict(by_alias=True),
                        "updatedAt": datetime.utcnow()
                    }
                }
            )
            
            if result.modified_count > 0:
                print(f"✅ Successfully updated skill profile")
                print(f"   - Skills: {len(skills)}")
                print(f"   - Embedding dimensions: {len(embedding)}")
                print(f"   - Last scanned: {skill_profile.last_scanned}")
            else:
                print("⚠️  No changes made to user profile")
            
        except ValueError:
            raise
        except Exception as e:
            raise Exception(f"Failed to update user profile: {e}")
    
    async def run(self, directory_path: str, github_id: str) -> None:
        """
        Execute complete repository scanning workflow.
        
        Args:
            directory_path: Target directory to scan
            github_id: User's GitHub ID
        """
        print("=" * 60)
        print("🚀 Starting Repository Scan")
        print("=" * 60)
        
        try:
            # Step 1: Scan directory for Python files
            file_paths = self.scan_directory(directory_path)
            
            if not file_paths:
                print("\n❌ No code files found. Exiting.")
                return
            
            # Step 2: Extract skills from files
            skills = await self.extract_skills_from_files(file_paths)
            
            if not skills:
                print("\n⚠️  No skills extracted. Exiting.")
                return
            
            # Display extracted skills
            print("\n📋 Extracted Skills:")
            for skill in sorted(skills, key=lambda s: s.confidence, reverse=True):
                print(f"   - {skill.name} (confidence: {skill.confidence:.2f})")
            
            # Step 3: Aggregate skills into summary
            skill_summary = await self.aggregate_skills_summary(skills)
            
            # Step 4: Generate master embedding
            embedding = await self.generate_master_embedding(skill_summary)
            
            # Step 5: Update user profile in MongoDB
            self.update_user_profile(github_id, skills, embedding)
            
            print("\n" + "=" * 60)
            print("✅ Repository Scan Complete!")
            print("=" * 60)
            
        except Exception as e:
            print(f"\n❌ Scan failed: {e}")
            raise
    
    def close(self):
        """Close database connection."""
        if self.db_client:
            self.db_client.close()
            print("🔌 Database connection closed")


def main():
    """Main entry point for CLI script."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='Scan local repository for technical skills and update user profile',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scan_local_repo.py --directory ./my-project --github-id john-doe
  python scan_local_repo.py --directory /path/to/repo --github-id jane-smith
        """
    )
    
    parser.add_argument(
        '--directory',
        required=True,
        help='Target directory to scan for code files'
    )
    
    parser.add_argument(
        '--github-id',
        required=True,
        help='User GitHub ID to update skill profile'
    )
    
    args = parser.parse_args()
    
    # Load configuration
    try:
        settings = get_settings()
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        print("💡 Make sure .env file is configured with required settings")
        sys.exit(1)
    
    # Validate Gemini API key
    if not settings.gemini_api_key:
        print("❌ GEMINI_API_KEY not configured")
        print("💡 Add GEMINI_API_KEY to your .env file")
        sys.exit(1)
    
    # Initialize scanner
    scanner = None
    try:
        scanner = RepositoryScanner(
            db_connection_string=settings.mongodb_connection_string,
            gemini_api_key=settings.gemini_api_key
        )
        
        # Run scanning workflow
        asyncio.run(scanner.run(args.directory, args.github_id))
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Scan interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)
    finally:
        if scanner:
            scanner.close()


if __name__ == "__main__":
    main()
