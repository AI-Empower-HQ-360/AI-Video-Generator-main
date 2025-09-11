"""
Cost Management API endpoints
"""
from flask import Blueprint, request, jsonify
from services.ai_service import AIService
import asyncio

cost_bp = Blueprint('cost', __name__)
ai_service = AIService()

@cost_bp.route('/analytics', methods=['GET'])
def get_cost_analytics():
    """Get cost analytics and usage statistics"""
    try:
        user_id = request.args.get('user_id')
        days = int(request.args.get('days', 30))
        
        analytics = ai_service.get_cost_analytics(user_id, days)
        
        return jsonify({
            'success': True,
            'analytics': analytics
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@cost_bp.route('/quota/<user_id>', methods=['GET'])
def get_user_quota(user_id):
    """Get user quota status"""
    try:
        quota_status = ai_service.get_user_quota_status(user_id)
        
        return jsonify({
            'success': True,
            'quota_status': quota_status
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@cost_bp.route('/quota/<user_id>', methods=['PUT'])
def update_user_quota(user_id):
    """Update user quota limits"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        result = ai_service.update_user_quota(user_id, data)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@cost_bp.route('/alerts', methods=['GET'])
def get_cost_alerts():
    """Get current cost alerts"""
    try:
        alerts = ai_service.get_cost_alerts()
        
        return jsonify({
            'success': True,
            'alerts': alerts
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@cost_bp.route('/optimize', methods=['POST'])
def get_optimization_suggestions():
    """Get prompt optimization suggestions"""
    try:
        data = request.get_json()
        if not data or 'guru_type' not in data or 'question' not in data:
            return jsonify({
                'success': False,
                'error': 'guru_type and question are required'
            }), 400
        
        suggestions = ai_service.get_prompt_optimization_suggestions(
            data['guru_type'], 
            data['question']
        )
        
        return jsonify({
            'success': True,
            'optimization': suggestions
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@cost_bp.route('/models/pricing', methods=['GET'])
def get_model_pricing():
    """Get current model pricing information"""
    try:
        pricing = ai_service.cost_manager.MODEL_PRICING
        
        return jsonify({
            'success': True,
            'pricing': pricing,
            'currency': 'USD',
            'unit': 'per 1K tokens'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@cost_bp.route('/cache/stats', methods=['GET'])
def get_cache_statistics():
    """Get cache statistics"""
    try:
        cache_size = len(ai_service.cost_manager.response_cache)
        max_size = ai_service.cost_manager.max_cache_size
        ttl = ai_service.cost_manager.cache_ttl
        
        # Calculate cache hit rate from recent usage
        recent_usage = ai_service.cost_manager.usage_history[-100:]  # Last 100 requests
        cached_count = len([u for u in recent_usage if u.cached])
        total_count = len(recent_usage)
        hit_rate = (cached_count / total_count * 100) if total_count > 0 else 0
        
        return jsonify({
            'success': True,
            'cache_stats': {
                'current_size': cache_size,
                'max_size': max_size,
                'utilization_percent': round((cache_size / max_size) * 100, 1),
                'ttl_seconds': ttl,
                'recent_hit_rate_percent': round(hit_rate, 1),
                'sample_size': total_count
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@cost_bp.route('/cache/clear', methods=['POST'])
def clear_cache():
    """Clear the response cache"""
    try:
        cache_size_before = len(ai_service.cost_manager.response_cache)
        ai_service.cost_manager.response_cache.clear()
        
        return jsonify({
            'success': True,
            'message': f'Cache cleared. Removed {cache_size_before} entries.'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@cost_bp.route('/budget/recommendations', methods=['GET'])
def get_budget_recommendations():
    """Get budget and cost optimization recommendations"""
    try:
        user_id = request.args.get('user_id')
        
        # Get analytics
        analytics = ai_service.get_cost_analytics(user_id, 30)
        
        recommendations = []
        
        # Cost-based recommendations
        if analytics['total_cost'] > 20:
            recommendations.append({
                'type': 'high_cost_alert',
                'message': 'Monthly costs are high. Consider using gpt-3.5-turbo for simpler queries.',
                'priority': 'medium',
                'potential_savings': '70-80%'
            })
        
        # Cache utilization recommendations
        if analytics['cache_hit_rate'] < 20:
            recommendations.append({
                'type': 'low_cache_utilization',
                'message': 'Low cache hit rate. Users may benefit from asking similar questions.',
                'priority': 'low',
                'action': 'Encourage FAQ usage'
            })
        
        # Model usage recommendations
        model_breakdown = analytics.get('model_breakdown', {})
        gpt4_usage = model_breakdown.get('gpt-4', {}).get('cost', 0)
        total_cost = analytics['total_cost']
        
        if gpt4_usage > total_cost * 0.7:
            recommendations.append({
                'type': 'model_optimization',
                'message': 'High GPT-4 usage detected. Consider gpt-3.5-turbo for general guidance.',
                'priority': 'high',
                'current_gpt4_percentage': round((gpt4_usage / total_cost) * 100, 1)
            })
        
        return jsonify({
            'success': True,
            'recommendations': recommendations,
            'current_analytics': analytics
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500