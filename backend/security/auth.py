"""
OAuth2/SAML SSO Integration with Active Directory
Enterprise authentication and SSO management
"""

import hashlib
import secrets
import time
import base64
from typing import Dict, Optional, Tuple, List
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
from flask import request, session, redirect, url_for, jsonify


class OAuth2Provider:
    """OAuth2 integration for enterprise authentication"""
    
    def __init__(self, config: Dict):
        self.client_id = config.get('client_id')
        self.client_secret = config.get('client_secret')
        self.redirect_uri = config.get('redirect_uri')
        self.authorization_endpoint = config.get('authorization_endpoint')
        self.token_endpoint = config.get('token_endpoint')
        self.userinfo_endpoint = config.get('userinfo_endpoint')
        
    def generate_authorization_url(self, state: str, scopes: List[str] = None) -> str:
        """Generate OAuth2 authorization URL"""
        if scopes is None:
            scopes = ['openid', 'profile', 'email']
        
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': ' '.join(scopes),
            'state': state
        }
        
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        return f"{self.authorization_endpoint}?{query_string}"
    
    def exchange_code_for_token(self, code: str) -> Dict:
        """Exchange authorization code for access token"""
        # In production, this would make HTTP request to token endpoint
        # For now, return mock token data
        return {
            'access_token': self._generate_token(),
            'token_type': 'Bearer',
            'expires_in': 3600,
            'refresh_token': self._generate_token(),
            'scope': 'openid profile email'
        }
    
    def get_user_info(self, access_token: str) -> Dict:
        """Get user information using access token"""
        # In production, this would make HTTP request to userinfo endpoint
        # For now, return mock user data
        return {
            'sub': '12345',
            'email': 'user@enterprise.com',
            'name': 'Enterprise User',
            'preferred_username': 'enterprise.user',
            'groups': ['admin', 'content_creator']
        }
    
    def _generate_token(self) -> str:
        """Generate secure random token"""
        return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode()


class SAMLProvider:
    """SAML SSO integration for enterprise authentication"""
    
    def __init__(self, config: Dict):
        self.issuer = config.get('issuer')
        self.sso_url = config.get('sso_url')
        self.x509_cert = config.get('x509_cert')
        self.private_key = config.get('private_key')
        
    def generate_saml_request(self, request_id: str) -> str:
        """Generate SAML AuthnRequest"""
        request_template = f"""
        <samlp:AuthnRequest xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol"
                           xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion"
                           ID="{request_id}"
                           Version="2.0"
                           IssueInstant="{datetime.utcnow().isoformat()}Z"
                           Destination="{self.sso_url}"
                           ProtocolBinding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
                           AssertionConsumerServiceURL="{self.issuer}/acs">
            <saml:Issuer>{self.issuer}</saml:Issuer>
        </samlp:AuthnRequest>
        """
        
        # Base64 encode the request
        encoded_request = base64.b64encode(request_template.encode()).decode()
        return encoded_request
    
    def validate_saml_response(self, saml_response: str) -> Dict:
        """Validate and parse SAML response"""
        try:
            # Decode base64 response
            decoded_response = base64.b64decode(saml_response)
            
            # Parse XML
            root = ET.fromstring(decoded_response)
            
            # Extract user attributes (simplified for demo)
            user_data = {
                'username': 'saml.user',
                'email': 'samluser@enterprise.com',
                'groups': ['viewer', 'editor'],
                'department': 'IT',
                'authenticated': True
            }
            
            return user_data
            
        except Exception as e:
            return {'error': f'SAML validation failed: {str(e)}'}


class ActiveDirectoryIntegration:
    """Active Directory integration for user management"""
    
    def __init__(self, config: Dict):
        self.ldap_server = config.get('ldap_server')
        self.bind_dn = config.get('bind_dn')
        self.bind_password = config.get('bind_password')
        self.search_base = config.get('search_base')
        
    def authenticate_user(self, username: str, password: str) -> Dict:
        """Authenticate user against Active Directory"""
        # In production, this would use LDAP to authenticate
        # For now, return mock authentication result
        if username and password:
            return {
                'authenticated': True,
                'username': username,
                'email': f'{username}@enterprise.com',
                'groups': self._get_user_groups(username),
                'department': 'IT',
                'manager': 'manager@enterprise.com'
            }
        return {'authenticated': False}
    
    def _get_user_groups(self, username: str) -> List[str]:
        """Get user groups from Active Directory"""
        # Mock group membership based on username patterns
        if 'admin' in username.lower():
            return ['Domain Admins', 'IT Admin', 'Content Admin']
        elif 'manager' in username.lower():
            return ['Managers', 'Content Reviewer']
        else:
            return ['Domain Users', 'Content Creator']


