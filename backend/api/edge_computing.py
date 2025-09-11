"""
Edge Computing API Endpoints
Manages edge node coordination and distributed processing
"""
from flask import Blueprint, request, jsonify
import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import asdict

from config.edge_config import edge_config, EdgeNodeConfig

edge_bp = Blueprint('edge', __name__)

# In-memory storage for edge nodes (in production, use Redis or database)
edge_nodes: Dict[str, EdgeNodeConfig] = {}
active_tasks: Dict[str, Dict] = {}
node_heartbeats: Dict[str, datetime] = {}


class EdgeNodeManager:
    """Manages edge node registration, health monitoring, and task distribution"""
    
    def __init__(self):
        self.nodes = edge_nodes
        self.heartbeats = node_heartbeats
        self.tasks = active_tasks
        
        # Initialize with default nodes
        for node in edge_config.default_nodes:
            self.register_node(node)
    
    def register_node(self, node_config: EdgeNodeConfig) -> bool:
        """Register a new edge node"""
        self.nodes[node_config.node_id] = node_config
        self.heartbeats[node_config.node_id] = datetime.utcnow()
        return True
    
    def update_node_status(self, node_id: str, status: str) -> bool:
        """Update node status and heartbeat"""
        if node_id in self.nodes:
            self.nodes[node_id].status = status
            self.heartbeats[node_id] = datetime.utcnow()
            return True
        return False
    
    def get_available_nodes(self) -> List[EdgeNodeConfig]:
        """Get list of online and available nodes"""
        available = []
        current_time = datetime.utcnow()
        timeout = timedelta(seconds=edge_config.node_timeout)
        
        for node_id, node in self.nodes.items():
            last_heartbeat = self.heartbeats.get(node_id, current_time - timeout - timedelta(seconds=1))
            
            # Check if node is still alive
            if current_time - last_heartbeat < timeout:
                if node.status in ['online', 'idle']:
                    available.append(node)
            else:
                # Mark as offline if timeout exceeded
                node.status = 'offline'
        
        # Sort by priority and processing capacity
        available.sort(key=lambda n: (n.priority, -n.processing_capacity))
        return available
    
    def select_best_node(self, requirements: Dict = None) -> Optional[EdgeNodeConfig]:
        """Select the best node for a given task"""
        available_nodes = self.get_available_nodes()
        
        if not available_nodes:
            return None
        
        if not requirements:
            return available_nodes[0]
        
        # Filter nodes based on requirements
        suitable_nodes = []
        for node in available_nodes:
            if requirements.get('gpu_required', False) and not node.gpu_available:
                continue
            if requirements.get('min_memory', 0) > node.memory:
                continue
            if requirements.get('min_gpu_memory', 0) > node.gpu_memory:
                continue
            suitable_nodes.append(node)
        
        return suitable_nodes[0] if suitable_nodes else None
    
    def get_cluster_status(self) -> Dict:
        """Get overall cluster status"""
        total_nodes = len(self.nodes)
        online_nodes = len([n for n in self.nodes.values() if n.status in ['online', 'idle', 'busy']])
        gpu_nodes = len([n for n in self.nodes.values() if n.gpu_available and n.status != 'offline'])
        
        total_memory = sum(n.memory for n in self.nodes.values() if n.status != 'offline')
        total_gpu_memory = sum(n.gpu_memory for n in self.nodes.values() if n.gpu_available and n.status != 'offline')
        
        return {
            'total_nodes': total_nodes,
            'online_nodes': online_nodes,
            'gpu_nodes': gpu_nodes,
            'total_memory_mb': total_memory,
            'total_gpu_memory_mb': total_gpu_memory,
            'active_tasks': len(self.tasks),
            'cluster_capacity': sum(n.processing_capacity for n in self.nodes.values() if n.status != 'offline')
        }


# Global edge node manager
edge_manager = EdgeNodeManager()


@edge_bp.route('/nodes', methods=['GET'])
def get_edge_nodes():
    """Get list of all edge nodes"""
    nodes_data = []
    for node_id, node in edge_manager.nodes.items():
        node_data = asdict(node)
        node_data['last_heartbeat'] = edge_manager.heartbeats.get(node_id, datetime.utcnow()).isoformat()
        nodes_data.append(node_data)
    
    return jsonify({
        'success': True,
        'nodes': nodes_data,
        'total': len(nodes_data)
    })


