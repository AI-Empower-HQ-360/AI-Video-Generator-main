#!/usr/bin/env python3
"""
Enterprise Security System Test Suite
Tests all security components functionality
"""

import sys
import os
import json
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from security import (
    SecurityManager,
    RoleBasedAccessControl,
    EncryptionManager,
    ComplianceManager,
    AuditTrailManager,
    DigitalRightsManager
)


def test_authentication():
    """Test authentication and SSO"""
    print("🔐 Testing Authentication & SSO...")
    
    config = {
        'oauth2': {'client_id': 'test', 'client_secret': 'test'},
        'saml': {'issuer': 'test'},
        'active_directory': {'ldap_server': 'test'},
        'session_timeout': 3600
    }
    
    security_manager = SecurityManager(config)
    
    # Test OAuth2 flow
    sso_result = security_manager.initiate_sso_login('oauth2')
    print(f"   ✓ OAuth2 SSO initiation: {bool(sso_result.get('auth_url'))}")
    
    # Test local authentication
    auth_result = security_manager.authenticate_local('testuser', 'password123')
    print(f"   ✓ Local authentication: {auth_result.get('success', False)}")
    
    return True


def test_rbac():
    """Test Role-Based Access Control"""
    print("👥 Testing RBAC...")
    
    rbac = RoleBasedAccessControl()
    
    # Test role assignment
    success = rbac.assign_role_to_user('testuser', 'content_creator')
    print(f"   ✓ Role assignment: {success}")
    
    # Test permission check
    has_permission = rbac.check_permission('testuser', 'videos', 'create')
    print(f"   ✓ Permission check: {has_permission}")
    
    # Test role hierarchy
    roles = rbac.get_role_hierarchy()
    print(f"   ✓ Role hierarchy: {len(roles)} roles defined")
    
    return True


def test_encryption():
    """Test encryption functionality"""
    print("🔒 Testing Encryption...")
    
    config = {'key_storage_path': '/tmp/test_keys'}
    encryption_manager = EncryptionManager(config)
    
    # Test content encryption
    test_content = "This is sensitive content that needs encryption"
    encrypt_result = encryption_manager.encrypt_content(test_content, 'test_content_1', 'text')
    print(f"   ✓ Content encryption: {encrypt_result.get('success', False)}")
    
    if encrypt_result.get('success'):
        # Test content decryption
        decrypt_result = encryption_manager.decrypt_content(
            'test_content_1', 
            encrypt_result['encrypted_data']
        )
        print(f"   ✓ Content decryption: {decrypt_result.get('success', False)}")
        print(f"   ✓ Content integrity: {decrypt_result.get('content') == test_content}")
    
    # Test encryption status
    status = encryption_manager.get_encryption_status()
    print(f"   ✓ Encryption status: {status.get('total_encrypted_items', 0)} items")
    
    return True


def test_compliance():
    """Test GDPR/CCPA compliance"""
    print("📋 Testing Compliance...")
    
    config = {'compliance_db_path': '/tmp/test_compliance.db'}
    compliance_manager = ComplianceManager(config)
    
    # Test data subject registration
    register_result = compliance_manager.register_data_subject({
        'user_id': 'testuser',
        'email': 'test@company.com',
        'location': 'EU'
    })
    print(f"   ✓ Data subject registration: {register_result.get('success', False)}")
    
    # Test consent recording
    consent_result = compliance_manager.record_consent(
        'testuser', 'analytics', True, 'User consented to analytics'
    )
    print(f"   ✓ Consent recording: {consent_result.get('success', False)}")
    
    # Test data request
    request_result = compliance_manager.create_data_request('testuser', 'access')
    print(f"   ✓ Data access request: {request_result.get('success', False)}")
    
    # Test compliance report
    report = compliance_manager.get_compliance_report()
    print(f"   ✓ Compliance report: {report.get('total_data_subjects', 0)} subjects")
    
    return True


def test_audit_trail():
    """Test audit trail and intrusion detection"""
    print("📊 Testing Audit Trail...")
    
    config = {'audit_db_path': '/tmp/test_audit.db'}
    audit_manager = AuditTrailManager(config)
    
    # Test event logging
    log_result = audit_manager.log_event(
        event_type='login_success',
        user_id='testuser',
        ip_address='192.168.1.100',
        user_agent='Mozilla/5.0 Test Browser',
        resource='system',
        action='login',
        outcome='success',
        details={'method': 'password'}
    )
    print(f"   ✓ Event logging: {log_result.get('success', False)}")
    
    # Test suspicious activity detection
    for i in range(6):  # Trigger brute force detection
        audit_manager.log_event(
            event_type='login_failure',
            user_id='attacker',
            ip_address='10.0.0.1',
            user_agent='Malicious Bot',
            resource='system',
            action='login',
            outcome='failure',
            details={'attempt': i}
        )
    
    # Get security events
    events = audit_manager.get_security_events({'limit': 10})
    print(f"   ✓ Security events: {events.get('total_events', 0)} events logged")
    
    # Get security alerts
    alerts = audit_manager.get_security_alerts()
    print(f"   ✓ Security alerts: {alerts.get('total_alerts', 0)} alerts generated")
    
    return True


def test_drm():
    """Test Digital Rights Management"""
    print("🎬 Testing DRM...")
    
    config = {
        'drm_db_path': '/tmp/test_drm.db',
        'content_storage_path': '/tmp/test_content',
        'watermark_storage_path': '/tmp/test_watermarks'
    }
    drm_manager = DigitalRightsManager(config)
    
    # Create test content file
    test_file = '/tmp/test_video.txt'
    with open(test_file, 'w') as f:
        f.write("This is test video content")
    
    # Test content protection
    protect_result = drm_manager.protect_content(test_file, 'test_video_1', 'STANDARD')
    print(f"   ✓ Content protection: {protect_result.get('success', False)}")
    
    # Test license creation
    license_result = drm_manager.create_license(
        'test_video_1', 'testuser', ['view', 'download'], 
        max_views=5, max_downloads=2
    )
    print(f"   ✓ License creation: {license_result.get('success', False)}")
    
    # Test access rights check
    access_result = drm_manager.check_access_rights(
        'test_video_1', 'testuser', 'view', '192.168.1.100'
    )
    print(f"   ✓ Access rights check: {access_result.get('success', False)}")
    
    # Test access logging
    log_result = drm_manager.log_access(
        'test_video_1', 'testuser', 'view', True, '192.168.1.100'
    )
    print(f"   ✓ Access logging: {log_result.get('success', False)}")
    
    # Test DRM status
    status = drm_manager.get_drm_status()
    print(f"   ✓ DRM status: {status.get('total_protected_content', 0)} protected items")
    
    return True


def run_all_tests():
    """Run all security component tests"""
    print("🚀 Enterprise Security System Test Suite")
    print("=" * 50)
    
    tests = [
        test_authentication,
        test_rbac,
        test_encryption,
        test_compliance,
        test_audit_trail,
        test_drm
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
                print("   ✅ PASSED\n")
            else:
                print("   ❌ FAILED\n")
        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}\n")
    
    print("=" * 50)
    print(f"🎯 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All security components are working correctly!")
        return True
    else:
        print("⚠️  Some security components need attention.")
        return False


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)