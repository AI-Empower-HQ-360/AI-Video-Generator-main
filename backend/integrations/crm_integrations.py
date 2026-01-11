"""
CRM integrations for Salesforce and HubSpot.
Manages customer data synchronization and video engagement tracking.
"""

import requests
import json
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


class SalesforceIntegration:
    """Salesforce CRM integration for lead tracking and video engagement."""
    
    def __init__(self, instance_url: str = None, access_token: str = None):
        self.instance_url = instance_url
        self.access_token = access_token
        self.api_version = "v58.0"
    
    def authenticate(self, client_id: str, client_secret: str, username: str, password: str) -> bool:
        """Authenticate with Salesforce using OAuth."""
        auth_url = f"{self.instance_url}/services/oauth2/token"
        
        data = {
            'grant_type': 'password',
            'client_id': client_id,
            'client_secret': client_secret,
            'username': username,
            'password': password
        }
        
        try:
            response = requests.post(auth_url, data=data)
            if response.status_code == 200:
                auth_data = response.json()
                self.access_token = auth_data['access_token']
                self.instance_url = auth_data['instance_url']
                return True
        except Exception as e:
            current_app.logger.error(f"Salesforce auth failed: {str(e)}")
        
        return False
    
    def create_lead(self, contact_data: Dict[str, Any]) -> Optional[str]:
        """Create a new lead in Salesforce."""
        if not self._is_authenticated():
            return None
        
        lead_data = {
            'FirstName': contact_data.get('first_name', ''),
            'LastName': contact_data.get('last_name', 'Unknown'),
            'Email': contact_data.get('email', ''),
            'Company': contact_data.get('company', 'AI Video Generator User'),
            'LeadSource': 'AI Video Generator',
            'Description': f"Generated {contact_data.get('video_count', 0)} videos"
        }
        
        return self._create_record('Lead', lead_data)
    
    def create_opportunity(self, opportunity_data: Dict[str, Any]) -> Optional[str]:
        """Create sales opportunity for premium upgrade."""
        if not self._is_authenticated():
            return None
        
        opp_data = {
            'Name': f"AI Video Generator - {opportunity_data.get('user_email', 'Unknown')}",
            'StageName': 'Prospecting',
            'CloseDate': datetime.utcnow().strftime('%Y-%m-%d'),
            'Amount': opportunity_data.get('value', 0),
            'Description': f"Video engagement: {opportunity_data.get('video_views', 0)} views"
        }
        
        return self._create_record('Opportunity', opp_data)
    
    def log_video_activity(self, contact_id: str, video_data: Dict[str, Any]) -> Optional[str]:
        """Log video generation/viewing activity."""
        if not self._is_authenticated():
            return None
        
        activity_data = {
            'WhoId': contact_id,
            'Subject': f"Generated Video: {video_data.get('title', 'Untitled')}",
            'Description': f"Video ID: {video_data.get('video_id')}\nDuration: {video_data.get('duration')}s",
            'ActivityDate': datetime.utcnow().strftime('%Y-%m-%d'),
            'Status': 'Completed'
        }
        
        return self._create_record('Task', activity_data)
    
    def _create_record(self, object_type: str, data: Dict[str, Any]) -> Optional[str]:
        """Create a record in Salesforce."""
        url = f"{self.instance_url}/services/data/{self.api_version}/sobjects/{object_type}/"
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 201:
                return response.json()['id']
        except Exception as e:
            current_app.logger.error(f"Salesforce record creation failed: {str(e)}")
        
        return None
    
    def _is_authenticated(self) -> bool:
        """Check if we have valid authentication."""
        return bool(self.access_token and self.instance_url)


