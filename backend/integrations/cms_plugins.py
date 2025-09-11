"""
CMS plugins for WordPress and Shopify.
Provides video embedding and e-commerce integration capabilities.
"""

import requests
import json
import base64
from datetime import datetime
from typing import Dict, Any, Optional, List
try:
    from flask import current_app
except ImportError:
    # Mock current_app when Flask is not available
    class MockApp:
        class Logger:
            def error(self, msg): print(f"ERROR: {msg}")
            def info(self, msg): print(f"INFO: {msg}")
        logger = Logger()
    current_app = MockApp()


class WordPressPlugin:
    """WordPress plugin integration for video embedding."""
    
    def __init__(self, site_url: str = None, username: str = None, password: str = None):
        self.site_url = site_url
        self.username = username
        self.password = password
        self.api_base = f"{site_url}/wp-json/wp/v2" if site_url else None
    
    def authenticate(self) -> str:
        """Create authentication header for WordPress REST API."""
        if not (self.username and self.password):
            return ""
        
        credentials = base64.b64encode(f"{self.username}:{self.password}".encode()).decode()
        return f"Basic {credentials}"
    
    def create_video_post(self, video_data: Dict[str, Any], post_data: Dict[str, Any] = None) -> Optional[str]:
        """Create a WordPress post with embedded video."""
        if not self.api_base:
            return None
        
        # Generate WordPress shortcode for video
        shortcode = self._generate_video_shortcode(video_data)
        
        # Prepare post content
        content = f"""
        <div class="ai-video-generator-embed">
            <h3>{video_data.get('title', 'AI Generated Video')}</h3>
            {shortcode}
            <p class="video-meta">
                <strong>Duration:</strong> {video_data.get('duration', 'Unknown')} seconds<br>
                <strong>Guru:</strong> {video_data.get('guru', 'Spiritual')}<br>
                <strong>Generated:</strong> {video_data.get('created_at', datetime.utcnow().isoformat())}
            </p>
        </div>
        """
        
        # Default post data
        default_post_data = {
            'title': video_data.get('title', 'AI Generated Video'),
            'content': content,
            'status': 'publish',
            'categories': [1],  # Default category
            'tags': ['ai-video', 'spiritual', video_data.get('guru', 'spiritual')]
        }
        
        # Merge with provided post data
        if post_data:
            default_post_data.update(post_data)
        
        return self._create_post(default_post_data)
    
    def create_video_page(self, video_data: Dict[str, Any]) -> Optional[str]:
        """Create a dedicated page for the video."""
        if not self.api_base:
            return None
        
        shortcode = self._generate_video_shortcode(video_data)
        
        content = f"""
        <div class="ai-video-page">
            <div class="video-container">
                {shortcode}
            </div>
            
            <div class="video-details">
                <h2>{video_data.get('title', 'AI Generated Video')}</h2>
                <div class="meta-info">
                    <p><strong>Duration:</strong> {video_data.get('duration', 'Unknown')} seconds</p>
                    <p><strong>Spiritual Guide:</strong> {video_data.get('guru', 'Spiritual')}</p>
                    <p><strong>Generated:</strong> {video_data.get('created_at', 'Recently')}</p>
                </div>
                
                <div class="video-description">
                    <p>{video_data.get('description', 'This video was generated using AI technology to provide spiritual guidance and wisdom.')}</p>
                </div>
            </div>
        </div>
        """
        
        page_data = {
            'title': f"Video: {video_data.get('title', 'AI Generated')}",
            'content': content,
            'status': 'publish',
            'type': 'page'
        }
        
        return self._create_post(page_data)
    
    def _generate_video_shortcode(self, video_data: Dict[str, Any]) -> str:
        """Generate WordPress shortcode for video embedding."""
        video_url = video_data.get('url', '')
        video_id = video_data.get('video_id', '')
        thumbnail = video_data.get('thumbnail', '')
        
        if video_url.endswith('.mp4'):
            # Direct video file
            return f'[video src="{video_url}" poster="{thumbnail}"]'
        elif 'youtube.com' in video_url or 'youtu.be' in video_url:
            # YouTube video
            return f'[embed]{video_url}[/embed]'
        else:
            # Custom shortcode
            return f'[ai_video id="{video_id}" url="{video_url}" thumbnail="{thumbnail}"]'
    
    def _create_post(self, post_data: Dict[str, Any]) -> Optional[str]:
        """Create a post/page in WordPress."""
        url = f"{self.api_base}/posts"
        
        headers = {
            'Authorization': self.authenticate(),
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(url, headers=headers, json=post_data)
            if response.status_code == 201:
                result = response.json()
                return str(result.get('id'))
        except Exception as e:
            current_app.logger.error(f"WordPress post creation failed: {str(e)}")
        
        return None
    
    def install_plugin(self) -> Dict[str, Any]:
        """Provide installation instructions for WordPress plugin."""
        return {
            'plugin_name': 'AI Video Generator Integration',
            'installation_steps': [
                'Download the plugin ZIP file',
                'Upload to /wp-content/plugins/ directory',
                'Activate the plugin in WordPress admin',
                'Configure API settings in plugin options'
            ],
            'shortcode_usage': '[ai_video id="video_id"]',
            'required_wp_version': '5.0+'
        }


class ShopifyIntegration:
    """Shopify integration for product video generation."""
    
    def __init__(self, shop_domain: str = None, access_token: str = None):
        self.shop_domain = shop_domain
        self.access_token = access_token
        self.api_version = "2023-10"
        self.base_url = f"https://{shop_domain}.myshopify.com/admin/api/{self.api_version}" if shop_domain else None
    
    def create_product_video(self, product_id: str, video_data: Dict[str, Any]) -> Optional[str]:
        """Add video to Shopify product."""
        if not self._is_authenticated():
            return None
        
        # Create metafield for video data
        metafield_data = {
            'metafield': {
                'namespace': 'ai_video_generator',
                'key': 'product_video',
                'value': json.dumps({
                    'video_url': video_data.get('url', ''),
                    'video_id': video_data.get('video_id', ''),
                    'title': video_data.get('title', ''),
                    'duration': video_data.get('duration', 0),
                    'thumbnail': video_data.get('thumbnail', ''),
                    'created_at': video_data.get('created_at', datetime.utcnow().isoformat())
                }),
                'type': 'json'
            }
        }
        
        url = f"{self.base_url}/products/{product_id}/metafields.json"
        
        return self._make_request('POST', url, metafield_data)
    
    def update_product_description(self, product_id: str, video_data: Dict[str, Any]) -> Optional[str]:
        """Update product description to include video."""
        if not self._is_authenticated():
            return None
        
        # Get current product
        product_url = f"{self.base_url}/products/{product_id}.json"
        product_response = self._make_request('GET', product_url)
        
        if not product_response:
            return None
        
        try:
            product = json.loads(product_response) if isinstance(product_response, str) else product_response
            current_description = product.get('product', {}).get('body_html', '')
            
            # Add video section to description
            video_section = f"""
            <div class="ai-generated-video">
                <h3>🎥 Product Video</h3>
                <video controls poster="{video_data.get('thumbnail', '')}">
                    <source src="{video_data.get('url', '')}" type="video/mp4">
                    Your browser does not support the video tag.
                </video>
                <p><em>This video was generated using AI technology to showcase our product.</em></p>
            </div>
            """
            
            updated_description = current_description + video_section
            
            update_data = {
                'product': {
                    'id': product_id,
                    'body_html': updated_description
                }
            }
            
            return self._make_request('PUT', product_url, update_data)
            
        except Exception as e:
            current_app.logger.error(f"Product description update failed: {str(e)}")
            return None
    
    def create_video_collection(self, video_data_list: List[Dict[str, Any]]) -> Optional[str]:
        """Create a collection for AI-generated videos."""
        if not self._is_authenticated():
            return None
        
        collection_data = {
            'custom_collection': {
                'title': 'AI Generated Product Videos',
                'body_html': '<p>Products featuring AI-generated videos for enhanced shopping experience.</p>',
                'published': True,
                'sort_order': 'created-desc'
            }
        }
        
        url = f"{self.base_url}/custom_collections.json"
        
        return self._make_request('POST', url, collection_data)
    
    def install_app(self) -> Dict[str, Any]:
        """Provide Shopify app installation information."""
        return {
            'app_name': 'AI Video Generator for Shopify',
            'installation_url': 'https://apps.shopify.com/ai-video-generator',
            'features': [
                'Automatic product video generation',
                'Custom video thumbnails',
                'Product description enhancement',
                'Video collection management',
                'Analytics integration'
            ],
            'pricing': 'Free tier available, premium features from $9.99/month'
        }
    
    def _make_request(self, method: str, url: str, data: Dict = None) -> Optional[str]:
        """Make authenticated request to Shopify API."""
        headers = {
            'X-Shopify-Access-Token': self.access_token,
            'Content-Type': 'application/json'
        }
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=data)
            elif method == 'PUT':
                response = requests.put(url, headers=headers, json=data)
            else:
                return None
            
            if response.status_code in [200, 201]:
                return response.json()
                
        except Exception as e:
            current_app.logger.error(f"Shopify API request failed: {str(e)}")
        
        return None
    
    def _is_authenticated(self) -> bool:
        """Check if we have valid authentication."""
        return bool(self.access_token and self.base_url)


