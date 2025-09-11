"""
Workflow API Endpoints
=====================

RESTful API endpoints for workflow management, execution, and template marketplace.
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import uuid

from models.database import (
    db, Workflow, WorkflowNode, WorkflowConnection, WorkflowExecution,
    WorkflowSchedule, WorkflowRating, User
)
from services.workflow_engine import WorkflowExecutionEngine, WorkflowTemplateService

# Create Blueprint
workflow_bp = Blueprint('workflows', __name__, url_prefix='/api/workflows')

# Initialize workflow engine
workflow_engine = WorkflowExecutionEngine()
template_service = WorkflowTemplateService()


# =============================================================================
# WORKFLOW CRUD OPERATIONS
# =============================================================================

@workflow_bp.route('/', methods=['GET'])
def list_workflows():
    """List workflows with filtering and pagination"""
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        category = request.args.get('category')
        status = request.args.get('status')
        is_template = request.args.get('is_template', type=bool)
        created_by = request.args.get('created_by')
        
        # Build query
        query = Workflow.query
        
        if category:
            query = query.filter(Workflow.category == category)
        if status:
            query = query.filter(Workflow.status == status)
        if is_template is not None:
            query = query.filter(Workflow.is_template == is_template)
        if created_by:
            query = query.filter(Workflow.created_by == created_by)
        
        # Order by creation date (newest first)
        query = query.order_by(Workflow.created_at.desc())
        
        # Paginate
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        workflows = [workflow.to_dict() for workflow in pagination.items]
        
        return jsonify({
            'success': True,
            'workflows': workflows,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@workflow_bp.route('/', methods=['POST'])
def create_workflow():
    """Create a new workflow"""
    try:
        data = request.get_json()
        
        if not data or not data.get('name'):
            return jsonify({'success': False, 'error': 'Name is required'}), 400
        
        # Create workflow
        workflow = Workflow(
            name=data['name'],
            description=data.get('description'),
            category=data.get('category'),
            status=data.get('status', 'draft'),
            is_template=data.get('is_template', False),
            template_category=data.get('template_category'),
            trigger_type=data.get('trigger_type', 'manual'),
            trigger_config=data.get('trigger_config'),
            created_by=data.get('created_by'),
            is_public=data.get('is_public', False)
        )
        
        db.session.add(workflow)
        db.session.flush()  # Get the ID
        
        # Create nodes if provided
        nodes_data = data.get('nodes', [])
        node_id_mapping = {}  # Map position indices to actual IDs
        
        for i, node_data in enumerate(nodes_data):
            node = WorkflowNode(
                workflow_id=workflow.id,
                node_type=node_data['node_type'],
                name=node_data['name'],
                description=node_data.get('description'),
                position_x=node_data.get('position_x', 0),
                position_y=node_data.get('position_y', 0),
                config=node_data.get('config'),
                condition_expression=node_data.get('condition_expression'),
                action_type=node_data.get('action_type'),
                action_config=node_data.get('action_config'),
                approval_required_from=node_data.get('approval_required_from'),
                approval_timeout_hours=node_data.get('approval_timeout_hours', 24),
                localization_enabled=node_data.get('localization_enabled', False),
                target_languages=node_data.get('target_languages')
            )
            
            db.session.add(node)
            db.session.flush()
            node_id_mapping[i] = node.id
        
        # Create connections if provided
        connections_data = data.get('connections', [])
        for conn_data in connections_data:
            from_node_idx = conn_data.get('from_node')
            to_node_idx = conn_data.get('to_node')
            
            if from_node_idx is not None and to_node_idx is not None:
                connection = WorkflowConnection(
                    workflow_id=workflow.id,
                    from_node_id=node_id_mapping[from_node_idx],
                    to_node_id=node_id_mapping[to_node_idx],
                    condition=conn_data.get('condition'),
                    condition_value=conn_data.get('condition_value')
                )
                db.session.add(connection)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'workflow': workflow.to_dict(),
            'message': 'Workflow created successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@workflow_bp.route('/<workflow_id>', methods=['GET'])
def get_workflow(workflow_id):
    """Get a specific workflow with all its nodes and connections"""
    try:
        workflow = Workflow.query.get(workflow_id)
        if not workflow:
            return jsonify({'success': False, 'error': 'Workflow not found'}), 404
        
        # Get connections for this workflow
        connections = WorkflowConnection.query.filter_by(workflow_id=workflow_id).all()
        connections_data = [conn.to_dict() for conn in connections]
        
        workflow_data = workflow.to_dict()
        workflow_data['connections'] = connections_data
        
        return jsonify({
            'success': True,
            'workflow': workflow_data
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@workflow_bp.route('/<workflow_id>', methods=['PUT'])
def update_workflow(workflow_id):
    """Update a workflow"""
    try:
        workflow = Workflow.query.get(workflow_id)
        if not workflow:
            return jsonify({'success': False, 'error': 'Workflow not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        # Update workflow fields
        if 'name' in data:
            workflow.name = data['name']
        if 'description' in data:
            workflow.description = data['description']
        if 'category' in data:
            workflow.category = data['category']
        if 'status' in data:
            workflow.status = data['status']
        if 'trigger_type' in data:
            workflow.trigger_type = data['trigger_type']
        if 'trigger_config' in data:
            workflow.trigger_config = data['trigger_config']
        if 'is_public' in data:
            workflow.is_public = data['is_public']
        
        workflow.updated_at = datetime.utcnow()
        workflow.version += 1
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'workflow': workflow.to_dict(),
            'message': 'Workflow updated successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@workflow_bp.route('/<workflow_id>', methods=['DELETE'])
def delete_workflow(workflow_id):
    """Delete a workflow"""
    try:
        workflow = Workflow.query.get(workflow_id)
        if not workflow:
            return jsonify({'success': False, 'error': 'Workflow not found'}), 404
        
        # Check if workflow has active executions
        active_executions = WorkflowExecution.query.filter_by(
            workflow_id=workflow_id,
            status='running'
        ).count()
        
        if active_executions > 0:
            return jsonify({
                'success': False, 
                'error': 'Cannot delete workflow with active executions'
            }), 400
        
        db.session.delete(workflow)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Workflow deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


# =============================================================================
# WORKFLOW EXECUTION
# =============================================================================

@workflow_bp.route('/<workflow_id>/execute', methods=['POST'])
def execute_workflow(workflow_id):
    """Execute a workflow"""
    try:
        data = request.get_json() or {}
        
        # Get input data and user context
        input_data = data.get('input_data', {})
        user_id = data.get('user_id')
        trigger_type = data.get('trigger_type', 'manual')
        
        # Execute workflow asynchronously
        execution_id = workflow_engine.execute_workflow(
            workflow_id=workflow_id,
            input_data=input_data,
            user_id=user_id,
            trigger_type=trigger_type
        )
        
        return jsonify({
            'success': True,
            'execution_id': execution_id,
            'message': 'Workflow execution started'
        }), 202
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@workflow_bp.route('/executions/<execution_id>', methods=['GET'])
def get_execution_status(execution_id):
    """Get workflow execution status and details"""
    try:
        execution = WorkflowExecution.query.get(execution_id)
        if not execution:
            return jsonify({'success': False, 'error': 'Execution not found'}), 404
        
        # Get execution logs
        logs = execution.execution_logs
        logs_data = [log.to_dict() for log in logs]
        
        execution_data = execution.to_dict()
        execution_data['logs'] = logs_data
        
        return jsonify({
            'success': True,
            'execution': execution_data
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@workflow_bp.route('/executions', methods=['GET'])
def list_executions():
    """List workflow executions with filtering"""
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        workflow_id = request.args.get('workflow_id')
        status = request.args.get('status')
        triggered_by = request.args.get('triggered_by')
        
        # Build query
        query = WorkflowExecution.query
        
        if workflow_id:
            query = query.filter(WorkflowExecution.workflow_id == workflow_id)
        if status:
            query = query.filter(WorkflowExecution.status == status)
        if triggered_by:
            query = query.filter(WorkflowExecution.triggered_by == triggered_by)
        
        # Order by start time (newest first)
        query = query.order_by(WorkflowExecution.started_at.desc())
        
        # Paginate
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        executions = [execution.to_dict() for execution in pagination.items]
        
        return jsonify({
            'success': True,
            'executions': executions,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# =============================================================================
# TEMPLATE MARKETPLACE
# =============================================================================

@workflow_bp.route('/templates', methods=['GET'])
def list_templates():
    """List workflow templates in the marketplace"""
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        category = request.args.get('category')
        sort_by = request.args.get('sort_by', 'rating')  # rating, downloads, created_at
        
        # Build query for public templates
        query = Workflow.query.filter(
            Workflow.is_template == True,
            Workflow.is_public == True
        )
        
        if category:
            query = query.filter(Workflow.template_category == category)
        
        # Apply sorting
        if sort_by == 'rating':
            query = query.order_by(Workflow.rating_average.desc())
        elif sort_by == 'downloads':
            query = query.order_by(Workflow.downloads_count.desc())
        else:
            query = query.order_by(Workflow.created_at.desc())
        
        # Paginate
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        templates = [template.to_dict() for template in pagination.items]
        
        return jsonify({
            'success': True,
            'templates': templates,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@workflow_bp.route('/templates/<template_id>/download', methods=['POST'])
def download_template(template_id):
    """Download and create a workflow from a template"""
    try:
        template = Workflow.query.get(template_id)
        if not template or not template.is_template or not template.is_public:
            return jsonify({'success': False, 'error': 'Template not found'}), 404
        
        data = request.get_json() or {}
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'success': False, 'error': 'User ID is required'}), 400
        
        # Create new workflow from template
        new_workflow = Workflow(
            name=f"{template.name} - Copy",
            description=template.description,
            category=template.category,
            status='draft',
            is_template=False,
            trigger_type=template.trigger_type,
            trigger_config=template.trigger_config,
            created_by=user_id,
            is_public=False
        )
        
        db.session.add(new_workflow)
        db.session.flush()
        
        # Copy nodes
        node_mapping = {}
        for template_node in template.nodes:
            new_node = WorkflowNode(
                workflow_id=new_workflow.id,
                node_type=template_node.node_type,
                name=template_node.name,
                description=template_node.description,
                position_x=template_node.position_x,
                position_y=template_node.position_y,
                config=template_node.config,
                condition_expression=template_node.condition_expression,
                action_type=template_node.action_type,
                action_config=template_node.action_config,
                approval_required_from=template_node.approval_required_from,
                approval_timeout_hours=template_node.approval_timeout_hours,
                localization_enabled=template_node.localization_enabled,
                target_languages=template_node.target_languages
            )
            
            db.session.add(new_node)
            db.session.flush()
            node_mapping[template_node.id] = new_node.id
        
        # Copy connections
        template_connections = WorkflowConnection.query.filter_by(
            workflow_id=template_id
        ).all()
        
        for template_conn in template_connections:
            new_connection = WorkflowConnection(
                workflow_id=new_workflow.id,
                from_node_id=node_mapping[template_conn.from_node_id],
                to_node_id=node_mapping[template_conn.to_node_id],
                condition=template_conn.condition,
                condition_value=template_conn.condition_value
            )
            db.session.add(new_connection)
        
        # Increment download count
        template.downloads_count += 1
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'workflow': new_workflow.to_dict(),
            'message': 'Template downloaded successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@workflow_bp.route('/templates/<template_id>/rate', methods=['POST'])
def rate_template(template_id):
    """Rate a workflow template"""
    try:
        template = Workflow.query.get(template_id)
        if not template or not template.is_template:
            return jsonify({'success': False, 'error': 'Template not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        user_id = data.get('user_id')
        rating = data.get('rating')
        review = data.get('review')
        
        if not user_id or not rating:
            return jsonify({'success': False, 'error': 'User ID and rating are required'}), 400
        
        if not (1 <= rating <= 5):
            return jsonify({'success': False, 'error': 'Rating must be between 1 and 5'}), 400
        
        # Check if user already rated this template
        existing_rating = WorkflowRating.query.filter_by(
            workflow_id=template_id,
            user_id=user_id
        ).first()
        
        if existing_rating:
            # Update existing rating
            old_rating = existing_rating.rating
            existing_rating.rating = rating
            existing_rating.review = review
            existing_rating.updated_at = datetime.utcnow()
        else:
            # Create new rating
            new_rating = WorkflowRating(
                workflow_id=template_id,
                user_id=user_id,
                rating=rating,
                review=review
            )
            db.session.add(new_rating)
            old_rating = 0
        
        db.session.flush()
        
        # Recalculate template rating average
        all_ratings = WorkflowRating.query.filter_by(workflow_id=template_id).all()
        total_rating = sum(r.rating for r in all_ratings)
        rating_count = len(all_ratings)
        
        template.rating_average = total_rating / rating_count if rating_count > 0 else 0
        template.rating_count = rating_count
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Rating submitted successfully',
            'template_rating': {
                'average': template.rating_average,
                'count': template.rating_count
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


# =============================================================================
# SCHEDULING
# =============================================================================

@workflow_bp.route('/<workflow_id>/schedule', methods=['POST'])
def schedule_workflow(workflow_id):
    """Schedule a workflow for automated execution"""
    try:
        workflow = Workflow.query.get(workflow_id)
        if not workflow:
            return jsonify({'success': False, 'error': 'Workflow not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        # Create schedule
        schedule = WorkflowSchedule(
            workflow_id=workflow_id,
            name=data.get('name', f'Schedule for {workflow.name}'),
            cron_expression=data.get('cron_expression'),
            timezone=data.get('timezone', 'UTC'),
            input_data=data.get('input_data', {}),
            max_runs=data.get('max_runs'),
            created_by=data.get('created_by')
        )
        
        # Calculate next run time (simplified - in production use proper cron parser)
        if schedule.cron_expression:
            # For demo, schedule for 1 hour from now
            schedule.next_run_at = datetime.utcnow() + timedelta(hours=1)
        
        db.session.add(schedule)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'schedule': schedule.to_dict(),
            'message': 'Workflow scheduled successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@workflow_bp.route('/schedules', methods=['GET'])
def list_schedules():
    """List workflow schedules"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        is_active = request.args.get('is_active', type=bool)
        
        query = WorkflowSchedule.query
        
        if is_active is not None:
            query = query.filter(WorkflowSchedule.is_active == is_active)
        
        query = query.order_by(WorkflowSchedule.created_at.desc())
        
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        schedules = [schedule.to_dict() for schedule in pagination.items]
        
        return jsonify({
            'success': True,
            'schedules': schedules,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# =============================================================================
# BUILT-IN TEMPLATES
# =============================================================================

@workflow_bp.route('/templates/built-in', methods=['GET'])
def get_built_in_templates():
    """Get built-in workflow templates"""
    try:
        templates = [
            template_service.create_content_creation_template(),
            template_service.create_approval_workflow_template()
        ]
        
        return jsonify({
            'success': True,
            'templates': templates
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@workflow_bp.route('/templates/built-in/<template_name>/create', methods=['POST'])
def create_from_built_in_template(template_name):
    """Create a workflow from a built-in template"""
    try:
        data = request.get_json() or {}
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'success': False, 'error': 'User ID is required'}), 400
        
        # Get template
        if template_name == 'content_creation':
            template_data = template_service.create_content_creation_template()
        elif template_name == 'approval_workflow':
            template_data = template_service.create_approval_workflow_template()
        else:
            return jsonify({'success': False, 'error': 'Template not found'}), 404
        
        # Customize template with user data
        template_data['created_by'] = user_id
        template_data['name'] = data.get('name', template_data['name'])
        template_data['description'] = data.get('description', template_data['description'])
        
        # Create workflow using the existing create_workflow logic
        # (This would be refactored in a real implementation)
        
        return jsonify({
            'success': True,
            'template': template_data,
            'message': 'Built-in template retrieved successfully'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# Error handler
@workflow_bp.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Resource not found'}), 404


@workflow_bp.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'error': 'Internal server error'}), 500