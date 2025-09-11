"""
Collaborative Video Editing API
Real-time collaborative editing with conflict resolution
"""
import json
import time
import uuid
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any
from flask import Blueprint, request, jsonify
from flask_socketio import emit, join_room, leave_room, disconnect

from config.edge_config import edge_config

collab_bp = Blueprint('collaborative', __name__)

@dataclass
class EditOperation:
    """Represents a single edit operation"""
    operation_id: str
    session_id: str
    user_id: str
    operation_type: str  # 'insert', 'delete', 'modify', 'move'
    timestamp: float
    position: float  # Time position in video (seconds)
    duration: float  # Duration of affected content
    data: Dict[str, Any]  # Operation-specific data
    applied: bool = False
    conflicts: List[str] = None  # List of conflicting operation IDs


@dataclass
class EditSession:
    """Represents a collaborative editing session"""
    session_id: str
    project_id: str
    video_file: str
    created_by: str
    created_at: float
    last_activity: float
    active_users: Dict[str, Dict] = None  # user_id -> user_info
    operations: List[EditOperation] = None
    version: int = 0
    locked_regions: Dict[str, Dict] = None  # region_id -> lock_info
    auto_save_enabled: bool = True
    sync_status: str = 'synced'  # synced, syncing, conflict, offline


class ConflictResolver:
    """Handles conflict resolution for collaborative editing"""
    
    def __init__(self, strategy: str = 'last_writer_wins'):
        self.strategy = strategy
    
    def detect_conflicts(self, new_op: EditOperation, existing_ops: List[EditOperation]) -> List[str]:
        """Detect conflicts between new operation and existing operations"""
        conflicts = []
        
        for op in existing_ops:
            if op.applied and self._operations_conflict(new_op, op):
                conflicts.append(op.operation_id)
        
        return conflicts
    
    def _operations_conflict(self, op1: EditOperation, op2: EditOperation) -> bool:
        """Check if two operations conflict"""
        # Different users editing the same time region
        if op1.user_id == op2.user_id:
            return False
        
        # Check temporal overlap
        op1_start = op1.position
        op1_end = op1.position + op1.duration
        op2_start = op2.position
        op2_end = op2.position + op2.duration
        
        # Operations overlap if they affect the same time region
        overlap = not (op1_end <= op2_start or op2_end <= op1_start)
        
        if not overlap:
            return False
        
        # Check operation types that typically conflict
        conflicting_combinations = [
            ('delete', 'modify'),
            ('delete', 'insert'),
            ('modify', 'modify'),
            ('move', 'delete'),
            ('move', 'modify')
        ]
        
        op_types = (op1.operation_type, op2.operation_type)
        return op_types in conflicting_combinations or op_types[::-1] in conflicting_combinations
    
    def resolve_conflicts(self, conflicted_ops: List[EditOperation]) -> List[EditOperation]:
        """Resolve conflicts between operations"""
        if self.strategy == 'last_writer_wins':
            return self._resolve_last_writer_wins(conflicted_ops)
        elif self.strategy == 'merge_compatible':
            return self._resolve_merge_compatible(conflicted_ops)
        elif self.strategy == 'manual_resolution':
            return self._mark_for_manual_resolution(conflicted_ops)
        else:
            return conflicted_ops
    
    def _resolve_last_writer_wins(self, ops: List[EditOperation]) -> List[EditOperation]:
        """Resolve by keeping the latest operation"""
        if not ops:
            return []
        
        # Sort by timestamp
        sorted_ops = sorted(ops, key=lambda op: op.timestamp)
        
        # Keep only the latest operation
        latest_op = sorted_ops[-1]
        latest_op.applied = True
        
        # Mark earlier operations as not applied
        for op in sorted_ops[:-1]:
            op.applied = False
        
        return [latest_op]
    
    def _resolve_merge_compatible(self, ops: List[EditOperation]) -> List[EditOperation]:
        """Try to merge compatible operations"""
        # This is a simplified implementation
        # In a real system, this would be much more sophisticated
        resolved_ops = []
        
        for op in sorted(ops, key=lambda o: o.timestamp):
            if self._can_merge_with_existing(op, resolved_ops):
                # Merge with existing operation
                self._merge_operation(op, resolved_ops)
            else:
                op.applied = True
                resolved_ops.append(op)
        
        return resolved_ops
    
    def _can_merge_with_existing(self, op: EditOperation, existing_ops: List[EditOperation]) -> bool:
        """Check if operation can be merged with existing operations"""
        # Simple heuristic: only merge insert operations
        return op.operation_type == 'insert' and any(
            existing_op.operation_type == 'insert' and 
            abs(existing_op.position - op.position) < 1.0
            for existing_op in existing_ops
        )
    
    def _merge_operation(self, op: EditOperation, existing_ops: List[EditOperation]):
        """Merge operation with compatible existing operations"""
        # Find the closest insert operation
        for existing_op in existing_ops:
            if (existing_op.operation_type == 'insert' and 
                abs(existing_op.position - op.position) < 1.0):
                # Merge the operations (simplified)
                existing_op.duration += op.duration
                existing_op.data['merged_operations'] = existing_op.data.get('merged_operations', [])
                existing_op.data['merged_operations'].append(op.operation_id)
                break
    
    def _mark_for_manual_resolution(self, ops: List[EditOperation]) -> List[EditOperation]:
        """Mark operations for manual resolution"""
        for op in ops:
            op.applied = False
            op.data['requires_manual_resolution'] = True
        
        return ops


