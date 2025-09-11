"""
Edge Computing Configuration
Manages edge node settings and distributed processing parameters
"""
import os
from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class EdgeNodeConfig:
    """Configuration for individual edge nodes"""
    node_id: str
    hostname: str
    port: int
    gpu_available: bool = False
    gpu_memory: int = 0  # MB
    cpu_cores: int = 4
    memory: int = 8192  # MB
    processing_capacity: float = 1.0  # Relative processing power
    priority: int = 1  # 1=high, 2=medium, 3=low
    status: str = "offline"  # offline, online, busy, error


class EdgeComputingConfig:
    """Global edge computing configuration"""
    
    def __init__(self):
        # Load configuration from environment variables
        self.max_nodes = int(os.environ.get('EDGE_MAX_NODES', '10'))
        self.node_timeout = int(os.environ.get('EDGE_NODE_TIMEOUT', '30'))
        self.heartbeat_interval = int(os.environ.get('EDGE_HEARTBEAT_INTERVAL', '5'))
        self.video_chunk_size = int(os.environ.get('EDGE_VIDEO_CHUNK_SIZE', '10'))  # seconds
        self.p2p_port_range = (8000, 8100)
        self.enable_gpu_acceleration = os.environ.get('EDGE_ENABLE_GPU', 'true').lower() == 'true'
        self.enable_p2p = os.environ.get('EDGE_ENABLE_P2P', 'true').lower() == 'true'
        self.enable_offline_mode = os.environ.get('EDGE_ENABLE_OFFLINE', 'true').lower() == 'true'
        
        # AI Inference settings
        self.ai_model_cache_size = int(os.environ.get('EDGE_AI_CACHE_SIZE', '1024'))  # MB
        self.edge_ai_models = {
            'video_enhancement': 'edge-video-enhance-v1',
            'object_detection': 'edge-yolo-v8',
            'style_transfer': 'edge-style-transfer-v1',
            'audio_enhancement': 'edge-audio-enhance-v1'
        }
        
        # Collaborative editing settings
        self.max_concurrent_editors = int(os.environ.get('EDGE_MAX_EDITORS', '10'))
        self.conflict_resolution_strategy = os.environ.get('EDGE_CONFLICT_RESOLUTION', 'last_writer_wins')
        self.auto_save_interval = int(os.environ.get('EDGE_AUTO_SAVE_INTERVAL', '5'))  # seconds
        
        # Default edge nodes (can be configured dynamically)
        self.default_nodes = [
            EdgeNodeConfig(
                node_id="local",
                hostname="localhost",
                port=8001,
                gpu_available=True,
                gpu_memory=8192,
                cpu_cores=8,
                memory=16384,
                processing_capacity=2.0,
                priority=1,
                status="online"
            )
        ]
    
    def get_video_processing_config(self) -> Dict[str, Any]:
        """Get video processing specific configuration"""
        return {
            'supported_formats': ['mp4', 'avi', 'mov', 'mkv', 'webm'],
            'max_resolution': '4K',
            'max_duration': 3600,  # seconds
            'chunk_size': self.video_chunk_size,
            'gpu_acceleration': self.enable_gpu_acceleration,
            'processing_quality': {
                'low': {'bitrate': '1M', 'fps': 24},
                'medium': {'bitrate': '5M', 'fps': 30},
                'high': {'bitrate': '10M', 'fps': 60},
                'ultra': {'bitrate': '20M', 'fps': 120}
            }
        }
    
    def get_p2p_config(self) -> Dict[str, Any]:
        """Get P2P networking configuration"""
        return {
            'enabled': self.enable_p2p,
            'port_range': self.p2p_port_range,
            'max_peers': 50,
            'chunk_size': 64 * 1024,  # 64KB
            'discovery_timeout': 10,
            'protocols': ['webrtc', 'websocket']
        }
    
    def get_offline_config(self) -> Dict[str, Any]:
        """Get offline mode configuration"""
        return {
            'enabled': self.enable_offline_mode,
            'cache_size': 2048,  # MB
            'sync_retry_interval': 30,  # seconds
            'conflict_resolution': self.conflict_resolution_strategy,
            'auto_save': self.auto_save_interval
        }


# Global instance
edge_config = EdgeComputingConfig()