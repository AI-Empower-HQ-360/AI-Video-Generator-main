#!/usr/bin/env python3
"""
Simple test script for cost management functionality
"""
import sys
import tempfile
import os

sys.path.append('backend')
from backend.services.cost_management import CostManagementService

def main():
    """Test basic cost management functionality"""
    print("Testing Cost Management System...")
    
    # Create temporary directory for testing
    temp_dir = tempfile.mkdtemp()
    cost_manager = CostManagementService(data_dir=temp_dir)
    
    try:
        # Test 1: Cost calculation
        cost = cost_manager.calculate_cost('gpt-3.5-turbo', 1000, 500)
        print(f'✅ Cost calculation test: ${cost:.6f}')
        
        # Test 2: Optimization strategy
        strategy = cost_manager.optimize_prompt_strategy('spiritual', 'What is meditation?')
        print(f'✅ Optimization strategy: model={strategy["model"]}, estimated_cost=${strategy["estimated_cost"]:.6f}')
        
        # Test 3: User quota
        quota_check = cost_manager.check_user_quota('test_user', 100, 0.01)
        print(f'✅ Quota check: within_limits={quota_check["within_limits"]}')
        
        # Test 4: Usage recording
        usage = cost_manager.record_usage('test_user', 'spiritual', 'gpt-3.5-turbo', 100, 50, False)
        print(f'✅ Usage recording: tokens={usage.total_tokens}, cost=${usage.cost_usd:.6f}')
        
        # Test 5: Analytics
        analytics = cost_manager.get_usage_analytics('test_user', 1)
        print(f'✅ Analytics: total_requests={analytics["total_requests"]}, total_cost=${analytics["total_cost"]:.6f}')
        
        # Test 6: Cache operations
        cache_key = cost_manager.get_cache_key('spiritual', 'test question', 'gpt-3.5-turbo', 0.7)
        test_response = {"response": "test response", "tokens": 100}
        cost_manager.cache_response(cache_key, test_response)
        cached = cost_manager.get_cached_response(cache_key)
        print(f'✅ Cache operations: cached_response_matches={cached == test_response}')
        
        print('\n🎉 All cost management tests passed!')
        
    except Exception as e:
        print(f'❌ Test failed: {e}')
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up
        import shutil
        shutil.rmtree(temp_dir)

if __name__ == '__main__':
    main()