"""
Test Edge Computing Video Processing Functionality
"""
import pytest
import json
import tempfile
import os
from unittest.mock import Mock, patch
import asyncio

# Import the modules we want to test
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from config.edge_config import EdgeComputingConfig, EdgeNodeConfig
from api.edge_computing import EdgeNodeManager
from services.video_processor import VideoProcessor, GPUAccelerator
from services.distributed_processor import DistributedProcessor
from api.collaborative_editing import CollaborativeEditingManager


class TestEdgeComputingConfig:
    """Test edge computing configuration"""
    
    def test_default_config_initialization(self):
        """Test that default configuration is properly initialized"""
        config = EdgeComputingConfig()
        
        assert config.max_nodes == 10
        assert config.node_timeout == 30
        assert config.heartbeat_interval == 5
        assert config.video_chunk_size == 10
        assert len(config.default_nodes) == 1
        assert config.default_nodes[0].node_id == "local"
    
    def test_video_processing_config(self):
        """Test video processing configuration"""
        config = EdgeComputingConfig()
        video_config = config.get_video_processing_config()
        
        assert 'supported_formats' in video_config
        assert 'mp4' in video_config['supported_formats']
        assert 'max_resolution' in video_config
        assert 'processing_quality' in video_config
        assert 'low' in video_config['processing_quality']
    
    def test_p2p_config(self):
        """Test P2P configuration"""
        config = EdgeComputingConfig()
        p2p_config = config.get_p2p_config()
        
        assert 'enabled' in p2p_config
        assert 'port_range' in p2p_config
        assert 'max_peers' in p2p_config
        assert len(p2p_config['port_range']) == 2


class TestEdgeNodeManager:
    """Test edge node management"""
    
    def test_node_registration(self):
        """Test node registration"""
        manager = EdgeNodeManager()
        
        node_config = EdgeNodeConfig(
            node_id="test_node",
            hostname="test.local",
            port=8001,
            gpu_available=True,
            gpu_memory=8192,
            status="online"
        )
        
        success = manager.register_node(node_config)
        assert success
        assert "test_node" in manager.nodes
        assert manager.nodes["test_node"].gpu_available
    
    def test_available_nodes_filtering(self):
        """Test filtering of available nodes"""
        manager = EdgeNodeManager()
        
        # Register multiple nodes
        for i in range(3):
            node = EdgeNodeConfig(
                node_id=f"node_{i}",
                hostname=f"node{i}.local",
                port=8000 + i,
                status="online" if i < 2 else "offline"
            )
            manager.register_node(node)
        
        available_nodes = manager.get_available_nodes()
        assert len(available_nodes) >= 2  # At least 2 online nodes (including local)
    
    def test_best_node_selection(self):
        """Test selection of best node for requirements"""
        manager = EdgeNodeManager()
        
        # Register a GPU node
        gpu_node = EdgeNodeConfig(
            node_id="gpu_node",
            hostname="gpu.local",
            port=8001,
            gpu_available=True,
            gpu_memory=8192,
            memory=16384,
            processing_capacity=2.0,
            priority=1,
            status="online"
        )
        manager.register_node(gpu_node)
        
        # Test selection with GPU requirement
        requirements = {'gpu_required': True, 'min_memory': 8192}
        best_node = manager.select_best_node(requirements)
        
        assert best_node is not None
        assert best_node.gpu_available
        assert best_node.memory >= 8192


class TestGPUAccelerator:
    """Test GPU acceleration functionality"""
    
    def test_gpu_detection(self):
        """Test GPU detection"""
        gpu_accelerator = GPUAccelerator()
        
        # GPU availability depends on system, so we just test the method exists
        assert hasattr(gpu_accelerator, 'gpu_available')
        assert hasattr(gpu_accelerator, 'gpu_devices')
        assert isinstance(gpu_accelerator.gpu_devices, list)
    
    def test_ffmpeg_args_generation(self):
        """Test FFmpeg GPU arguments generation"""
        gpu_accelerator = GPUAccelerator()
        
        # Mock a GPU device
        mock_device = {
            'index': 0,
            'name': 'Test GPU',
            'memory_available': 4096,
            'type': 'nvidia'
        }
        
        args = gpu_accelerator.get_ffmpeg_gpu_args(mock_device)
        
        if mock_device['type'] == 'nvidia':
            assert '-hwaccel' in args
            assert 'cuda' in args


