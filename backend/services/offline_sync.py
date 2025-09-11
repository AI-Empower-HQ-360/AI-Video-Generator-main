"""
Offline-First Video Editing with Sync Capabilities
Handles offline video editing and synchronization when connection is restored
"""
import json
import os
import sqlite3
import time
import uuid
import hashlib
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta

from config.edge_config import edge_config


@dataclass
class OfflineOperation:
    """Represents an operation performed while offline"""
    operation_id: str
    session_id: str
    user_id: str
    operation_type: str
    timestamp: float
    data: Dict[str, Any]
    local_version: int
    sync_status: str = 'pending'  # pending, syncing, synced, conflict
    conflict_resolution: Optional[str] = None
    checksum: Optional[str] = None


@dataclass
class OfflineProject:
    """Represents an offline video editing project"""
    project_id: str
    name: str
    video_file: str
    created_at: float
    last_modified: float
    operations: List[OfflineOperation]
    local_version: int
    server_version: int
    sync_status: str = 'offline'  # offline, syncing, synced, conflict


class OfflineStorageManager:
    """Manages local storage for offline editing"""
    
    def __init__(self, storage_dir: str = None):
        self.storage_dir = storage_dir or os.path.join(os.path.expanduser('~'), '.video_editor_offline')
        self.db_path = os.path.join(self.storage_dir, 'offline_data.db')
        self._ensure_storage_directory()
        self._initialize_database()
    
    def _ensure_storage_directory(self):
        """Ensure storage directory exists"""
        os.makedirs(self.storage_dir, exist_ok=True)
    
    def _initialize_database(self):
        """Initialize SQLite database for offline storage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Projects table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                project_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                video_file TEXT NOT NULL,
                created_at REAL NOT NULL,
                last_modified REAL NOT NULL,
                local_version INTEGER NOT NULL DEFAULT 0,
                server_version INTEGER NOT NULL DEFAULT 0,
                sync_status TEXT NOT NULL DEFAULT 'offline',
                metadata TEXT
            )
        ''')
        
        # Operations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS operations (
                operation_id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                session_id TEXT,
                user_id TEXT NOT NULL,
                operation_type TEXT NOT NULL,
                timestamp REAL NOT NULL,
                data TEXT NOT NULL,
                local_version INTEGER NOT NULL,
                sync_status TEXT NOT NULL DEFAULT 'pending',
                conflict_resolution TEXT,
                checksum TEXT,
                FOREIGN KEY (project_id) REFERENCES projects (project_id)
            )
        ''')
        
        # Sync queue table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sync_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT NOT NULL,
                operation_id TEXT,
                action TEXT NOT NULL,
                priority INTEGER NOT NULL DEFAULT 0,
                created_at REAL NOT NULL,
                attempts INTEGER NOT NULL DEFAULT 0,
                last_attempt REAL,
                error_message TEXT,
                FOREIGN KEY (project_id) REFERENCES projects (project_id)
            )
        ''')
        
        # Cache table for video chunks
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS video_cache (
                chunk_id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                file_path TEXT NOT NULL,
                size_bytes INTEGER NOT NULL,
                created_at REAL NOT NULL,
                last_accessed REAL NOT NULL,
                FOREIGN KEY (project_id) REFERENCES projects (project_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_project(self, project: OfflineProject) -> bool:
        """Save project to offline storage"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Save project
            cursor.execute('''
                INSERT OR REPLACE INTO projects 
                (project_id, name, video_file, created_at, last_modified, 
                 local_version, server_version, sync_status, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                project.project_id,
                project.name,
                project.video_file,
                project.created_at,
                project.last_modified,
                project.local_version,
                project.server_version,
                project.sync_status,
                json.dumps({'operations_count': len(project.operations)})
            ))
            
            # Save operations
            for operation in project.operations:
                cursor.execute('''
                    INSERT OR REPLACE INTO operations
                    (operation_id, project_id, session_id, user_id, operation_type,
                     timestamp, data, local_version, sync_status, conflict_resolution, checksum)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    operation.operation_id,
                    project.project_id,
                    operation.session_id,
                    operation.user_id,
                    operation.operation_type,
                    operation.timestamp,
                    json.dumps(operation.data),
                    operation.local_version,
                    operation.sync_status,
                    operation.conflict_resolution,
                    operation.checksum
                ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error saving project: {e}")
            return False
    
    def load_project(self, project_id: str) -> Optional[OfflineProject]:
        """Load project from offline storage"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Load project
            cursor.execute('''
                SELECT project_id, name, video_file, created_at, last_modified,
                       local_version, server_version, sync_status
                FROM projects WHERE project_id = ?
            ''', (project_id,))
            
            project_row = cursor.fetchone()
            if not project_row:
                conn.close()
                return None
            
            # Load operations
            cursor.execute('''
                SELECT operation_id, session_id, user_id, operation_type, timestamp,
                       data, local_version, sync_status, conflict_resolution, checksum
                FROM operations WHERE project_id = ?
                ORDER BY timestamp ASC
            ''', (project_id,))
            
            operations = []
            for op_row in cursor.fetchall():
                operation = OfflineOperation(
                    operation_id=op_row[0],
                    session_id=op_row[1],
                    user_id=op_row[2],
                    operation_type=op_row[3],
                    timestamp=op_row[4],
                    data=json.loads(op_row[5]),
                    local_version=op_row[6],
                    sync_status=op_row[7],
                    conflict_resolution=op_row[8],
                    checksum=op_row[9]
                )
                operations.append(operation)
            
            project = OfflineProject(
                project_id=project_row[0],
                name=project_row[1],
                video_file=project_row[2],
                created_at=project_row[3],
                last_modified=project_row[4],
                operations=operations,
                local_version=project_row[5],
                server_version=project_row[6],
                sync_status=project_row[7]
            )
            
            conn.close()
            return project
            
        except Exception as e:
            print(f"Error loading project: {e}")
            return None
    
    def list_projects(self) -> List[Dict]:
        """List all offline projects"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT project_id, name, video_file, created_at, last_modified,
                       local_version, server_version, sync_status
                FROM projects ORDER BY last_modified DESC
            ''')
            
            projects = []
            for row in cursor.fetchall():
                projects.append({
                    'project_id': row[0],
                    'name': row[1],
                    'video_file': row[2],
                    'created_at': row[3],
                    'last_modified': row[4],
                    'local_version': row[5],
                    'server_version': row[6],
                    'sync_status': row[7]
                })
            
            conn.close()
            return projects
            
        except Exception as e:
            print(f"Error listing projects: {e}")
            return []
    
    def add_to_sync_queue(self, project_id: str, operation_id: str = None, 
                         action: str = 'sync', priority: int = 0) -> bool:
        """Add item to sync queue"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO sync_queue 
                (project_id, operation_id, action, priority, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (project_id, operation_id, action, priority, time.time()))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error adding to sync queue: {e}")
            return False
    
    def get_sync_queue(self, limit: int = 10) -> List[Dict]:
        """Get items from sync queue"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, project_id, operation_id, action, priority, 
                       created_at, attempts, last_attempt, error_message
                FROM sync_queue 
                ORDER BY priority DESC, created_at ASC
                LIMIT ?
            ''', (limit,))
            
            items = []
            for row in cursor.fetchall():
                items.append({
                    'id': row[0],
                    'project_id': row[1],
                    'operation_id': row[2],
                    'action': row[3],
                    'priority': row[4],
                    'created_at': row[5],
                    'attempts': row[6],
                    'last_attempt': row[7],
                    'error_message': row[8]
                })
            
            conn.close()
            return items
            
        except Exception as e:
            print(f"Error getting sync queue: {e}")
            return []
    
    def remove_from_sync_queue(self, queue_id: int) -> bool:
        """Remove item from sync queue"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM sync_queue WHERE id = ?', (queue_id,))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error removing from sync queue: {e}")
            return False


class OfflineSyncManager:
    """Manages synchronization between offline and online state"""
    
    def __init__(self):
        self.storage_manager = OfflineStorageManager()
        self.sync_in_progress = False
        self.conflict_resolver = self._get_conflict_resolver()
    
    def _get_conflict_resolver(self):
        """Get conflict resolution strategy"""
        strategy = edge_config.conflict_resolution_strategy
        
        if strategy == 'last_writer_wins':
            return self._resolve_last_writer_wins
        elif strategy == 'manual_resolution':
            return self._mark_for_manual_resolution
        else:
            return self._resolve_last_writer_wins
    
    async def create_offline_project(self, name: str, video_file: str, user_id: str) -> OfflineProject:
        """Create a new offline project"""
        project_id = str(uuid.uuid4())
        
        project = OfflineProject(
            project_id=project_id,
            name=name,
            video_file=video_file,
            created_at=time.time(),
            last_modified=time.time(),
            operations=[],
            local_version=0,
            server_version=0,
            sync_status='offline'
        )
        
        self.storage_manager.save_project(project)
        return project
    
    async def add_offline_operation(self, project_id: str, operation_type: str,
                                  user_id: str, data: Dict[str, Any]) -> bool:
        """Add an operation to offline project"""
        project = self.storage_manager.load_project(project_id)
        if not project:
            return False
        
        operation_id = str(uuid.uuid4())
        
        # Calculate checksum for conflict detection
        operation_data = {
            'operation_type': operation_type,
            'timestamp': time.time(),
            'data': data
        }
        checksum = hashlib.md5(json.dumps(operation_data, sort_keys=True).encode()).hexdigest()
        
        operation = OfflineOperation(
            operation_id=operation_id,
            session_id=project_id,  # Use project_id as session_id for offline
            user_id=user_id,
            operation_type=operation_type,
            timestamp=time.time(),
            data=data,
            local_version=project.local_version + 1,
            sync_status='pending',
            checksum=checksum
        )
        
        project.operations.append(operation)
        project.local_version += 1
        project.last_modified = time.time()
        
        # Save project
        success = self.storage_manager.save_project(project)
        
        if success:
            # Add to sync queue
            self.storage_manager.add_to_sync_queue(project_id, operation_id, 'sync_operation')
        
        return success
    
    async def sync_with_server(self, server_url: str = None) -> Dict[str, Any]:
        """Synchronize offline projects with server"""
        if self.sync_in_progress:
            return {'success': False, 'error': 'Sync already in progress'}
        
        self.sync_in_progress = True
        sync_results = {
            'projects_synced': 0,
            'operations_synced': 0,
            'conflicts_resolved': 0,
            'errors': []
        }
        
        try:
            # Get sync queue
            sync_queue = self.storage_manager.get_sync_queue(50)
            
            for queue_item in sync_queue:
                try:
                    project_id = queue_item['project_id']
                    
                    if queue_item['action'] == 'sync_operation':
                        success = await self._sync_operation(project_id, queue_item['operation_id'])
                        if success:
                            sync_results['operations_synced'] += 1
                            self.storage_manager.remove_from_sync_queue(queue_item['id'])
                    elif queue_item['action'] == 'sync_project':
                        success = await self._sync_project(project_id)
                        if success:
                            sync_results['projects_synced'] += 1
                            self.storage_manager.remove_from_sync_queue(queue_item['id'])
                
                except Exception as e:
                    sync_results['errors'].append(f"Error syncing {queue_item}: {str(e)}")
            
            return {'success': True, 'results': sync_results}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
        finally:
            self.sync_in_progress = False
    
    async def _sync_operation(self, project_id: str, operation_id: str) -> bool:
        """Sync a single operation with server"""
        # In a real implementation, this would:
        # 1. Send operation to server
        # 2. Handle conflicts if they occur
        # 3. Update local operation status
        
        # For now, simulate sync
        project = self.storage_manager.load_project(project_id)
        if not project:
            return False
        
        # Find operation
        operation = next((op for op in project.operations if op.operation_id == operation_id), None)
        if not operation:
            return False
        
        # Simulate server communication
        await asyncio.sleep(0.1)
        
        # Mark as synced
        operation.sync_status = 'synced'
        self.storage_manager.save_project(project)
        
        return True
    
    async def _sync_project(self, project_id: str) -> bool:
        """Sync entire project with server"""
        project = self.storage_manager.load_project(project_id)
        if not project:
            return False
        
        # Simulate project sync
        await asyncio.sleep(0.2)
        
        project.sync_status = 'synced'
        project.server_version = project.local_version
        
        self.storage_manager.save_project(project)
        return True
    
    def _resolve_last_writer_wins(self, local_op: OfflineOperation, server_op: Dict) -> OfflineOperation:
        """Resolve conflict using last writer wins strategy"""
        local_timestamp = local_op.timestamp
        server_timestamp = server_op.get('timestamp', 0)
        
        if local_timestamp > server_timestamp:
            local_op.sync_status = 'synced'
            return local_op
        else:
            # Server operation wins, mark local as conflicted
            local_op.sync_status = 'conflict'
            local_op.conflict_resolution = 'server_wins'
            return local_op
    
    def _mark_for_manual_resolution(self, local_op: OfflineOperation, server_op: Dict) -> OfflineOperation:
        """Mark operation for manual conflict resolution"""
        local_op.sync_status = 'conflict'
        local_op.conflict_resolution = 'manual_required'
        local_op.data['conflict_info'] = {
            'server_operation': server_op,
            'conflict_detected_at': time.time()
        }
        return local_op
    
    def get_offline_projects(self) -> List[Dict]:
        """Get list of offline projects"""
        return self.storage_manager.list_projects()
    
    def get_project_status(self, project_id: str) -> Optional[Dict]:
        """Get project sync status"""
        project = self.storage_manager.load_project(project_id)
        if not project:
            return None
        
        pending_operations = len([op for op in project.operations if op.sync_status == 'pending'])
        conflicted_operations = len([op for op in project.operations if op.sync_status == 'conflict'])
        
        return {
            'project_id': project.project_id,
            'name': project.name,
            'sync_status': project.sync_status,
            'local_version': project.local_version,
            'server_version': project.server_version,
            'total_operations': len(project.operations),
            'pending_operations': pending_operations,
            'conflicted_operations': conflicted_operations,
            'last_modified': project.last_modified
        }


# Global offline sync manager
offline_sync_manager = OfflineSyncManager()