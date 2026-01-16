"""
Skill Engine AI module for code analysis and embedding generation.
Uses Google Gemini Flash for fast code analysis and local SentenceTransformers for semantic vectors.
"""

import asyncio
import logging
from typing import List, Optional
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from sentence_transformers import SentenceTransformer
from backend.config import get_settings

logger = logging.getLogger(__name__)

# Load local embedder globally (downloads once, runs offline)
# 384-dimensional vector, fast and free
local_embedder = SentenceTransformer('all-MiniLM-L6-v2')


class SkillEngine:
    """AI-powered skill extraction and embedding generation using Google Gemini Flash and local SentenceTransformers."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Skill Engine with Gemini API key.
        
        Args:
            api_key: Optional Gemini API key. If not provided, loads from config.
            
        Raises:
            ValueError: If API key is not provided and not found in config
        """
        # Load API key from config if not provided
        if api_key is None:
            settings = get_settings()
            api_key = settings.gemini_api_key
        
        if not api_key:
            raise ValueError("Gemini API key is required for Skill Engine")
        
        self.api_key = api_key
        
        # Configure Gemini API
        genai.configure(api_key=self.api_key)
        
        # Initialize Flash model for code analysis
        self.flash_model = genai.GenerativeModel(
            model_name='gemini-2.0-flash',
            safety_settings={
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }
        )
        
        logger.info("Skill Engine initialized with Gemini Flash and local SentenceTransformers")
    
    async def analyze_code_file(self, filename: str, content: str) -> str:
        """
        Analyze code content and extract technical skills using Gemini Flash.
        
        Args:
            filename: Name of the file being analyzed
            content: Source code file content
            
        Returns:
            Comma-separated string of technical skills
            Example: "FastAPI, AsyncIO, MongoDB"
            
        Raises:
            Exception: If API call fails or response is invalid
        """
        try:
            logger.info(f"Analyzing code file: {filename}")
            
            # Craft prompt optimized for skill extraction
            prompt = self._create_skill_extraction_prompt(filename, content)
            
            # Generate response using Gemini Flash
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.flash_model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.1,  # Low temperature for consistent extraction
                        max_output_tokens=512,
                        top_p=0.8,
                        top_k=40
                    )
                )
            )
            
            if not response.text:
                logger.warning("Empty response from Gemini Flash API")
                return ""
            
            # Extract and clean skills from response
            skills = self._parse_skills_response(response.text)
            
            logger.info(f"Extracted skills: {skills}")
            return skills
            
        except Exception as e:
            logger.error(f"Code analysis failed: {str(e)}")
            return ""  # Return empty string on error instead of raising
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate 384-dimensional embedding vector locally using SentenceTransformers.
        
        Args:
            text: Skill summary or job description text
            
        Returns:
            List of 384 floats representing semantic embedding
            
        Note:
            - Runs completely offline after initial model download
            - No API calls, no rate limits, zero cost
            - Uses all-MiniLM-L6-v2 model for fast, efficient embeddings
            
        Raises:
            ValueError: If embedding dimensions are incorrect
        """
        try:
            logger.info("Generating embedding vector using local SentenceTransformers")
            
            # Generate embedding using local model
            # encode returns numpy array, convert to list for MongoDB
            embedding = local_embedder.encode(text).tolist()
            
            # Validate dimensions
            if len(embedding) != 384:
                raise ValueError(
                    f"Invalid embedding dimensions: expected 384, got {len(embedding)}"
                )
            
            logger.info(f"Generated embedding with {len(embedding)} dimensions")
            return embedding
            
        except ValueError:
            # Re-raise validation errors
            raise
        except Exception as e:
            logger.error(f"Embedding generation failed: {str(e)}")
            raise Exception(f"Failed to generate embedding: {str(e)}")
    
    def _create_skill_extraction_prompt(self, filename: str, code_content: str) -> str:
        """
        Create optimized prompt for skill extraction from code.
        
        Args:
            filename: Name of the file being analyzed
            code_content: Source code to analyze
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""Analyze this code file: '{filename}'.
Identify the top 3 specific technical skills/libraries used.
Return ONLY a comma-separated list.

CODE:
{code_content[:3000]}

Technical Skills:"""
        
        return prompt
    
    def _parse_skills_response(self, response_text: str) -> str:
        """
        Parse and clean skills from Gemini response.
        
        Args:
            response_text: Raw response from Gemini
            
        Returns:
            Cleaned comma-separated skills string
        """
        # Remove common markdown formatting
        cleaned = response_text.strip()
        cleaned = cleaned.replace('```', '')
        cleaned = cleaned.replace('**', '')
        cleaned = cleaned.replace('*', '')
        
        # Remove any leading labels
        if ':' in cleaned[:50]:
            cleaned = cleaned.split(':', 1)[1].strip()
        
        # Remove newlines and extra spaces
        cleaned = ' '.join(cleaned.split())
        
        # Ensure it's a comma-separated list
        if '\n' in cleaned:
            # Convert newline-separated to comma-separated
            skills = [s.strip() for s in cleaned.split('\n') if s.strip()]
            cleaned = ', '.join(skills)
        
        return cleaned


# Global instance cache
_skill_engine: Optional[SkillEngine] = None


def get_skill_engine() -> SkillEngine:
    """Get or create Skill Engine singleton."""
    global _skill_engine
    if _skill_engine is None:
        _skill_engine = SkillEngine()
    return _skill_engine
