// API utility for making authenticated requests with enterprise features

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

class ApiClient {
  constructor() {
    this.baseURL = API_BASE_URL;
  }

  getHeaders() {
    const token = localStorage.getItem('auth_token');
    const tenantData = localStorage.getItem('tenant_data');
    const tenant = tenantData ? JSON.parse(tenantData) : null;

    const headers = {
      'Content-Type': 'application/json',
    };

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    if (tenant) {
      headers['X-Tenant-ID'] = tenant.id;
    }

    return headers;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      headers: this.getHeaders(),
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      // Handle rate limiting
      if (response.status === 429) {
        const error = await response.json();
        throw new RateLimitError(error.message, error);
      }

      // Handle authentication errors
      if (response.status === 401) {
        // Clear invalid token
        localStorage.removeItem('auth_token');
        localStorage.removeItem('user_data');
        localStorage.removeItem('tenant_data');
        window.location.href = '/login';
        return;
      }

      if (!response.ok) {
        const error = await response.json();
        throw new ApiError(error.message || 'API request failed', response.status);
      }

      return response;
    } catch (error) {
      if (error instanceof ApiError || error instanceof RateLimitError) {
        throw error;
      }
      throw new ApiError('Network error', 0);
    }
  }

  async get(endpoint) {
    const response = await this.request(endpoint);
    return response.json();
  }

  async post(endpoint, data) {
    const response = await this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    });
    return response.json();
  }

  async put(endpoint, data) {
    const response = await this.request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
    return response.json();
  }

  async delete(endpoint) {
    const response = await this.request(endpoint, {
      method: 'DELETE',
    });
    return response.json();
  }

  // API Key specific methods
  async makeApiKeyRequest(endpoint, apiKey, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': apiKey,
      },
      ...options,
    };

    const response = await fetch(url, config);
    
    if (response.status === 429) {
      const error = await response.json();
      throw new RateLimitError(error.message, error);
    }

    if (!response.ok) {
      const error = await response.json();
      throw new ApiError(error.message || 'API request failed', response.status);
    }

    return response.json();
  }

  // Enterprise specific methods
  async getTenantAnalytics() {
    return this.get('/enterprise/admin/analytics');
  }

  async createTenant(tenantData) {
    return this.post('/enterprise/tenants', tenantData);
  }

  async updateCustomization(customizationData) {
    return this.put('/customization/customization', customizationData);
  }

  async createCheckoutSession(planId, successUrl, cancelUrl) {
    return this.post('/billing/create-checkout-session', {
      plan_id: planId,
      success_url: successUrl,
      cancel_url: cancelUrl,
    });
  }

  async getSubscription(tenantId) {
    return this.get(`/billing/subscription?tenant_id=${tenantId}`);
  }

  async createApiKey(keyData) {
    return this.post('/enterprise/api-keys', keyData);
  }

  async getRateLimitStatus(apiKey) {
    return this.makeApiKeyRequest('/rate-limit/status', apiKey);
  }
}

class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

class RateLimitError extends Error {
  constructor(message, details) {
    super(message);
    this.name = 'RateLimitError';
    this.details = details;
  }
}

export const api = new ApiClient();
export { ApiError, RateLimitError };