"""
Enterprise API endpoints for multi-tenant support
"""
from flask import Blueprint, request, jsonify, g
from functools import wraps
import jwt
import os
from datetime import datetime

enterprise_bp = Blueprint('enterprise', __name__)

# Middleware for tenant isolation
def require_tenant():
    """Middleware to extract and validate tenant context"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get tenant from header or subdomain
            tenant_id = request.headers.get('X-Tenant-ID')
            if not tenant_id:
                # Try extracting from subdomain
                host = request.headers.get('Host', '')
                if '.' in host:
                    subdomain = host.split('.')[0]
                    # Look up tenant by subdomain
                    from models.enterprise import Tenant
                    tenant = Tenant.query.filter_by(slug=subdomain).first()
                    if tenant:
                        tenant_id = tenant.id
            
            if not tenant_id:
                return jsonify({'error': 'Tenant context required'}), 400
                
            g.tenant_id = tenant_id
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def require_auth():
    """Middleware for authentication"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = request.headers.get('Authorization', '').replace('Bearer ', '')
            if not token:
                return jsonify({'error': 'Authentication required'}), 401
            
            try:
                # Decode JWT token
                payload = jwt.decode(token, os.environ.get('SECRET_KEY', 'spiritual-wisdom-key'), algorithms=['HS256'])
                g.user_id = payload['user_id']
                g.tenant_id = payload.get('tenant_id')
            except jwt.InvalidTokenError:
                return jsonify({'error': 'Invalid token'}), 401
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def require_admin():
    """Middleware for admin access"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check if user has admin role
            from models.enterprise import User
            user = User.query.filter_by(id=g.user_id, tenant_id=g.tenant_id).first()
            if not user or user.role not in ['admin', 'super_admin']:
                return jsonify({'error': 'Admin access required'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Tenant management endpoints
@enterprise_bp.route('/tenants', methods=['POST'])
def create_tenant():
    """Create a new tenant workspace"""
    data = request.json
    
    try:
        from models.enterprise import Tenant, db
        
        tenant = Tenant(
            name=data['name'],
            slug=data['slug'],
            domain=data.get('domain'),
            subscription_tier=data.get('subscription_tier', 'free'),
            user_limit=data.get('user_limit', 5),
            api_rate_limit=data.get('api_rate_limit', 1000)
        )
        
        db.session.add(tenant)
        db.session.commit()
        
        # Log tenant creation
        log_audit_event('tenant_created', tenant.id, {'tenant_name': tenant.name})
        
        return jsonify({
            'id': tenant.id,
            'name': tenant.name,
            'slug': tenant.slug,
            'subscription_tier': tenant.subscription_tier,
            'created_at': tenant.created_at.isoformat()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@enterprise_bp.route('/tenants/<tenant_id>', methods=['GET'])
@require_tenant()
@require_auth()
def get_tenant(tenant_id):
    """Get tenant details"""
    try:
        from models.enterprise import Tenant
        
        tenant = Tenant.query.filter_by(id=tenant_id).first()
        if not tenant:
            return jsonify({'error': 'Tenant not found'}), 404
            
        return jsonify({
            'id': tenant.id,
            'name': tenant.name,
            'slug': tenant.slug,
            'domain': tenant.domain,
            'subscription_tier': tenant.subscription_tier,
            'subscription_status': tenant.subscription_status,
            'user_limit': tenant.user_limit,
            'api_rate_limit': tenant.api_rate_limit,
            'theme_config': tenant.theme_config,
            'custom_branding': tenant.custom_branding,
            'created_at': tenant.created_at.isoformat(),
            'is_active': tenant.is_active
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# User management endpoints
@enterprise_bp.route('/admin/users', methods=['GET'])
@require_tenant()
@require_auth()
@require_admin()
def list_users():
    """List all users in tenant"""
    try:
        from models.enterprise import User
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        users = User.query.filter_by(tenant_id=g.tenant_id).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'users': [{
                'id': user.id,
                'email': user.email,
                'full_name': user.full_name,
                'role': user.role,
                'api_usage_count': user.api_usage_count,
                'last_login': user.last_login.isoformat() if user.last_login else None,
                'created_at': user.created_at.isoformat(),
                'is_active': user.is_active
            } for user in users.items],
            'pagination': {
                'page': users.page,
                'pages': users.pages,
                'per_page': users.per_page,
                'total': users.total
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@enterprise_bp.route('/admin/users', methods=['POST'])
@require_tenant()
@require_auth()
@require_admin()
def create_user():
    """Create a new user in tenant"""
    data = request.json
    
    try:
        from models.enterprise import User, db
        from werkzeug.security import generate_password_hash
        
        # Check user limit
        from models.enterprise import Tenant
        tenant = Tenant.query.filter_by(id=g.tenant_id).first()
        current_users = User.query.filter_by(tenant_id=g.tenant_id, is_active=True).count()
        
        if current_users >= tenant.user_limit:
            return jsonify({'error': 'User limit reached for this tenant'}), 403
        
        user = User(
            tenant_id=g.tenant_id,
            email=data['email'],
            password_hash=generate_password_hash(data['password']),
            full_name=data['full_name'],
            role=data.get('role', 'user'),
            permissions=data.get('permissions', [])
        )
        
        db.session.add(user)
        db.session.commit()
        
        # Log user creation
        log_audit_event('user_created', g.tenant_id, {
            'user_id': user.id,
            'email': user.email,
            'role': user.role
        })
        
        return jsonify({
            'id': user.id,
            'email': user.email,
            'full_name': user.full_name,
            'role': user.role,
            'created_at': user.created_at.isoformat()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# API Key management
@enterprise_bp.route('/api-keys', methods=['GET'])
@require_tenant()
@require_auth()
def list_api_keys():
    """List user's API keys"""
    try:
        from models.enterprise import ApiKey
        
        api_keys = ApiKey.query.filter_by(
            tenant_id=g.tenant_id,
            user_id=g.user_id,
            is_active=True
        ).all()
        
        return jsonify({
            'api_keys': [{
                'id': key.id,
                'name': key.name,
                'description': key.description,
                'rate_limit': key.rate_limit,
                'usage_count': key.usage_count,
                'last_used': key.last_used.isoformat() if key.last_used else None,
                'scopes': key.scopes,
                'created_at': key.created_at.isoformat(),
                'expires_at': key.expires_at.isoformat() if key.expires_at else None
            } for key in api_keys]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@enterprise_bp.route('/api-keys', methods=['POST'])
@require_tenant()
@require_auth()
def create_api_key():
    """Create a new API key"""
    data = request.json
    
    try:
        from models.enterprise import ApiKey, db
        from werkzeug.security import generate_password_hash
        
        api_key = ApiKey.generate_key()
        
        key_record = ApiKey(
            tenant_id=g.tenant_id,
            user_id=g.user_id,
            key_hash=generate_password_hash(api_key),
            name=data['name'],
            description=data.get('description'),
            rate_limit=data.get('rate_limit', 1000),
            scopes=data.get('scopes', ['read'])
        )
        
        db.session.add(key_record)
        db.session.commit()
        
        # Log API key creation
        log_audit_event('api_key_created', g.tenant_id, {
            'api_key_id': key_record.id,
            'name': key_record.name
        })
        
        return jsonify({
            'id': key_record.id,
            'key': api_key,  # Only return the key once
            'name': key_record.name,
            'rate_limit': key_record.rate_limit,
            'scopes': key_record.scopes,
            'created_at': key_record.created_at.isoformat()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Audit logging helper
def log_audit_event(action, tenant_id, details=None, user_id=None, success=True, error_message=None):
    """Log audit event"""
    try:
        from models.enterprise import AuditLog, db
        
        log = AuditLog(
            tenant_id=tenant_id,
            user_id=user_id or getattr(g, 'user_id', None),
            action=action,
            ip_address=request.environ.get('REMOTE_ADDR'),
            user_agent=request.headers.get('User-Agent'),
            request_method=request.method,
            request_path=request.path,
            details=details or {},
            success=success,
            error_message=error_message
        )
        
        db.session.add(log)
        db.session.commit()
        
    except Exception as e:
        # Don't fail the main operation if audit logging fails
        print(f"Audit logging error: {e}")

# Analytics endpoint
@enterprise_bp.route('/admin/analytics', methods=['GET'])
@require_tenant()
@require_auth()
@require_admin()
def get_analytics():
    """Get tenant analytics"""
    try:
        from models.enterprise import User, ApiKey, AuditLog
        from sqlalchemy import func, text
        
        # Basic stats
        total_users = User.query.filter_by(tenant_id=g.tenant_id, is_active=True).count()
        total_api_keys = ApiKey.query.filter_by(tenant_id=g.tenant_id, is_active=True).count()
        
        # Usage stats (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        api_calls_count = AuditLog.query.filter(
            AuditLog.tenant_id == g.tenant_id,
            AuditLog.action == 'api_call',
            AuditLog.timestamp >= thirty_days_ago
        ).count()
        
        # Top users by API usage
        top_users = User.query.filter_by(tenant_id=g.tenant_id).order_by(
            User.api_usage_count.desc()
        ).limit(10).all()
        
        return jsonify({
            'total_users': total_users,
            'total_api_keys': total_api_keys,
            'api_calls_last_30_days': api_calls_count,
            'top_users': [{
                'id': user.id,
                'email': user.email,
                'full_name': user.full_name,
                'api_usage_count': user.api_usage_count
            } for user in top_users]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500