class TestVideoProcessor:
    """Test video processing functionality"""
    
    @pytest.fixture
    def video_processor(self):
        """Create a video processor instance for testing"""
        return VideoProcessor()
    
    @pytest.mark.asyncio
    async def test_task_creation(self, video_processor):
        """Test video processing task creation"""
        task = await video_processor.create_task(
            operation='transcode',
            input_file='/test/input.mp4',
            output_file='/test/output.mp4',
            parameters={'codec': 'h264', 'quality': 'medium'}
        )
        
        assert task.operation == 'transcode'
        assert task.status == 'pending'
        assert task.task_id in video_processor.active_tasks
    
    def test_task_status_retrieval(self, video_processor):
        """Test task status retrieval"""
        # Create a mock task
        task_id = "test_task_123"
        with patch.object(video_processor, 'active_tasks', {task_id: Mock(task_id=task_id)}):
            status = video_processor.get_task_status(task_id)
            assert status is not None
    
    def test_task_cancellation(self, video_processor):
        """Test task cancellation"""
        # Create a mock task
        mock_task = Mock()
        mock_task.status = 'processing'
        task_id = "test_task_123"
        
        with patch.object(video_processor, 'active_tasks', {task_id: mock_task}):
            success = video_processor.cancel_task(task_id)
            assert success
            assert mock_task.status == 'cancelled'


class TestCollaborativeEditingManager:
    """Test collaborative editing functionality"""
    
    @pytest.fixture
    def collab_manager(self):
        """Create a collaborative editing manager for testing"""
        return CollaborativeEditingManager()
    
    def test_session_creation(self, collab_manager):
        """Test collaborative session creation"""
        session = collab_manager.create_session(
            project_id="test_project",
            video_file="/test/video.mp4",
            user_id="user123"
        )
        
        assert session.project_id == "test_project"
        assert session.created_by == "user123"
        assert session.session_id in collab_manager.sessions
    
    def test_user_join_leave(self, collab_manager):
        """Test user joining and leaving sessions"""
        session = collab_manager.create_session(
            project_id="test_project",
            video_file="/test/video.mp4",
            user_id="user123"
        )
        
        # Test joining
        success = collab_manager.join_session(
            session.session_id,
            "user456",
            {"name": "Test User"}
        )
        assert success
        assert "user456" in session.active_users
        
        # Test leaving
        success = collab_manager.leave_session(session.session_id, "user456")
        assert success
        assert "user456" not in session.active_users
    
    def test_region_locking(self, collab_manager):
        """Test time region locking for exclusive editing"""
        session = collab_manager.create_session(
            project_id="test_project",
            video_file="/test/video.mp4",
            user_id="user123"
        )
        
        # Test locking a region
        result = collab_manager.lock_region(
            session.session_id,
            "user123",
            start_time=10.0,
            end_time=20.0
        )
        
        assert result['success']
        region_id = result['region_id']
        assert region_id in session.locked_regions
        
        # Test unlocking
        success = collab_manager.unlock_region(
            session.session_id,
            "user123",
            region_id
        )
        assert success
        assert region_id not in session.locked_regions


class TestAPIIntegration:
    """Test API endpoint integration"""
    
    @pytest.fixture
    def app(self):
        """Create Flask app for testing"""
        import sys
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
        
        from app import app
        app.config['TESTING'] = True
        return app
    
    def test_home_endpoint_includes_edge_features(self, app):
        """Test that home endpoint includes edge computing features"""
        with app.test_client() as client:
            response = client.get('/')
            data = json.loads(response.data)
            
            assert response.status_code == 200
            assert 'edge_computing_features' in data
            assert 'distributed_video_processing' in data['edge_computing_features']
            assert 'collaborative_editing' in data['edge_computing_features']
    
    def test_edge_nodes_endpoint(self, app):
        """Test edge nodes API endpoint"""
        with app.test_client() as client:
            response = client.get('/api/edge/nodes')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success']
            assert 'nodes' in data
    
    def test_video_formats_endpoint(self, app):
        """Test video formats API endpoint"""
        with app.test_client() as client:
            response = client.get('/api/video/formats')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success']
            assert 'formats' in data
            assert 'input_formats' in data['formats']


if __name__ == '__main__':
    """Run tests when script is executed directly"""
    pytest.main([__file__, '-v'])