@edge_bp.route('/nodes/register', methods=['POST'])
def register_edge_node():
    """Register a new edge node"""
    data = request.get_json()
    
    required_fields = ['node_id', 'hostname', 'port']
    if not all(field in data for field in required_fields):
        return jsonify({
            'success': False,
            'error': f'Missing required fields: {required_fields}'
        }), 400
    
    try:
        node_config = EdgeNodeConfig(
            node_id=data['node_id'],
            hostname=data['hostname'],
            port=data['port'],
            gpu_available=data.get('gpu_available', False),
            gpu_memory=data.get('gpu_memory', 0),
            cpu_cores=data.get('cpu_cores', 4),
            memory=data.get('memory', 8192),
            processing_capacity=data.get('processing_capacity', 1.0),
            priority=data.get('priority', 2),
            status='online'
        )
        
        success = edge_manager.register_node(node_config)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Node {node_config.node_id} registered successfully',
                'node': asdict(node_config)
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to register node'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Registration failed: {str(e)}'
        }), 400


@edge_bp.route('/nodes/<node_id>/heartbeat', methods=['POST'])
def node_heartbeat(node_id):
    """Receive heartbeat from edge node"""
    data = request.get_json() or {}
    status = data.get('status', 'online')
    
    success = edge_manager.update_node_status(node_id, status)
    
    if success:
        return jsonify({
            'success': True,
            'message': 'Heartbeat received',
            'timestamp': datetime.utcnow().isoformat()
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Node not found'
        }), 404


@edge_bp.route('/nodes/<node_id>/status', methods=['PUT'])
def update_node_status(node_id):
    """Update node status"""
    data = request.get_json()
    status = data.get('status')
    
    if not status:
        return jsonify({
            'success': False,
            'error': 'Status is required'
        }), 400
    
    valid_statuses = ['online', 'offline', 'busy', 'idle', 'error']
    if status not in valid_statuses:
        return jsonify({
            'success': False,
            'error': f'Invalid status. Must be one of: {valid_statuses}'
        }), 400
    
    success = edge_manager.update_node_status(node_id, status)
    
    if success:
        return jsonify({
            'success': True,
            'message': f'Node {node_id} status updated to {status}'
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Node not found'
        }), 404


@edge_bp.route('/cluster/status', methods=['GET'])
def get_cluster_status():
    """Get overall edge cluster status"""
    status = edge_manager.get_cluster_status()
    config = {
        'video_processing': edge_config.get_video_processing_config(),
        'p2p': edge_config.get_p2p_config(),
        'offline': edge_config.get_offline_config()
    }
    
    return jsonify({
        'success': True,
        'cluster_status': status,
        'configuration': config
    })


@edge_bp.route('/nodes/available', methods=['GET'])
def get_available_nodes():
    """Get list of available nodes for task assignment"""
    requirements = request.args.to_dict()
    
    # Convert string parameters to appropriate types
    if 'gpu_required' in requirements:
        requirements['gpu_required'] = requirements['gpu_required'].lower() == 'true'
    if 'min_memory' in requirements:
        requirements['min_memory'] = int(requirements['min_memory'])
    if 'min_gpu_memory' in requirements:
        requirements['min_gpu_memory'] = int(requirements['min_gpu_memory'])
    
    available_nodes = edge_manager.get_available_nodes()
    
    # Filter by requirements if provided
    if requirements:
        filtered_nodes = []
        for node in available_nodes:
            if requirements.get('gpu_required', False) and not node.gpu_available:
                continue
            if requirements.get('min_memory', 0) > node.memory:
                continue
            if requirements.get('min_gpu_memory', 0) > node.gpu_memory:
                continue
            filtered_nodes.append(node)
        available_nodes = filtered_nodes
    
    nodes_data = [asdict(node) for node in available_nodes]
    
    return jsonify({
        'success': True,
        'available_nodes': nodes_data,
        'total': len(nodes_data),
        'requirements': requirements
    })


@edge_bp.route('/nodes/select', methods=['POST'])
def select_optimal_node():
    """Select the optimal node for a specific task"""
    data = request.get_json() or {}
    requirements = data.get('requirements', {})
    
    best_node = edge_manager.select_best_node(requirements)
    
    if best_node:
        return jsonify({
            'success': True,
            'selected_node': asdict(best_node),
            'requirements': requirements
        })
    else:
        return jsonify({
            'success': False,
            'error': 'No suitable nodes available',
            'requirements': requirements
        }), 404