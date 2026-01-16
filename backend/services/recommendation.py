"""
Recommendation Service for job matching using local vector search.

Uses local SentenceTransformers for embedding generation and scikit-learn
for cosine similarity calculations. No cloud vector databases required.
"""

import logging
from typing import List, Optional
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# Load local embedder globally for efficiency
# 384-dimensional vector, fast and free
local_embedder = SentenceTransformer('all-MiniLM-L6-v2')


class CandidateMatch(BaseModel):
    """Candidate match result with user info and similarity score."""
    
    user: dict = Field(..., description="User document from MongoDB")
    match_score: float = Field(..., ge=0.0, le=1.0, description="Cosine similarity score")


class RecommendationService:
    """
    Service for finding students matching job descriptions using local vector search.
    
    Uses SentenceTransformers for embedding generation and scikit-learn for
    cosine similarity calculations. All operations run locally without external APIs.
    """
    
    def __init__(self, db: AsyncIOMotorDatabase):
        """
        Initialize Recommendation Service.
        
        Args:
            db: Motor async MongoDB database instance
        """
        self.db = db
        logger.info("Recommendation Service initialized with local SentenceTransformers")
    
    async def find_matching_students(
        self,
        job_description: str,
        top_k: int = 5,
        threshold: float = 0.6
    ) -> List[CandidateMatch]:
        """
        Find students matching a job description using cosine similarity.
        
        Args:
            job_description: Text describing job requirements
            top_k: Number of top candidates to return (default: 5)
            threshold: Minimum similarity score 0.0-1.0 (default: 0.6)
            
        Returns:
            List of CandidateMatch objects with user info and scores,
            sorted by match_score in descending order
            
        Raises:
            ValueError: If job_description is empty
            Exception: If database query or similarity calculation fails
        """
        if not job_description or not job_description.strip():
            raise ValueError("Job description cannot be empty")
        
        try:
            logger.info(f"Finding candidates for job description (threshold: {threshold}, top_k: {top_k})")
            
            # Step 1: Generate job embedding using local model
            logger.info("Generating job embedding using local SentenceTransformers")
            job_embedding = local_embedder.encode(job_description).tolist()
            
            if len(job_embedding) != 384:
                raise ValueError(f"Invalid job embedding dimensions: expected 384, got {len(job_embedding)}")
            
            # Step 2: Retrieve all users with skill embeddings from MongoDB
            logger.info("Retrieving users with skill embeddings from MongoDB")
            cursor = self.db.users.find(
                {"skill_profile.skill_embedding": {"$exists": True}},
                {
                    "_id": 1,
                    "githubId": 1,
                    "username": 1,
                    "email": 1,
                    "skill_profile": 1
                }
            )
            
            users = await cursor.to_list(length=None)
            
            if not users:
                logger.warning("No users found with skill embeddings")
                return []
            
            logger.info(f"Found {len(users)} users with skill embeddings")
            
            # Step 3: Extract embeddings into numpy array
            user_embeddings = []
            valid_users = []
            
            for user in users:
                try:
                    embedding = user['skill_profile']['skill_embedding']
                    
                    # Validate embedding dimensions
                    if len(embedding) != 384:
                        logger.warning(
                            f"Skipping user {user.get('username', 'unknown')}: "
                            f"invalid embedding dimensions ({len(embedding)})"
                        )
                        continue
                    
                    user_embeddings.append(embedding)
                    valid_users.append(user)
                    
                except (KeyError, TypeError) as e:
                    logger.warning(f"Skipping user with invalid skill profile: {e}")
                    continue
            
            if not valid_users:
                logger.warning("No valid user embeddings found")
                return []
            
            # Convert to numpy arrays for vectorized operations
            user_embeddings_array = np.array(user_embeddings)
            job_vector = np.array(job_embedding).reshape(1, -1)
            
            # Step 4: Calculate cosine similarities
            logger.info(f"Calculating cosine similarities for {len(valid_users)} users")
            similarities = cosine_similarity(job_vector, user_embeddings_array)[0]
            
            # Step 5: Filter and rank results
            matches = []
            for idx, score in enumerate(similarities):
                if score >= threshold:
                    matches.append(CandidateMatch(
                        user=valid_users[idx],
                        match_score=float(score)
                    ))
            
            # Step 6: Sort by score and return top K
            matches.sort(key=lambda x: x.match_score, reverse=True)
            top_matches = matches[:top_k]
            
            logger.info(f"Found {len(matches)} candidates above threshold, returning top {len(top_matches)}")
            
            return top_matches
            
        except ValueError:
            # Re-raise validation errors
            raise
        except Exception as e:
            logger.error(f"Failed to find matching students: {str(e)}")
            raise Exception(f"Candidate search failed: {str(e)}")
