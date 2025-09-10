"""
White-label customization API endpoints
"""
from flask import Blueprint, request, jsonify, g
from api.enterprise import require_tenant, require_auth, require_admin

customization_bp = Blueprint('customization', __name__)

@customization_bp.route('/customization', methods=['GET'])
@require_tenant()
@require_auth()
def get_customization():
    """Get current tenant customization settings"""
    try:
        from models.enterprise import CustomizationConfig, Tenant
        
        tenant = Tenant.query.filter_by(id=g.tenant_id).first()
        if not tenant:
            return jsonify({'error': 'Tenant not found'}), 404
        
        customization = CustomizationConfig.query.filter_by(tenant_id=g.tenant_id).first()
        
        if not customization:
            # Return default customization
            return jsonify({
                'tenant_id': g.tenant_id,
                'company_name': tenant.name,
                'logo_url': None,
                'favicon_url': None,
                'primary_color': '#3B82F6',
                'secondary_color': '#1F2937',
                'accent_color': '#F59E0B',
                'welcome_message': None,
                'footer_text': None,
                'custom_css': None,
                'enabled_features': ['spiritual_guidance', 'meditation']
            })
        
        return jsonify({
            'tenant_id': customization.tenant_id,
            'company_name': customization.company_name,
            'logo_url': customization.logo_url,
            'favicon_url': customization.favicon_url,
            'primary_color': customization.primary_color,
            'secondary_color': customization.secondary_color,
            'accent_color': customization.accent_color,
            'welcome_message': customization.welcome_message,
            'footer_text': customization.footer_text,
            'custom_css': customization.custom_css,
            'enabled_features': customization.enabled_features,
            'created_at': customization.created_at.isoformat(),
            'updated_at': customization.updated_at.isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@customization_bp.route('/customization', methods=['PUT'])
@require_tenant()
@require_auth()
@require_admin()
def update_customization():
    """Update tenant customization settings"""
    data = request.json
    
    try:
        from models.enterprise import CustomizationConfig, Tenant, db
        
        # Check if tenant has white-label features
        tenant = Tenant.query.filter_by(id=g.tenant_id).first()
        if tenant.subscription_tier not in ['pro', 'enterprise']:
            return jsonify({'error': 'White-label customization requires Pro or Enterprise plan'}), 403
        
        customization = CustomizationConfig.query.filter_by(tenant_id=g.tenant_id).first()
        
        if not customization:
            customization = CustomizationConfig(tenant_id=g.tenant_id)
            db.session.add(customization)
        
        # Update fields if provided
        if 'company_name' in data:
            customization.company_name = data['company_name']
        if 'logo_url' in data:
            customization.logo_url = data['logo_url']
        if 'favicon_url' in data:
            customization.favicon_url = data['favicon_url']
        if 'primary_color' in data:
            customization.primary_color = data['primary_color']
        if 'secondary_color' in data:
            customization.secondary_color = data['secondary_color']
        if 'accent_color' in data:
            customization.accent_color = data['accent_color']
        if 'welcome_message' in data:
            customization.welcome_message = data['welcome_message']
        if 'footer_text' in data:
            customization.footer_text = data['footer_text']
        if 'custom_css' in data:
            customization.custom_css = data['custom_css']
        if 'enabled_features' in data:
            customization.enabled_features = data['enabled_features']
        
        db.session.commit()
        
        # Log customization update
        from api.enterprise import log_audit_event
        log_audit_event('customization_updated', g.tenant_id, {
            'fields_updated': list(data.keys())
        })
        
        return jsonify({
            'message': 'Customization updated successfully',
            'tenant_id': customization.tenant_id,
            'updated_at': customization.updated_at.isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@customization_bp.route('/themes/preview', methods=['POST'])
@require_tenant()
@require_auth()
def preview_theme():
    """Generate theme preview CSS"""
    data = request.json
    
    try:
        primary_color = data.get('primary_color', '#3B82F6')
        secondary_color = data.get('secondary_color', '#1F2937')
        accent_color = data.get('accent_color', '#F59E0B')
        
        # Generate CSS variables for theme
        css = f"""
        :root {{
            --primary-color: {primary_color};
            --secondary-color: {secondary_color};
            --accent-color: {accent_color};
            --primary-rgb: {hex_to_rgb(primary_color)};
            --secondary-rgb: {hex_to_rgb(secondary_color)};
            --accent-rgb: {hex_to_rgb(accent_color)};
        }}
        
        .btn-primary {{
            background-color: var(--primary-color);
            border-color: var(--primary-color);
        }}
        
        .btn-primary:hover {{
            background-color: rgba(var(--primary-rgb), 0.8);
            border-color: rgba(var(--primary-rgb), 0.8);
        }}
        
        .navbar {{
            background-color: var(--secondary-color);
        }}
        
        .accent {{
            color: var(--accent-color);
        }}
        
        .bg-accent {{
            background-color: var(--accent-color);
        }}
        
        a {{
            color: var(--primary-color);
        }}
        
        a:hover {{
            color: rgba(var(--primary-rgb), 0.8);
        }}
        """
        
        return jsonify({
            'css': css,
            'colors': {
                'primary': primary_color,
                'secondary': secondary_color,
                'accent': accent_color
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@customization_bp.route('/branding/upload', methods=['POST'])
@require_tenant()
@require_auth()
@require_admin()
def upload_branding_asset():
    """Upload branding assets (logo, favicon)"""
    try:
        # This is a placeholder - in production, you'd integrate with a file storage service
        file_type = request.form.get('type')  # 'logo' or 'favicon'
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file type
        allowed_extensions = {'png', 'jpg', 'jpeg', 'svg', 'ico'}
        if not file.filename.lower().endswith(tuple(allowed_extensions)):
            return jsonify({'error': 'Invalid file type'}), 400
        
        # In production, upload to S3/CloudFlare/etc and return URL
        # For now, return a placeholder URL
        file_url = f"https://cdn.example.com/{g.tenant_id}/{file_type}/{file.filename}"
        
        # Update customization record
        from models.enterprise import CustomizationConfig, db
        
        customization = CustomizationConfig.query.filter_by(tenant_id=g.tenant_id).first()
        if not customization:
            customization = CustomizationConfig(tenant_id=g.tenant_id)
            db.session.add(customization)
        
        if file_type == 'logo':
            customization.logo_url = file_url
        elif file_type == 'favicon':
            customization.favicon_url = file_url
        
        db.session.commit()
        
        # Log asset upload
        from api.enterprise import log_audit_event
        log_audit_event('branding_asset_uploaded', g.tenant_id, {
            'asset_type': file_type,
            'filename': file.filename,
            'url': file_url
        })
        
        return jsonify({
            'message': f'{file_type.title()} uploaded successfully',
            'url': file_url,
            'type': file_type
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@customization_bp.route('/domain', methods=['PUT'])
@require_tenant()
@require_auth()
@require_admin()
def update_custom_domain():
    """Update custom domain for tenant"""
    data = request.json
    
    try:
        from models.enterprise import Tenant, db
        
        tenant = Tenant.query.filter_by(id=g.tenant_id).first()
        
        # Check if tenant has custom domain feature
        if tenant.subscription_tier != 'enterprise':
            return jsonify({'error': 'Custom domain requires Enterprise plan'}), 403
        
        domain = data.get('domain')
        if not domain:
            return jsonify({'error': 'Domain is required'}), 400
        
        # Basic domain validation
        if not is_valid_domain(domain):
            return jsonify({'error': 'Invalid domain format'}), 400
        
        # Check if domain is already taken
        existing_tenant = Tenant.query.filter_by(domain=domain).first()
        if existing_tenant and existing_tenant.id != g.tenant_id:
            return jsonify({'error': 'Domain already taken'}), 409
        
        tenant.domain = domain
        db.session.commit()
        
        # Log domain update
        from api.enterprise import log_audit_event
        log_audit_event('custom_domain_updated', g.tenant_id, {
            'domain': domain
        })
        
        return jsonify({
            'message': 'Custom domain updated successfully',
            'domain': domain,
            'verification_required': True,
            'instructions': 'Please create a CNAME record pointing to platform.example.com'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@customization_bp.route('/features', methods=['GET'])
@require_tenant()
@require_auth()
def get_available_features():
    """Get available features for tenant's subscription"""
    try:
        from models.enterprise import Tenant
        
        tenant = Tenant.query.filter_by(id=g.tenant_id).first()
        
        # Define features by subscription tier
        features_by_tier = {
            'free': [
                'spiritual_guidance',
                'meditation',
                'basic_slokas'
            ],
            'basic': [
                'spiritual_guidance',
                'meditation',
                'basic_slokas',
                'analytics',
                'api_access',
                'email_support'
            ],
            'pro': [
                'spiritual_guidance',
                'meditation',
                'advanced_slokas',
                'analytics',
                'api_access',
                'custom_branding',
                'priority_support',
                'user_management'
            ],
            'enterprise': [
                'all_features',
                'white_label',
                'sso',
                'custom_domain',
                'dedicated_support',
                'audit_logs',
                'compliance_reports',
                'advanced_analytics'
            ]
        }
        
        available_features = features_by_tier.get(tenant.subscription_tier, [])
        
        return jsonify({
            'tenant_id': g.tenant_id,
            'subscription_tier': tenant.subscription_tier,
            'available_features': available_features,
            'feature_descriptions': get_feature_descriptions()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return ', '.join(str(int(hex_color[i:i+2], 16)) for i in (0, 2, 4))

def is_valid_domain(domain):
    """Basic domain validation"""
    import re
    pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
    return re.match(pattern, domain) is not None

def get_feature_descriptions():
    """Get feature descriptions"""
    return {
        'spiritual_guidance': 'AI-powered spiritual guidance and wisdom',
        'meditation': 'Guided meditation sessions and practices',
        'basic_slokas': 'Access to basic Sanskrit slokas and translations',
        'advanced_slokas': 'Complete sloka database with detailed explanations',
        'analytics': 'Usage analytics and insights',
        'api_access': 'REST API access for integrations',
        'custom_branding': 'Customize colors, logos, and basic branding',
        'white_label': 'Complete white-label customization',
        'sso': 'Single Sign-On integration',
        'custom_domain': 'Use your own domain name',
        'user_management': 'Advanced user management features',
        'audit_logs': 'Comprehensive audit logging',
        'compliance_reports': 'Compliance and security reports',
        'advanced_analytics': 'Advanced analytics and reporting',
        'email_support': 'Email support',
        'priority_support': 'Priority customer support',
        'dedicated_support': 'Dedicated customer success manager'
    }