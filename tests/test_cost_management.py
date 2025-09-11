"""
Test cases for cost management functionality
"""
import unittest
import tempfile
import os
import json
from datetime import datetime, timedelta
from backend.services.cost_management import CostManagementService, APIUsage, UserQuota


class TestCostManagementService(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.cost_manager = CostManagementService(data_dir=self.temp_dir)
    
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_calculate_cost(self):
        """Test cost calculation for different models"""
        # Test GPT-4 pricing
        cost = self.cost_manager.calculate_cost("gpt-4", 1000, 500)
        expected_cost = (1000/1000) * 0.03 + (500/1000) * 0.06
        self.assertAlmostEqual(cost, expected_cost, places=6)
        
        # Test GPT-3.5-turbo pricing
        cost = self.cost_manager.calculate_cost("gpt-3.5-turbo", 1000, 500)
        expected_cost = (1000/1000) * 0.0015 + (500/1000) * 0.002
        self.assertAlmostEqual(cost, expected_cost, places=6)
        
        # Test unknown model (should default to gpt-3.5-turbo)
        cost = self.cost_manager.calculate_cost("unknown-model", 1000, 500)
        expected_cost = (1000/1000) * 0.0015 + (500/1000) * 0.002
        self.assertAlmostEqual(cost, expected_cost, places=6)
    
    def test_cache_operations(self):
        """Test caching functionality"""
        cache_key = "test_key"
        test_response = {"response": "test response", "tokens": 100}
        
        # Test cache miss
        cached = self.cost_manager.get_cached_response(cache_key)
        self.assertIsNone(cached)
        
        # Test cache set
        self.cost_manager.cache_response(cache_key, test_response)
        cached = self.cost_manager.get_cached_response(cache_key)
        self.assertEqual(cached, test_response)
        
        # Test cache expiration
        self.cost_manager.cache_ttl = 0  # Expire immediately
        cached = self.cost_manager.get_cached_response(cache_key)
        self.assertIsNone(cached)
    
    def test_user_quota_management(self):
        """Test user quota functionality"""
        user_id = "test_user"
        
        # Test quota creation
        quota = self.cost_manager.get_user_quota(user_id)
        self.assertIsInstance(quota, UserQuota)
        self.assertEqual(quota.user_id, user_id)
        
        # Test quota check within limits
        quota_check = self.cost_manager.check_user_quota(user_id, 100, 0.01)
        self.assertTrue(quota_check["within_limits"])
        
        # Test quota exceeded
        quota_check = self.cost_manager.check_user_quota(user_id, 20000, 100.0)
        self.assertFalse(quota_check["within_limits"])
        self.assertTrue(quota_check["limits_exceeded"]["daily_tokens"])
        self.assertTrue(quota_check["limits_exceeded"]["daily_cost"])
    
    def test_usage_recording(self):
        """Test usage recording and analytics"""
        user_id = "test_user"
        
        # Record some usage
        usage1 = self.cost_manager.record_usage(
            user_id=user_id,
            guru_type="spiritual",
            model="gpt-3.5-turbo",
            prompt_tokens=100,
            completion_tokens=50,
            cached=False
        )
        
        usage2 = self.cost_manager.record_usage(
            user_id=user_id,
            guru_type="meditation",
            model="gpt-4",
            prompt_tokens=200,
            completion_tokens=100,
            cached=True
        )
        
        # Test usage objects
        self.assertIsInstance(usage1, APIUsage)
        self.assertEqual(usage1.user_id, user_id)
        self.assertEqual(usage1.total_tokens, 150)
        self.assertFalse(usage1.cached)
        
        self.assertIsInstance(usage2, APIUsage)
        self.assertEqual(usage2.cost_usd, 0.0)  # Cached, so no cost
        self.assertTrue(usage2.cached)
        
        # Test analytics
        analytics = self.cost_manager.get_usage_analytics(user_id, 1)
        self.assertEqual(analytics["total_requests"], 2)
        self.assertEqual(analytics["cached_requests"], 1)
        self.assertEqual(analytics["cache_hit_rate"], 50.0)
    
    def test_prompt_optimization(self):
        """Test prompt optimization strategies"""
        # Test spiritual guru optimization
        strategy = self.cost_manager.optimize_prompt_strategy(
            "spiritual", 
            "What is the meaning of life?"
        )
        self.assertEqual(strategy["model"], "gpt-3.5-turbo")
        self.assertEqual(strategy["max_tokens"], 400)
        self.assertIn("estimated_cost", strategy)
        self.assertIn("estimated_tokens", strategy)
        
        # Test sloka guru optimization (should use GPT-4)
        strategy = self.cost_manager.optimize_prompt_strategy(
            "sloka",
            "Please provide a Bhagavad Gita verse"
        )
        self.assertEqual(strategy["model"], "gpt-4")
        self.assertEqual(strategy["max_tokens"], 600)
        
        # Test long question optimization
        long_question = "This is a very long question " * 20
        strategy = self.cost_manager.optimize_prompt_strategy(
            "meditation",
            long_question
        )
        self.assertGreater(strategy["max_tokens"], 300)  # Should increase for long questions
    
    def test_alert_generation(self):
        """Test cost alert generation"""
        # Set low thresholds for testing
        self.cost_manager.alert_thresholds["daily_cost"] = 0.01
        self.cost_manager.alert_thresholds["monthly_cost"] = 0.05
        
        # Record usage that exceeds thresholds
        self.cost_manager.record_usage(
            user_id="test_user",
            guru_type="spiritual",
            model="gpt-4",
            prompt_tokens=1000,
            completion_tokens=1000,
            cached=False
        )
        
        alerts = self.cost_manager.check_alerts()
        self.assertGreater(len(alerts), 0)
        
        # Check alert structure
        for alert in alerts:
            self.assertIn("type", alert)
            self.assertIn("message", alert)
            self.assertIn("severity", alert)
    
    def test_data_persistence(self):
        """Test data saving and loading"""
        user_id = "test_user"
        
        # Record some data
        self.cost_manager.record_usage(
            user_id=user_id,
            guru_type="spiritual",
            model="gpt-3.5-turbo",
            prompt_tokens=100,
            completion_tokens=50,
            cached=False
        )
        
        # Save data
        self.cost_manager._save_data()
        
        # Create new instance and load data
        new_manager = CostManagementService(data_dir=self.temp_dir)
        
        # Verify data was loaded
        self.assertEqual(len(new_manager.usage_history), 1)
        self.assertIn(user_id, new_manager.user_quotas)
        
        usage = new_manager.usage_history[0]
        self.assertEqual(usage.user_id, user_id)
        self.assertEqual(usage.guru_type, "spiritual")
    
    def test_cache_size_limit(self):
        """Test cache size limiting"""
        # Set small cache size for testing
        self.cost_manager.max_cache_size = 3
        
        # Add entries beyond limit
        for i in range(5):
            cache_key = f"key_{i}"
            self.cost_manager.cache_response(cache_key, {"response": f"response_{i}"})
        
        # Should only keep the maximum allowed entries
        self.assertEqual(len(self.cost_manager.response_cache), 3)
        
        # First entries should be evicted (oldest first)
        self.assertNotIn("key_0", self.cost_manager.response_cache)
        self.assertNotIn("key_1", self.cost_manager.response_cache)
        self.assertIn("key_4", self.cost_manager.response_cache)


class TestCostManagementAPI(unittest.TestCase):
    """Test the cost management API endpoints"""
    
    def setUp(self):
        """Set up test Flask app"""
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
        
        from backend.app import app
        app.config['TESTING'] = True
        self.client = app.test_client()
    
    def test_cost_analytics_endpoint(self):
        """Test the cost analytics endpoint"""
        response = self.client.get('/api/cost/analytics')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('analytics', data)
    
    def test_quota_endpoints(self):
        """Test quota-related endpoints"""
        user_id = "test_user"
        
        # Test get quota
        response = self.client.get(f'/api/cost/quota/{user_id}')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('quota_status', data)
        
        # Test update quota
        quota_updates = {
            'daily_token_limit': 5000,
            'daily_cost_limit': 2.5
        }
        response = self.client.put(
            f'/api/cost/quota/{user_id}',
            json=quota_updates,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('new_quota', data)
    
    def test_optimization_endpoint(self):
        """Test the optimization suggestions endpoint"""
        request_data = {
            'guru_type': 'spiritual',
            'question': 'What is the meaning of life?'
        }
        
        response = self.client.post(
            '/api/cost/optimize',
            json=request_data,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('optimization', data)
        self.assertIn('optimal_strategy', data['optimization'])
        self.assertIn('suggestions', data['optimization'])
    
    def test_model_pricing_endpoint(self):
        """Test the model pricing endpoint"""
        response = self.client.get('/api/cost/models/pricing')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('pricing', data)
        self.assertIn('gpt-4', data['pricing'])
        self.assertIn('gpt-3.5-turbo', data['pricing'])
    
    def test_cache_stats_endpoint(self):
        """Test the cache statistics endpoint"""
        response = self.client.get('/api/cost/cache/stats')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('cache_stats', data)
        
        cache_stats = data['cache_stats']
        self.assertIn('current_size', cache_stats)
        self.assertIn('max_size', cache_stats)
        self.assertIn('utilization_percent', cache_stats)
    
    def test_alerts_endpoint(self):
        """Test the alerts endpoint"""
        response = self.client.get('/api/cost/alerts')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('alerts', data)
    
    def test_budget_recommendations_endpoint(self):
        """Test the budget recommendations endpoint"""
        response = self.client.get('/api/cost/budget/recommendations')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('recommendations', data)
        self.assertIn('current_analytics', data)


if __name__ == '__main__':
    unittest.main()