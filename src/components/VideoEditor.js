/**
 * Video Editor Component with Edge Computing Support
 * Provides video editing interface with collaborative features
 */
import React, { useState, useEffect, useRef } from 'react';
import { videoProcessingAPI } from '../api/video-processing.js';

const VideoEditor = () => {
    const [currentProject, setCurrentProject] = useState(null);
    const [videoFile, setVideoFile] = useState(null);
    const [isUploading, setIsUploading] = useState(false);
    const [isProcessing, setIsProcessing] = useState(false);
    const [processingTasks, setProcessingTasks] = useState([]);
    const [collaborativeSession, setCollaborativeSession] = useState(null);
    const [connectedUsers, setConnectedUsers] = useState([]);
    const [edgeNodeStatus, setEdgeNodeStatus] = useState(null);
    
    const videoRef = useRef(null);
    const timelineRef = useRef(null);

    useEffect(() => {
        // Load edge node status
        loadEdgeNodeStatus();
        
        // Set up polling for task updates
        const interval = setInterval(() => {
            updateProcessingTasks();
        }, 2000);

        return () => clearInterval(interval);
    }, []);

    const loadEdgeNodeStatus = async () => {
        try {
            const response = await videoProcessingAPI.getClusterStatus();
            if (response.success) {
                setEdgeNodeStatus(response.cluster_status);
            }
        } catch (error) {
            console.error('Failed to load edge node status:', error);
        }
    };

    const updateProcessingTasks = async () => {
        try {
            const response = await videoProcessingAPI.getTasks();
            if (response.success) {
                setProcessingTasks(response.tasks.filter(task => 
                    task.status === 'processing' || task.status === 'pending'
                ));
            }
        } catch (error) {
            console.error('Failed to update tasks:', error);
        }
    };

    const handleVideoUpload = async (event) => {
        const file = event.target.files[0];
        if (!file) return;

        setIsUploading(true);
        try {
            const response = await videoProcessingAPI.uploadVideo(file);
            if (response.success) {
                setVideoFile({
                    id: response.file_id,
                    name: response.original_filename,
                    path: response.file_path,
                    size: response.file_size
                });
                
                // Load video in player
                if (videoRef.current) {
                    videoRef.current.src = URL.createObjectURL(file);
                }
            }
        } catch (error) {
            console.error('Upload failed:', error);
            alert('Failed to upload video. Please try again.');
        } finally {
            setIsUploading(false);
        }
    };

    const startVideoProcessing = async (operation, parameters = {}, distributed = false) => {
        if (!videoFile) {
            alert('Please upload a video first');
            return;
        }

        setIsProcessing(true);
        try {
            const response = await videoProcessingAPI.startProcessing({
                operation,
                input_file: videoFile.path,
                parameters,
                distributed
            });

            if (response.success) {
                setProcessingTasks(prev => [...prev, {
                    task_id: response.task_id,
                    operation,
                    status: response.status,
                    task_type: response.task_type,
                    progress: 0
                }]);
                
                alert(`${operation} task started successfully!`);
            }
        } catch (error) {
            console.error('Processing failed:', error);
            alert('Failed to start processing. Please try again.');
        } finally {
            setIsProcessing(false);
        }
    };

    const startCollaborativeSession = async () => {
        if (!videoFile) {
            alert('Please upload a video first');
            return;
        }

        try {
            const response = await videoProcessingAPI.createCollaborativeSession({
                project_id: videoFile.id,
                video_file: videoFile.path,
                user_id: 'current_user' // In real app, get from auth
            });

            if (response.success) {
                setCollaborativeSession(response.session);
                alert('Collaborative session started! Share the session ID with others.');
            }
        } catch (error) {
            console.error('Failed to start collaborative session:', error);
        }
    };

    const renderTaskStatus = (task) => {
        const statusColor = {
            'pending': 'text-yellow-600',
            'processing': 'text-blue-600',
            'completed': 'text-green-600',
            'failed': 'text-red-600',
            'cancelled': 'text-gray-600'
        }[task.status] || 'text-gray-600';

        return (
            <div key={task.task_id} className="bg-white p-4 rounded-lg shadow border">
                <div className="flex justify-between items-center mb-2">
                    <h3 className="font-semibold capitalize">{task.operation}</h3>
                    <span className={`text-sm font-medium ${statusColor}`}>
                        {task.status}
                    </span>
                </div>
                
                <div className="text-sm text-gray-600 mb-2">
                    Type: {task.task_type} | ID: {task.task_id.slice(0, 8)}...
                </div>

                {task.status === 'processing' && (
                    <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                            className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                            style={{ width: `${task.progress || 0}%` }}
                        ></div>
                    </div>
                )}

                {task.status === 'completed' && (
                    <button 
                        onClick={() => downloadResult(task.task_id)}
                        className="mt-2 px-3 py-1 bg-green-600 text-white rounded text-sm hover:bg-green-700"
                    >
                        Download Result
                    </button>
                )}
            </div>
        );
    };

    const downloadResult = async (taskId) => {
        try {
            const blob = await videoProcessingAPI.downloadResult(taskId);
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `processed_${taskId}.mp4`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        } catch (error) {
            console.error('Download failed:', error);
            alert('Failed to download result.');
        }
    };

    return (
        <div className="min-h-screen bg-gray-50 p-6">
            <div className="max-w-7xl mx-auto">
                <h1 className="text-3xl font-bold text-gray-900 mb-8">
                    Edge Computing Video Editor
                </h1>

                {/* Edge Node Status */}
                {edgeNodeStatus && (
                    <div className="bg-white p-6 rounded-lg shadow mb-6">
                        <h2 className="text-xl font-semibold mb-4">Edge Cluster Status</h2>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                            <div className="text-center">
                                <div className="text-2xl font-bold text-blue-600">
                                    {edgeNodeStatus.online_nodes}
                                </div>
                                <div className="text-sm text-gray-600">Online Nodes</div>
                            </div>
                            <div className="text-center">
                                <div className="text-2xl font-bold text-green-600">
                                    {edgeNodeStatus.gpu_nodes}
                                </div>
                                <div className="text-sm text-gray-600">GPU Nodes</div>
                            </div>
                            <div className="text-center">
                                <div className="text-2xl font-bold text-purple-600">
                                    {Math.round(edgeNodeStatus.total_memory_mb / 1024)}GB
                                </div>
                                <div className="text-sm text-gray-600">Total Memory</div>
                            </div>
                            <div className="text-center">
                                <div className="text-2xl font-bold text-orange-600">
                                    {edgeNodeStatus.active_tasks}
                                </div>
                                <div className="text-sm text-gray-600">Active Tasks</div>
                            </div>
                        </div>
                    </div>
                )}

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Video Player and Controls */}
                    <div className="lg:col-span-2">
                        <div className="bg-white p-6 rounded-lg shadow">
                            <h2 className="text-xl font-semibold mb-4">Video Player</h2>
                            
                            {/* File Upload */}
                            <div className="mb-4">
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Upload Video
                                </label>
                                <input
                                    type="file"
                                    accept="video/*"
                                    onChange={handleVideoUpload}
                                    disabled={isUploading}
                                    className="block w-full text-sm text-gray-500
                                        file:mr-4 file:py-2 file:px-4
                                        file:rounded-full file:border-0
                                        file:text-sm file:font-semibold
                                        file:bg-blue-50 file:text-blue-700
                                        hover:file:bg-blue-100"
                                />
                                {isUploading && (
                                    <div className="mt-2 text-sm text-blue-600">
                                        Uploading...
                                    </div>
                                )}
                            </div>

                            {/* Video Player */}
                            <div className="mb-4">
                                <video
                                    ref={videoRef}
                                    controls
                                    className="w-full h-64 bg-black rounded"
                                />
                            </div>

                            {/* Timeline (placeholder) */}
                            <div ref={timelineRef} className="h-16 bg-gray-100 rounded border">
                                <div className="p-4 text-center text-gray-500">
                                    Timeline (drag and drop editing would go here)
                                </div>
                            </div>
                        </div>

                        {/* Processing Controls */}
                        <div className="bg-white p-6 rounded-lg shadow mt-6">
                            <h2 className="text-xl font-semibold mb-4">Video Processing</h2>
                            
                            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                                <button
                                    onClick={() => startVideoProcessing('transcode', 
                                        { codec: 'h264', quality: 'medium' }, false)}
                                    disabled={!videoFile || isProcessing}
                                    className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
                                >
                                    Transcode (Local)
                                </button>
                                
                                <button
                                    onClick={() => startVideoProcessing('transcode', 
                                        { codec: 'h264', quality: 'high' }, true)}
                                    disabled={!videoFile || isProcessing}
                                    className="px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700 disabled:opacity-50"
                                >
                                    Transcode (Distributed)
                                </button>
                                
                                <button
                                    onClick={() => startVideoProcessing('enhance', 
                                        { denoise: true, sharpen: true })}
                                    disabled={!videoFile || isProcessing}
                                    className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
                                >
                                    Enhance Video
                                </button>
                                
                                <button
                                    onClick={() => startVideoProcessing('analyze')}
                                    disabled={!videoFile || isProcessing}
                                    className="px-4 py-2 bg-orange-600 text-white rounded hover:bg-orange-700 disabled:opacity-50"
                                >
                                    Analyze Video
                                </button>
                                
                                <button
                                    onClick={startCollaborativeSession}
                                    disabled={!videoFile}
                                    className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 disabled:opacity-50"
                                >
                                    Start Collaboration
                                </button>
                            </div>
                        </div>
                    </div>

                    {/* Side Panel */}
                    <div className="space-y-6">
                        {/* Collaborative Session */}
                        {collaborativeSession && (
                            <div className="bg-white p-6 rounded-lg shadow">
                                <h3 className="text-lg font-semibold mb-4">Collaborative Session</h3>
                                <div className="text-sm text-gray-600 mb-2">
                                    Session ID: {collaborativeSession.session_id.slice(0, 8)}...
                                </div>
                                <div className="text-sm text-gray-600 mb-4">
                                    Connected Users: {connectedUsers.length}
                                </div>
                                <button className="w-full px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700">
                                    End Session
                                </button>
                            </div>
                        )}

                        {/* Active Tasks */}
                        <div className="bg-white p-6 rounded-lg shadow">
                            <h3 className="text-lg font-semibold mb-4">
                                Processing Tasks ({processingTasks.length})
                            </h3>
                            
                            <div className="space-y-3 max-h-96 overflow-y-auto">
                                {processingTasks.length === 0 ? (
                                    <div className="text-center text-gray-500 py-4">
                                        No active tasks
                                    </div>
                                ) : (
                                    processingTasks.map(renderTaskStatus)
                                )}
                            </div>
                        </div>

                        {/* Quick Actions */}
                        <div className="bg-white p-6 rounded-lg shadow">
                            <h3 className="text-lg font-semibold mb-4">Quick Actions</h3>
                            
                            <div className="space-y-2">
                                <button className="w-full px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700">
                                    View All Tasks
                                </button>
                                <button className="w-full px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700">
                                    Edge Node Dashboard
                                </button>
                                <button className="w-full px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700">
                                    P2P Network Status
                                </button>
                                <button className="w-full px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700">
                                    Offline Projects
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default VideoEditor;