class CollaborativeEditingManager:
    """Manages collaborative editing sessions"""
    
    def __init__(self):
        self.sessions: Dict[str, EditSession] = {}
        self.user_sessions: Dict[str, str] = {}  # user_id -> session_id
        self.conflict_resolver = ConflictResolver(edge_config.conflict_resolution_strategy)
        self.auto_save_interval = edge_config.auto_save_interval
    
    def create_session(self, project_id: str, video_file: str, user_id: str) -> EditSession:
        """Create a new collaborative editing session"""
        session_id = str(uuid.uuid4())
        
        session = EditSession(
            session_id=session_id,
            project_id=project_id,
            video_file=video_file,
            created_by=user_id,
            created_at=time.time(),
            last_activity=time.time(),
            active_users={},
            operations=[],
            version=0,
            locked_regions={},
            auto_save_enabled=True,
            sync_status='synced'
        )
        
        self.sessions[session_id] = session
        return session
    
    def join_session(self, session_id: str, user_id: str, user_info: Dict) -> bool:
        """Add user to editing session"""
        if session_id not in self.sessions:
            return False
        
        session = self.sessions[session_id]
        session.active_users[user_id] = {
            'user_id': user_id,
            'joined_at': time.time(),
            'last_activity': time.time(),
            **user_info
        }
        
        self.user_sessions[user_id] = session_id
        session.last_activity = time.time()
        
        return True
    
    def leave_session(self, session_id: str, user_id: str) -> bool:
        """Remove user from editing session"""
        if session_id not in self.sessions:
            return False
        
        session = self.sessions[session_id]
        
        if user_id in session.active_users:
            del session.active_users[user_id]
        
        if user_id in self.user_sessions:
            del self.user_sessions[user_id]
        
        # Release any locked regions by this user
        to_release = []
        for region_id, lock_info in session.locked_regions.items():
            if lock_info['user_id'] == user_id:
                to_release.append(region_id)
        
        for region_id in to_release:
            del session.locked_regions[region_id]
        
        session.last_activity = time.time()
        return True
    
    def apply_operation(self, session_id: str, operation: EditOperation) -> Dict[str, Any]:
        """Apply an edit operation to the session"""
        if session_id not in self.sessions:
            return {'success': False, 'error': 'Session not found'}
        
        session = self.sessions[session_id]
        
        # Check if region is locked by another user
        if self._is_region_locked(session, operation):
            return {'success': False, 'error': 'Region is locked by another user'}
        
        # Detect conflicts
        conflicts = self.conflict_resolver.detect_conflicts(operation, session.operations)
        
        if conflicts:
            operation.conflicts = conflicts
            # Resolve conflicts
            conflicted_ops = [op for op in session.operations if op.operation_id in conflicts]
            conflicted_ops.append(operation)
            
            resolved_ops = self.conflict_resolver.resolve_conflicts(conflicted_ops)
            
            # Update operations in session
            for op in session.operations:
                if op.operation_id in conflicts:
                    # Update with resolved version
                    resolved_op = next((r for r in resolved_ops if r.operation_id == op.operation_id), None)
                    if resolved_op:
                        op.applied = resolved_op.applied
            
            # Check if new operation was applied
            resolved_new_op = next((r for r in resolved_ops if r.operation_id == operation.operation_id), None)
            if resolved_new_op and resolved_new_op.applied:
                operation.applied = True
            else:
                operation.applied = False
        else:
            operation.applied = True
        
        # Add operation to session
        session.operations.append(operation)
        session.version += 1
        session.last_activity = time.time()
        
        # Update user activity
        if operation.user_id in session.active_users:
            session.active_users[operation.user_id]['last_activity'] = time.time()
        
        return {
            'success': True,
            'operation_id': operation.operation_id,
            'applied': operation.applied,
            'conflicts': operation.conflicts or [],
            'session_version': session.version
        }
    
    def _is_region_locked(self, session: EditSession, operation: EditOperation) -> bool:
        """Check if the operation's region is locked by another user"""
        op_start = operation.position
        op_end = operation.position + operation.duration
        
        for region_id, lock_info in session.locked_regions.items():
            if lock_info['user_id'] == operation.user_id:
                continue  # User can edit their own locked regions
            
            lock_start = lock_info['start_time']
            lock_end = lock_info['end_time']
            
            # Check overlap
            if not (op_end <= lock_start or lock_end <= op_start):
                return True
        
        return False
    
    def lock_region(self, session_id: str, user_id: str, start_time: float, end_time: float) -> Dict[str, Any]:
        """Lock a time region for exclusive editing"""
        if session_id not in self.sessions:
            return {'success': False, 'error': 'Session not found'}
        
        session = self.sessions[session_id]
        
        # Check if region is already locked
        for region_id, lock_info in session.locked_regions.items():
            if lock_info['user_id'] != user_id:
                lock_start = lock_info['start_time']
                lock_end = lock_info['end_time']
                
                # Check overlap
                if not (end_time <= lock_start or lock_end <= start_time):
                    return {'success': False, 'error': 'Region already locked by another user'}
        
        # Create lock
        region_id = str(uuid.uuid4())
        session.locked_regions[region_id] = {
            'region_id': region_id,
            'user_id': user_id,
            'start_time': start_time,
            'end_time': end_time,
            'locked_at': time.time()
        }
        
        return {'success': True, 'region_id': region_id}
    
    def unlock_region(self, session_id: str, user_id: str, region_id: str) -> bool:
        """Unlock a time region"""
        if session_id not in self.sessions:
            return False
        
        session = self.sessions[session_id]
        
        if (region_id in session.locked_regions and 
            session.locked_regions[region_id]['user_id'] == user_id):
            del session.locked_regions[region_id]
            return True
        
        return False
    
    def get_session_state(self, session_id: str) -> Optional[Dict]:
        """Get complete session state"""
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        
        return {
            'session': asdict(session),
            'operations': [asdict(op) for op in session.operations],
            'active_users': session.active_users,
            'locked_regions': session.locked_regions
        }
    
    def cleanup_inactive_sessions(self, max_idle_hours: int = 24):
        """Clean up inactive sessions"""
        current_time = time.time()
        max_idle_seconds = max_idle_hours * 3600
        
        to_remove = []
        for session_id, session in self.sessions.items():
            if (current_time - session.last_activity) > max_idle_seconds:
                to_remove.append(session_id)
        
        for session_id in to_remove:
            # Clean up user mappings
            session = self.sessions[session_id]
            for user_id in session.active_users:
                if user_id in self.user_sessions:
                    del self.user_sessions[user_id]
            
            del self.sessions[session_id]


