try:
    from flask_sqlalchemy import SQLAlchemy
except ImportError:
    raise ImportError(
        "The 'flask_sqlalchemy' package is required. "
        "Install it with 'pip install flask_sqlalchemy'."
    )

from datetime import datetime
import uuid
import json

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(120), unique=True, nullable=True)
    name = db.Column(db.String(100), nullable=True)
    spiritual_level = db.Column(db.String(50), default='beginner')
    preferred_gurus = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_active = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    sessions = db.relationship('SpiritualSession', backref='user', lazy=True)
    user_sessions = db.relationship('UserSession', backref='user', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'spiritual_level': self.spiritual_level,
            'preferred_gurus': self.preferred_gurus,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class SpiritualSession(db.Model):
    __tablename__ = 'spiritual_sessions'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    guru_type = db.Column(db.String(50), nullable=False)
    question = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=False)
    satisfaction_rating = db.Column(db.Integer)
    session_duration = db.Column(db.Integer)  # in seconds
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'guru_type': self.guru_type,
            'question': self.question,
            'response': self.response,
            'satisfaction_rating': self.satisfaction_rating,
            'created_at': self.created_at.isoformat()
        }

class DailyWisdom(db.Model):
    __tablename__ = 'daily_wisdom'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    date = db.Column(db.Date, unique=True, nullable=False)
    sloka_sanskrit = db.Column(db.Text)
    sloka_translation = db.Column(db.Text)
    wisdom_message = db.Column(db.Text)
    guru_type = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.isoformat(),
            'sloka_sanskrit': self.sloka_sanskrit,
            'sloka_translation': self.sloka_translation,
            'wisdom_message': self.wisdom_message,
            'guru_type': self.guru_type
        }

class UserSession(db.Model):
    __tablename__ = 'user_sessions'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    session_type = db.Column(db.String(50), nullable=False, default='meditation')
    status = db.Column(db.String(20), nullable=False, default='active')  # active, completed, cancelled
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    duration = db.Column(db.Integer)  # in seconds
    notes = db.Column(db.Text)
    reflection = db.Column(db.Text)
    real_life_application = db.Column(db.Text)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'session_type': self.session_type,
            'status': self.status,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration': self.duration,
            'notes': self.notes,
            'reflection': self.reflection,
            'real_life_application': self.real_life_application
        }


# =============================================================================
# WORKFLOW AUTOMATION MODELS
# =============================================================================