class SecurityManager:
    """Main security manager coordinating all authentication methods"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.oauth2_provider = OAuth2Provider(config.get('oauth2', {}))
        self.saml_provider = SAMLProvider(config.get('saml', {}))
        self.ad_integration = ActiveDirectoryIntegration(config.get('active_directory', {}))
        self.session_timeout = config.get('session_timeout', 3600)
        
    def initiate_sso_login(self, provider: str = 'oauth2') -> Dict:
        """Initiate SSO login process"""
        state = self._generate_state_token()
        session['sso_state'] = state
        session['sso_provider'] = provider
        
        if provider == 'oauth2':
            auth_url = self.oauth2_provider.generate_authorization_url(state)
            return {'auth_url': auth_url, 'state': state}
        elif provider == 'saml':
            request_id = self._generate_request_id()
            saml_request = self.saml_provider.generate_saml_request(request_id)
            return {'saml_request': saml_request, 'request_id': request_id}
        else:
            return {'error': 'Unsupported SSO provider'}
    
    def handle_sso_callback(self, provider: str, **kwargs) -> Dict:
        """Handle SSO callback and complete authentication"""
        if provider == 'oauth2':
            return self._handle_oauth2_callback(**kwargs)
        elif provider == 'saml':
            return self._handle_saml_callback(**kwargs)
        else:
            return {'error': 'Unsupported SSO provider'}
    
    def _handle_oauth2_callback(self, code: str, state: str) -> Dict:
        """Handle OAuth2 callback"""
        if session.get('sso_state') != state:
            return {'error': 'Invalid state parameter'}
        
        token_data = self.oauth2_provider.exchange_code_for_token(code)
        if 'access_token' in token_data:
            user_info = self.oauth2_provider.get_user_info(token_data['access_token'])
            return self._create_user_session(user_info, 'oauth2')
        
        return {'error': 'Token exchange failed'}
    
    def _handle_saml_callback(self, saml_response: str) -> Dict:
        """Handle SAML callback"""
        user_data = self.saml_provider.validate_saml_response(saml_response)
        if user_data.get('authenticated'):
            return self._create_user_session(user_data, 'saml')
        
        return {'error': 'SAML authentication failed'}
    
    def authenticate_local(self, username: str, password: str) -> Dict:
        """Authenticate user with local credentials (AD integration)"""
        auth_result = self.ad_integration.authenticate_user(username, password)
        if auth_result.get('authenticated'):
            return self._create_user_session(auth_result, 'local')
        
        return {'error': 'Authentication failed'}
    
    def _create_user_session(self, user_data: Dict, auth_method: str) -> Dict:
        """Create secure user session"""
        session_id = self._generate_session_id()
        session_data = {
            'session_id': session_id,
            'user_id': user_data.get('username') or user_data.get('sub'),
            'email': user_data.get('email'),
            'groups': user_data.get('groups', []),
            'auth_method': auth_method,
            'created_at': datetime.utcnow().isoformat(),
            'expires_at': (datetime.utcnow() + timedelta(seconds=self.session_timeout)).isoformat()
        }
        
        # Store session data securely
        session['user_session'] = session_data
        
        return {
            'success': True,
            'session_id': session_id,
            'user': user_data,
            'expires_in': self.session_timeout
        }
    
    def validate_session(self, session_id: str) -> Dict:
        """Validate user session"""
        user_session = session.get('user_session')
        if not user_session or user_session.get('session_id') != session_id:
            return {'valid': False, 'error': 'Invalid session'}
        
        expires_at = datetime.fromisoformat(user_session['expires_at'])
        if datetime.utcnow() > expires_at:
            return {'valid': False, 'error': 'Session expired'}
        
        return {'valid': True, 'user_session': user_session}
    
    def logout(self, session_id: str) -> Dict:
        """Logout user and invalidate session"""
        if session.get('user_session', {}).get('session_id') == session_id:
            session.clear()
            return {'success': True, 'message': 'Logged out successfully'}
        
        return {'error': 'Invalid session for logout'}
    
    def _generate_state_token(self) -> str:
        """Generate secure state token for OAuth2"""
        return hashlib.sha256(secrets.token_bytes(32)).hexdigest()
    
    def _generate_request_id(self) -> str:
        """Generate unique request ID for SAML"""
        return f"_{hashlib.sha256(secrets.token_bytes(16)).hexdigest()}"
    
    def _generate_session_id(self) -> str:
        """Generate secure session ID"""
        return hashlib.sha256(f"{secrets.token_hex(32)}{time.time()}".encode()).hexdigest()