# Global collaborative editing manager
collab_manager = CollaborativeEditingManager()


@collab_bp.route('/sessions', methods=['POST'])
def create_editing_session():
    """Create a new collaborative editing session"""
    data = request.get_json()
    
    required_fields = ['project_id', 'video_file', 'user_id']
    if not all(field in data for field in required_fields):
        return jsonify({
            'success': False,
            'error': f'Missing required fields: {required_fields}'
        }), 400
    
    try:
        session = collab_manager.create_session(
            data['project_id'],
            data['video_file'],
            data['user_id']
        )
        
        return jsonify({
            'success': True,
            'session': asdict(session)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to create session: {str(e)}'
        }), 500


@collab_bp.route('/sessions/<session_id>/join', methods=['POST'])
def join_editing_session(session_id):
    """Join an existing editing session"""
    data = request.get_json()
    
    required_fields = ['user_id']
    if not all(field in data for field in required_fields):
        return jsonify({
            'success': False,
            'error': f'Missing required fields: {required_fields}'
        }), 400
    
    user_info = data.get('user_info', {})
    
    success = collab_manager.join_session(session_id, data['user_id'], user_info)
    
    if success:
        session_state = collab_manager.get_session_state(session_id)
        return jsonify({
            'success': True,
            'session_state': session_state
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Session not found'
        }), 404


