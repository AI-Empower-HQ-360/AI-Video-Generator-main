"""
Cost Management Service for AI API usage optimization
Provides cost tracking, user quotas, caching, and alerting
"""
import os
import json
import time
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from collections import defaultdict


@dataclass
class APIUsage:
    """Track API usage details"""
    timestamp: datetime
    user_id: str
    guru_type: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost_usd: float
    cached: bool = False


@dataclass
class UserQuota:
    """User quota configuration"""
    user_id: str
    daily_token_limit: int = 10000
    daily_cost_limit: float = 5.0
    monthly_token_limit: int = 100000
    monthly_cost_limit: float = 50.0
    current_daily_tokens: int = 0
    current_daily_cost: float = 0.0
    current_monthly_tokens: int = 0
    current_monthly_cost: float = 0.0
    last_reset_date: str = ""


class CostManagementService:
    """Manages AI API costs, caching, and user quotas"""
    
    # Model pricing per 1K tokens (as of 2024)
    MODEL_PRICING = {
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-4-32k": {"input": 0.06, "output": 0.12},
        "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002},
        "gpt-3.5-turbo-16k": {"input": 0.003, "output": 0.004},
        "claude-3-opus-20240229": {"input": 0.015, "output": 0.075},
        "claude-3-sonnet-20240229": {"input": 0.003, "output": 0.015},
        "claude-3-haiku-20240307": {"input": 0.00025, "output": 0.00125}
    }
    
    def __init__(self, data_dir: str = None):
        self.data_dir = data_dir or os.path.join(os.path.dirname(__file__), "..", "data")
        os.makedirs(self.data_dir, exist_ok=True)
        
        # In-memory caches
        self.response_cache: Dict[str, Dict] = {}
        self.usage_history: List[APIUsage] = []
        self.user_quotas: Dict[str, UserQuota] = {}
        
        # Cache configuration
        self.cache_ttl = 3600  # 1 hour default
        self.max_cache_size = 1000
        
        # Cost thresholds for alerts
        self.alert_thresholds = {
            "daily_cost": 10.0,
            "monthly_cost": 100.0,
            "user_daily_cost": 5.0,
            "user_monthly_cost": 50.0
        }
        
        self._load_data()
    
    def calculate_cost(self, model: str, prompt_tokens: int, completion_tokens: int) -> float:
        """Calculate cost for API usage"""
        if model not in self.MODEL_PRICING:
            # Default to gpt-3.5-turbo pricing for unknown models
            pricing = self.MODEL_PRICING["gpt-3.5-turbo"]
        else:
            pricing = self.MODEL_PRICING[model]
        
        input_cost = (prompt_tokens / 1000) * pricing["input"]
        output_cost = (completion_tokens / 1000) * pricing["output"]
        return round(input_cost + output_cost, 6)
    
    def get_cache_key(self, guru_type: str, prompt: str, model: str, temperature: float) -> str:
        """Generate cache key for API responses"""
        cache_string = f"{guru_type}:{model}:{temperature}:{prompt}"
        return hashlib.md5(cache_string.encode()).hexdigest()
    
    def get_cached_response(self, cache_key: str) -> Optional[Dict]:
        """Retrieve cached response if available and not expired"""
        if cache_key not in self.response_cache:
            return None
        
        cached_data = self.response_cache[cache_key]
        
        # Check if cache entry has expired
        if time.time() - cached_data["timestamp"] > self.cache_ttl:
            del self.response_cache[cache_key]
            return None
        
        return cached_data["response"]
    
    def cache_response(self, cache_key: str, response: Dict) -> None:
        """Cache API response"""
        # Remove oldest entries if cache is full
        if len(self.response_cache) >= self.max_cache_size:
            oldest_key = min(self.response_cache.keys(), 
                           key=lambda k: self.response_cache[k]["timestamp"])
            del self.response_cache[oldest_key]
        
        self.response_cache[cache_key] = {
            "response": response,
            "timestamp": time.time()
        }
    
    def check_user_quota(self, user_id: str, estimated_tokens: int = 0, estimated_cost: float = 0.0) -> Dict[str, Any]:
        """Check if user is within quota limits"""
        quota = self.get_user_quota(user_id)
        
        # Reset quotas if new day/month
        self._reset_quotas_if_needed(quota)
        
        # Check daily limits
        daily_tokens_ok = (quota.current_daily_tokens + estimated_tokens) <= quota.daily_token_limit
        daily_cost_ok = (quota.current_daily_cost + estimated_cost) <= quota.daily_cost_limit
        
        # Check monthly limits  
        monthly_tokens_ok = (quota.current_monthly_tokens + estimated_tokens) <= quota.monthly_token_limit
        monthly_cost_ok = (quota.current_monthly_cost + estimated_cost) <= quota.monthly_cost_limit
        
        within_limits = daily_tokens_ok and daily_cost_ok and monthly_tokens_ok and monthly_cost_ok
        
        return {
            "within_limits": within_limits,
            "daily_tokens_remaining": max(0, quota.daily_token_limit - quota.current_daily_tokens),
            "daily_cost_remaining": max(0, quota.daily_cost_limit - quota.current_daily_cost),
            "monthly_tokens_remaining": max(0, quota.monthly_token_limit - quota.current_monthly_tokens),
            "monthly_cost_remaining": max(0, quota.monthly_cost_limit - quota.current_monthly_cost),
            "limits_exceeded": {
                "daily_tokens": not daily_tokens_ok,
                "daily_cost": not daily_cost_ok,
                "monthly_tokens": not monthly_tokens_ok,
                "monthly_cost": not monthly_cost_ok
            }
        }
    
    def record_usage(self, user_id: str, guru_type: str, model: str, 
                    prompt_tokens: int, completion_tokens: int, cached: bool = False) -> APIUsage:
        """Record API usage and update quotas"""
        total_tokens = prompt_tokens + completion_tokens
        cost = self.calculate_cost(model, prompt_tokens, completion_tokens) if not cached else 0.0
        
        usage = APIUsage(
            timestamp=datetime.utcnow(),
            user_id=user_id,
            guru_type=guru_type,
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            cost_usd=cost,
            cached=cached
        )
        
        self.usage_history.append(usage)
        
        # Update user quota
        quota = self.get_user_quota(user_id)
        quota.current_daily_tokens += total_tokens
        quota.current_daily_cost += cost
        quota.current_monthly_tokens += total_tokens
        quota.current_monthly_cost += cost
        
        self._save_data()
        return usage
    
    def get_user_quota(self, user_id: str) -> UserQuota:
        """Get or create user quota"""
        if user_id not in self.user_quotas:
            self.user_quotas[user_id] = UserQuota(
                user_id=user_id,
                last_reset_date=datetime.utcnow().strftime("%Y-%m-%d")
            )
        return self.user_quotas[user_id]
    
    def optimize_prompt_strategy(self, guru_type: str, question: str, user_context: Dict = None) -> Dict[str, Any]:
        """Suggest optimal prompt strategy to minimize costs"""
        strategies = {
            "spiritual": {
                "model": "gpt-3.5-turbo",  # Cost-effective for general guidance
                "max_tokens": 400,
                "temperature": 0.7,
                "system_prompt_optimization": "concise_wisdom"
            },
            "sloka": {
                "model": "gpt-4",  # Need accuracy for Sanskrit
                "max_tokens": 600,
                "temperature": 0.3,
                "system_prompt_optimization": "structured_response"
            },
            "meditation": {
                "model": "gpt-3.5-turbo",
                "max_tokens": 300,
                "temperature": 0.8,
                "system_prompt_optimization": "guided_practice"
            }
        }
        
        # Default strategy
        default_strategy = {
            "model": "gpt-3.5-turbo",
            "max_tokens": 400,
            "temperature": 0.7,
            "system_prompt_optimization": "balanced"
        }
        
        strategy = strategies.get(guru_type, default_strategy)
        
        # Adjust based on question complexity
        if len(question) > 200:
            strategy["max_tokens"] = min(strategy["max_tokens"] + 100, 800)
        
        # Estimate cost
        estimated_prompt_tokens = len(question.split()) * 1.3  # Rough estimation
        estimated_completion_tokens = strategy["max_tokens"] * 0.8  # Typical usage
        estimated_cost = self.calculate_cost(
            strategy["model"], 
            int(estimated_prompt_tokens), 
            int(estimated_completion_tokens)
        )
        
        strategy["estimated_cost"] = estimated_cost
        strategy["estimated_tokens"] = int(estimated_prompt_tokens + estimated_completion_tokens)
        
        return strategy
    
    def get_usage_analytics(self, user_id: str = None, days: int = 30) -> Dict[str, Any]:
        """Get usage analytics and cost breakdown"""
        since_date = datetime.utcnow() - timedelta(days=days)
        
        # Filter usage history
        filtered_usage = [
            usage for usage in self.usage_history
            if usage.timestamp >= since_date and (not user_id or usage.user_id == user_id)
        ]
        
        if not filtered_usage:
            return {"total_cost": 0, "total_tokens": 0, "total_requests": 0}
        
        # Calculate analytics
        total_cost = sum(usage.cost_usd for usage in filtered_usage)
        total_tokens = sum(usage.total_tokens for usage in filtered_usage)
        total_requests = len(filtered_usage)
        cached_requests = len([u for u in filtered_usage if u.cached])
        
        # Group by model
        model_usage = defaultdict(lambda: {"cost": 0, "tokens": 0, "requests": 0})
        for usage in filtered_usage:
            model_usage[usage.model]["cost"] += usage.cost_usd
            model_usage[usage.model]["tokens"] += usage.total_tokens
            model_usage[usage.model]["requests"] += 1
        
        # Group by guru type
        guru_usage = defaultdict(lambda: {"cost": 0, "tokens": 0, "requests": 0})
        for usage in filtered_usage:
            guru_usage[usage.guru_type]["cost"] += usage.cost_usd
            guru_usage[usage.guru_type]["tokens"] += usage.total_tokens
            guru_usage[usage.guru_type]["requests"] += 1
        
        return {
            "total_cost": round(total_cost, 4),
            "total_tokens": total_tokens,
            "total_requests": total_requests,
            "cached_requests": cached_requests,
            "cache_hit_rate": round(cached_requests / total_requests * 100, 1) if total_requests > 0 else 0,
            "average_cost_per_request": round(total_cost / total_requests, 4) if total_requests > 0 else 0,
            "model_breakdown": dict(model_usage),
            "guru_breakdown": dict(guru_usage),
            "cost_savings_from_cache": round(sum(
                self.calculate_cost(usage.model, usage.prompt_tokens, usage.completion_tokens)
                for usage in filtered_usage if usage.cached
            ), 4)
        }
    
    def check_alerts(self) -> List[Dict[str, Any]]:
        """Check for cost threshold alerts"""
        alerts = []
        
        # Check daily/monthly totals
        today = datetime.utcnow().date()
        month_start = today.replace(day=1)
        
        daily_usage = [u for u in self.usage_history if u.timestamp.date() == today]
        monthly_usage = [u for u in self.usage_history if u.timestamp.date() >= month_start]
        
        daily_cost = sum(u.cost_usd for u in daily_usage)
        monthly_cost = sum(u.cost_usd for u in monthly_usage)
        
        if daily_cost > self.alert_thresholds["daily_cost"]:
            alerts.append({
                "type": "daily_cost_exceeded",
                "message": f"Daily cost threshold exceeded: ${daily_cost:.2f}",
                "severity": "warning"
            })
        
        if monthly_cost > self.alert_thresholds["monthly_cost"]:
            alerts.append({
                "type": "monthly_cost_exceeded", 
                "message": f"Monthly cost threshold exceeded: ${monthly_cost:.2f}",
                "severity": "critical"
            })
        
        return alerts
    
    def _reset_quotas_if_needed(self, quota: UserQuota) -> None:
        """Reset user quotas if new day/month"""
        today = datetime.utcnow().strftime("%Y-%m-%d")
        
        if quota.last_reset_date != today:
            # Reset daily quotas
            quota.current_daily_tokens = 0
            quota.current_daily_cost = 0.0
            quota.last_reset_date = today
            
            # Reset monthly quotas if new month
            last_reset = datetime.strptime(quota.last_reset_date, "%Y-%m-%d")
            current = datetime.utcnow()
            if last_reset.month != current.month or last_reset.year != current.year:
                quota.current_monthly_tokens = 0
                quota.current_monthly_cost = 0.0
    
    def _load_data(self) -> None:
        """Load usage history and quotas from disk"""
        try:
            # Load usage history
            usage_file = os.path.join(self.data_dir, "usage_history.json")
            if os.path.exists(usage_file):
                with open(usage_file, 'r') as f:
                    usage_data = json.load(f)
                    self.usage_history = [
                        APIUsage(
                            timestamp=datetime.fromisoformat(u["timestamp"]),
                            user_id=u["user_id"],
                            guru_type=u["guru_type"],
                            model=u["model"],
                            prompt_tokens=u["prompt_tokens"],
                            completion_tokens=u["completion_tokens"],
                            total_tokens=u["total_tokens"],
                            cost_usd=u["cost_usd"],
                            cached=u.get("cached", False)
                        ) for u in usage_data
                    ]
            
            # Load user quotas
            quotas_file = os.path.join(self.data_dir, "user_quotas.json")
            if os.path.exists(quotas_file):
                with open(quotas_file, 'r') as f:
                    quotas_data = json.load(f)
                    self.user_quotas = {
                        uid: UserQuota(**data) for uid, data in quotas_data.items()
                    }
        except Exception as e:
            print(f"Warning: Could not load cost management data: {e}")
    
    def _save_data(self) -> None:
        """Save usage history and quotas to disk"""
        try:
            # Save usage history
            usage_file = os.path.join(self.data_dir, "usage_history.json")
            with open(usage_file, 'w') as f:
                usage_data = []
                for usage in self.usage_history[-1000:]:  # Keep last 1000 entries
                    data = asdict(usage)
                    data["timestamp"] = usage.timestamp.isoformat()
                    usage_data.append(data)
                json.dump(usage_data, f, indent=2)
            
            # Save user quotas
            quotas_file = os.path.join(self.data_dir, "user_quotas.json")
            with open(quotas_file, 'w') as f:
                quotas_data = {
                    uid: asdict(quota) for uid, quota in self.user_quotas.items()
                }
                json.dump(quotas_data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save cost management data: {e}")