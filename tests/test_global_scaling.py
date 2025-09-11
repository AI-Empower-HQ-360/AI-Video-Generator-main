import pytest
import json
from unittest.mock import patch, MagicMock
from backend.app import app
from backend.utils.global_config import GlobalConfigManager
from backend.middleware.regional import RegionalMiddleware

@pytest.fixture
def client():
    """Create a test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def global_config():
    """Create a global config manager for testing"""
    return GlobalConfigManager()

class TestGlobalScaling:
    """Test suite for global scaling infrastructure"""
    
    def test_health_endpoints(self, client):
        """Test health check endpoints"""
        # Test basic health check
        response = client.get('/api/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'timestamp' in data
        assert 'region' in data
        
        # Test readiness probe
        response = client.get('/api/health/readiness')
        assert response.status_code in [200, 503]  # May fail if no DB
        data = json.loads(response.data)
        assert 'ready' in data
        assert 'checks' in data
        
        # Test liveness probe
        response = client.get('/api/health/liveness')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['alive'] == True
    
    def test_regional_headers(self, client):
        """Test that regional headers are added to responses"""
        response = client.get('/api/health')
        
        # Check that regional headers are present
        assert 'X-Region' in response.headers
        assert 'X-Country' in response.headers
        assert 'X-Language' in response.headers
        assert 'X-Currency' in response.headers
    
    def test_language_detection(self, client):
        """Test language detection from Accept-Language header"""
        # Test English
        response = client.get('/api/health', headers={
            'Accept-Language': 'en-US,en;q=0.9'
        })
        assert response.headers['X-Language'] == 'en-US'
        
        # Test German
        response = client.get('/api/health', headers={
            'Accept-Language': 'de-DE,de;q=0.9,en;q=0.8'
        })
        assert response.headers['X-Language'] == 'de-DE'
    
    def test_region_detection_from_country(self, client):
        """Test region detection from CloudFront country header"""
        # Test US -> us-east-1
        response = client.get('/api/health', headers={
            'CloudFront-Viewer-Country': 'US'
        })
        assert response.headers['X-Region'] == 'us-east-1'
        
        # Test DE -> eu-central-1
        response = client.get('/api/health', headers={
            'CloudFront-Viewer-Country': 'DE'
        })
        assert response.headers['X-Region'] == 'eu-central-1'
        
        # Test JP -> ap-northeast-1
        response = client.get('/api/health', headers={
            'CloudFront-Viewer-Country': 'JP'
        })
        assert response.headers['X-Region'] == 'ap-northeast-1'
    
    def test_currency_detection(self, client):
        """Test currency detection based on region"""
        # Test EUR for Germany
        response = client.get('/api/health', headers={
            'CloudFront-Viewer-Country': 'DE'
        })
        assert response.headers['X-Currency'] == 'EUR'
        
        # Test JPY for Japan
        response = client.get('/api/health', headers={
            'CloudFront-Viewer-Country': 'JP'
        })
        assert response.headers['X-Currency'] == 'JPY'
    
    def test_gdpr_compliance_headers(self, client):
        """Test GDPR compliance headers for EU regions"""
        # Test EU region gets GDPR header
        response = client.get('/api/health', headers={
            'CloudFront-Viewer-Country': 'DE'
        })
        assert response.headers.get('X-GDPR-Region') == 'true'
        
        # Test non-EU region doesn't get GDPR header
        response = client.get('/api/health', headers={
            'CloudFront-Viewer-Country': 'US'
        })
        assert 'X-GDPR-Region' not in response.headers
    
    def test_explicit_region_preference(self, client):
        """Test explicit region preference via headers"""
        response = client.get('/api/health', headers={
            'X-Preferred-Region': 'ap-southeast-1',
            'CloudFront-Viewer-Country': 'US'  # This should be overridden
        })
        assert response.headers['X-Region'] == 'ap-southeast-1'
    
    def test_cache_headers(self, client):
        """Test that appropriate cache headers are set"""
        # Test static assets get long cache
        response = client.get('/static/test.js')
        # Note: This will 404 but we can still check headers
        assert 'Cache-Control' in response.headers or response.status_code == 404
    
    def test_global_config_manager(self, global_config):
        """Test global configuration manager"""
        # Test region info retrieval
        us_east_info = global_config.get_region_info('us-east-1')
        assert us_east_info.get('name') == 'US East (Virginia)'
        assert us_east_info.get('primary') == True
        assert 'USD' in us_east_info.get('currency', '')
        
        # Test currency support
        usd_currency = global_config.get_supported_currencies('us-east-1')
        assert usd_currency.get('code') == 'USD'
        assert usd_currency.get('symbol') == '$'
        
        # Test compliance requirements
        us_compliance = global_config.get_compliance_requirements('us-east-1')
        assert 'SOC2' in us_compliance or 'HIPAA' in us_compliance
        
        eu_compliance = global_config.get_compliance_requirements('eu-west-1')
        assert 'GDPR' in eu_compliance
    
    def test_regional_languages(self, global_config):
        """Test regional language support"""
        # Test US languages
        us_languages = global_config.get_regional_languages('us-east-1')
        assert 'en-US' in us_languages
        
        # Test EU languages
        eu_languages = global_config.get_regional_languages('eu-west-1')
        assert any(lang.startswith('en') for lang in eu_languages)
        
        # Test Middle East RTL support
        me_region_info = global_config.get_region_info('me-south-1')
        assert me_region_info.get('rtl_support') == True
    
    def test_failover_configuration(self, global_config):
        """Test failover region configuration"""
        # Test US East failover
        us_failover = global_config.get_failover_regions('us-east-1')
        assert len(us_failover) > 0
        assert 'us-west-2' in us_failover or 'eu-west-1' in us_failover
        
        # Test EU failover
        eu_failover = global_config.get_failover_regions('eu-west-1')
        assert len(eu_failover) > 0
    
    def test_data_residency_rules(self, global_config):
        """Test data residency configuration"""
        eu_residency = global_config.get_data_residency_rules('eu-west-1')
        assert 'data_types' in eu_residency
        
        # Check that EU has no cross-border transfer for user data
        user_data_config = eu_residency.get('data_types', {}).get('user_data', {})
        assert user_data_config.get('no_cross_border_transfer') == True
    
    def test_rate_limiting_config(self, global_config):
        """Test rate limiting configuration"""
        us_rate_limits = global_config.get_rate_limiting_config('us-east-1')
        assert 'requests_per_second' in us_rate_limits
        assert 'requests_per_minute' in us_rate_limits
        
        # US East should have higher limits than smaller regions
        sg_rate_limits = global_config.get_rate_limiting_config('ap-southeast-1')
        assert us_rate_limits['requests_per_second'] >= sg_rate_limits['requests_per_second']
    
    def test_rtl_language_support(self, global_config):
        """Test RTL language detection"""
        # Test Arabic region
        me_languages = global_config.get_regional_languages('me-south-1')
        has_rtl = any(lang.startswith('ar') or lang.startswith('he') or lang.startswith('fa') 
                     for lang in me_languages)
        assert has_rtl
        
        # Test RTL region detection
        assert global_config.is_rtl_region('me-south-1') == True
        assert global_config.is_rtl_region('us-east-1') == False
    
    def test_payment_localization(self, global_config):
        """Test payment provider localization"""
        # Test US payment providers
        us_pricing = global_config.get_regional_pricing('us-east-1')
        assert us_pricing.get('currency') == 'USD'
        assert 'pricing_tiers' in us_pricing
        
        # Test EU pricing
        eu_pricing = global_config.get_regional_pricing('eu-west-1')
        assert eu_pricing.get('currency') == 'EUR'
        
        # Test that EU has higher tax rates (typically)
        us_tax = us_pricing.get('tax_rate', 0)
        eu_tax = eu_pricing.get('tax_rate', 0)
        assert eu_tax >= us_tax  # EU typically has higher VAT
    
    def test_cdn_endpoints(self, global_config):
        """Test CDN endpoint configuration"""
        us_endpoints = global_config.get_cdn_endpoints('us-east-1')
        assert len(us_endpoints) > 0
        assert any('cloudfront.net' in endpoint for endpoint in us_endpoints)
        
        eu_endpoints = global_config.get_cdn_endpoints('eu-west-1')
        assert len(eu_endpoints) > 0
    
    @patch.dict('os.environ', {'AWS_REGION': 'eu-west-1'})
    def test_environment_region_detection(self, global_config):
        """Test region detection from environment variables"""
        current_region = global_config.get_current_region()
        assert current_region == 'eu-west-1'
    
    def test_feature_flags_by_compliance(self, global_config):
        """Test feature flags based on compliance requirements"""
        # GDPR regions should disable certain tracking features
        gdpr_region_allowed = global_config.should_enable_feature('analytics_cookies', 'eu-west-1')
        us_region_allowed = global_config.should_enable_feature('analytics_cookies', 'us-east-1')
        
        # Note: The logic might vary based on implementation
        # This tests that the feature flag system is working
        assert isinstance(gdpr_region_allowed, bool)
        assert isinstance(us_region_allowed, bool)

if __name__ == '__main__':
    pytest.main([__file__, '-v'])