import React, { useState, useEffect } from 'react';
import { usePerformanceMonitor } from '../hooks/useIntersectionObserver';

const PerformanceDashboard = ({ className = '' }) => {
  const { metrics, isLoading, refreshMetrics } = usePerformanceMonitor();
  const [alertsOpen, setAlertsOpen] = useState(false);
  const [cacheStats, setCacheStats] = useState(null);
  const [dbStats, setDbStats] = useState(null);

  useEffect(() => {
    fetchCacheStats();
    fetchDatabaseStats();
  }, []);

  const fetchCacheStats = async () => {
    try {
      const response = await fetch('/api/performance/cache/stats');
      if (response.ok) {
        const data = await response.json();
        setCacheStats(data);
      }
    } catch (error) {
      console.error('Failed to fetch cache stats:', error);
    }
  };

  const fetchDatabaseStats = async () => {
    try {
      const response = await fetch('/api/performance/database/stats');
      if (response.ok) {
        const data = await response.json();
        setDbStats(data);
      }
    } catch (error) {
      console.error('Failed to fetch database stats:', error);
    }
  };

  const clearCache = async () => {
    try {
      const response = await fetch('/api/performance/cache/clear', {
        method: 'POST'
      });
      if (response.ok) {
        fetchCacheStats();
        alert('Cache cleared successfully');
      }
    } catch (error) {
      console.error('Failed to clear cache:', error);
      alert('Failed to clear cache');
    }
  };

  const getStatusColor = (value, thresholds) => {
    if (value >= thresholds.danger) return 'text-red-600';
    if (value >= thresholds.warning) return 'text-yellow-600';
    return 'text-green-600';
  };

  const formatBytes = (bytes) => {
    if (!bytes) return '0 B';
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${sizes[i]}`;
  };

  const MetricCard = ({ title, value, unit, description, status = 'good' }) => {
    const statusColors = {
      good: 'border-green-500 bg-green-50',
      warning: 'border-yellow-500 bg-yellow-50',
      danger: 'border-red-500 bg-red-50'
    };

    return (
      <div className={`border-2 rounded-lg p-4 ${statusColors[status]}`}>
        <h3 className="text-sm font-medium text-gray-700">{title}</h3>
        <p className="text-2xl font-bold text-gray-900">
          {typeof value === 'number' ? value.toFixed(2) : value}
          <span className="text-sm text-gray-500 ml-1">{unit}</span>
        </p>
        {description && (
          <p className="text-xs text-gray-600 mt-1">{description}</p>
        )}
      </div>
    );
  };

  if (isLoading && !metrics.timestamp) {
    return (
      <div className={`bg-white rounded-lg shadow-lg p-6 ${className}`}>
        <div className="animate-pulse">
          <div className="h-6 bg-gray-300 rounded mb-4"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {[...Array(8)].map((_, i) => (
              <div key={i} className="h-24 bg-gray-300 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-white rounded-lg shadow-lg p-6 ${className}`}>
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-bold text-gray-900">Performance Dashboard</h2>
        <div className="flex space-x-2">
          <button
            onClick={refreshMetrics}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
            disabled={isLoading}
          >
            {isLoading ? 'Refreshing...' : 'Refresh'}
          </button>
          <button
            onClick={() => setAlertsOpen(!alertsOpen)}
            className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700 transition-colors"
          >
            Alerts
          </button>
        </div>
      </div>

      {/* System Metrics */}
      <div className="mb-8">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">System Performance</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <MetricCard
            title="CPU Usage"
            value={metrics.cpu_usage?.latest || 0}
            unit="%"
            description={`Avg: ${(metrics.cpu_usage?.avg || 0).toFixed(1)}%`}
            status={
              (metrics.cpu_usage?.latest || 0) > 80 ? 'danger' :
              (metrics.cpu_usage?.latest || 0) > 60 ? 'warning' : 'good'
            }
          />
          <MetricCard
            title="Memory Usage"
            value={metrics.memory_usage?.latest || 0}
            unit="%"
            description={`Avg: ${(metrics.memory_usage?.avg || 0).toFixed(1)}%`}
            status={
              (metrics.memory_usage?.latest || 0) > 85 ? 'danger' :
              (metrics.memory_usage?.latest || 0) > 70 ? 'warning' : 'good'
            }
          />
          <MetricCard
            title="Disk Usage"
            value={metrics.disk_usage?.latest || 0}
            unit="%"
            description={`Avg: ${(metrics.disk_usage?.avg || 0).toFixed(1)}%`}
            status={
              (metrics.disk_usage?.latest || 0) > 90 ? 'danger' :
              (metrics.disk_usage?.latest || 0) > 75 ? 'warning' : 'good'
            }
          />
          <MetricCard
            title="Response Time"
            value={(metrics.response_time?.avg || 0) * 1000}
            unit="ms"
            description={`Max: ${((metrics.response_time?.max || 0) * 1000).toFixed(0)}ms`}
            status={
              (metrics.response_time?.avg || 0) > 2 ? 'danger' :
              (metrics.response_time?.avg || 0) > 1 ? 'warning' : 'good'
            }
          />
        </div>
      </div>

      {/* Application Metrics */}
      <div className="mb-8">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Application Performance</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <MetricCard
            title="Request Rate"
            value={metrics.request_rate?.count || 0}
            unit="req/5min"
            description={`Avg: ${(metrics.request_rate?.avg || 0).toFixed(1)}`}
          />
          <MetricCard
            title="Cache Hit Rate"
            value={metrics.cache_hit_rate?.avg || 0}
            unit="%"
            description={cacheStats?.cache_type || 'Unknown'}
            status={
              (metrics.cache_hit_rate?.avg || 0) < 70 ? 'warning' :
              (metrics.cache_hit_rate?.avg || 0) < 50 ? 'danger' : 'good'
            }
          />
          <MetricCard
            title="DB Query Time"
            value={(metrics.database_query_time?.avg || 0) * 1000}
            unit="ms"
            description={`Max: ${((metrics.database_query_time?.max || 0) * 1000).toFixed(0)}ms`}
            status={
              (metrics.database_query_time?.avg || 0) > 0.5 ? 'danger' :
              (metrics.database_query_time?.avg || 0) > 0.2 ? 'warning' : 'good'
            }
          />
        </div>
      </div>

      {/* Cache Information */}
      {cacheStats && (
        <div className="mb-8">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-semibold text-gray-800">Cache Status</h3>
            <button
              onClick={clearCache}
              className="px-3 py-1 bg-red-600 text-white text-sm rounded hover:bg-red-700 transition-colors"
            >
              Clear Cache
            </button>
          </div>
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <p className="text-sm text-gray-600">Cache Type</p>
                <p className="font-semibold">{cacheStats.cache_type}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Redis Connected</p>
                <p className={`font-semibold ${cacheStats.redis_connected ? 'text-green-600' : 'text-red-600'}`}>
                  {cacheStats.redis_connected ? 'Yes' : 'No'}
                </p>
              </div>
              {cacheStats.redis_info && (
                <>
                  <div>
                    <p className="text-sm text-gray-600">Memory Used</p>
                    <p className="font-semibold">{cacheStats.redis_info.used_memory}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Connected Clients</p>
                    <p className="font-semibold">{cacheStats.redis_info.connected_clients}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Uptime</p>
                    <p className="font-semibold">{Math.floor(cacheStats.redis_info.uptime / 3600)}h</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Hit Ratio</p>
                    <p className="font-semibold">
                      {cacheStats.redis_info.hits + cacheStats.redis_info.misses > 0
                        ? ((cacheStats.redis_info.hits / (cacheStats.redis_info.hits + cacheStats.redis_info.misses)) * 100).toFixed(1)
                        : 0}%
                    </p>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Database Statistics */}
      {dbStats && (
        <div className="mb-8">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Database Statistics</h3>
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
              <div>
                <p className="text-sm text-gray-600">Users</p>
                <p className="text-lg font-semibold">{dbStats.tables.users}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Sessions</p>
                <p className="text-lg font-semibold">{dbStats.tables.spiritual_sessions}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Videos</p>
                <p className="text-lg font-semibold">{dbStats.tables.videos}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Video Views</p>
                <p className="text-lg font-semibold">{dbStats.tables.video_views}</p>
              </div>
            </div>
            <div className="border-t pt-4">
              <h4 className="font-medium text-gray-700 mb-2">Recent Activity (24h)</h4>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <p className="text-xs text-gray-600">New Users</p>
                  <p className="font-semibold text-green-600">{dbStats.recent_activity.new_users}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-600">New Sessions</p>
                  <p className="font-semibold text-blue-600">{dbStats.recent_activity.new_sessions}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-600">New Videos</p>
                  <p className="font-semibold text-purple-600">{dbStats.recent_activity.new_videos}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-600">Video Views</p>
                  <p className="font-semibold text-orange-600">{dbStats.recent_activity.video_views}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Timestamp */}
      <div className="text-xs text-gray-500 text-center">
        Last updated: {metrics.timestamp ? new Date(metrics.timestamp).toLocaleString() : 'Never'}
      </div>
    </div>
  );
};

export default PerformanceDashboard;