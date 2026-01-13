"""
Google Gemini API client for AI feedback generation.
Handles communication with Google Gemini Flash API for fast feedback generation.
"""

import asyncio
import logging
from typing import Dict, Any, Optional
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from backend.config import get_settings

logger = logging.getLogger(__name__)


class GeminiClient:
    """Client for Google Gemini Flash API integration."""
    
    def __init__(self):
        """Initialize Gemini client with configuration."""
        self.settings = get_settings()
        if not self.settings.gemini_api_key:
            raise ValueError("Gemini API key is required")
        
        # Configure Gemini API
        genai.configure(api_key=self.settings.gemini_api_key)
        
        # Initialize model with safety settings
        self.model = genai.GenerativeModel(
            model_name=self.settings.gemini_model,
            safety_settings={
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            }
        )
        
        # Generation configuration optimized for Flash model
        self.generation_config = genai.types.GenerationConfig(
            temperature=self.settings.gemini_temperature,
            max_output_tokens=self.settings.gemini_max_output_tokens,
            top_p=0.8,
            top_k=40
        )
    
    async def generate_feedback(self, prompt: str) -> Dict[str, Any]:
        """
        Generate AI feedback using Gemini Flash API.
        
        Args:
            prompt: The formatted prompt for feedback generation
            
        Returns:
            Dict containing parsed feedback response
            
        Raises:
            Exception: If API call fails or response is invalid
        """
        try:
            logger.info("Generating AI feedback with Gemini Flash API")
            
            # Use asyncio to run the synchronous Gemini API call
            response = await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda: self.model.generate_content(
                    prompt,
                    generation_config=self.generation_config
                )
            )
            
            if not response.text:
                raise ValueError("Empty response from Gemini API")
            
            logger.info("Successfully generated AI feedback")
            return self._parse_response(response.text)
            
        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            raise Exception(f"Failed to generate AI feedback: {str(e)}")
    
    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse Gemini Flash API response into structured feedback.
        
        Args:
            response_text: Raw response text from Gemini
            
        Returns:
            Dict with quality_score, strengths, issues, suggestions
        """
        try:
            # Initialize default structure
            feedback = {
                "quality_score": 5.0,
                "strengths": [],
                "issues": [],
                "suggestions": []
            }
            
            lines = response_text.strip().split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Parse quality score
                if line.lower().startswith('quality score:') or line.lower().startswith('score:'):
                    try:
                        score_text = line.split(':', 1)[1].strip()
                        # Extract numeric value (handle formats like "7.5/10" or "7.5")
                        score_parts = score_text.split('/')
                        score = float(score_parts[0])
                        if len(score_parts) > 1 and score_parts[1].strip() == '10':
                            feedback["quality_score"] = score
                        else:
                            # Assume it's already on 0-10 scale
                            feedback["quality_score"] = min(10.0, max(0.0, score))
                    except (ValueError, IndexError):
                        logger.warning(f"Could not parse quality score from: {line}")
                
                # Identify sections
                elif line.lower().startswith('strengths:') or line.lower().startswith('**strengths'):
                    current_section = 'strengths'
                elif line.lower().startswith('issues:') or line.lower().startswith('**issues') or line.lower().startswith('areas for improvement:'):
                    current_section = 'issues'
                elif line.lower().startswith('suggestions:') or line.lower().startswith('**suggestions') or line.lower().startswith('recommendations:'):
                    current_section = 'suggestions'
                
                # Parse list items
                elif line.startswith('-') or line.startswith('•') or line.startswith('*'):
                    item = line[1:].strip()
                    if current_section and item:
                        feedback[current_section].append(item)
                
                # Parse numbered items
                elif current_section and (line[0].isdigit() and '.' in line[:3]):
                    item = line.split('.', 1)[1].strip()
                    if item:
                        feedback[current_section].append(item)
            
            # Ensure we have at least some content
            if not any([feedback["strengths"], feedback["issues"], feedback["suggestions"]]):
                # Fallback: treat entire response as a general suggestion
                feedback["suggestions"] = [response_text.strip()]
            
            logger.info(f"Parsed feedback: score={feedback['quality_score']}, "
                       f"strengths={len(feedback['strengths'])}, "
                       f"issues={len(feedback['issues'])}, "
                       f"suggestions={len(feedback['suggestions'])}")
            
            return feedback
            
        except Exception as e:
            logger.error(f"Error parsing Gemini response: {str(e)}")
            # Return fallback response
            return {
                "quality_score": 5.0,
                "strengths": ["Code analysis completed"],
                "issues": ["Unable to parse detailed feedback"],
                "suggestions": ["Please review the code manually for improvements"]
            }
    
    async def test_connection(self) -> bool:
        """
        Test connection to Gemini API.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            test_prompt = "Please respond with 'Connection successful' if you can read this."
            response = await self.generate_feedback(test_prompt)
            return True
        except Exception as e:
            logger.error(f"Gemini API connection test failed: {str(e)}")
            return False


# Global client instance
_gemini_client: Optional[GeminiClient] = None


def get_gemini_client() -> GeminiClient:
    """Get or create Gemini client singleton."""
    global _gemini_client
    if _gemini_client is None:
        _gemini_client = GeminiClient()
    return _gemini_client