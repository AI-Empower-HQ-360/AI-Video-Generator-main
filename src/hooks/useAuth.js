import { useState, useEffect, createContext, useContext } from 'react';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [tenant, setTenant] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Initialize auth state from localStorage
    const token = localStorage.getItem('auth_token');
    const userData = localStorage.getItem('user_data');
    const tenantData = localStorage.getItem('tenant_data');

    if (token && userData && tenantData) {
      setUser(JSON.parse(userData));
      setTenant(JSON.parse(tenantData));
    }
    
    setLoading(false);
  }, []);

  const login = async (email, password, tenantSlug) => {
    try {
      // This would integrate with your authentication API
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Tenant-ID': tenantSlug
        },
        body: JSON.stringify({ email, password })
      });

      if (response.ok) {
        const data = await response.json();
        
        localStorage.setItem('auth_token', data.token);
        localStorage.setItem('user_data', JSON.stringify(data.user));
        localStorage.setItem('tenant_data', JSON.stringify(data.tenant));
        
        setUser(data.user);
        setTenant(data.tenant);
        
        return { success: true };
      } else {
        const error = await response.json();
        return { success: false, error: error.message };
      }
    } catch (error) {
      return { success: false, error: 'Network error' };
    }
  };

  const logout = () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_data');
    localStorage.removeItem('tenant_data');
    setUser(null);
    setTenant(null);
  };

  const value = {
    user,
    tenant,
    loading,
    login,
    logout,
    isAuthenticated: !!user,
    isAdmin: user?.role === 'admin'
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};