class Workflow(db.Model):
    """
    Core workflow model for defining automated processes
    """
    __tablename__ = 'workflows'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))  # content_creation, approval, localization, etc.
    status = db.Column(db.String(20), default='draft')  # draft, active, inactive, deprecated
    is_template = db.Column(db.Boolean, default=False)
    template_category = db.Column(db.String(50))  # if is_template=True
    
    # Workflow configuration
    trigger_type = db.Column(db.String(50))  # manual, scheduled, event_based
    trigger_config = db.Column(db.JSON)  # configuration for triggers
    
    # Metadata
    created_by = db.Column(db.String(36), db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    version = db.Column(db.Integer, default=1)
    
    # Community features for template marketplace
    is_public = db.Column(db.Boolean, default=False)
    downloads_count = db.Column(db.Integer, default=0)
    rating_average = db.Column(db.Float, default=0.0)
    rating_count = db.Column(db.Integer, default=0)
    
    # Relationships
    nodes = db.relationship('WorkflowNode', backref='workflow', lazy=True, cascade='all, delete-orphan')
    executions = db.relationship('WorkflowExecution', backref='workflow', lazy=True)
    ratings = db.relationship('WorkflowRating', backref='workflow', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'status': self.status,
            'is_template': self.is_template,
            'template_category': self.template_category,
            'trigger_type': self.trigger_type,
            'trigger_config': self.trigger_config,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'version': self.version,
            'is_public': self.is_public,
            'downloads_count': self.downloads_count,
            'rating_average': self.rating_average,
            'rating_count': self.rating_count,
            'nodes': [node.to_dict() for node in self.nodes]
        }


class WorkflowNode(db.Model):
    """
    Individual nodes/steps in a workflow
    """
    __tablename__ = 'workflow_nodes'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_id = db.Column(db.String(36), db.ForeignKey('workflows.id'), nullable=False)
    
    # Node properties
    node_type = db.Column(db.String(50), nullable=False)  # start, action, condition, approval, end
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # Position in workflow builder UI
    position_x = db.Column(db.Float, default=0)
    position_y = db.Column(db.Float, default=0)
    
    # Node configuration
    config = db.Column(db.JSON)  # Node-specific configuration
    
    # Conditional logic
    condition_expression = db.Column(db.Text)  # For condition nodes
    
    # Action configuration
    action_type = db.Column(db.String(50))  # api_call, content_generation, approval_request, etc.
    action_config = db.Column(db.JSON)  # Action-specific configuration
    
    # Approval configuration (for approval nodes)
    approval_required_from = db.Column(db.JSON)  # List of user IDs or roles
    approval_timeout_hours = db.Column(db.Integer, default=24)
    
    # Localization settings
    localization_enabled = db.Column(db.Boolean, default=False)
    target_languages = db.Column(db.JSON)  # List of language codes
    
    # Relationships
    connections_from = db.relationship('WorkflowConnection', 
                                     foreign_keys='WorkflowConnection.from_node_id',
                                     backref='from_node', lazy=True)
    connections_to = db.relationship('WorkflowConnection',
                                   foreign_keys='WorkflowConnection.to_node_id', 
                                   backref='to_node', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'workflow_id': self.workflow_id,
            'node_type': self.node_type,
            'name': self.name,
            'description': self.description,
            'position_x': self.position_x,
            'position_y': self.position_y,
            'config': self.config,
            'condition_expression': self.condition_expression,
            'action_type': self.action_type,
            'action_config': self.action_config,
            'approval_required_from': self.approval_required_from,
            'approval_timeout_hours': self.approval_timeout_hours,
            'localization_enabled': self.localization_enabled,
            'target_languages': self.target_languages
        }


class WorkflowConnection(db.Model):
    """
    Connections between workflow nodes
    """
    __tablename__ = 'workflow_connections'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_id = db.Column(db.String(36), db.ForeignKey('workflows.id'), nullable=False)
    from_node_id = db.Column(db.String(36), db.ForeignKey('workflow_nodes.id'), nullable=False)
    to_node_id = db.Column(db.String(36), db.ForeignKey('workflow_nodes.id'), nullable=False)
    
    # Connection properties
    condition = db.Column(db.String(100))  # e.g., 'success', 'failure', 'approved', 'rejected'
    condition_value = db.Column(db.String(200))  # Value to match for conditional connections
    
    def to_dict(self):
        return {
            'id': self.id,
            'workflow_id': self.workflow_id,
            'from_node_id': self.from_node_id,
            'to_node_id': self.to_node_id,
            'condition': self.condition,
            'condition_value': self.condition_value
        }


class WorkflowExecution(db.Model):
    """
    Tracks workflow execution instances
    """
    __tablename__ = 'workflow_executions'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_id = db.Column(db.String(36), db.ForeignKey('workflows.id'), nullable=False)
    
    # Execution properties
    status = db.Column(db.String(20), default='running')  # running, completed, failed, cancelled
    triggered_by = db.Column(db.String(36), db.ForeignKey('users.id'))
    trigger_type = db.Column(db.String(50))  # manual, scheduled, event
    
    # Execution context
    input_data = db.Column(db.JSON)  # Input data for the workflow
    current_node_id = db.Column(db.String(36), db.ForeignKey('workflow_nodes.id'))
    context_data = db.Column(db.JSON)  # Runtime context data
    
    # Timing
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    # Results
    output_data = db.Column(db.JSON)
    error_message = db.Column(db.Text)
    
    # Relationships
    execution_logs = db.relationship('WorkflowExecutionLog', backref='execution', lazy=True)
    approvals = db.relationship('WorkflowApproval', backref='execution', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'workflow_id': self.workflow_id,
            'status': self.status,
            'triggered_by': self.triggered_by,
            'trigger_type': self.trigger_type,
            'input_data': self.input_data,
            'current_node_id': self.current_node_id,
            'context_data': self.context_data,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'output_data': self.output_data,
            'error_message': self.error_message
        }


class WorkflowExecutionLog(db.Model):
    """
    Detailed logs for workflow execution steps
    """
    __tablename__ = 'workflow_execution_logs'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    execution_id = db.Column(db.String(36), db.ForeignKey('workflow_executions.id'), nullable=False)
    node_id = db.Column(db.String(36), db.ForeignKey('workflow_nodes.id'))
    
    # Log properties
    level = db.Column(db.String(20), default='info')  # debug, info, warning, error
    message = db.Column(db.Text, nullable=False)
    details = db.Column(db.JSON)  # Additional structured data
    
    # Timing
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'execution_id': self.execution_id,
            'node_id': self.node_id,
            'level': self.level,
            'message': self.message,
            'details': self.details,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }


