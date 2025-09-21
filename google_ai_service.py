"""
Google AI Services Integration - Essential Services Only
Provides AI-powered features using Google's Gemini API and Google Translate
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any

try:
    import google.generativeai as genai
    from google.cloud import translate_v2 as translate
    GOOGLE_AI_AVAILABLE = True
except ImportError:
    GOOGLE_AI_AVAILABLE = False
    logging.warning("Google AI libraries not available. Install with: pip install google-generativeai google-cloud-translate")

from config import Config

class GoogleAIService:
    """Main Google AI service class - Essential services only"""
    
    def __init__(self):
        self.config = Config()
        self.logger = logging.getLogger(__name__)
        
        if GOOGLE_AI_AVAILABLE:
            self._initialize_services()
        else:
            self.logger.warning("Google AI services not available")
    
    def _initialize_services(self):
        """Initialize essential Google AI services"""
        try:
            # Initialize Gemini API
            if self.config.GOOGLE_API_KEY:
                genai.configure(api_key=self.config.GOOGLE_API_KEY)
                self.gemini_model = genai.GenerativeModel('gemini-pro')
                self.logger.info("Gemini API initialized successfully")
            
            # Initialize Translation API
            if self.config.GOOGLE_CLOUD_PROJECT:
                self.translate_client = translate.Client()
                self.logger.info("Google Translate initialized successfully")
                
        except Exception as e:
            self.logger.error(f"Failed to initialize Google AI services: {e}")
    
    def generate_text(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.7) -> str:
        """Generate text using Gemini API"""
        if not GOOGLE_AI_AVAILABLE or not hasattr(self, 'gemini_model'):
            return self._fallback_text_generation(prompt)
        
        try:
            generation_config = genai.types.GenerationConfig(
                max_output_tokens=max_tokens,
                temperature=temperature,
            )
            
            response = self.gemini_model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            return response.text if response.text else self._fallback_text_generation(prompt)
            
        except Exception as e:
            self.logger.error(f"Gemini API error: {e}")
            return self._fallback_text_generation(prompt)
    
    def translate_text(self, text: str, target_language: str = 'en', source_language: str = None) -> str:
        """Translate text using Google Translate API"""
        if not GOOGLE_AI_AVAILABLE or not hasattr(self, 'translate_client'):
            return text  # Return original text if translation not available
        
        try:
            result = self.translate_client.translate(
                text,
                target_language=target_language,
                source_language=source_language
            )
            return result['translatedText']
            
        except Exception as e:
            self.logger.error(f"Translation error: {e}")
            return text
    
    def _fallback_text_generation(self, prompt: str) -> str:
        """Fallback text generation when AI services are unavailable"""
        fallback_responses = {
            "artisan_bio": "Passionate artisan creating beautiful handcrafted pieces with traditional techniques passed down through generations. Each creation tells a story of cultural heritage and artistic dedication.",
            "product_description": "Exquisite handcrafted item made with premium materials and traditional techniques. Perfect for those who appreciate authentic artisanal quality and unique design.",
            "story_title": "Artisan's Journey",
            "marketing_content": "Discover authentic handcrafted treasures that celebrate traditional artistry and cultural heritage.",
            "default": "Beautiful handcrafted creation that embodies traditional artistry and cultural heritage."
        }
        
        # Simple keyword matching for appropriate fallback
        prompt_lower = prompt.lower()
        if "bio" in prompt_lower or "artisan" in prompt_lower:
            return fallback_responses["artisan_bio"]
        elif "product" in prompt_lower or "description" in prompt_lower:
            return fallback_responses["product_description"]
        elif "title" in prompt_lower:
            return fallback_responses["story_title"]
        elif "marketing" in prompt_lower or "campaign" in prompt_lower:
            return fallback_responses["marketing_content"]
        else:
            return fallback_responses["default"]


class ArtisanStorytellingAgent:
    """AI agent for generating artisan stories and bios using Gemini"""
    
    def __init__(self):
        self.ai_service = GoogleAIService()
        self.logger = logging.getLogger(__name__)
    
    def generate_artisan_bio(self, artisan_data: Dict[str, Any], tone: str = "warm") -> str:
        """Generate artisan biography using Gemini"""
        prompt = f"""
        Create a compelling artisan biography with the following details:
        
        Name: {artisan_data.get('name', 'Artisan')}
        Craft: {artisan_data.get('craft_type', 'Traditional Craft')}
        Location: {artisan_data.get('location', 'India')}
        Experience: {artisan_data.get('experience_years', 10)} years
        Tone: {tone}
        
        Write a {tone} and engaging biography (150-200 words) that:
        1. Tells their personal story and journey into the craft
        2. Highlights their unique techniques or specializations
        3. Connects their work to cultural heritage
        4. Shows their passion and dedication
        5. Makes customers feel connected to the artisan
        
        Make it authentic, personal, and inspiring.
        """
        
        return self.ai_service.generate_text(prompt, max_tokens=300, temperature=0.8)
    
    def generate_story_title(self, artisan_data: Dict[str, Any], tone: str = "poetic") -> str:
        """Generate compelling story title using Gemini"""
        prompt = f"""
        Create a captivating story title for an artisan:
        
        Craft: {artisan_data.get('craft_type', 'Traditional Craft')}
        Location: {artisan_data.get('location', 'India')}
        Tone: {tone}
        
        Generate a {tone} title (3-6 words) that:
        1. Captures the essence of their craft
        2. Evokes emotion and curiosity
        3. Reflects cultural heritage
        4. Is memorable and shareable
        
        Examples: "Clay Whispers Ancient Secrets", "Threads of Heritage", "Carving Stories in Teak"
        
        Return only the title, no explanation.
        """
        
        title = self.ai_service.generate_text(prompt, max_tokens=50, temperature=0.9)
        return title.strip().strip('"').strip("'")
    
    def generate_product_description(self, product_data: Dict[str, Any], artisan_persona: str = "warm") -> str:
        """Generate product description with artisan's voice using Gemini"""
        prompt = f"""
        Write a product description in the artisan's voice:
        
        Product: {product_data.get('name', 'Handcrafted Item')}
        Category: {product_data.get('category', 'Craft')}
        Materials: {product_data.get('materials', 'Traditional materials')}
        Artisan Persona: {artisan_persona}
        
        Create a {artisan_persona} description (100-150 words) that:
        1. Describes the product from the artisan's perspective
        2. Explains the crafting process and techniques
        3. Highlights unique features and quality
        4. Connects to cultural significance
        5. Creates emotional connection with buyers
        
        Write in first person as if the artisan is speaking directly to the customer.
        """
        
        return self.ai_service.generate_text(prompt, max_tokens=250, temperature=0.7)


# Initialize global AI service instances
google_ai_service = GoogleAIService()
artisan_storytelling_agent = ArtisanStorytellingAgent()
