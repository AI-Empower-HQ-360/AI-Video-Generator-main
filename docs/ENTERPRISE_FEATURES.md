# Enterprise Features Documentation

## Overview

The AI Heart Development Platform has been enhanced with enterprise-grade capabilities to support multi-tenant SaaS operations, subscription management, and white-label customization.

## Features Implemented

### 1. Multi-Tenant Architecture with Workspace Isolation

**Database Models:**
- `Tenant` - Workspace isolation with subscription tiers
- `User` - Scoped to tenants with role-based permissions
- Enhanced data separation with tenant-based queries

**API Endpoints:**
- `POST /api/enterprise/tenants` - Create new tenant
- `GET /api/enterprise/tenants/{id}` - Get tenant details
- Middleware for automatic tenant context extraction

**Key Features:**
- Subdomain-based tenant detection
- Header-based tenant context (`X-Tenant-ID`)
- Complete data isolation between tenants
- Configurable resource limits per tenant

### 2. Admin Dashboard with User Management and Analytics

**React Components:**
- `AdminDashboard.jsx` - Complete admin interface
- User management with role-based access
- Real-time analytics and usage statistics
- Responsive design with Tailwind CSS

**Backend Endpoints:**
- `GET /api/enterprise/admin/analytics` - Usage analytics
- `GET /api/enterprise/admin/users` - List users
- `POST /api/enterprise/admin/users` - Create users
- Role-based access control (admin, manager, user)

**Analytics Features:**
- Total users and API keys per tenant
- API usage over time periods
- Top API consumers
- Subscription status monitoring

### 3. Billing Integration with Stripe

**Subscription Plans:**
- **Free**: 5 users, 1,000 API calls/hour
- **Basic**: 25 users, 10,000 API calls/hour ($29/month)
- **Pro**: 100 users, 50,000 API calls/hour ($99/month)
- **Enterprise**: 1,000 users, 200,000 API calls/hour ($299/month)

**API Endpoints:**
- `GET /api/billing/plans` - Available subscription plans
- `POST /api/billing/create-checkout-session` - Stripe checkout
- `POST /api/billing/portal` - Customer portal access
- `POST /api/billing/webhook` - Stripe webhook handler

**Webhook Handling:**
- Subscription creation/updates
- Payment success/failure tracking
- Automatic tier upgrades/downgrades
- Comprehensive audit logging

### 4. API Key Management and Rate Limiting

**API Key Features:**
- Secure key generation with `aih_` prefix
- Configurable rate limits per key
- Scope-based permissions (read, write, admin)
- Usage tracking and analytics
- Expiration date support

**Rate Limiting:**
- Per-API-key rate limiting
- Per-tenant rate limiting
- In-memory limiter with Redis-ready design
- Sliding window algorithm
- Rate limit headers in responses

**Endpoints:**
- `GET /api/enterprise/api-keys` - List user's API keys
- `POST /api/enterprise/api-keys` - Create new API key
- `GET /api/rate-limit/status` - Check current usage

### 5. Audit Logging and Compliance Reporting

**Audit Log Model:**
- Comprehensive action tracking
- IP address and user agent logging
- Request method and path capture
- Success/failure tracking with error details
- JSON metadata storage

**Logged Events:**
- User authentication
- API key creation/usage
- Subscription changes
- User management actions
- Customization updates
- Payment events

**Compliance Features:**
- Complete audit trail
- User action attribution
- Time-based filtering
- Export capabilities
- GDPR compliance ready

### 6. White-Label Customization Options

**Customization Features:**
- Company branding (name, logo, favicon)
- Color scheme customization (primary, secondary, accent)
- Custom welcome messages and footer text
- CSS injection for advanced styling
- Feature toggle per subscription tier

**API Endpoints:**
- `GET /api/customization/customization` - Get current settings
- `PUT /api/customization/customization` - Update branding
- `POST /api/customization/themes/preview` - Preview theme
- `POST /api/customization/branding/upload` - Upload assets
- `PUT /api/customization/domain` - Set custom domain

**Enterprise Features:**
- Custom domain support (Enterprise tier)
- Complete white-label experience
- SSO integration ready
- Advanced CSS customization

## Technical Implementation

### Database Schema

