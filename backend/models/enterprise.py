"""
Enterprise multi-tenant models for the AI Heart platform
"""
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
import uuid
import secrets

db = SQLAlchemy()

class Tenant(db.Model):
    """Multi-tenant workspace model"""
    __tablename__ = 'tenants'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    domain = db.Column(db.String(255), unique=True, nullable=True)  # Custom domain
    
    # Subscription info
    subscription_tier = db.Column(db.String(50), default='free')  # free, basic, pro, enterprise
    subscription_status = db.Column(db.String(50), default='active')
    stripe_customer_id = db.Column(db.String(100), nullable=True)
    
    # Customization
    theme_config = db.Column(db.JSON, default={})  # Colors, logos, etc.
    custom_branding = db.Column(db.JSON, default={})
    
    # Limits
    user_limit = db.Column(db.Integer, default=5)
    api_rate_limit = db.Column(db.Integer, default=1000)  # per hour
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    users = db.relationship('User', backref='tenant', lazy='dynamic')
    api_keys = db.relationship('ApiKey', backref='tenant', lazy='dynamic')
    audit_logs = db.relationship('AuditLog', backref='tenant', lazy='dynamic')

class User(db.Model):
    """Enhanced user model with tenant support"""
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = db.Column(db.String(36), db.ForeignKey('tenants.id'), nullable=False)
    
    email = db.Column(db.String(255), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(255), nullable=False)
    
    # Roles and permissions
    role = db.Column(db.String(50), default='user')  # admin, manager, user
    permissions = db.Column(db.JSON, default=[])
    
    # Usage tracking
    api_usage_count = db.Column(db.Integer, default=0)
    last_api_call = db.Column(db.DateTime, nullable=True)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    api_keys = db.relationship('ApiKey', backref='user', lazy='dynamic')
    
    __table_args__ = (db.UniqueConstraint('tenant_id', 'email', name='unique_email_per_tenant'),)

class ApiKey(db.Model):
    """API key management for rate limiting and access control"""
    __tablename__ = 'api_keys'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = db.Column(db.String(36), db.ForeignKey('tenants.id'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    
    key_hash = db.Column(db.String(255), nullable=False, unique=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    # Rate limiting
    rate_limit = db.Column(db.Integer, default=1000)  # requests per hour
    usage_count = db.Column(db.Integer, default=0)
    last_used = db.Column(db.DateTime, nullable=True)
    
    # Permissions
    scopes = db.Column(db.JSON, default=['read'])  # read, write, admin
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    
    @staticmethod
    def generate_key():
        """Generate a secure API key"""
        return f"aih_{secrets.token_urlsafe(32)}"

class Subscription(db.Model):
    """Stripe subscription management"""
    __tablename__ = 'subscriptions'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = db.Column(db.String(36), db.ForeignKey('tenants.id'), nullable=False)
    
    stripe_subscription_id = db.Column(db.String(100), unique=True, nullable=False)
    stripe_customer_id = db.Column(db.String(100), nullable=False)
    stripe_price_id = db.Column(db.String(100), nullable=False)
    
    status = db.Column(db.String(50), nullable=False)  # active, canceled, past_due, etc.
    current_period_start = db.Column(db.DateTime, nullable=False)
    current_period_end = db.Column(db.DateTime, nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    tenant = db.relationship('Tenant', backref='subscriptions')

class AuditLog(db.Model):
    """Comprehensive audit logging for compliance"""
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = db.Column(db.String(36), db.ForeignKey('tenants.id'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    
    # Action details
    action = db.Column(db.String(100), nullable=False)  # login, api_call, user_created, etc.
    resource_type = db.Column(db.String(50), nullable=True)  # user, api_key, subscription
    resource_id = db.Column(db.String(36), nullable=True)
    
    # Request details
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.Text, nullable=True)
    request_method = db.Column(db.String(10), nullable=True)
    request_path = db.Column(db.String(500), nullable=True)
    
    # Additional data
    details = db.Column(db.JSON, default={})
    success = db.Column(db.Boolean, default=True)
    error_message = db.Column(db.Text, nullable=True)
    
    # Metadata
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
class CustomizationConfig(db.Model):
    """White-label customization configuration"""
    __tablename__ = 'customization_configs'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = db.Column(db.String(36), db.ForeignKey('tenants.id'), nullable=False)
    
    # Branding
    company_name = db.Column(db.String(255), nullable=True)
    logo_url = db.Column(db.String(500), nullable=True)
    favicon_url = db.Column(db.String(500), nullable=True)
    
    # Theme colors
    primary_color = db.Column(db.String(7), default='#3B82F6')  # Hex color
    secondary_color = db.Column(db.String(7), default='#1F2937')
    accent_color = db.Column(db.String(7), default='#F59E0B')
    
    # Custom content
    welcome_message = db.Column(db.Text, nullable=True)
    footer_text = db.Column(db.Text, nullable=True)
    custom_css = db.Column(db.Text, nullable=True)
    
    # Features
    enabled_features = db.Column(db.JSON, default=['spiritual_guidance', 'meditation'])
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    tenant = db.relationship('Tenant', backref='customization', uselist=False)