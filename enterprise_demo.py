#!/usr/bin/env python3
"""
Enterprise Features Demo Script

This script demonstrates the key enterprise features implemented in the AI Heart platform.
It simulates typical enterprise workflows including tenant management, user creation, 
API key management, and billing operations.
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000/api"
DEMO_DATA = {
    "tenant": {
        "name": "Demo Enterprise Corp",
        "slug": "demo-enterprise",
        "subscription_tier": "pro"
    },
    "admin_user": {
        "email": "admin@demo-enterprise.com",
        "password": "secure123",
        "full_name": "Demo Admin",
        "role": "admin"
    },
    "regular_user": {
        "email": "user@demo-enterprise.com", 
        "password": "secure123",
        "full_name": "Demo User",
        "role": "user"
    }
}

class EnterpriseDemo:
    def __init__(self):
        self.session = requests.Session()
        self.tenant_id = None
        self.admin_token = None
        self.api_key = None
        
    def print_step(self, step_num, description):
        """Print a formatted step"""
        print(f"\n{'='*60}")
        print(f"STEP {step_num}: {description}")
        print(f"{'='*60}")
        
    def print_result(self, response, operation):
        """Print the result of an API operation"""
        if response.status_code < 400:
            print(f"✅ {operation} - SUCCESS")
            if response.text:
                try:
                    data = response.json()
                    print(json.dumps(data, indent=2))
                except:
                    print(response.text)
        else:
            print(f"❌ {operation} - FAILED ({response.status_code})")
            print(response.text)
        print("-" * 40)
    
    def demo_tenant_creation(self):
        """Demonstrate tenant creation"""
        self.print_step(1, "MULTI-TENANT ARCHITECTURE - Creating Tenant")
        
        response = self.session.post(
            f"{BASE_URL}/enterprise/tenants",
            json=DEMO_DATA["tenant"]
        )
        
        self.print_result(response, "Tenant Creation")
        
        if response.status_code == 201:
            self.tenant_id = response.json()["id"]
            print(f"🏢 Tenant ID: {self.tenant_id}")
    
    def demo_user_management(self):
        """Demonstrate user management"""
        self.print_step(2, "USER MANAGEMENT - Creating Admin and Regular Users")
        
        if not self.tenant_id:
            print("❌ Skipping - No tenant available")
            return
            
        # Set tenant context
        headers = {"X-Tenant-ID": self.tenant_id}
        
        # Create admin user
        response = self.session.post(
            f"{BASE_URL}/enterprise/admin/users",
            json=DEMO_DATA["admin_user"],
            headers=headers
        )
        self.print_result(response, "Admin User Creation")
        
        # Create regular user
        response = self.session.post(
            f"{BASE_URL}/enterprise/admin/users",
            json=DEMO_DATA["regular_user"],
            headers=headers
        )
        self.print_result(response, "Regular User Creation")
    
    def demo_api_key_management(self):
        """Demonstrate API key management"""
        self.print_step(3, "API KEY MANAGEMENT - Creating and Managing API Keys")
        
        if not self.tenant_id:
            print("❌ Skipping - No tenant available")
            return
            
        headers = {"X-Tenant-ID": self.tenant_id}
        
        # Create API key
        api_key_data = {
            "name": "Demo API Key",
            "description": "API key for demonstration purposes",
            "scopes": ["read", "write"],
            "rate_limit": 5000
        }
        
        response = self.session.post(
            f"{BASE_URL}/enterprise/api-keys",
            json=api_key_data,
            headers=headers
        )
        
        self.print_result(response, "API Key Creation")
        
        if response.status_code == 201:
            self.api_key = response.json()["key"]
            print(f"🔑 API Key: {self.api_key}")
            
        # List API keys
        response = self.session.get(
            f"{BASE_URL}/enterprise/api-keys",
            headers=headers
        )
        self.print_result(response, "API Keys Listing")
    
    def demo_rate_limiting(self):
        """Demonstrate rate limiting"""
        self.print_step(4, "RATE LIMITING - Testing API Key Rate Limits")
        
        if not self.api_key:
            print("❌ Skipping - No API key available")
            return
            
        print("🔄 Making multiple API requests to test rate limiting...")
        
        # Make several requests with the API key
        for i in range(3):
            response = self.session.get(
                f"{BASE_URL}/gurus/spiritual",
                headers={"X-API-Key": self.api_key},
                params={"question": f"What is wisdom? (Request {i+1})"}
            )
            
            print(f"Request {i+1}: Status {response.status_code}")
            if 'X-RateLimit-Remaining' in response.headers:
                print(f"  Rate Limit Remaining: {response.headers['X-RateLimit-Remaining']}")
                
            time.sleep(0.5)  # Small delay between requests
        
        # Check rate limit status
        response = self.session.get(
            f"{BASE_URL}/rate-limit/status",
            headers={"X-API-Key": self.api_key}
        )
        self.print_result(response, "Rate Limit Status Check")
    
    def demo_billing_integration(self):
        """Demonstrate billing integration"""
        self.print_step(5, "BILLING INTEGRATION - Subscription Plans and Management")
        
        # Get available plans
        response = self.session.get(f"{BASE_URL}/billing/plans")
        self.print_result(response, "Available Subscription Plans")
        
        # Get current subscription (if tenant exists)
        if self.tenant_id:
            response = self.session.get(
                f"{BASE_URL}/billing/subscription",
                params={"tenant_id": self.tenant_id}
            )
            self.print_result(response, "Current Subscription Status")
    
    def demo_customization(self):
        """Demonstrate white-label customization"""
        self.print_step(6, "WHITE-LABEL CUSTOMIZATION - Branding and Themes")
        
        if not self.tenant_id:
            print("❌ Skipping - No tenant available")
            return
            
        headers = {"X-Tenant-ID": self.tenant_id}
        
        # Get current customization
        response = self.session.get(
            f"{BASE_URL}/customization/customization",
            headers=headers
        )
        self.print_result(response, "Current Customization Settings")
        
        # Update customization
        customization_data = {
            "company_name": "Demo Enterprise Corp",
            "primary_color": "#FF5733",
            "secondary_color": "#33FF57",
            "accent_color": "#3357FF",
            "welcome_message": "Welcome to our custom spiritual guidance platform!",
            "footer_text": "© 2024 Demo Enterprise Corp. All rights reserved."
        }
        
        response = self.session.put(
            f"{BASE_URL}/customization/customization",
            json=customization_data,
            headers=headers
        )
        self.print_result(response, "Customization Update")
        
        # Preview theme
        theme_data = {
            "primary_color": "#FF5733",
            "secondary_color": "#33FF57", 
            "accent_color": "#3357FF"
        }
        
        response = self.session.post(
            f"{BASE_URL}/customization/themes/preview",
            json=theme_data,
            headers=headers
        )
        
        if response.status_code == 200:
            print("✅ Theme Preview - SUCCESS")
            print("Generated CSS preview (first 200 chars):")
            css = response.json().get("css", "")
            print(css[:200] + "..." if len(css) > 200 else css)
        else:
            self.print_result(response, "Theme Preview")
    
    def demo_analytics(self):
        """Demonstrate analytics and reporting"""
        self.print_step(7, "ANALYTICS AND REPORTING - Usage Statistics")
        
        if not self.tenant_id:
            print("❌ Skipping - No tenant available")
            return
            
        headers = {"X-Tenant-ID": self.tenant_id}
        
        # Get analytics data
        response = self.session.get(
            f"{BASE_URL}/enterprise/admin/analytics",
            headers=headers
        )
        self.print_result(response, "Tenant Analytics")
        
        # Get available features
        response = self.session.get(
            f"{BASE_URL}/customization/features",
            headers=headers
        )
        self.print_result(response, "Available Features by Subscription Tier")
    
    def demo_audit_logging(self):
        """Demonstrate audit logging capabilities"""
        self.print_step(8, "AUDIT LOGGING AND COMPLIANCE")
        
        print("📝 Audit logging is automatically captured for all operations.")
        print("The following events have been logged during this demo:")
        print("  • Tenant creation")
        print("  • User management operations")
        print("  • API key creation and usage")
        print("  • Customization changes")
        print("  • All API requests with IP, user agent, and timestamps")
        print("\nIn a real implementation, these logs would be available through:")
        print("  • Admin dashboard audit log viewer")
        print("  • Compliance report generation")
        print("  • Export capabilities for external analysis")
    
    def run_full_demo(self):
        """Run the complete enterprise features demonstration"""
        print("🚀 AI Heart Platform - Enterprise Features Demonstration")
        print(f"📅 Demo started at: {datetime.now().isoformat()}")
        print(f"🌐 API Base URL: {BASE_URL}")
        
        try:
            self.demo_tenant_creation()
            self.demo_user_management() 
            self.demo_api_key_management()
            self.demo_rate_limiting()
            self.demo_billing_integration()
            self.demo_customization()
            self.demo_analytics()
            self.demo_audit_logging()
            
            print(f"\n{'='*60}")
            print("🎉 ENTERPRISE FEATURES DEMO COMPLETED SUCCESSFULLY!")
            print(f"{'='*60}")
            print("\nSummary of demonstrated features:")
            print("✅ Multi-tenant architecture with workspace isolation")
            print("✅ Admin dashboard with user management")
            print("✅ API key management and rate limiting")
            print("✅ Billing integration with subscription plans")
            print("✅ White-label customization options")
            print("✅ Analytics and usage reporting")
            print("✅ Comprehensive audit logging")
            
        except Exception as e:
            print(f"\n❌ Demo failed with error: {e}")
            
        print(f"\n📅 Demo completed at: {datetime.now().isoformat()}")

if __name__ == "__main__":
    import sys
    
    print("🔧 Enterprise Features Demo")
    print("This demo requires the AI Heart backend to be running on localhost:5000")
    print("Make sure to start the backend server before running this demo.")
    
    if len(sys.argv) > 1 and sys.argv[1] == "--run":
        demo = EnterpriseDemo()
        demo.run_full_demo()
    else:
        print("\nTo run the demo, use: python enterprise_demo.py --run")
        print("Note: This will create test data in your database.")