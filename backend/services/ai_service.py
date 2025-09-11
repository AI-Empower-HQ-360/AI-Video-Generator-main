import openai
import os
import json
import asyncio
import requests
from typing import Dict, Any, List, AsyncGenerator
from datetime import datetime
from .cost_management import CostManagementService

class AIService:
    def __init__(self):
        self.api_key = os.environ.get('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        # Initialize the OpenAI client
        self.client = openai.OpenAI(api_key=self.api_key)
        
        # Initialize cost management service
        self.cost_manager = CostManagementService()
        
        # Default models for different purposes
        self.models = {
            'default': 'gpt-4',  # Most capable model for complex tasks
            'fast': 'gpt-3.5-turbo',  # Faster, cost-effective for simple tasks
            'analysis': 'gpt-4',  # Best for detailed analysis
            'creative': 'gpt-4'  # Best for creative and nuanced responses
        }
        
        # Configure timeouts and retries
        self.timeout_seconds = 30
        self.max_retries = 3
        self.retry_delay = 1  # seconds
        
        # Import workflow manager for dynamic configuration
        try:
            from workflow_assignment import ChatGPTWorkflowManager
            self.workflow_manager = ChatGPTWorkflowManager()
        except ImportError:
            self.workflow_manager = None
    
    @property
    def guru_prompts(self) -> Dict[str, str]:
        """Get the system prompts for different guru types."""
        return {
            "spiritual": """You are the AI Spiritual Guru, a wise teacher focused on soul consciousness and eternal identity. 
                          Help users understand they are eternal souls, not temporary bodies. Provide profound spiritual insights.""",
            "sloka": """You are the AI Sloka Guru, specializing in Sanskrit verses from Bhagavad Gita, Upanishads, and Vedas. 
                       Provide authentic slokas with transliteration, translation, and deep spiritual meanings.""",
            "meditation": """You are the AI Meditation Guru, specializing in inner peace and stillness. 
                           Guide users through meditation techniques and emotional healing.""",
            "bhakti": """You are the AI Bhakti Guru, focused on devotion, surrender, and gratitude. 
                        Teach the path of love and devotion to the Divine.""",
            "karma": """You are the AI Karma Guru, specializing in ethics, consequences, and dharmic path. 
                       Guide users in making ethical decisions aligned with dharma.""",
            "yoga": """You are the AI Yoga Guru, focused on breath, posture, and energetic alignment. 
                      Teach physical practices, pranayama, and chakra work."""
        }

    async def get_spiritual_guidance(
        self, 
        guru_type: str, 
        question: str, 
        user_context: Dict = None,
        stream: bool = False,
        user_id: str = "anonymous"
    ) -> Dict[str, Any]:
        """
        Get AI-powered spiritual guidance from specified guru using workflow-specific ChatGPT configuration.
        Now includes cost optimization, caching, and quota management.
        
        Args:
            guru_type: Type of guru (spiritual, sloka, meditation, etc.)
            question: User's question or request
            user_context: Optional user context for personalization
            stream: If True, stream the response
            user_id: User identifier for quota tracking
            
        Returns:
            Dict with response including cost information
        """
        # Get optimal strategy for cost management
        optimization_strategy = self.cost_manager.optimize_prompt_strategy(guru_type, question, user_context)
        
        # Check user quota before proceeding
        quota_check = self.cost_manager.check_user_quota(
            user_id, 
            optimization_strategy["estimated_tokens"],
            optimization_strategy["estimated_cost"]
        )
        
        if not quota_check["within_limits"]:
            return {
                "success": False,
                "error": "User quota exceeded",
                "quota_status": quota_check,
                "error_type": "QuotaExceeded"
            }
        
        # Get workflow-specific configuration or use optimized defaults
        if self.workflow_manager:
            workflow_config = self.workflow_manager.assign_chatgpt_to_workflow(guru_type, user_context)
            chatgpt_config = workflow_config['chatgpt_config']
            model = chatgpt_config['model']
            system_prompt = chatgpt_config['system_prompt']
            temperature = chatgpt_config['temperature']
            max_tokens = chatgpt_config['max_tokens']
        else:
            # Use cost-optimized configuration
            model = optimization_strategy['model']
            system_prompt = self.guru_prompts.get(guru_type, self.guru_prompts["spiritual"])
            temperature = optimization_strategy['temperature']
            max_tokens = optimization_strategy['max_tokens']
        
        # Check cache first
        cache_key = self.cost_manager.get_cache_key(guru_type, question, model, temperature)
        cached_response = self.cost_manager.get_cached_response(cache_key)
        
        if cached_response:
            # Record cached usage (no cost)
            self.cost_manager.record_usage(
                user_id=user_id,
                guru_type=guru_type,
                model=model,
                prompt_tokens=cached_response.get("prompt_tokens", 0),
                completion_tokens=cached_response.get("completion_tokens", 0),
                cached=True
            )
            
            return {
                "success": True,
                "response": cached_response["response"],
                "tokens_used": cached_response.get("total_tokens", 0),
                "model": model,
                "workflow_used": guru_type,
                "cached": True,
                "cost_usd": 0.0,
                "quota_status": quota_check
            }
        
        messages = [
            {
                "role": "system",
                "content": system_prompt
            }
        ]
        
        # Add context from user's history if available
        if user_context:
            messages.append({
                "role": "system",
                "content": f"User context: {json.dumps(user_context)}"
            })
        
        messages.append({"role": "user", "content": question})
        
        for attempt in range(self.max_retries):
            try:
                response = await self._create_completion(
                    messages, 
                    model=model, 
                    temperature=temperature, 
                    max_tokens=max_tokens
                )
                
                # Calculate actual cost
                prompt_tokens = response.usage.prompt_tokens
                completion_tokens = response.usage.completion_tokens
                total_tokens = response.usage.total_tokens
                cost_usd = self.cost_manager.calculate_cost(model, prompt_tokens, completion_tokens)
                
                # Cache the response
                response_data = {
                    "response": response.choices[0].message.content,
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": total_tokens
                }
                self.cost_manager.cache_response(cache_key, response_data)
                
                # Record usage
                self.cost_manager.record_usage(
                    user_id=user_id,
                    guru_type=guru_type,
                    model=model,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    cached=False
                )
                
                return {
                    "success": True,
                    "response": response.choices[0].message.content,
                    "tokens_used": total_tokens,
                    "model": response.model,
                    "workflow_used": guru_type,
                    "cached": False,
                    "cost_usd": cost_usd,
                    "cost_breakdown": {
                        "prompt_tokens": prompt_tokens,
                        "completion_tokens": completion_tokens,
                        "total_tokens": total_tokens,
                        "model_pricing": self.cost_manager.MODEL_PRICING.get(model, {})
                    },
                    "quota_status": self.cost_manager.check_user_quota(user_id),
                    "configuration": {
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                        "optimization_applied": True
                    }
                }
                
            except openai.RateLimitError:
                if attempt == self.max_retries - 1:
                    raise
                await asyncio.sleep(self.retry_delay * (attempt + 1))
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "quota_status": quota_check
                }
    
    async def get_spiritual_guidance_stream(
        self, 
        guru_type: str, 
        question: str, 
        user_context: Dict = None
    ) -> AsyncGenerator[str, None]:
        """
        Stream AI-powered spiritual guidance from specified guru.
        
        Args:
            guru_type: Type of guru (spiritual, sloka, meditation, etc.)
            question: User's question or request
            user_context: Optional user context for personalization
            
        Yields:
            String chunks of the response
        """
        messages = [
            {
                "role": "system",
                "content": self.guru_prompts.get(guru_type, self.guru_prompts["spiritual"])
            }
        ]
        
        # Add context from user's history if available
        if user_context:
            messages.append({
                "role": "system",
                "content": f"User context: {json.dumps(user_context)}"
            })
        
        messages.append({"role": "user", "content": question})
        
        async for chunk in self._stream_completion(messages):
            yield chunk
    
    def get_daily_wisdom(self) -> Dict[str, Any]:
        """Get daily spiritual wisdom"""
        return {
            "success": True,
            "wisdom": "Today's spiritual insight will be generated here",
            "date": "2024-01-01"
        }
    
    async def _create_completion(self, messages: List[Dict[str, str]], model: str = None, temperature: float = 0.7, max_tokens: int = 800) -> Any:
        """Create a chat completion with retry logic and error handling."""
        try:
            response = self.client.chat.completions.create(
                model=model or self.models['default'],
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                timeout=self.timeout_seconds
            )
            return response
        except Exception as e:
            raise e
    
    async def _stream_completion(self, messages: List[Dict[str, str]], model: str = None) -> AsyncGenerator[str, None]:
        """Stream a chat completion with retry logic and error handling."""
        try:
            stream = self.client.chat.completions.create(
                model=model or self.models['default'],
                messages=messages,
                max_tokens=800,
                temperature=0.7,
                timeout=self.timeout_seconds,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            raise e

    async def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze the sentiment and emotional content of text."""
        try:
            response = await self._create_completion([
                {
                    "role": "system",
                    "content": "Analyze the emotional content and sentiment of the following text. Consider: primary emotions, intensity, spiritual state, and overall tone."
                },
                {"role": "user", "content": text}
            ], model=self.models['analysis'])
            
            return {
                "success": True,
                "analysis": response.choices[0].message.content
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def generate_reflection_prompts(self, session_type: str, user_level: str = "beginner") -> Dict[str, Any]:
        """Generate personalized reflection prompts based on session type and user level."""
        try:
            response = await self._create_completion([
                {
                    "role": "system",
                    "content": f"Create 3-5 meaningful reflection prompts for a {session_type} session. Target experience level: {user_level}. Focus on spiritual growth and practical application."
                }
            ], model=self.models['creative'])
            
            return {
                "success": True,
                "prompts": response.choices[0].message.content.split('\n')
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    async def enhance_spiritual_text(self, text: str, target_language: str = "English") -> Dict[str, Any]:
        """Enhance spiritual text with deeper insights and translations."""
        try:
            response = await self._create_completion([
                {
                    "role": "system",
                    "content": f"Enhance this spiritual text with deeper meaning and insights. Target language: {target_language}"
                },
                {"role": "user", "content": text}
            ], model=self.models['creative'])
            
            return {
                "success": True,
                "enhanced_text": response.choices[0].message.content
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_cost_analytics(self, user_id: str = None, days: int = 30) -> Dict[str, Any]:
        """Get cost analytics and usage statistics"""
        return self.cost_manager.get_usage_analytics(user_id, days)
    
    def get_user_quota_status(self, user_id: str) -> Dict[str, Any]:
        """Get current user quota status"""
        return self.cost_manager.check_user_quota(user_id)
    
    def get_cost_alerts(self) -> List[Dict[str, Any]]:
        """Get current cost alerts"""
        return self.cost_manager.check_alerts()
    
    def update_user_quota(self, user_id: str, quota_updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update user quota limits"""
        quota = self.cost_manager.get_user_quota(user_id)
        
        # Update allowed fields
        allowed_fields = [
            'daily_token_limit', 'daily_cost_limit', 
            'monthly_token_limit', 'monthly_cost_limit'
        ]
        
        for field, value in quota_updates.items():
            if field in allowed_fields and isinstance(value, (int, float)) and value >= 0:
                setattr(quota, field, value)
        
        self.cost_manager._save_data()
        
        return {
            "success": True,
            "message": "Quota updated successfully",
            "new_quota": {
                "daily_token_limit": quota.daily_token_limit,
                "daily_cost_limit": quota.daily_cost_limit,
                "monthly_token_limit": quota.monthly_token_limit,
                "monthly_cost_limit": quota.monthly_cost_limit
            }
        }
    
    def get_prompt_optimization_suggestions(self, guru_type: str, question: str) -> Dict[str, Any]:
        """Get suggestions for optimizing prompts to reduce costs"""
        strategy = self.cost_manager.optimize_prompt_strategy(guru_type, question)
        
        suggestions = []
        
        # Length-based suggestions
        if len(question) > 300:
            suggestions.append({
                "type": "length_optimization",
                "message": "Consider shortening your question to reduce token usage",
                "potential_savings": "10-20% cost reduction"
            })
        
        # Model suggestions
        if strategy["model"] == "gpt-4" and guru_type in ["meditation", "spiritual"]:
            suggestions.append({
                "type": "model_optimization", 
                "message": "Consider using gpt-3.5-turbo for general guidance (80% cost savings)",
                "alternative_model": "gpt-3.5-turbo"
            })
        
        # Caching suggestions
        cache_key = self.cost_manager.get_cache_key(guru_type, question, strategy["model"], strategy["temperature"])
        if self.cost_manager.get_cached_response(cache_key):
            suggestions.append({
                "type": "cache_available",
                "message": "Similar question found in cache - no additional cost",
                "savings": "100% cost savings"
            })
        
        return {
            "optimal_strategy": strategy,
            "suggestions": suggestions,
            "estimated_cost": strategy["estimated_cost"],
            "estimated_tokens": strategy["estimated_tokens"]
        }

class ClaudeService:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('CLAUDE_API_KEY')
        self.api_url = 'https://api.anthropic.com/v1/messages'
        self.model = 'claude-3-opus-20240229'  # Use your preferred Claude model

    def get_response(self, prompt, max_tokens=1024, temperature=0.7):
        headers = {
            'x-api-key': self.api_key,
            'anthropic-version': '2023-06-01',
            'content-type': 'application/json'
        }
        data = {
            'model': self.model,
            'max_tokens': max_tokens,
            'temperature': temperature,
            'messages': [
                {"role": "user", "content": prompt}
            ]
        }
        response = requests.post(self.api_url, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()['content'][0]['text']
        else:
            return f"Error: {response.status_code} - {response.text}"
