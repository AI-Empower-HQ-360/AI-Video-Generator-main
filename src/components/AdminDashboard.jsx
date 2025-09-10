import React, { useState, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';
import { api } from '../utils/api';

const AdminDashboard = () => {
  const { user, tenant } = useAuth();
  const [analytics, setAnalytics] = useState(null);
  const [users, setUsers] = useState([]);
  const [apiKeys, setApiKeys] = useState([]);
  const [customization, setCustomization] = useState(null);
  const [subscription, setSubscription] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    if (user?.role === 'admin') {
      loadDashboardData();
    }
  }, [user]);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const [analyticsRes, usersRes, customizationRes, subscriptionRes] = await Promise.all([
        api.get('/admin/analytics'),
        api.get('/admin/users'),
        api.get('/customization'),
        api.get(`/billing/subscription?tenant_id=${tenant.id}`)
      ]);

      setAnalytics(analyticsRes.data);
      setUsers(usersRes.data.users || []);
      setCustomization(customizationRes.data);
      setSubscription(subscriptionRes.data);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateUser = async (userData) => {
    try {
      await api.post('/admin/users', userData);
      loadDashboardData(); // Refresh data
    } catch (error) {
      console.error('Failed to create user:', error);
    }
  };

  const handleUpdateCustomization = async (customizationData) => {
    try {
      await api.put('/customization', customizationData);
      setCustomization({ ...customization, ...customizationData });
    } catch (error) {
      console.error('Failed to update customization:', error);
    }
  };

  if (user?.role !== 'admin') {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900">Access Denied</h2>
          <p className="text-gray-600">You need admin privileges to access this dashboard.</p>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Admin Dashboard</h1>
              <p className="text-gray-600">{tenant?.name} - {subscription?.current_plan}</p>
            </div>
            <div className="flex space-x-4">
              <button
                onClick={() => window.open('/billing/portal', '_blank')}
                className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700"
              >
                Billing Portal
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-6">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            {[
              { id: 'overview', name: 'Overview' },
              { id: 'users', name: 'Users' },
              { id: 'api-keys', name: 'API Keys' },
              { id: 'customization', name: 'Branding' },
              { id: 'analytics', name: 'Analytics' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`${
                  activeTab === tab.id
                    ? 'border-indigo-500 text-indigo-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                } whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm`}
              >
                {tab.name}
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {activeTab === 'overview' && (
          <OverviewTab analytics={analytics} subscription={subscription} />
        )}
        {activeTab === 'users' && (
          <UsersTab users={users} onCreateUser={handleCreateUser} />
        )}
        {activeTab === 'api-keys' && (
          <ApiKeysTab />
        )}
        {activeTab === 'customization' && (
          <CustomizationTab
            customization={customization}
            onUpdate={handleUpdateCustomization}
          />
        )}
        {activeTab === 'analytics' && (
          <AnalyticsTab analytics={analytics} />
        )}
      </div>
    </div>
  );
};

const OverviewTab = ({ analytics, subscription }) => (
  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
    <StatCard
      title="Total Users"
      value={analytics?.total_users || 0}
      icon="👥"
    />
    <StatCard
      title="API Keys"
      value={analytics?.total_api_keys || 0}
      icon="🔑"
    />
    <StatCard
      title="API Calls (30d)"
      value={analytics?.api_calls_last_30_days || 0}
      icon="📊"
    />
    <StatCard
      title="Subscription"
      value={subscription?.current_plan || 'Free'}
      icon="💎"
    />
  </div>
);

const StatCard = ({ title, value, icon }) => (
  <div className="bg-white p-6 rounded-lg shadow">
    <div className="flex items-center">
      <div className="text-2xl mr-3">{icon}</div>
      <div>
        <p className="text-sm font-medium text-gray-600">{title}</p>
        <p className="text-2xl font-semibold text-gray-900">{value}</p>
      </div>
    </div>
  </div>
);