class CMSManager:
    """Manages CMS integrations and plugin installations."""
    
    def __init__(self):
        self.wordpress = WordPressPlugin()
        self.shopify = ShopifyIntegration()
        self.enabled_platforms = []
    
    def configure_wordpress(self, site_url: str, username: str, password: str) -> bool:
        """Configure WordPress integration."""
        self.wordpress = WordPressPlugin(site_url, username, password)
        
        if 'wordpress' not in self.enabled_platforms:
            self.enabled_platforms.append('wordpress')
        
        return True
    
    def configure_shopify(self, shop_domain: str, access_token: str) -> bool:
        """Configure Shopify integration."""
        self.shopify = ShopifyIntegration(shop_domain, access_token)
        
        if 'shopify' not in self.enabled_platforms:
            self.enabled_platforms.append('shopify')
        
        return True
    
    def publish_video_to_cms(self, video_data: Dict[str, Any], platforms: List[str] = None, 
                           options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Publish video to configured CMS platforms."""
        target_platforms = platforms or self.enabled_platforms
        results = {}
        options = options or {}
        
        if 'wordpress' in target_platforms and 'wordpress' in self.enabled_platforms:
            if options.get('create_page', False):
                page_id = self.wordpress.create_video_page(video_data)
                results['wordpress'] = {'page_id': page_id, 'type': 'page', 'success': bool(page_id)}
            else:
                post_id = self.wordpress.create_video_post(video_data, options.get('post_data'))
                results['wordpress'] = {'post_id': post_id, 'type': 'post', 'success': bool(post_id)}
        
        if 'shopify' in target_platforms and 'shopify' in self.enabled_platforms:
            product_id = options.get('product_id')
            if product_id:
                metafield_id = self.shopify.create_product_video(product_id, video_data)
                if options.get('update_description', True):
                    self.shopify.update_product_description(product_id, video_data)
                
                results['shopify'] = {
                    'metafield_id': metafield_id, 
                    'product_id': product_id,
                    'success': bool(metafield_id)
                }
        
        return results


# Global CMS manager instance
cms_manager = CMSManager()