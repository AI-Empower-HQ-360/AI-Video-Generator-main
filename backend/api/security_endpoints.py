"""
Security API Endpoints
Enterprise security features integration with Flask
"""

from flask import Blueprint, request, jsonify, session, g
from functools import wraps
import os
from datetime import datetime

# Import security modules
from security import (
    SecurityManager, 
    RoleBasedAccessControl, 
    EncryptionManager,
    ComplianceManager,
    AuditTrailManager,
    DigitalRightsManager
)

# Create blueprint
security_bp = Blueprint('security', __name__)

# Initialize security managers
config = {
    'oauth2': {
        'client_id': os.getenv('OAUTH2_CLIENT_ID', 'demo_client'),
        'client_secret': os.getenv('OAUTH2_CLIENT_SECRET', 'demo_secret'),
        'redirect_uri': os.getenv('OAUTH2_REDIRECT_URI', 'http://localhost:5000/api/security/oauth2/callback'),
        'authorization_endpoint': os.getenv('OAUTH2_AUTH_ENDPOINT', 'https://login.microsoftonline.com/common/oauth2/v2.0/authorize'),
        'token_endpoint': os.getenv('OAUTH2_TOKEN_ENDPOINT', 'https://login.microsoftonline.com/common/oauth2/v2.0/token'),
        'userinfo_endpoint': os.getenv('OAUTH2_USERINFO_ENDPOINT', 'https://graph.microsoft.com/v1.0/me')
    },
    'saml': {
        'issuer': os.getenv('SAML_ISSUER', 'http://localhost:5000'),
        'sso_url': os.getenv('SAML_SSO_URL', 'https://adfs.company.com/adfs/ls/'),
        'x509_cert': os.getenv('SAML_CERT'),
        'private_key': os.getenv('SAML_PRIVATE_KEY')
    },
    'active_directory': {
        'ldap_server': os.getenv('AD_LDAP_SERVER', 'ldap://dc.company.com'),
        'bind_dn': os.getenv('AD_BIND_DN', 'CN=Service,OU=Users,DC=company,DC=com'),
        'bind_password': os.getenv('AD_BIND_PASSWORD'),
        'search_base': os.getenv('AD_SEARCH_BASE', 'OU=Users,DC=company,DC=com')
    },
    'session_timeout': int(os.getenv('SESSION_TIMEOUT', 3600)),
    'key_storage_path': os.getenv('KEY_STORAGE_PATH', '/tmp/keys'),
    'compliance_db_path': os.getenv('COMPLIANCE_DB_PATH', '/tmp/compliance.db'),
    'audit_db_path': os.getenv('AUDIT_DB_PATH', '/tmp/audit_trail.db'),
    'drm_db_path': os.getenv('DRM_DB_PATH', '/tmp/drm.db')
}

# Initialize managers
security_manager = SecurityManager(config)
rbac = RoleBasedAccessControl()
encryption_manager = EncryptionManager(config)
compliance_manager = ComplianceManager(config)
audit_manager = AuditTrailManager(config)
drm_manager = DigitalRightsManager(config)


def log_security_event(event_type: str, resource: str, action: str, outcome: str, details: dict = None):
    """Helper function to log security events"""
    user_session = session.get('user_session', {})
    audit_manager.log_event(
        event_type=event_type,
        user_id=user_session.get('user_id'),
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent', ''),
        resource=resource,
        action=action,
        outcome=outcome,
        details=details or {},
        session_id=user_session.get('session_id')
    )


# Authentication Endpoints
@security_bp.route('/auth/sso/initiate', methods=['POST'])
def initiate_sso():
    """Initiate SSO login process"""
    data = request.get_json()
    provider = data.get('provider', 'oauth2')
    
    log_security_event('login_attempt', 'sso', 'initiate', 'started', {'provider': provider})
    
    result = security_manager.initiate_sso_login(provider)
    
    if 'error' in result:
        log_security_event('login_failure', 'sso', 'initiate', 'failed', result)
        return jsonify(result), 400
    
    log_security_event('login_success', 'sso', 'initiate', 'success', {'provider': provider})
    return jsonify(result)


