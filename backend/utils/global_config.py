import os
import json
from typing import Dict, Any, Optional
from pathlib import Path

class GlobalConfigManager:
    """Manages global scaling configuration across regions"""
    
    def __init__(self):
        self.config_dir = Path(__file__).parent.parent.parent / 'infrastructure'
        self._regions_config = None
        self._cdn_config = None
        self._payment_config = None
        self._compliance_config = None
        self._load_balancer_config = None
        
    def _load_json_config(self, filename: str) -> Dict[str, Any]:
        """Load JSON configuration file"""
        config_path = self.config_dir / filename
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: Configuration file {filename} not found")
            return {}
        except json.JSONDecodeError as e:
            print(f"Error parsing {filename}: {e}")
            return {}
    
    @property
    def regions_config(self) -> Dict[str, Any]:
        """Get regions configuration"""
        if self._regions_config is None:
            self._regions_config = self._load_json_config('regions.json')
        return self._regions_config
    
    @property
    def cdn_config(self) -> Dict[str, Any]:
        """Get CDN configuration"""
        if self._cdn_config is None:
            self._cdn_config = self._load_json_config('cdn-config.json')
        return self._cdn_config
    
    @property
    def payment_config(self) -> Dict[str, Any]:
        """Get payment localization configuration"""
        if self._payment_config is None:
            self._payment_config = self._load_json_config('payment-localization.json')
        return self._payment_config
    
    @property
    def compliance_config(self) -> Dict[str, Any]:
        """Get compliance configuration"""
        if self._compliance_config is None:
            self._compliance_config = self._load_json_config('compliance-config.json')
        return self._compliance_config
    
    @property
    def load_balancer_config(self) -> Dict[str, Any]:
        """Get load balancer configuration"""
        if self._load_balancer_config is None:
            self._load_balancer_config = self._load_json_config('load-balancer-config.json')
        return self._load_balancer_config
    
    def get_current_region(self) -> str:
        """Get current AWS region from environment or default"""
        return os.environ.get('AWS_REGION', 'us-east-1')
    
    def get_region_info(self, region: Optional[str] = None) -> Dict[str, Any]:
        """Get information for a specific region"""
        if region is None:
            region = self.get_current_region()
        
        regions = self.regions_config.get('regions', {})
        return regions.get(region, {})
    
    def get_supported_currencies(self, region: Optional[str] = None) -> Dict[str, Any]:
        """Get supported currencies for a region"""
        region_info = self.get_region_info(region)
        currency_code = region_info.get('currency', 'USD')
        
        currencies = self.payment_config.get('currencies', {})
        return currencies.get(currency_code, {})
    
    def get_compliance_requirements(self, region: Optional[str] = None) -> Dict[str, Any]:
        """Get compliance requirements for a region"""
        region_info = self.get_region_info(region)
        compliance_list = region_info.get('compliance', [])
        
        requirements = {}
        compliance_frameworks = self.compliance_config.get('compliance_frameworks', {})
        
        for framework in compliance_list:
            if framework in compliance_frameworks:
                requirements[framework] = compliance_frameworks[framework]
        
        return requirements
    
    def get_regional_languages(self, region: Optional[str] = None) -> list:
        """Get supported languages for a region"""
        region_info = self.get_region_info(region)
        return region_info.get('languages', ['en-US'])
    
    def get_cdn_endpoints(self, region: Optional[str] = None) -> list:
        """Get CDN endpoints for a region"""
        region_info = self.get_region_info(region)
        return region_info.get('cdn_endpoints', [])
    
    def get_failover_regions(self, region: Optional[str] = None) -> list:
        """Get failover regions for a specific region"""
        if region is None:
            region = self.get_current_region()
        
        failover_routes = self.regions_config.get('failover_policies', {}).get('failover_routes', {})
        return failover_routes.get(region, [])
    
    def is_rtl_region(self, region: Optional[str] = None) -> bool:
        """Check if region primarily uses RTL languages"""
        region_info = self.get_region_info(region)
        return region_info.get('rtl_support', False)
    
    def get_regional_pricing(self, region: Optional[str] = None) -> Dict[str, Any]:
        """Get pricing configuration for a region"""
        if region is None:
            region = self.get_current_region()
        
        regional_pricing = self.payment_config.get('regional_pricing', {})
        return regional_pricing.get(region, {})
    
    def get_data_residency_rules(self, region: Optional[str] = None) -> Dict[str, Any]:
        """Get data residency rules for a region"""
        if region is None:
            region = self.get_current_region()
        
        data_residency = self.compliance_config.get('data_residency', {}).get('regions', {})
        return data_residency.get(region, {})
    
    def get_health_check_config(self) -> Dict[str, Any]:
        """Get health check configuration"""
        return self.load_balancer_config.get('health_checks', {})
    
    def get_rate_limiting_config(self, region: Optional[str] = None) -> Dict[str, Any]:
        """Get rate limiting configuration for a region"""
        if region is None:
            region = self.get_current_region()
        
        rate_limiting = self.load_balancer_config.get('rate_limiting', {})
        regional_limits = rate_limiting.get('regional_limits', {})
        global_limits = rate_limiting.get('global_limits', {})
        
        # Merge global and regional limits
        config = global_limits.copy()
        if region in regional_limits:
            config.update(regional_limits[region])
        
        return config
    
    def get_cache_headers(self, path: str) -> Dict[str, str]:
        """Get appropriate cache headers for a given path"""
        cache_behaviors = self.cdn_config.get('cdn_config', {}).get('cache_behaviors', {})
        
        # Determine cache behavior based on path
        if path.startswith('/static/'):
            behavior = cache_behaviors.get('static_assets', {})
        elif path.startswith('/api/'):
            behavior = cache_behaviors.get('api_responses', {})
        elif path.startswith('/media/'):
            behavior = cache_behaviors.get('media_content', {})
        else:
            behavior = cache_behaviors.get('html_pages', {})
        
        headers = {}
        if 'cache_ttl' in behavior:
            headers['Cache-Control'] = f"max-age={behavior['cache_ttl']}"
        
        # Add security headers
        security_headers = self.cdn_config.get('cdn_config', {}).get('security_headers', {})
        headers.update(security_headers)
        
        return headers
    
    def should_enable_feature(self, feature: str, region: Optional[str] = None) -> bool:
        """Check if a feature should be enabled for a region based on compliance"""
        compliance_requirements = self.get_compliance_requirements(region)
        
        # Define feature-compliance mappings
        feature_mappings = {
            'analytics_cookies': not any('GDPR' in req for req in compliance_requirements.keys()),
            'cross_border_data_transfer': not any(
                compliance_requirements.get(req, {}).get('requirements', {}).get('data_localization', False)
                for req in compliance_requirements.keys()
            ),
            'user_tracking': not any('GDPR' in req for req in compliance_requirements.keys()),
        }
        
        return feature_mappings.get(feature, True)

# Global instance
global_config = GlobalConfigManager()