@collab_bp.route('/sessions/<session_id>/leave', methods=['POST'])
def leave_editing_session(session_id):
    """Leave an editing session"""
    data = request.get_json()
    
    required_fields = ['user_id']
    if not all(field in data for field in required_fields):
        return jsonify({
            'success': False,
            'error': f'Missing required fields: {required_fields}'
        }), 400
    
    success = collab_manager.leave_session(session_id, data['user_id'])
    
    if success:
        return jsonify({
            'success': True,
            'message': 'Left session successfully'
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Session not found'
        }), 404


@collab_bp.route('/sessions/<session_id>/operations', methods=['POST'])
def apply_edit_operation(session_id):
    """Apply an edit operation to the session"""
    data = request.get_json()
    
    required_fields = ['user_id', 'operation_type', 'position', 'duration', 'data']
    if not all(field in data for field in required_fields):
        return jsonify({
            'success': False,
            'error': f'Missing required fields: {required_fields}'
        }), 400
    
    try:
        operation = EditOperation(
            operation_id=str(uuid.uuid4()),
            session_id=session_id,
            user_id=data['user_id'],
            operation_type=data['operation_type'],
            timestamp=time.time(),
            position=data['position'],
            duration=data['duration'],
            data=data['data']
        )
        
        result = collab_manager.apply_operation(session_id, operation)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to apply operation: {str(e)}'
        }), 500


@collab_bp.route('/sessions/<session_id>/lock', methods=['POST'])
def lock_region(session_id):
    """Lock a time region for exclusive editing"""
    data = request.get_json()
    
    required_fields = ['user_id', 'start_time', 'end_time']
    if not all(field in data for field in required_fields):
        return jsonify({
            'success': False,
            'error': f'Missing required fields: {required_fields}'
        }), 400
    
    result = collab_manager.lock_region(
        session_id,
        data['user_id'],
        data['start_time'],
        data['end_time']
    )
    
    return jsonify(result)


@collab_bp.route('/sessions/<session_id>/unlock/<region_id>', methods=['POST'])
def unlock_region(session_id, region_id):
    """Unlock a time region"""
    data = request.get_json()
    
    required_fields = ['user_id']
    if not all(field in data for field in required_fields):
        return jsonify({
            'success': False,
            'error': f'Missing required fields: {required_fields}'
        }), 400
    
    success = collab_manager.unlock_region(session_id, data['user_id'], region_id)
    
    if success:
        return jsonify({
            'success': True,
            'message': 'Region unlocked successfully'
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Failed to unlock region'
        }), 400


@collab_bp.route('/sessions/<session_id>/state', methods=['GET'])
def get_session_state(session_id):
    """Get current session state"""
    session_state = collab_manager.get_session_state(session_id)
    
    if session_state:
        return jsonify({
            'success': True,
            'session_state': session_state
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Session not found'
        }), 404


@collab_bp.route('/sessions', methods=['GET'])
def list_sessions():
    """List all active editing sessions"""
    sessions = []
    
    for session_id, session in collab_manager.sessions.items():
        session_info = {
            'session_id': session_id,
            'project_id': session.project_id,
            'created_by': session.created_by,
            'created_at': session.created_at,
            'last_activity': session.last_activity,
            'active_users_count': len(session.active_users),
            'operations_count': len(session.operations),
            'version': session.version,
            'sync_status': session.sync_status
        }
        sessions.append(session_info)
    
    return jsonify({
        'success': True,
        'sessions': sessions,
        'total': len(sessions)
    })


@collab_bp.route('/cleanup', methods=['POST'])
def cleanup_sessions():
    """Clean up inactive sessions"""
    data = request.get_json() or {}
    max_idle_hours = data.get('max_idle_hours', 24)
    
    sessions_before = len(collab_manager.sessions)
    collab_manager.cleanup_inactive_sessions(max_idle_hours)
    sessions_after = len(collab_manager.sessions)
    
    return jsonify({
        'success': True,
        'message': f'Cleaned up {sessions_before - sessions_after} inactive sessions',
        'sessions_removed': sessions_before - sessions_after,
        'active_sessions': sessions_after
    })