```sql
-- Core enterprise tables
CREATE TABLE tenants (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    domain VARCHAR(255) UNIQUE,
    subscription_tier VARCHAR(50) DEFAULT 'free',
    subscription_status VARCHAR(50) DEFAULT 'active',
    user_limit INTEGER DEFAULT 5,
    api_rate_limit INTEGER DEFAULT 1000,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) REFERENCES tenants(id),
    email VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'user',
    api_usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(tenant_id, email)
);

CREATE TABLE api_keys (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) REFERENCES tenants(id),
    user_id VARCHAR(36) REFERENCES users(id),
    name VARCHAR(255) NOT NULL,
    rate_limit INTEGER DEFAULT 1000,
    usage_count INTEGER DEFAULT 0,
    scopes JSON DEFAULT '["read"]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE audit_logs (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) REFERENCES tenants(id),
    action VARCHAR(100) NOT NULL,
    ip_address VARCHAR(45),
    details JSON,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Frontend Architecture

```jsx
// Enterprise-ready component structure
<AuthProvider>
  <TenantProvider>
    <App>
      <AdminDashboard>
        <UserManagement />
        <ApiKeyManagement />
        <BillingPortal />
        <CustomizationPanel />
        <AnalyticsDashboard />
      </AdminDashboard>
    </App>
  </TenantProvider>
</AuthProvider>
```

### API Authentication

```javascript
// Multi-tenant API requests
const headers = {
  'Authorization': `Bearer ${token}`,
  'X-Tenant-ID': tenant.id,
  'X-API-Key': apiKey  // For API key auth
};
```

## Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost/db_name

# Stripe
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_BASIC_PRICE_ID=price_...
STRIPE_PRO_PRICE_ID=price_...
STRIPE_ENTERPRISE_PRICE_ID=price_...

# Security
SECRET_KEY=your-secret-key

# Redis (for production rate limiting)
REDIS_URL=redis://localhost:6379
```

### Subscription Tier Configuration

```python
SUBSCRIPTION_PLANS = {
    'free': {
        'user_limit': 5,
        'api_rate_limit': 1000,
        'features': ['basic_guidance', 'meditation']
    },
    'basic': {
        'user_limit': 25,
        'api_rate_limit': 10000,
        'features': ['basic_guidance', 'meditation', 'analytics', 'api_access']
    },
    'pro': {
        'user_limit': 100,
        'api_rate_limit': 50000,
        'features': ['all_basic', 'custom_branding', 'priority_support']
    },
    'enterprise': {
        'user_limit': 1000,
        'api_rate_limit': 200000,
        'features': ['all_features', 'white_label', 'sso', 'custom_domain']
    }
}
```

## Usage Examples

### Creating a Tenant

```bash
curl -X POST http://localhost:5000/api/enterprise/tenants \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Acme Corp",
    "slug": "acme-corp",
    "subscription_tier": "pro"
  }'
```

### Using API Keys

```bash
curl -X GET http://localhost:5000/api/gurus/spiritual \
  -H "X-API-Key: aih_abc123..." \
  -H "Content-Type: application/json"
```

### Updating Customization

```bash
curl -X PUT http://localhost:5000/api/customization/customization \
  -H "Authorization: Bearer token" \
  -H "X-Tenant-ID: tenant-id" \
  -H "Content-Type: application/json" \
  -d '{
    "primary_color": "#FF5733",
    "company_name": "Custom Corp"
  }'
```

## Security Considerations

1. **Data Isolation**: All queries are scoped to tenant context
2. **Rate Limiting**: Prevents API abuse and ensures fair usage
3. **Audit Logging**: Complete tracking of all actions
4. **Role-Based Access**: Granular permissions per user
5. **API Key Security**: Hashed storage and secure generation
6. **Input Validation**: All inputs validated and sanitized

## Scalability Features

1. **Horizontal Scaling**: Stateless design supports multiple instances
2. **Database Sharding**: Ready for tenant-based database sharding
3. **Caching**: Redis integration for rate limiting and sessions
4. **CDN Ready**: Static assets can be served from CDN
5. **Load Balancing**: Supports multiple backend instances

## Monitoring and Analytics

1. **Usage Metrics**: Per-tenant and per-user usage tracking
2. **Performance Monitoring**: Request timing and error rates
3. **Business Metrics**: Subscription conversions and churn
4. **Health Checks**: Automated service health monitoring
5. **Alerting**: Critical event notifications

## Next Steps for Production

1. **Redis Integration**: Replace in-memory rate limiting
2. **Database Migration**: Set up production PostgreSQL
3. **SSL/TLS Configuration**: Enable HTTPS
4. **Monitoring Setup**: Configure application monitoring
5. **Backup Strategy**: Implement database backups
6. **CI/CD Pipeline**: Automated testing and deployment
7. **Documentation**: API documentation with OpenAPI/Swagger