const UsersTab = ({ users, onCreateUser }) => {
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [formData, setFormData] = useState({
    email: '',
    full_name: '',
    role: 'user',
    password: ''
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    await onCreateUser(formData);
    setFormData({ email: '', full_name: '', role: 'user', password: '' });
    setShowCreateForm(false);
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-900">Users</h2>
        <button
          onClick={() => setShowCreateForm(true)}
          className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700"
        >
          Add User
        </button>
      </div>

      {showCreateForm && (
        <div className="bg-white p-6 rounded-lg shadow mb-6">
          <h3 className="text-lg font-medium mb-4">Create New User</h3>
          <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <input
              type="email"
              placeholder="Email"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              className="border rounded-md px-3 py-2"
              required
            />
            <input
              type="text"
              placeholder="Full Name"
              value={formData.full_name}
              onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
              className="border rounded-md px-3 py-2"
              required
            />
            <select
              value={formData.role}
              onChange={(e) => setFormData({ ...formData, role: e.target.value })}
              className="border rounded-md px-3 py-2"
            >
              <option value="user">User</option>
              <option value="manager">Manager</option>
              <option value="admin">Admin</option>
            </select>
            <input
              type="password"
              placeholder="Password"
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              className="border rounded-md px-3 py-2"
              required
            />
            <div className="md:col-span-2 flex space-x-4">
              <button
                type="submit"
                className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700"
              >
                Create User
              </button>
              <button
                type="button"
                onClick={() => setShowCreateForm(false)}
                className="bg-gray-300 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-400"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="bg-white shadow rounded-lg">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                User
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Role
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                API Usage
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Last Login
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {users.map((user) => (
              <tr key={user.id}>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div>
                    <div className="text-sm font-medium text-gray-900">{user.full_name}</div>
                    <div className="text-sm text-gray-500">{user.email}</div>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                    user.role === 'admin' ? 'bg-purple-100 text-purple-800' :
                    user.role === 'manager' ? 'bg-blue-100 text-blue-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {user.role}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {user.api_usage_count || 0}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {user.last_login ? new Date(user.last_login).toLocaleDateString() : 'Never'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                    user.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                  }`}>
                    {user.is_active ? 'Active' : 'Inactive'}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

const ApiKeysTab = () => {
  const [apiKeys, setApiKeys] = useState([]);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newKey, setNewKey] = useState(null);

  useEffect(() => {
    loadApiKeys();
  }, []);

  const loadApiKeys = async () => {
    try {
      const response = await api.get('/api-keys');
      setApiKeys(response.data.api_keys || []);
    } catch (error) {
      console.error('Failed to load API keys:', error);
    }
  };

  const handleCreateApiKey = async (formData) => {
    try {
      const response = await api.post('/api-keys', formData);
      setNewKey(response.data);
      setShowCreateForm(false);
      loadApiKeys();
    } catch (error) {
      console.error('Failed to create API key:', error);
    }
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-900">API Keys</h2>
        <button
          onClick={() => setShowCreateForm(true)}
          className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700"
        >
          Create API Key
        </button>
      </div>

      {newKey && (
        <div className="bg-yellow-50 border border-yellow-200 p-4 rounded-md mb-6">
          <h3 className="text-lg font-medium text-yellow-800 mb-2">API Key Created</h3>
          <p className="text-sm text-yellow-700 mb-2">
            Please copy this key now. You won't be able to see it again.
          </p>
          <code className="bg-yellow-100 px-2 py-1 rounded text-sm font-mono">
            {newKey.key}
          </code>
          <button
            onClick={() => setNewKey(null)}
            className="ml-4 text-yellow-800 hover:text-yellow-900"
          >
            ✕
          </button>
        </div>
      )}

      {showCreateForm && (
        <CreateApiKeyForm
          onSubmit={handleCreateApiKey}
          onCancel={() => setShowCreateForm(false)}
        />
      )}

      <div className="bg-white shadow rounded-lg">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Name
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Scopes
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Usage
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Last Used
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Rate Limit
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {apiKeys.map((key) => (
              <tr key={key.id}>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div>
                    <div className="text-sm font-medium text-gray-900">{key.name}</div>
                    <div className="text-sm text-gray-500">{key.description}</div>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  {key.scopes.map((scope) => (
                    <span
                      key={scope}
                      className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800 mr-1"
                    >
                      {scope}
                    </span>
                  ))}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {key.usage_count || 0}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {key.last_used ? new Date(key.last_used).toLocaleDateString() : 'Never'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {key.rate_limit}/hour
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

const CreateApiKeyForm = ({ onSubmit, onCancel }) => {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    scopes: ['read'],
    rate_limit: 1000
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow mb-6">
      <h3 className="text-lg font-medium mb-4">Create API Key</h3>
      <form onSubmit={handleSubmit} className="space-y-4">
        <input
          type="text"
          placeholder="Key Name"
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          className="w-full border rounded-md px-3 py-2"
          required
        />
        <textarea
          placeholder="Description (optional)"
          value={formData.description}
          onChange={(e) => setFormData({ ...formData, description: e.target.value })}
          className="w-full border rounded-md px-3 py-2"
          rows="2"
        />
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Scopes</label>
          <div className="space-y-2">
            {['read', 'write', 'admin'].map((scope) => (
              <label key={scope} className="flex items-center">
                <input
                  type="checkbox"
                  checked={formData.scopes.includes(scope)}
                  onChange={(e) => {
                    if (e.target.checked) {
                      setFormData({ ...formData, scopes: [...formData.scopes, scope] });
                    } else {
                      setFormData({ ...formData, scopes: formData.scopes.filter(s => s !== scope) });
                    }
                  }}
                  className="mr-2"
                />
                {scope}
              </label>
            ))}
          </div>
        </div>
        <input
          type="number"
          placeholder="Rate Limit (requests per hour)"
          value={formData.rate_limit}
          onChange={(e) => setFormData({ ...formData, rate_limit: parseInt(e.target.value) })}
          className="w-full border rounded-md px-3 py-2"
          min="1"
          max="100000"
        />
        <div className="flex space-x-4">
          <button
            type="submit"
            className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700"
          >
            Create API Key
          </button>
          <button
            type="button"
            onClick={onCancel}
            className="bg-gray-300 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-400"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
};

const CustomizationTab = ({ customization, onUpdate }) => {
  const [formData, setFormData] = useState({
    company_name: customization?.company_name || '',
    primary_color: customization?.primary_color || '#3B82F6',
    secondary_color: customization?.secondary_color || '#1F2937',
    accent_color: customization?.accent_color || '#F59E0B',
    welcome_message: customization?.welcome_message || '',
    footer_text: customization?.footer_text || ''
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    onUpdate(formData);
  };

  return (
    <div className="max-w-2xl">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Branding & Customization</h2>
      
      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Company Name
          </label>
          <input
            type="text"
            value={formData.company_name}
            onChange={(e) => setFormData({ ...formData, company_name: e.target.value })}
            className="w-full border rounded-md px-3 py-2"
          />
        </div>

        <div className="grid grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Primary Color
            </label>
            <input
              type="color"
              value={formData.primary_color}
              onChange={(e) => setFormData({ ...formData, primary_color: e.target.value })}
              className="w-full h-10 border rounded-md"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Secondary Color
            </label>
            <input
              type="color"
              value={formData.secondary_color}
              onChange={(e) => setFormData({ ...formData, secondary_color: e.target.value })}
              className="w-full h-10 border rounded-md"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Accent Color
            </label>
            <input
              type="color"
              value={formData.accent_color}
              onChange={(e) => setFormData({ ...formData, accent_color: e.target.value })}
              className="w-full h-10 border rounded-md"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Welcome Message
          </label>
          <textarea
            value={formData.welcome_message}
            onChange={(e) => setFormData({ ...formData, welcome_message: e.target.value })}
            className="w-full border rounded-md px-3 py-2"
            rows="3"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Footer Text
          </label>
          <textarea
            value={formData.footer_text}
            onChange={(e) => setFormData({ ...formData, footer_text: e.target.value })}
            className="w-full border rounded-md px-3 py-2"
            rows="2"
          />
        </div>

        <button
          type="submit"
          className="bg-indigo-600 text-white px-6 py-2 rounded-md hover:bg-indigo-700"
        >
          Save Changes
        </button>
      </form>
    </div>
  );
};

const AnalyticsTab = ({ analytics }) => (
  <div>
    <h2 className="text-2xl font-bold text-gray-900 mb-6">Analytics</h2>
    
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Top API Users</h3>
        <div className="space-y-3">
          {analytics?.top_users?.map((user, index) => (
            <div key={user.id} className="flex justify-between items-center">
              <div>
                <span className="text-sm font-medium text-gray-900">{user.full_name}</span>
                <span className="text-sm text-gray-500 ml-2">{user.email}</span>
              </div>
              <span className="text-sm text-gray-600">{user.api_usage_count} calls</span>
            </div>
          ))}
        </div>
      </div>

      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Quick Stats</h3>
        <div className="space-y-3">
          <div className="flex justify-between">
            <span className="text-sm text-gray-600">Total Users</span>
            <span className="text-sm font-medium">{analytics?.total_users || 0}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-sm text-gray-600">Active API Keys</span>
            <span className="text-sm font-medium">{analytics?.total_api_keys || 0}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-sm text-gray-600">API Calls (30d)</span>
            <span className="text-sm font-medium">{analytics?.api_calls_last_30_days || 0}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
);

export default AdminDashboard;