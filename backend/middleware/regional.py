from flask import request, g, jsonify, make_response
import os
import geoip2.database
import geoip2.errors
from backend.utils.global_config import global_config
from functools import wraps

class RegionalMiddleware:
    """Middleware for handling regional routing and localization"""
    
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize the middleware with Flask app"""
        self.app = app
        app.before_request(self.before_request)
        app.after_request(self.after_request)
    
    def before_request(self):
        """Process request before routing"""
        # Detect user region
        g.user_region = self.detect_user_region()
        g.user_country = self.detect_user_country()
        g.user_language = self.detect_user_language()
        g.user_currency = self.get_user_currency()
        
        # Set regional configuration
        g.region_config = global_config.get_region_info(g.user_region)
        g.compliance_requirements = global_config.get_compliance_requirements(g.user_region)
        g.rate_limits = global_config.get_rate_limiting_config(g.user_region)
        
        # Check if request should be routed to different region
        if self.should_redirect_region():
            return self.redirect_to_optimal_region()
    
    def after_request(self, response):
        """Process response after routing"""
        # Add regional headers
        response.headers['X-Region'] = g.get('user_region', 'unknown')
        response.headers['X-Country'] = g.get('user_country', 'unknown')
        response.headers['X-Language'] = g.get('user_language', 'en-US')
        response.headers['X-Currency'] = g.get('user_currency', 'USD')
        
        # Add cache headers based on path
        if request.path:
            cache_headers = global_config.get_cache_headers(request.path)
            for header, value in cache_headers.items():
                response.headers[header] = value
        
        # Add GDPR compliance headers if in EU
        if self.is_gdpr_region(g.get('user_region')):
            response.headers['X-GDPR-Region'] = 'true'
        
        return response
    
    def detect_user_region(self):
        """Detect user's AWS region based on various factors"""
        # Check for explicit region override in headers or query params
        explicit_region = (
            request.headers.get('X-Preferred-Region') or 
            request.args.get('region')
        )
        if explicit_region and self.is_valid_region(explicit_region):
            return explicit_region
        
        # Check user's stored preference (from cookie or session)
        stored_region = request.cookies.get('preferred_region')
        if stored_region and self.is_valid_region(stored_region):
            return stored_region
        
        # Detect based on CloudFront headers (if available)
        cf_region = request.headers.get('CloudFront-Viewer-Country')
        if cf_region:
            return self.country_to_region(cf_region)
        
        # Fallback to geo-IP detection
        user_ip = self.get_client_ip()
        return self.ip_to_region(user_ip)
    
    def detect_user_country(self):
        """Detect user's country"""
        # Check CloudFront header first
        cf_country = request.headers.get('CloudFront-Viewer-Country')
        if cf_country:
            return cf_country.upper()
        
        # Fallback to geo-IP
        user_ip = self.get_client_ip()
        try:
            # This would require a GeoIP database file
            # For demo purposes, we'll use a simple mapping
            return self.ip_to_country(user_ip)
        except:
            return 'US'  # Default fallback
    
    def detect_user_language(self):
        """Detect user's preferred language"""
        # Check explicit language preference
        explicit_lang = (
            request.headers.get('X-Preferred-Language') or
            request.args.get('lang') or
            request.cookies.get('language')
        )
        if explicit_lang:
            return explicit_lang
        
        # Check Accept-Language header
        accept_languages = request.headers.get('Accept-Language', '')
        if accept_languages:
            # Parse and find best match
            preferred = self.parse_accept_language(accept_languages)
            regional_languages = global_config.get_regional_languages(g.get('user_region'))
            
            for lang in preferred:
                if lang in regional_languages:
                    return lang
        
        # Default to regional primary language
        regional_languages = global_config.get_regional_languages(g.get('user_region'))
        return regional_languages[0] if regional_languages else 'en-US'
    
    def get_user_currency(self):
        """Get user's preferred currency"""
        # Check explicit preference
        explicit_currency = (
            request.headers.get('X-Preferred-Currency') or
            request.args.get('currency') or
            request.cookies.get('currency')
        )
        if explicit_currency:
            return explicit_currency.upper()
        
        # Default to regional currency
        region_info = global_config.get_region_info(g.get('user_region'))
        return region_info.get('currency', 'USD')
    
    def get_client_ip(self):
        """Get client IP address, considering proxies"""
        # Check various headers for real IP
        real_ip = (
            request.headers.get('CF-Connecting-IP') or  # Cloudflare
            request.headers.get('X-Forwarded-For', '').split(',')[0].strip() or
            request.headers.get('X-Real-IP') or
            request.environ.get('REMOTE_ADDR')
        )
        return real_ip or '127.0.0.1'
    
    def country_to_region(self, country_code):
        """Map country code to AWS region"""
        country_region_mapping = {
            'US': 'us-east-1',
            'CA': 'us-east-1',
            'MX': 'us-east-1',
            'BR': 'us-east-1',
            'GB': 'eu-west-1',
            'IE': 'eu-west-1',
            'FR': 'eu-west-1',
            'DE': 'eu-central-1',
            'IT': 'eu-west-1',
            'ES': 'eu-west-1',
            'NL': 'eu-west-1',
            'SG': 'ap-southeast-1',
            'MY': 'ap-southeast-1',
            'TH': 'ap-southeast-1',
            'JP': 'ap-northeast-1',
            'KR': 'ap-northeast-1',
            'CN': 'ap-southeast-1',  # Approximate, as AWS China is separate
            'IN': 'ap-southeast-1',
            'AE': 'me-south-1',
            'SA': 'me-south-1',
            'IL': 'me-south-1',
            'IR': 'me-south-1',
        }
        return country_region_mapping.get(country_code.upper(), 'us-east-1')
    
    def ip_to_region(self, ip_address):
        """Convert IP address to AWS region (simplified)"""
        # This is a simplified implementation
        # In production, you'd use a proper GeoIP service
        
        # For demo purposes, we'll use a basic mapping
        try:
            # Parse IP to determine general location
            # This would typically use MaxMind GeoIP2 or similar
            country = self.ip_to_country(ip_address)
            return self.country_to_region(country)
        except:
            return 'us-east-1'  # Default fallback
    
    def ip_to_country(self, ip_address):
        """Convert IP address to country code (simplified)"""
        # Simplified implementation - in production use proper GeoIP
        if ip_address.startswith('127.') or ip_address.startswith('192.168.') or ip_address.startswith('10.'):
            return 'US'  # Local/private IPs default to US
        
        # You would implement actual GeoIP lookup here
        return 'US'
    
    def parse_accept_language(self, accept_language):
        """Parse Accept-Language header and return ordered list of languages"""
        languages = []
        for lang_item in accept_language.split(','):
            lang = lang_item.strip().split(';')[0]
            languages.append(lang)
        return languages
    
    def is_valid_region(self, region):
        """Check if region is valid"""
        valid_regions = global_config.regions_config.get('regions', {}).keys()
        return region in valid_regions
    
    def should_redirect_region(self):
        """Determine if request should be redirected to a different region"""
        current_deployment_region = os.environ.get('AWS_REGION', 'us-east-1')
        optimal_region = g.get('user_region', 'us-east-1')
        
        # Don't redirect if we're already in the optimal region
        if current_deployment_region == optimal_region:
            return False
        
        # Don't redirect API requests to avoid breaking functionality
        if request.path.startswith('/api/'):
            return False
        
        # Don't redirect if user explicitly chose this region
        if request.cookies.get('preferred_region') == current_deployment_region:
            return False
        
        return False  # Disable redirects for now
    
    def redirect_to_optimal_region(self):
        """Redirect to optimal region"""
        optimal_region = g.get('user_region')
        regional_config = global_config.cdn_config.get('regional_configurations', {})
        
        if optimal_region in regional_config:
            target_domain = regional_config[optimal_region].get('origin_domain')
            if target_domain:
                redirect_url = f"https://{target_domain}{request.path}"
                if request.query_string:
                    redirect_url += f"?{request.query_string.decode()}"
                
                response = make_response('', 302)
                response.headers['Location'] = redirect_url
                return response
        
        return None
    
    def is_gdpr_region(self, region):
        """Check if region falls under GDPR"""
        compliance_requirements = global_config.get_compliance_requirements(region)
        return 'GDPR' in compliance_requirements

def require_region(*allowed_regions):
    """Decorator to restrict access to specific regions"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_region = g.get('user_region', 'unknown')
            if allowed_regions and user_region not in allowed_regions:
                return jsonify({
                    'error': 'Access not available in your region',
                    'region': user_region,
                    'allowed_regions': list(allowed_regions)
                }), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def require_compliance(*frameworks):
    """Decorator to ensure compliance requirements are met"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            compliance_requirements = g.get('compliance_requirements', {})
            missing_frameworks = []
            
            for framework in frameworks:
                if framework not in compliance_requirements:
                    missing_frameworks.append(framework)
            
            if missing_frameworks:
                return jsonify({
                    'error': 'Compliance requirements not met',
                    'missing_frameworks': missing_frameworks,
                    'region': g.get('user_region', 'unknown')
                }), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator