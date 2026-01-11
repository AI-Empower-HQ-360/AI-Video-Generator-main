"""
Role-Based Access Control (RBAC) with Granular Permissions
Enterprise-grade permission management system
"""

from typing import Dict, List, Set, Optional, Callable
from functools import wraps
from flask import session, jsonify, g
from dataclasses import dataclass
from enum import Enum
import json


class PermissionLevel(Enum):
    """Permission levels for granular access control"""
    NONE = 0
    READ = 1
    WRITE = 2
    DELETE = 3
    ADMIN = 4


@dataclass
class Permission:
    """Individual permission definition"""
    resource: str
    action: str
    level: PermissionLevel
    conditions: Optional[Dict] = None


@dataclass
class Role:
    """Role definition with permissions"""
    name: str
    description: str
    permissions: List[Permission]
    inherits_from: Optional[List[str]] = None


class RoleBasedAccessControl:
    """Main RBAC system for managing roles and permissions"""
    
    def __init__(self):
        self.roles = {}
        self.user_roles = {}
        self.resource_permissions = {}
        self._initialize_default_roles()
    
    def _initialize_default_roles(self):
        """Initialize default enterprise roles"""
        
        # Super Admin role
        super_admin = Role(
            name="super_admin",
            description="Full system administration access",
            permissions=[
                Permission("*", "*", PermissionLevel.ADMIN),
            ]
        )
        
        # Content Admin role
        content_admin = Role(
            name="content_admin",
            description="Content management and user administration",
            permissions=[
                Permission("videos", "create", PermissionLevel.WRITE),
                Permission("videos", "read", PermissionLevel.READ),
                Permission("videos", "update", PermissionLevel.WRITE),
                Permission("videos", "delete", PermissionLevel.DELETE),
                Permission("slokas", "*", PermissionLevel.ADMIN),
                Permission("users", "read", PermissionLevel.READ),
                Permission("users", "update", PermissionLevel.WRITE),
                Permission("analytics", "read", PermissionLevel.READ),
            ]
        )
        
        # Content Creator role
        content_creator = Role(
            name="content_creator",
            description="Create and manage own content",
            permissions=[
                Permission("videos", "create", PermissionLevel.WRITE),
                Permission("videos", "read", PermissionLevel.READ, {"owner_only": True}),
                Permission("videos", "update", PermissionLevel.WRITE, {"owner_only": True}),
                Permission("slokas", "read", PermissionLevel.READ),
                Permission("ai_gurus", "use", PermissionLevel.WRITE),
                Permission("whisper", "use", PermissionLevel.WRITE),
            ]
        )
        
        # Content Reviewer role
        content_reviewer = Role(
            name="content_reviewer",
            description="Review and approve content",
            permissions=[
                Permission("videos", "read", PermissionLevel.READ),
                Permission("videos", "review", PermissionLevel.WRITE),
                Permission("videos", "approve", PermissionLevel.WRITE),
                Permission("videos", "reject", PermissionLevel.WRITE),
                Permission("slokas", "read", PermissionLevel.READ),
                Permission("analytics", "read", PermissionLevel.READ),
            ]
        )
        
        # Viewer role
        viewer = Role(
            name="viewer",
            description="View published content only",
            permissions=[
                Permission("videos", "read", PermissionLevel.READ, {"published_only": True}),
                Permission("slokas", "read", PermissionLevel.READ),
            ]
        )
        
        # IT Admin role
        it_admin = Role(
            name="it_admin",
            description="System administration and security",
            permissions=[
                Permission("system", "*", PermissionLevel.ADMIN),
                Permission("users", "*", PermissionLevel.ADMIN),
                Permission("security", "*", PermissionLevel.ADMIN),
                Permission("audit_logs", "read", PermissionLevel.READ),
                Permission("backups", "*", PermissionLevel.ADMIN),
            ]
        )
        
        # Manager role
        manager = Role(
            name="manager",
            description="Team management and analytics access",
            permissions=[
                Permission("videos", "read", PermissionLevel.READ),
                Permission("analytics", "read", PermissionLevel.READ),
                Permission("reports", "generate", PermissionLevel.WRITE),
                Permission("users", "read", PermissionLevel.READ, {"department_only": True}),
                Permission("workflows", "manage", PermissionLevel.WRITE),
            ]
        )
        
        # Register all roles
        for role in [super_admin, content_admin, content_creator, content_reviewer, viewer, it_admin, manager]:
            self.add_role(role)
    
    def add_role(self, role: Role) -> bool:
        """Add a new role to the system"""
        try:
            self.roles[role.name] = role
            return True
        except Exception as e:
            print(f"Error adding role {role.name}: {e}")
            return False
    
    def assign_role_to_user(self, user_id: str, role_name: str) -> bool:
        """Assign a role to a user"""
        if role_name not in self.roles:
            return False
        
        if user_id not in self.user_roles:
            self.user_roles[user_id] = set()
        
        self.user_roles[user_id].add(role_name)
        return True
    
    def remove_role_from_user(self, user_id: str, role_name: str) -> bool:
        """Remove a role from a user"""
        if user_id in self.user_roles and role_name in self.user_roles[user_id]:
            self.user_roles[user_id].remove(role_name)
            return True
        return False
    
    def get_user_roles(self, user_id: str) -> List[str]:
        """Get all roles assigned to a user"""
        return list(self.user_roles.get(user_id, set()))
    
    def get_user_permissions(self, user_id: str) -> List[Permission]:
        """Get all permissions for a user (including inherited)"""
        user_roles = self.get_user_roles(user_id)
        permissions = []
        
        for role_name in user_roles:
            role = self.roles.get(role_name)
            if role:
                permissions.extend(role.permissions)
                
                # Handle role inheritance
                if role.inherits_from:
                    for parent_role_name in role.inherits_from:
                        parent_role = self.roles.get(parent_role_name)
                        if parent_role:
                            permissions.extend(parent_role.permissions)
        
        return permissions
    
    def check_permission(self, user_id: str, resource: str, action: str, context: Optional[Dict] = None) -> bool:
        """Check if user has permission for specific resource and action"""
        permissions = self.get_user_permissions(user_id)
        
        for permission in permissions:
            # Check for wildcard permissions
            if permission.resource == "*" or permission.action == "*":
                if self._check_permission_conditions(permission, context):
                    return True
            
            # Check for exact match
            if permission.resource == resource and permission.action == action:
                if self._check_permission_conditions(permission, context):
                    return True
        
        return False
    
    def _check_permission_conditions(self, permission: Permission, context: Optional[Dict] = None) -> bool:
        """Check if permission conditions are met"""
        if not permission.conditions or not context:
            return True
        
        # Check owner_only condition
        if permission.conditions.get("owner_only"):
            return context.get("owner_id") == context.get("user_id")
        
        # Check published_only condition
        if permission.conditions.get("published_only"):
            return context.get("status") == "published"
        
        # Check department_only condition
        if permission.conditions.get("department_only"):
            return context.get("user_department") == context.get("target_department")
        
        return True
    
    def get_accessible_resources(self, user_id: str, resource_type: str) -> List[str]:
        """Get list of resources user can access"""
        permissions = self.get_user_permissions(user_id)
        accessible_resources = []
        
        for permission in permissions:
            if permission.resource == resource_type or permission.resource == "*":
                if permission.level.value >= PermissionLevel.READ.value:
                    accessible_resources.append(permission.resource)
        
        return list(set(accessible_resources))
    
    def require_permission(self, resource: str, action: str, context_provider: Optional[Callable] = None):
        """Decorator to require specific permission for endpoint access"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                # Get current user from session
                user_session = session.get('user_session')
                if not user_session:
                    return jsonify({'error': 'Authentication required'}), 401
                
                user_id = user_session.get('user_id')
                if not user_id:
                    return jsonify({'error': 'Invalid session'}), 401
                
                # Get context if provider is given
                context = {}
                if context_provider:
                    context = context_provider(*args, **kwargs)
                
                # Check permission
                if not self.check_permission(user_id, resource, action, context):
                    return jsonify({'error': 'Insufficient permissions'}), 403
                
                # Store user info in g for use in the function
                g.current_user = user_session
                
                return f(*args, **kwargs)
            return decorated_function
        return decorator
    
    def require_role(self, required_roles: List[str]):
        """Decorator to require specific roles for endpoint access"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                user_session = session.get('user_session')
                if not user_session:
                    return jsonify({'error': 'Authentication required'}), 401
                
                user_id = user_session.get('user_id')
                if not user_id:
                    return jsonify({'error': 'Invalid session'}), 401
                
                user_roles = self.get_user_roles(user_id)
                if not any(role in user_roles for role in required_roles):
                    return jsonify({'error': 'Insufficient role permissions'}), 403
                
                g.current_user = user_session
                return f(*args, **kwargs)
            return decorated_function
        return decorator
    
    def get_role_hierarchy(self) -> Dict:
        """Get the complete role hierarchy for management"""
        hierarchy = {}
        for role_name, role in self.roles.items():
            hierarchy[role_name] = {
                'description': role.description,
                'permissions_count': len(role.permissions),
                'inherits_from': role.inherits_from or [],
                'permissions': [
                    {
                        'resource': p.resource,
                        'action': p.action,
                        'level': p.level.name,
                        'conditions': p.conditions
                    }
                    for p in role.permissions
                ]
            }
        return hierarchy
    
    def assign_roles_from_groups(self, user_id: str, groups: List[str]) -> bool:
        """Assign roles based on AD/SSO groups"""
        group_role_mapping = {
            'Domain Admins': 'super_admin',
            'IT Admin': 'it_admin',
            'Content Admin': 'content_admin',
            'Content Creator': 'content_creator',
            'Content Reviewer': 'content_reviewer',
            'Managers': 'manager',
            'Domain Users': 'viewer'
        }
        
        assigned_roles = []
        for group in groups:
            role = group_role_mapping.get(group)
            if role:
                self.assign_role_to_user(user_id, role)
                assigned_roles.append(role)
        
        return len(assigned_roles) > 0
    
    def export_permissions(self) -> str:
        """Export current permissions configuration as JSON"""
        export_data = {
            'roles': {},
            'user_roles': dict(self.user_roles)
        }
        
        for role_name, role in self.roles.items():
            export_data['roles'][role_name] = {
                'name': role.name,
                'description': role.description,
                'inherits_from': role.inherits_from,
                'permissions': [
                    {
                        'resource': p.resource,
                        'action': p.action,
                        'level': p.level.value,
                        'conditions': p.conditions
                    }
                    for p in role.permissions
                ]
            }
        
        return json.dumps(export_data, indent=2)
    
    def import_permissions(self, json_data: str) -> bool:
        """Import permissions configuration from JSON"""
        try:
            data = json.loads(json_data)
            
            # Clear current configuration
            self.roles.clear()
            self.user_roles.clear()
            
            # Import roles
            for role_name, role_data in data.get('roles', {}).items():
                permissions = []
                for perm_data in role_data.get('permissions', []):
                    permission = Permission(
                        resource=perm_data['resource'],
                        action=perm_data['action'],
                        level=PermissionLevel(perm_data['level']),
                        conditions=perm_data.get('conditions')
                    )
                    permissions.append(permission)
                
                role = Role(
                    name=role_data['name'],
                    description=role_data['description'],
                    permissions=permissions,
                    inherits_from=role_data.get('inherits_from')
                )
                self.add_role(role)
            
            # Import user roles
            for user_id, roles in data.get('user_roles', {}).items():
                self.user_roles[user_id] = set(roles)
            
            return True
        except Exception as e:
            print(f"Error importing permissions: {e}")
            return False