@security_bp.route('/auth/sso/callback', methods=['POST'])
def sso_callback():
    """Handle SSO callback"""
    data = request.get_json()
    provider = data.get('provider')
    
    result = security_manager.handle_sso_callback(provider, **data)
    
    if result.get('success'):
        # Assign roles based on groups
        user_groups = result.get('user', {}).get('groups', [])
        rbac.assign_roles_from_groups(result['session_id'], user_groups)
        
        log_security_event('login_success', 'sso', 'callback', 'success', {
            'provider': provider,
            'user_id': result.get('user', {}).get('username')
        })
        return jsonify(result)
    else:
        log_security_event('login_failure', 'sso', 'callback', 'failed', result)
        return jsonify(result), 401


@security_bp.route('/auth/local', methods=['POST'])
def local_auth():
    """Local authentication with Active Directory"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    log_security_event('login_attempt', 'local', 'authenticate', 'started', {'username': username})
    
    result = security_manager.authenticate_local(username, password)
    
    if result.get('success'):
        # Register compliance data
        compliance_manager.register_data_subject({
            'user_id': username,
            'email': f'{username}@company.com',
            'location': request.headers.get('CF-IPCountry', 'unknown')
        })
        
        # Assign roles based on groups
        user_groups = result.get('user', {}).get('groups', [])
        rbac.assign_roles_from_groups(username, user_groups)
        
        log_security_event('login_success', 'local', 'authenticate', 'success', {'username': username})
        return jsonify(result)
    else:
        log_security_event('login_failure', 'local', 'authenticate', 'failed', {'username': username})
        return jsonify(result), 401


@security_bp.route('/auth/logout', methods=['POST'])
def logout():
    """User logout"""
    user_session = session.get('user_session')
    if not user_session:
        return jsonify({'error': 'No active session'}), 400
    
    session_id = user_session.get('session_id')
    user_id = user_session.get('user_id')
    
    result = security_manager.logout(session_id)
    
    log_security_event('logout', 'session', 'logout', 'success', {'user_id': user_id})
    return jsonify(result)


# RBAC Endpoints
@security_bp.route('/rbac/roles', methods=['GET'])
@rbac.require_permission('system', 'read')
def get_roles():
    """Get role hierarchy"""
    roles = rbac.get_role_hierarchy()
    return jsonify({'roles': roles})


@security_bp.route('/rbac/assign-role', methods=['POST'])
@rbac.require_permission('users', 'update')
def assign_role():
    """Assign role to user"""
    data = request.get_json()
    user_id = data.get('user_id')
    role_name = data.get('role_name')
    
    success = rbac.assign_role_to_user(user_id, role_name)
    
    log_security_event('admin_action', 'rbac', 'assign_role', 
                      'success' if success else 'failed',
                      {'target_user': user_id, 'role': role_name})
    
    if success:
        return jsonify({'success': True, 'message': f'Role {role_name} assigned to {user_id}'})
    else:
        return jsonify({'success': False, 'error': 'Failed to assign role'}), 400


@security_bp.route('/rbac/check-permission', methods=['POST'])
def check_permission():
    """Check user permission"""
    data = request.get_json()
    user_session = session.get('user_session')
    
    if not user_session:
        return jsonify({'error': 'Authentication required'}), 401
    
    user_id = user_session.get('user_id')
    resource = data.get('resource')
    action = data.get('action')
    context = data.get('context', {})
    
    has_permission = rbac.check_permission(user_id, resource, action, context)
    
    return jsonify({
        'user_id': user_id,
        'resource': resource,
        'action': action,
        'permitted': has_permission
    })


# Encryption Endpoints
@security_bp.route('/encryption/encrypt', methods=['POST'])
@rbac.require_permission('content', 'create')
def encrypt_content():
    """Encrypt content"""
    data = request.get_json()
    content = data.get('content')
    content_id = data.get('content_id')
    content_type = data.get('content_type', 'text')
    
    result = encryption_manager.encrypt_content(content, content_id, content_type)
    
    log_security_event('data_modification', 'encryption', 'encrypt', 
                      'success' if result['success'] else 'failed',
                      {'content_id': content_id})
    
    return jsonify(result)


@security_bp.route('/encryption/decrypt', methods=['POST'])
@rbac.require_permission('content', 'read')
def decrypt_content():
    """Decrypt content"""
    data = request.get_json()
    content_id = data.get('content_id')
    encrypted_data = data.get('encrypted_data')
    
    result = encryption_manager.decrypt_content(content_id, encrypted_data)
    
    log_security_event('data_access', 'encryption', 'decrypt',
                      'success' if result['success'] else 'failed',
                      {'content_id': content_id})
    
    return jsonify(result)


@security_bp.route('/encryption/status', methods=['GET'])
@rbac.require_permission('system', 'read')
def encryption_status():
    """Get encryption system status"""
    status = encryption_manager.get_encryption_status()
    return jsonify(status)


# Compliance Endpoints
@security_bp.route('/compliance/consent', methods=['POST'])
def record_consent():
    """Record user consent"""
    data = request.get_json()
    user_session = session.get('user_session')
    
    if not user_session:
        return jsonify({'error': 'Authentication required'}), 401
    
    user_id = user_session.get('user_id')
    purpose = data.get('purpose')
    granted = data.get('granted')
    consent_text = data.get('consent_text')
    
    result = compliance_manager.record_consent(
        user_id, purpose, granted, consent_text,
        request.remote_addr, request.headers.get('User-Agent', '')
    )
    
    log_security_event('data_modification', 'compliance', 'consent',
                      'success' if result['success'] else 'failed',
                      {'purpose': purpose, 'granted': granted})
    
    return jsonify(result)


@security_bp.route('/compliance/data-request', methods=['POST'])
def create_data_request():
    """Create data subject access request"""
    data = request.get_json()
    user_session = session.get('user_session')
    
    if not user_session:
        return jsonify({'error': 'Authentication required'}), 401
    
    user_id = user_session.get('user_id')
    request_type = data.get('request_type')
    
    result = compliance_manager.create_data_request(user_id, request_type)
    
    log_security_event('data_access', 'compliance', 'data_request',
                      'success' if result['success'] else 'failed',
                      {'request_type': request_type})
    
    return jsonify(result)


@security_bp.route('/compliance/report', methods=['GET'])
@rbac.require_permission('analytics', 'read')
def compliance_report():
    """Generate compliance report"""
    report = compliance_manager.get_compliance_report()
    return jsonify(report)


# Audit Endpoints
@security_bp.route('/audit/events', methods=['GET'])
@rbac.require_permission('audit_logs', 'read')
def get_audit_events():
    """Get security events"""
    filters = {
        'user_id': request.args.get('user_id'),
        'ip_address': request.args.get('ip_address'),
        'event_type': request.args.get('event_type'),
        'start_date': request.args.get('start_date'),
        'end_date': request.args.get('end_date'),
        'risk_level': request.args.get('risk_level'),
        'limit': int(request.args.get('limit', 100))
    }
    
    # Remove None values
    filters = {k: v for k, v in filters.items() if v is not None}
    
    events = audit_manager.get_security_events(filters)
    return jsonify(events)


@security_bp.route('/audit/alerts', methods=['GET'])
@rbac.require_permission('security', 'read')
def get_security_alerts():
    """Get security alerts"""
    status = request.args.get('status')
    severity = request.args.get('severity')
    
    alerts = audit_manager.get_security_alerts(status, severity)
    return jsonify(alerts)


@security_bp.route('/audit/alerts/<alert_id>/update', methods=['PUT'])
@rbac.require_permission('security', 'update')
def update_alert(alert_id):
    """Update security alert"""
    data = request.get_json()
    status = data.get('status')
    assigned_to = data.get('assigned_to')
    resolution_notes = data.get('resolution_notes')
    
    result = audit_manager.update_alert_status(alert_id, status, assigned_to, resolution_notes)
    
    log_security_event('admin_action', 'security', 'update_alert',
                      'success' if result['success'] else 'failed',
                      {'alert_id': alert_id, 'new_status': status})
    
    return jsonify(result)


@security_bp.route('/audit/report', methods=['GET'])
@rbac.require_permission('analytics', 'read')
def security_report():
    """Generate security report"""
    start_date = request.args.get('start_date', '2024-01-01')
    end_date = request.args.get('end_date', datetime.utcnow().isoformat())
    
    report = audit_manager.generate_security_report(start_date, end_date)
    return jsonify(report)


# DRM Endpoints
@security_bp.route('/drm/protect', methods=['POST'])
@rbac.require_permission('content', 'create')
def protect_content():
    """Apply DRM protection to content"""
    data = request.get_json()
    content_path = data.get('content_path')
    content_id = data.get('content_id')
    protection_level = data.get('protection_level', 'STANDARD')
    
    result = drm_manager.protect_content(content_path, content_id, protection_level)
    
    log_security_event('data_modification', 'drm', 'protect',
                      'success' if result['success'] else 'failed',
                      {'content_id': content_id, 'protection_level': protection_level})
    
    return jsonify(result)


@security_bp.route('/drm/license', methods=['POST'])
@rbac.require_permission('content', 'create')
def create_license():
    """Create content license"""
    data = request.get_json()
    content_id = data.get('content_id')
    user_id = data.get('user_id')
    rights = data.get('rights', ['view'])
    expiry_date = data.get('expiry_date')
    max_views = data.get('max_views')
    max_downloads = data.get('max_downloads')
    
    result = drm_manager.create_license(
        content_id, user_id, rights, expiry_date, max_views, max_downloads
    )
    
    log_security_event('admin_action', 'drm', 'create_license',
                      'success' if result['success'] else 'failed',
                      {'content_id': content_id, 'target_user': user_id})
    
    return jsonify(result)


@security_bp.route('/drm/watermark', methods=['POST'])
@rbac.require_permission('content', 'update')
def apply_watermark():
    """Apply watermark to content"""
    data = request.get_json()
    content_id = data.get('content_id')
    watermark_config = data.get('watermark_config', {})
    
    result = drm_manager.apply_watermark(content_id, watermark_config)
    
    log_security_event('data_modification', 'drm', 'watermark',
                      'success' if result['success'] else 'failed',
                      {'content_id': content_id})
    
    return jsonify(result)


@security_bp.route('/drm/access-check', methods=['POST'])
def check_content_access():
    """Check content access rights"""
    data = request.get_json()
    user_session = session.get('user_session')
    
    if not user_session:
        return jsonify({'error': 'Authentication required'}), 401
    
    content_id = data.get('content_id')
    access_type = data.get('access_type', 'view')
    user_id = user_session.get('user_id')
    
    result = drm_manager.check_access_rights(
        content_id, user_id, access_type,
        request.remote_addr, request.headers.get('User-Agent', '')
    )
    
    # Log the access attempt
    drm_manager.log_access(
        content_id, user_id, access_type, result['success'],
        request.remote_addr, request.headers.get('User-Agent', ''),
        user_session.get('session_id')
    )
    
    log_security_event('data_access', 'drm', 'access_check',
                      'success' if result['success'] else 'denied',
                      {'content_id': content_id, 'access_type': access_type})
    
    return jsonify(result)


@security_bp.route('/drm/status', methods=['GET'])
@rbac.require_permission('system', 'read')
def drm_status():
    """Get DRM system status"""
    status = drm_manager.get_drm_status()
    return jsonify(status)


# System Status Endpoint
@security_bp.route('/status', methods=['GET'])
@rbac.require_permission('system', 'read')
def security_system_status():
    """Get overall security system status"""
    encryption_status = encryption_manager.get_encryption_status()
    compliance_report = compliance_manager.get_compliance_report()
    drm_status = drm_manager.get_drm_status()
    
    return jsonify({
        'security_system': 'operational',
        'timestamp': datetime.utcnow().isoformat(),
        'components': {
            'authentication': 'active',
            'rbac': 'active',
            'encryption': encryption_status,
            'compliance': compliance_report,
            'audit_trail': 'active',
            'drm': drm_status
        }
    })


# Health Check Endpoint
@security_bp.route('/health', methods=['GET'])
def security_health_check():
    """Security system health check"""
    return jsonify({
        'status': 'healthy',
        'service': 'enterprise-security',
        'components': {
            'sso': 'available',
            'rbac': 'available',
            'encryption': 'available',
            'compliance': 'available',
            'audit': 'available',
            'drm': 'available'
        },
        'timestamp': datetime.utcnow().isoformat()
    })