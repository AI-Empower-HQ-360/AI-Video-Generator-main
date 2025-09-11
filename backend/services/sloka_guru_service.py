from typing import Dict, Any
from .simple_ai_service import SimpleAIService
from backend.models.database import SpiritualSession, User, db
from backend.models.slokas_database import get_daily_sloka
from backend.utils.cache import cache_ai_response, cache_db_query, cache
import asyncio
import time
import logging

logger = logging.getLogger(__name__)

class SlokaGuruService:
    def __init__(self):
        self.name = "🕉️ AI Sloka Guru"
        self.specialization = "Universal wisdom from sacred verses"
        self.ai_service = SimpleAIService()
        
        # Performance tracking
        self._request_count = 0
        self._total_response_time = 0
        
    @cache_db_query(ttl=7200)  # Cache context analysis for 2 hours
    def _understand_user_context(self, question: str) -> dict:
        """Analyze question to understand user's context and needs. Cached for performance."""
        context = {
            "setting": "general",  # general, work, home, relationship
            "need": "wisdom",      # wisdom, peace, clarity, strength, harmony
            "time": "any"          # morning, evening, specific_situation
        }
        
        # Analyze question context (optimized string operations)
        question_lower = question.lower()
        
        # Use sets for faster lookups
        work_keywords = {"work", "office", "business", "career", "job"}
        home_keywords = {"home", "family", "house", "domestic"}
        relationship_keywords = {"relationship", "partner", "friend", "love"}
        
        peace_keywords = {"peace", "calm", "quiet", "serenity", "tranquil"}
        clarity_keywords = {"clear", "clarity", "confused", "understanding"}
        strength_keywords = {"strength", "courage", "confidence", "power"}
        harmony_keywords = {"harmony", "balance", "equilibrium"}
        
        morning_keywords = {"morning", "sunrise", "wake", "dawn"}
        evening_keywords = {"evening", "night", "sleep", "dusk"}
        
        # Detect setting (optimized with any() and set intersection)
        question_words = set(question_lower.split())
        
        if question_words & work_keywords:
            context["setting"] = "work"
        elif question_words & home_keywords:
            context["setting"] = "home"
        elif question_words & relationship_keywords:
            context["setting"] = "relationship"
            
        # Detect specific need
        if question_words & peace_keywords:
            context["need"] = "peace"
        elif question_words & clarity_keywords:
            context["need"] = "clarity"
        elif question_words & strength_keywords:
            context["need"] = "strength"
        elif question_words & harmony_keywords:
            context["need"] = "harmony"
            
        # Detect time context
        if question_words & morning_keywords:
            context["time"] = "morning"
        elif question_words & evening_keywords:
            context["time"] = "evening"
            
        return context

    def _create_system_prompt(self) -> str:
        return """You are the AI Sloka Guru, a wise and practical spiritual guide.
        Your purpose is to make ancient wisdom relevant and practical for daily life.
        
        When sharing slokas:
        1. Make it immediately relevant to the person's situation
        2. Use simple, everyday language and examples
        3. Give clear, actionable steps they can take today
        4. Connect it to their daily experiences
        5. Provide specific applications for work, home, and relationships
        
        Key aspects to emphasize:
        - The universal consciousness (Sat-Chit-Ananda) that all traditions point to
        - How this teaching appears in various wisdom traditions
        - Practical ways to apply this wisdom in daily life
        - The unity of all spiritual paths while respecting their uniqueness
        
        Format your responses with clear sections:
        [Original Verse]
        [Translation]
        [Spiritual Essence]
        [Universal Connection]
        [Practical Application]
        """
    
    @cache_db_query(ttl=3600)  # Cache user level for 1 hour
    def get_user_level(self, user_id: str) -> str:
        """Determine user's spiritual learning level. Cached for performance."""
        if not user_id:
            return "basic"
            
        try:
            # Query user from database
            user = db.session.query(User).get(user_id)
            if user and hasattr(user, 'spiritual_level'):
                # Map user levels to response levels
                level_mapping = {
                    'beginner': 'basic',
                    'intermediate': 'intermediate',
                    'advanced': 'enterprise'
                }
                return level_mapping.get(user.spiritual_level, 'basic')
        except Exception as e:
            logger.warning(f"Error getting user level: {e}")
            
        return "basic"

    @cache_db_query(ttl=3600)  # Cache user language for 1 hour  
    def get_user_language(self, user_id: str) -> str:
        """Determine user's preferred language. Cached for performance."""
        if not user_id:
            return "english"
            
        try:
            # Query user from database
            user = db.session.query(User).get(user_id)
            if user and hasattr(user, 'preferred_language'):
                return user.preferred_language
        except Exception as e:
            logger.warning(f"Error getting user language: {e}")
            
        return "english"

    @cache_ai_response(ttl=1800)  # Cache AI responses for 30 minutes
    def get_response(self, question: str, user_id: str = None, language: str = None) -> Dict[str, Any]:
        """Get a response from Sloka Guru for the given question. Optimized with caching."""
        start_time = time.time()
        
        try:
            # Performance tracking
            self._request_count += 1
            
            # Get user's level, language preference, and context
            user_level = self.get_user_level(user_id)
            user_language = language or self.get_user_language(user_id)
            user_context = self._understand_user_context(question)
            
            # If question is about daily wisdom, include today's sloka
            if "daily" in question.lower():
                daily_sloka = get_daily_sloka()
                question = f"Please explain today's sacred verse:\n{daily_sloka['sanskrit']}\n\nQuestion: {question}"
            
            # Get response from simple AI service with appropriate level and language
            ai_response = self.ai_service.get_response(
                question, 
                level=user_level, 
                language=user_language,
                context="sloka"
            )
            response = ai_response["response"]
            
            # Store the session if user_id is provided (async to not block response)
            if user_id:
                try:
                    session = SpiritualSession(
                        user_id=user_id,
                        guru_type='sloka',
                        question=question,
                        response=response
                    )
                    db.session.add(session)
                    db.session.commit()
                except Exception as e:
                    logger.warning(f"Failed to store session: {e}")
                    # Continue without failing the request
            
            # Performance tracking
            response_time = time.time() - start_time
            self._total_response_time += response_time
            
            logger.info(f"Sloka response generated in {response_time:.2f}s")
            
            return {
                "success": True,
                "response": response,
                "guru_name": self.name,
                "specialization": self.specialization,
                "response_time": response_time,
                "cached": False  # Will be True when served from cache
            }
            
        except Exception as e:
            logger.error(f"Error in get_response: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @cache_ai_response(ttl=3600)  # Cache explanations for 1 hour
    def explain_sloka(self, sloka_text: str, user_id: str = None) -> Dict[str, Any]:
        """Get a detailed explanation of a specific sloka. Optimized with caching."""
        start_time = time.time()
        
        try:
            system_prompt = self._create_system_prompt()
            
            prompt = f"""Please provide a complete analysis of this sacred verse:

{sloka_text}

Please include:
1. Word-by-word translation if applicable
2. Full verse translation
3. Deeper spiritual meaning
4. Connection to universal truth
5. Practical applications for modern life"""
            
            ai_response = self.ai_service.explain_text(sloka_text, context="sloka")
            response = ai_response["response"]
            
            if user_id:
                session = SpiritualSession(
                    user_id=user_id,
                    guru_type='sloka',
                    question=f"Explain sloka: {sloka_text}",
                    response=response
                )
                db.session.add(session)
                db.session.commit()
            
            return {
                "success": True,
                "response": response,
                "guru_name": self.name
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