class HubSpotIntegration:
    """HubSpot CRM integration for customer management."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.base_url = "https://api.hubapi.com"
    
    def create_contact(self, contact_data: Dict[str, Any]) -> Optional[str]:
        """Create a new contact in HubSpot."""
        if not self.api_key:
            return None
        
        url = f"{self.base_url}/crm/v3/objects/contacts"
        
        properties = {
            'email': contact_data.get('email', ''),
            'firstname': contact_data.get('first_name', ''),
            'lastname': contact_data.get('last_name', ''),
            'company': contact_data.get('company', ''),
            'lifecyclestage': 'lead',
            'leadsource': 'AI Video Generator'
        }
        
        # Add custom properties for video engagement
        if contact_data.get('video_count'):
            properties['videos_generated'] = contact_data['video_count']
        
        if contact_data.get('subscription_type'):
            properties['subscription_type'] = contact_data['subscription_type']
        
        data = {'properties': properties}
        
        return self._make_request('POST', url, data)
    
    def create_deal(self, deal_data: Dict[str, Any]) -> Optional[str]:
        """Create a sales deal for premium upgrades."""
        if not self.api_key:
            return None
        
        url = f"{self.base_url}/crm/v3/objects/deals"
        
        properties = {
            'dealname': f"AI Video Generator - {deal_data.get('user_email', 'Unknown')}",
            'dealstage': 'appointmentscheduled',
            'amount': deal_data.get('value', 0),
            'closedate': datetime.utcnow().strftime('%Y-%m-%d'),
            'pipeline': 'default'
        }
        
        data = {'properties': properties}
        
        return self._make_request('POST', url, data)
    
    def log_video_engagement(self, contact_id: str, video_data: Dict[str, Any]) -> Optional[str]:
        """Log video engagement as custom activity."""
        if not self.api_key:
            return None
        
        url = f"{self.base_url}/crm/v3/objects/contacts/{contact_id}"
        
        # Update contact with video engagement data
        properties = {
            'last_video_generated': datetime.utcnow().isoformat(),
            'last_video_title': video_data.get('title', ''),
            'total_video_duration': video_data.get('total_duration', 0)
        }
        
        data = {'properties': properties}
        
        return self._make_request('PATCH', url, data)
    
    def create_timeline_event(self, contact_id: str, video_data: Dict[str, Any]) -> Optional[str]:
        """Create timeline event for video generation."""
        if not self.api_key:
            return None
        
        url = f"{self.base_url}/crm/v3/timeline/events"
        
        event_data = {
            'eventTemplateId': 'video_generated',  # Custom event template
            'objectId': contact_id,
            'objectType': 'contact',
            'eventType': 'video_generation',
            'timestamp': datetime.utcnow().isoformat(),
            'properties': {
                'video_title': video_data.get('title', ''),
                'video_duration': video_data.get('duration', 0),
                'guru_type': video_data.get('guru', ''),
                'video_url': video_data.get('url', '')
            }
        }
        
        return self._make_request('POST', url, event_data)
    
    def _make_request(self, method: str, url: str, data: Dict = None) -> Optional[str]:
        """Make authenticated request to HubSpot API."""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        try:
            if method == 'POST':
                response = requests.post(url, headers=headers, json=data)
            elif method == 'PATCH':
                response = requests.patch(url, headers=headers, json=data)
            else:
                response = requests.get(url, headers=headers)
            
            if response.status_code in [200, 201]:
                result = response.json()
                return result.get('id', str(result))
                
        except Exception as e:
            current_app.logger.error(f"HubSpot API request failed: {str(e)}")
        
        return None


class CRMManager:
    """Manages CRM integrations and data synchronization."""
    
    def __init__(self):
        self.salesforce = SalesforceIntegration()
        self.hubspot = HubSpotIntegration()
        self.enabled_crms = []
    
    def configure_salesforce(self, instance_url: str, client_id: str, client_secret: str, 
                           username: str, password: str) -> bool:
        """Configure Salesforce integration."""
        self.salesforce = SalesforceIntegration(instance_url)
        success = self.salesforce.authenticate(client_id, client_secret, username, password)
        
        if success and 'salesforce' not in self.enabled_crms:
            self.enabled_crms.append('salesforce')
        
        return success
    
    def configure_hubspot(self, api_key: str) -> bool:
        """Configure HubSpot integration."""
        self.hubspot = HubSpotIntegration(api_key)
        
        if 'hubspot' not in self.enabled_crms:
            self.enabled_crms.append('hubspot')
        
        return True
    
    def sync_user_to_crm(self, user_data: Dict[str, Any], crms: List[str] = None) -> Dict[str, Any]:
        """Sync user data to configured CRM systems."""
        target_crms = crms or self.enabled_crms
        results = {}
        
        if 'salesforce' in target_crms and 'salesforce' in self.enabled_crms:
            lead_id = self.salesforce.create_lead(user_data)
            results['salesforce'] = {'lead_id': lead_id, 'success': bool(lead_id)}
        
        if 'hubspot' in target_crms and 'hubspot' in self.enabled_crms:
            contact_id = self.hubspot.create_contact(user_data)
            results['hubspot'] = {'contact_id': contact_id, 'success': bool(contact_id)}
        
        return results
    
    def track_video_engagement(self, user_id: str, video_data: Dict[str, Any], 
                             crms: List[str] = None) -> Dict[str, Any]:
        """Track video engagement across CRM systems."""
        target_crms = crms or self.enabled_crms
        results = {}
        
        # Note: In a real implementation, you'd need to map user_id to CRM contact IDs
        
        if 'salesforce' in target_crms and 'salesforce' in self.enabled_crms:
            # Assuming we have a way to get contact_id from user_id
            contact_id = f"sf_{user_id}"  # Placeholder
            activity_id = self.salesforce.log_video_activity(contact_id, video_data)
            results['salesforce'] = {'activity_id': activity_id, 'success': bool(activity_id)}
        
        if 'hubspot' in target_crms and 'hubspot' in self.enabled_crms:
            contact_id = f"hs_{user_id}"  # Placeholder
            event_id = self.hubspot.create_timeline_event(contact_id, video_data)
            results['hubspot'] = {'event_id': event_id, 'success': bool(event_id)}
        
        return results


# Global CRM manager instance
crm_manager = CRMManager()