class WorkflowApproval(db.Model):
    """
    Approval requests and responses for workflow steps
    """
    __tablename__ = 'workflow_approvals'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    execution_id = db.Column(db.String(36), db.ForeignKey('workflow_executions.id'), nullable=False)
    node_id = db.Column(db.String(36), db.ForeignKey('workflow_nodes.id'), nullable=False)
    
    # Approval properties
    required_from = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected, expired
    
    # Request details
    subject = db.Column(db.String(200))
    content = db.Column(db.Text)
    approval_data = db.Column(db.JSON)  # Content to be approved
    
    # Response details
    approved_by = db.Column(db.String(36), db.ForeignKey('users.id'))
    response_message = db.Column(db.Text)
    
    # Timing
    requested_at = db.Column(db.DateTime, default=datetime.utcnow)
    responded_at = db.Column(db.DateTime)
    expires_at = db.Column(db.DateTime)
    
    def to_dict(self):
        return {
            'id': self.id,
            'execution_id': self.execution_id,
            'node_id': self.node_id,
            'required_from': self.required_from,
            'status': self.status,
            'subject': self.subject,
            'content': self.content,
            'approval_data': self.approval_data,
            'approved_by': self.approved_by,
            'response_message': self.response_message,
            'requested_at': self.requested_at.isoformat() if self.requested_at else None,
            'responded_at': self.responded_at.isoformat() if self.responded_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }


class WorkflowSchedule(db.Model):
    """
    Scheduled workflow executions
    """
    __tablename__ = 'workflow_schedules'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_id = db.Column(db.String(36), db.ForeignKey('workflows.id'), nullable=False)
    
    # Schedule properties
    name = db.Column(db.String(200))
    cron_expression = db.Column(db.String(100))  # Cron-style schedule
    timezone = db.Column(db.String(50), default='UTC')
    
    # Schedule status
    is_active = db.Column(db.Boolean, default=True)
    next_run_at = db.Column(db.DateTime)
    last_run_at = db.Column(db.DateTime)
    last_run_status = db.Column(db.String(20))  # success, failed
    
    # Schedule configuration
    input_data = db.Column(db.JSON)  # Default input data for scheduled runs
    max_runs = db.Column(db.Integer)  # Maximum number of runs (null = unlimited)
    run_count = db.Column(db.Integer, default=0)
    
    # Metadata
    created_by = db.Column(db.String(36), db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'workflow_id': self.workflow_id,
            'name': self.name,
            'cron_expression': self.cron_expression,
            'timezone': self.timezone,
            'is_active': self.is_active,
            'next_run_at': self.next_run_at.isoformat() if self.next_run_at else None,
            'last_run_at': self.last_run_at.isoformat() if self.last_run_at else None,
            'last_run_status': self.last_run_status,
            'input_data': self.input_data,
            'max_runs': self.max_runs,
            'run_count': self.run_count,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class WorkflowRating(db.Model):
    """
    Community ratings for workflow templates
    """
    __tablename__ = 'workflow_ratings'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_id = db.Column(db.String(36), db.ForeignKey('workflows.id'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    
    # Rating details
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    review = db.Column(db.Text)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Unique constraint
    __table_args__ = (db.UniqueConstraint('workflow_id', 'user_id', name='unique_user_workflow_rating'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'workflow_id': self.workflow_id,
            'user_id': self.user_id,
            'rating': self.rating,
            'review': self.review,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
