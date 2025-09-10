"""
Test suite for enterprise features
"""
import pytest
import json
import uuid
from datetime import datetime
from backend.app import app
from backend.models.enterprise import db, Tenant, User, ApiKey, CustomizationConfig

@pytest.fixture
def client():
    """Create a test client"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            # Create a test tenant
            tenant = Tenant(
                name='Test Company',
                slug='test-company',
                subscription_tier='pro',
                user_limit=100,
                api_rate_limit=10000
            )
            db.session.add(tenant)
            db.session.commit()
            
            # Create a test admin user
            from werkzeug.security import generate_password_hash
            admin_user = User(
                tenant_id=tenant.id,
                email='admin@test.com',
                password_hash=generate_password_hash('password123'),
                full_name='Test Admin',
                role='admin'
            )
            db.session.add(admin_user)
            db.session.commit()
            
            # Store test data for use in tests
            client.test_tenant = tenant
            client.test_admin = admin_user
            
        yield client

def test_tenant_creation(client):
    """Test tenant creation"""
    tenant_data = {
        'name': 'New Test Company',
        'slug': 'new-test-company',
        'subscription_tier': 'basic',
        'user_limit': 25
    }
    
    response = client.post('/api/enterprise/tenants', 
                          data=json.dumps(tenant_data),
                          content_type='application/json')
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['name'] == tenant_data['name']
    assert data['slug'] == tenant_data['slug']

def test_user_management(client):
    """Test user creation and management"""
    # Mock authentication
    with client.session_transaction() as sess:
        sess['user_id'] = client.test_admin.id
        sess['tenant_id'] = client.test_tenant.id
    
    user_data = {
        'email': 'newuser@test.com',
        'password': 'password123',
        'full_name': 'New Test User',
        'role': 'user'
    }
    
    response = client.post('/api/enterprise/admin/users',
                          data=json.dumps(user_data),
                          content_type='application/json',
                          headers={'X-Tenant-ID': client.test_tenant.id})
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['email'] == user_data['email']
    assert data['role'] == user_data['role']

def test_api_key_creation(client):
    """Test API key creation and management"""
    with client.session_transaction() as sess:
        sess['user_id'] = client.test_admin.id
        sess['tenant_id'] = client.test_tenant.id
    
    key_data = {
        'name': 'Test API Key',
        'description': 'Key for testing',
        'scopes': ['read', 'write'],
        'rate_limit': 5000
    }
    
    response = client.post('/api/enterprise/api-keys',
                          data=json.dumps(key_data),
                          content_type='application/json',
                          headers={'X-Tenant-ID': client.test_tenant.id})
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['name'] == key_data['name']
    assert 'key' in data  # API key should be returned
    assert data['rate_limit'] == key_data['rate_limit']

def test_customization_update(client):
    """Test white-label customization"""
    with client.session_transaction() as sess:
        sess['user_id'] = client.test_admin.id
        sess['tenant_id'] = client.test_tenant.id
    
    customization_data = {
        'company_name': 'Custom Company Name',
        'primary_color': '#FF5733',
        'secondary_color': '#33FF57',
        'welcome_message': 'Welcome to our platform!'
    }
    
    response = client.put('/api/customization/customization',
                         data=json.dumps(customization_data),
                         content_type='application/json',
                         headers={'X-Tenant-ID': client.test_tenant.id})
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'updated_at' in data

def test_analytics_endpoint(client):
    """Test analytics data retrieval"""
    with client.session_transaction() as sess:
        sess['user_id'] = client.test_admin.id
        sess['tenant_id'] = client.test_tenant.id
    
    response = client.get('/api/enterprise/admin/analytics',
                         headers={'X-Tenant-ID': client.test_tenant.id})
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'total_users' in data
    assert 'total_api_keys' in data
    assert 'api_calls_last_30_days' in data

def test_subscription_plans(client):
    """Test subscription plans endpoint"""
    response = client.get('/api/billing/plans')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'plans' in data
    assert 'free' in data['plans']
    assert 'basic' in data['plans']
    assert 'pro' in data['plans']
    assert 'enterprise' in data['plans']

def test_rate_limiting_validation():
    """Test rate limiting logic"""
    from backend.middleware.rate_limiting import RateLimiter
    
    limiter = RateLimiter()
    
    # Test that rate limiting works
    test_key = 'test_key'
    limit = 5
    
    # Should allow first 5 requests
    for i in range(5):
        allowed, current, max_limit = limiter.is_allowed(test_key, limit)
        assert allowed == True
        assert current == i + 1
        assert max_limit == limit
    
    # 6th request should be denied
    allowed, current, max_limit = limiter.is_allowed(test_key, limit)
    assert allowed == False
    assert current >= limit

def test_theme_preview(client):
    """Test theme preview generation"""
    with client.session_transaction() as sess:
        sess['user_id'] = client.test_admin.id
        sess['tenant_id'] = client.test_tenant.id
    
    theme_data = {
        'primary_color': '#3B82F6',
        'secondary_color': '#1F2937',
        'accent_color': '#F59E0B'
    }
    
    response = client.post('/api/customization/themes/preview',
                          data=json.dumps(theme_data),
                          content_type='application/json',
                          headers={'X-Tenant-ID': client.test_tenant.id})
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'css' in data
    assert 'colors' in data
    assert ':root' in data['css']  # CSS should contain root variables

def test_feature_availability(client):
    """Test feature availability by subscription tier"""
    with client.session_transaction() as sess:
        sess['user_id'] = client.test_admin.id
        sess['tenant_id'] = client.test_tenant.id
    
    response = client.get('/api/customization/features',
                         headers={'X-Tenant-ID': client.test_tenant.id})
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'available_features' in data
    assert 'subscription_tier' in data
    assert data['subscription_tier'] == 'pro'  # Test tenant is pro
    
    # Pro tier should include these features
    expected_features = ['custom_branding', 'analytics', 'api_access']
    for feature in expected_features:
        assert feature in data['available_features']

def test_audit_logging():
    """Test that audit logging works"""
    from backend.api.enterprise import log_audit_event
    from backend.models.enterprise import AuditLog
    
    with app.app_context():
        # Create test data
        tenant_id = str(uuid.uuid4())
        user_id = str(uuid.uuid4())
        
        # Log an event
        log_audit_event(
            action='test_action',
            tenant_id=tenant_id,
            details={'test': 'data'},
            user_id=user_id
        )
        
        # Check that log was created
        log = AuditLog.query.filter_by(tenant_id=tenant_id).first()
        assert log is not None
        assert log.action == 'test_action'
        assert log.user_id == user_id
        assert log.details['test'] == 'data'

if __name__ == '__main__':
    pytest.main([__file__])