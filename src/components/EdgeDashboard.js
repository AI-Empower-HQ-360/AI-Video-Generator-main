/**
 * Edge Computing Dashboard Component
 * Displays edge node status, performance metrics, and system monitoring
 */
import React, { useState, useEffect } from 'react';
import { videoProcessingAPI } from '../api/video-processing.js';

const EdgeDashboard = () => {
    const [edgeNodes, setEdgeNodes] = useState([]);
    const [clusterStatus, setClusterStatus] = useState(null);
    const [performanceStats, setPerformanceStats] = useState(null);
    const [gpuStatus, setGpuStatus] = useState(null);
    const [aiInferenceStats, setAiInferenceStats] = useState(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        loadDashboardData();
        
        // Set up auto-refresh
        const interval = setInterval(loadDashboardData, 5000);
        return () => clearInterval(interval);
    }, []);

    const loadDashboardData = async () => {
        try {
            setIsLoading(true);
            
            // Load all dashboard data in parallel
            const [
                nodesResponse,
                clusterResponse,
                gpuResponse
            ] = await Promise.all([
                videoProcessingAPI.getEdgeNodes(),
                videoProcessingAPI.getClusterStatus(),
                videoProcessingAPI.getGpuStatus()
            ]);

            if (nodesResponse.success) {
                setEdgeNodes(nodesResponse.nodes);
            }

            if (clusterResponse.success) {
                setClusterStatus(clusterResponse.cluster_status);
            }

            if (gpuResponse.success) {
                setGpuStatus(gpuResponse.gpu_status);
            }

        } catch (error) {
            console.error('Failed to load dashboard data:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const getNodeStatusColor = (status) => {
        const colors = {
            'online': 'text-green-600 bg-green-100',
            'offline': 'text-red-600 bg-red-100',
            'busy': 'text-yellow-600 bg-yellow-100',
            'idle': 'text-blue-600 bg-blue-100',
            'error': 'text-red-600 bg-red-100'
        };
        return colors[status] || 'text-gray-600 bg-gray-100';
    };

    const formatBytes = (bytes) => {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    };

    const formatUptime = (seconds) => {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        return `${hours}h ${minutes}m`;
    };

    const renderClusterOverview = () => (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <div className="bg-white p-6 rounded-lg shadow">
                <div className="flex items-center">
                    <div className="p-3 rounded-full bg-blue-100 text-blue-600">
                        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" 
                                d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
                        </svg>
                    </div>
                    <div className="ml-4">
                        <p className="text-sm font-medium text-gray-600">Total Nodes</p>
                        <p className="text-2xl font-semibold text-gray-900">
                            {clusterStatus?.total_nodes || 0}
                        </p>
                    </div>
                </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow">
                <div className="flex items-center">
                    <div className="p-3 rounded-full bg-green-100 text-green-600">
                        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" 
                                d="M13 10V3L4 14h7v7l9-11h-7z" />
                        </svg>
                    </div>
                    <div className="ml-4">
                        <p className="text-sm font-medium text-gray-600">Online Nodes</p>
                        <p className="text-2xl font-semibold text-gray-900">
                            {clusterStatus?.online_nodes || 0}
                        </p>
                    </div>
                </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow">
                <div className="flex items-center">
                    <div className="p-3 rounded-full bg-purple-100 text-purple-600">
                        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" 
                                d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
                        </svg>
                    </div>
                    <div className="ml-4">
                        <p className="text-sm font-medium text-gray-600">GPU Nodes</p>
                        <p className="text-2xl font-semibold text-gray-900">
                            {clusterStatus?.gpu_nodes || 0}
                        </p>
                    </div>
                </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow">
                <div className="flex items-center">
                    <div className="p-3 rounded-full bg-orange-100 text-orange-600">
                        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" 
                                d="M13 10V3L4 14h7v7l9-11h-7z" />
                        </svg>
                    </div>
                    <div className="ml-4">
                        <p className="text-sm font-medium text-gray-600">Active Tasks</p>
                        <p className="text-2xl font-semibold text-gray-900">
                            {clusterStatus?.active_tasks || 0}
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );

    const renderNodeList = () => (
        <div className="bg-white rounded-lg shadow mb-8">
            <div className="px-6 py-4 border-b border-gray-200">
                <h2 className="text-lg font-semibold text-gray-900">Edge Nodes</h2>
            </div>
            <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                        <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Node
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Status
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Resources
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                GPU
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Last Seen
                            </th>
                        </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                        {edgeNodes.map((node) => (
                            <tr key={node.node_id} className="hover:bg-gray-50">
                                <td className="px-6 py-4 whitespace-nowrap">
                                    <div>
                                        <div className="text-sm font-medium text-gray-900">
                                            {node.node_id}
                                        </div>
                                        <div className="text-sm text-gray-500">
                                            {node.hostname}:{node.port}
                                        </div>
                                    </div>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap">
                                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getNodeStatusColor(node.status)}`}>
                                        {node.status}
                                    </span>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                    <div>CPU: {node.cpu_cores} cores</div>
                                    <div>Memory: {formatBytes(node.memory * 1024 * 1024)}</div>
                                    <div>Capacity: {node.processing_capacity}x</div>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                    {node.gpu_available ? (
                                        <div>
                                            <div className="text-green-600">✓ Available</div>
                                            <div>{formatBytes(node.gpu_memory * 1024 * 1024)}</div>
                                        </div>
                                    ) : (
                                        <span className="text-gray-400">No GPU</span>
                                    )}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                    {new Date(node.last_heartbeat).toLocaleTimeString()}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );

    const renderGpuStatus = () => (
        <div className="bg-white rounded-lg shadow mb-8">
            <div className="px-6 py-4 border-b border-gray-200">
                <h2 className="text-lg font-semibold text-gray-900">GPU Status</h2>
            </div>
            <div className="p-6">
                <div className="mb-4">
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium text-gray-700">GPU Acceleration</span>
                        <span className={`text-sm font-medium ${gpuStatus?.acceleration_enabled ? 'text-green-600' : 'text-red-600'}`}>
                            {gpuStatus?.acceleration_enabled ? 'Enabled' : 'Disabled'}
                        </span>
                    </div>
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium text-gray-700">GPU Available</span>
                        <span className={`text-sm font-medium ${gpuStatus?.gpu_available ? 'text-green-600' : 'text-red-600'}`}>
                            {gpuStatus?.gpu_available ? 'Yes' : 'No'}
                        </span>
                    </div>
                </div>
                
                {gpuStatus?.gpu_devices && gpuStatus.gpu_devices.length > 0 && (
                    <div>
                        <h3 className="text-sm font-medium text-gray-700 mb-3">Available GPUs</h3>
                        <div className="space-y-3">
                            {gpuStatus.gpu_devices.map((device, index) => (
                                <div key={index} className="border rounded-lg p-4">
                                    <div className="flex justify-between items-start mb-2">
                                        <div>
                                            <div className="font-medium text-gray-900">{device.name}</div>
                                            <div className="text-sm text-gray-500">Device {device.index}</div>
                                        </div>
                                        <div className="text-right">
                                            <div className="text-sm font-medium text-gray-900">
                                                {formatBytes(device.memory_available * 1024 * 1024)} available
                                            </div>
                                            <div className="text-sm text-gray-500">
                                                of {formatBytes(device.memory_total * 1024 * 1024)}
                                            </div>
                                        </div>
                                    </div>
                                    <div className="w-full bg-gray-200 rounded-full h-2">
                                        <div 
                                            className="bg-blue-600 h-2 rounded-full"
                                            style={{ width: `${(device.memory_used / device.memory_total) * 100}%` }}
                                        ></div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );

    const renderPerformanceMetrics = () => (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-white rounded-lg shadow">
                <div className="px-6 py-4 border-b border-gray-200">
                    <h2 className="text-lg font-semibold text-gray-900">Cluster Performance</h2>
                </div>
                <div className="p-6">
                    <div className="space-y-4">
                        <div>
                            <div className="flex justify-between text-sm">
                                <span className="text-gray-600">Total Capacity</span>
                                <span className="font-medium">{clusterStatus?.cluster_capacity || 0}x</span>
                            </div>
                        </div>
                        <div>
                            <div className="flex justify-between text-sm">
                                <span className="text-gray-600">Memory Usage</span>
                                <span className="font-medium">
                                    {formatBytes((clusterStatus?.total_memory_mb || 0) * 1024 * 1024)}
                                </span>
                            </div>
                        </div>
                        <div>
                            <div className="flex justify-between text-sm">
                                <span className="text-gray-600">GPU Memory</span>
                                <span className="font-medium">
                                    {formatBytes((clusterStatus?.total_gpu_memory_mb || 0) * 1024 * 1024)}
                                </span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div className="bg-white rounded-lg shadow">
                <div className="px-6 py-4 border-b border-gray-200">
                    <h2 className="text-lg font-semibold text-gray-900">System Health</h2>
                </div>
                <div className="p-6">
                    <div className="space-y-4">
                        <div className="flex items-center justify-between">
                            <span className="text-sm text-gray-600">Network Status</span>
                            <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-600">
                                Connected
                            </span>
                        </div>
                        <div className="flex items-center justify-between">
                            <span className="text-sm text-gray-600">Edge AI Status</span>
                            <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-600">
                                Active
                            </span>
                        </div>
                        <div className="flex items-center justify-between">
                            <span className="text-sm text-gray-600">P2P Network</span>
                            <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-600">
                                Enabled
                            </span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );

    if (isLoading) {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
                    <p className="mt-4 text-gray-600">Loading dashboard...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50 p-6">
            <div className="max-w-7xl mx-auto">
                <div className="mb-8">
                    <h1 className="text-3xl font-bold text-gray-900">Edge Computing Dashboard</h1>
                    <p className="mt-2 text-gray-600">
                        Monitor and manage your distributed video processing cluster
                    </p>
                </div>

                {renderClusterOverview()}
                {renderNodeList()}
                {renderGpuStatus()}
                {renderPerformanceMetrics()}
            </div>
        </div>
    );
};

export default EdgeDashboard;